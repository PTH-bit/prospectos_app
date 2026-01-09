"""
Script de migración completa para:
1. Arreglar foreign keys (CASCADE DELETE)
2. Agregar nuevos campos (fecha_nacimiento, numero_identificacion, estado_anterior)
3. Agregar nuevo estado VENTA_CANCELADA
4. Agregar medio de ingreso "Formulario"
"""
import psycopg2
from psycopg2 import sql
import sys

PG_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "Producto24*",
    "database": "prospectos_crm"
}

def ejecutar_migracion():
    try:
        print("="*60)
        print("MIGRACIÓN COMPLETA - Nuevas Funcionalidades")
        print("="*60)
        
        conn = psycopg2.connect(**PG_CONFIG)
        conn.autocommit = False
        cursor = conn.cursor()
        
        # 1. Arreglar foreign keys con CASCADE DELETE
        print("\n1. Arreglando foreign keys...")
        
        # Eliminar constraint existente de historial_estados
        cursor.execute("""
            ALTER TABLE historial_estados 
            DROP CONSTRAINT IF EXISTS historial_estados_prospecto_id_fkey;
        """)
        
        # Agregar con CASCADE DELETE
        cursor.execute("""
            ALTER TABLE historial_estados 
            ADD CONSTRAINT historial_estados_prospecto_id_fkey 
            FOREIGN KEY (prospecto_id) 
            REFERENCES prospectos(id) 
            ON DELETE CASCADE;
        """)
        print("   OK: Foreign key historial_estados arreglada")
        
        # Hacer lo mismo para notificaciones
        cursor.execute("""
            ALTER TABLE notificaciones 
            DROP CONSTRAINT IF EXISTS notificaciones_prospecto_id_fkey;
        """)
        
        cursor.execute("""
            ALTER TABLE notificaciones 
            ADD CONSTRAINT notificaciones_prospecto_id_fkey 
            FOREIGN KEY (prospecto_id) 
            REFERENCES prospectos(id) 
            ON DELETE CASCADE;
        """)
        print("   OK: Foreign key notificaciones arreglada")
        
        # 2. Agregar nuevas columnas a prospectos
        print("\n2. Agregando nuevas columnas a prospectos...")
        
        # Verificar y agregar fecha_nacimiento
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='prospectos' AND column_name='fecha_nacimiento';
        """)
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE prospectos 
                ADD COLUMN fecha_nacimiento DATE;
            """)
            print("   OK: Columna fecha_nacimiento agregada")
        else:
            print("   - fecha_nacimiento ya existe")
        
        # Verificar y agregar numero_identificacion
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='prospectos' AND column_name='numero_identificacion';
        """)
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE prospectos 
                ADD COLUMN numero_identificacion VARCHAR(50);
            """)
            print("   OK: Columna numero_identificacion agregada")
        else:
            print("   - numero_identificacion ya existe")
        
        # Verificar y agregar estado_anterior
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='prospectos' AND column_name='estado_anterior';
        """)
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE prospectos 
                ADD COLUMN estado_anterior VARCHAR(20);
            """)
            print("   OK: Columna estado_anterior agregada")
        else:
            print("   - estado_anterior ya existe")
        
        # 3. Agregar medio de ingreso "Formulario"
        print("\n3. Agregando medio de ingreso 'Formulario'...")
        
        cursor.execute("""
            SELECT nombre FROM medios_ingreso WHERE nombre = 'Formulario';
        """)
        if not cursor.fetchone():
            # Arreglar secuencia primero
            cursor.execute("""
                SELECT setval('medios_ingreso_id_seq', (SELECT MAX(id) FROM medios_ingreso));
            """)
            cursor.execute("""
                INSERT INTO medios_ingreso (nombre, activo) 
                VALUES ('Formulario', 1);
            """)
            print("   OK: Medio 'Formulario' agregado")
        else:
            print("   - Medio 'Formulario' ya existe")
        
        # Commit de todos los cambios
        conn.commit()
        
        print("\n" + "="*60)
        print("MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*60)
        print("\nCambios aplicados:")
        print("  ✓ Foreign keys con CASCADE DELETE")
        print("  ✓ Columna fecha_nacimiento")
        print("  ✓ Columna numero_identificacion")
        print("  ✓ Columna estado_anterior")
        print("  ✓ Medio de ingreso 'Formulario'")
        print("\nNota: El estado VENTA_CANCELADA se maneja en el código (enum)")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = ejecutar_migracion()
    sys.exit(0 if success else 1)
