"""
Script para agregar la columna agente_original_id a la tabla prospectos.
Esta columna es necesaria para mantener el historial del agente original cuando se reasignan prospectos.
"""

import sqlite3
import shutil
from datetime import datetime

# Hacer backup de la base de datos
db_path = "prospectos.db"
backup_path = f"prospectos_backup_agente_original_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

print(f"Creando backup de la base de datos: {backup_path}")
shutil.copy(db_path, backup_path)
print("Backup creado exitosamente")

# Conectar a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\nAgregando columna agente_original_id a la tabla prospectos...")

try:
    # Verificar si la columna ya existe
    cursor.execute("PRAGMA table_info(prospectos)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'agente_original_id' in columns:
        print("La columna agente_original_id ya existe. No se requiere migración.")
    else:
        # Agregar la columna
        cursor.execute("""
            ALTER TABLE prospectos 
            ADD COLUMN agente_original_id INTEGER
        """)
        
        conn.commit()
        print("Columna agente_original_id agregada exitosamente")
        print("La aplicación ahora puede funcionar correctamente")
    
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
    print(f"La base de datos no fue modificada. Puedes restaurar desde: {backup_path}")
    raise

finally:
    conn.close()

print(f"\nBackup guardado en: {backup_path}")
print("Migración completada. Puedes reiniciar la aplicación.")
