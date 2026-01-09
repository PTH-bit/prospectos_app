"""
Script para eliminar la restricción UNIQUE del campo email en la tabla usuarios.
Esto permite que múltiples usuarios inactivos compartan el mismo email.
"""

import sqlite3
import shutil
from datetime import datetime

# Hacer backup de la base de datos
db_path = "prospectos.db"
backup_path = f"prospectos_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

print(f"Creando backup de la base de datos: {backup_path}")
shutil.copy(db_path, backup_path)
print("Backup creado exitosamente")

# Conectar a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\nEliminando restricción UNIQUE del campo email...")

try:
    # SQLite no permite modificar restricciones directamente
    # Necesitamos recrear la tabla
    
    # 1. Crear tabla temporal con la nueva estructura
    cursor.execute("""
        CREATE TABLE usuarios_new (
            id INTEGER PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            tipo_usuario VARCHAR(20) NOT NULL DEFAULT 'agente',
            activo INTEGER DEFAULT 1,
            fecha_creacion DATETIME
        )
    """)
    
    # 2. Copiar datos de la tabla original
    cursor.execute("""
        INSERT INTO usuarios_new (id, username, email, hashed_password, tipo_usuario, activo, fecha_creacion)
        SELECT id, username, email, hashed_password, tipo_usuario, activo, fecha_creacion
        FROM usuarios
    """)
    
    # 3. Eliminar tabla original
    cursor.execute("DROP TABLE usuarios")
    
    # 4. Renombrar tabla nueva
    cursor.execute("ALTER TABLE usuarios_new RENAME TO usuarios")
    
    conn.commit()
    print("✓ Restricción UNIQUE eliminada exitosamente")
    print("✓ Ahora puedes importar múltiples usuarios inactivos con el mismo email")
    
except Exception as e:
    conn.rollback()
    print(f"✗ Error: {e}")
    print(f"La base de datos no fue modificada. Puedes restaurar desde: {backup_path}")
    raise

finally:
    conn.close()

print(f"\nBackup guardado en: {backup_path}")
print("Puedes eliminar el backup si todo funciona correctamente")
