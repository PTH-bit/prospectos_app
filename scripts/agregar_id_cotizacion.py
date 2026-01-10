"""
Script para agregar la columna id_cotizacion a la tabla prospectos
"""
import sqlite3
import shutil
from datetime import datetime

# Hacer backup de la base de datos
db_path = "prospectos.db"
backup_path = f"prospectos_backup_id_cotizacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

print(f"Creando backup de la base de datos: {backup_path}")
shutil.copy(db_path, backup_path)
print("✅ Backup creado exitosamente")

# Conectar a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n🔧 Agregando columna id_cotizacion a la tabla prospectos...")

try:
    # Verificar si la columna ya existe
    cursor.execute("PRAGMA table_info(prospectos)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'id_cotizacion' in columns:
        print("⚠️  La columna id_cotizacion ya existe. No se requiere migración.")
    else:
        # Agregar la columna
        cursor.execute("""
            ALTER TABLE prospectos 
            ADD COLUMN id_cotizacion VARCHAR(20)
        """)
        
        conn.commit()
        print("✅ Columna id_cotizacion agregada exitosamente")
        print("✅ La aplicación ahora puede generar IDs de cotización correctamente")
    
except Exception as e:
    conn.rollback()
    print(f"❌ Error: {e}")
    print(f"La base de datos no fue modificada. Puedes restaurar desde: {backup_path}")
    raise

finally:
    conn.close()

print(f"\n✅ Migración completada")
print(f"📁 Backup guardado en: {backup_path}")
print("\n🚀 Ahora puedes reiniciar la aplicación y probar la funcionalidad de ID de cotización")
