"""
Script de migración para agregar la columna direccion a la tabla prospectos
"""
from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL
import sys

def migrate_add_direccion():
    """Agregar columna direccion a la tabla prospectos"""
    
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    try:
        with engine.connect() as connection:
            # Verificar si la columna ya existe
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='prospectos' AND column_name='direccion'
            """)
            
            result = connection.execute(check_query)
            exists = result.fetchone()
            
            if exists:
                print("[INFO] La columna 'direccion' ya existe en la tabla 'prospectos'")
                return True
            
            # Agregar la columna direccion
            alter_query = text("""
                ALTER TABLE prospectos 
                ADD COLUMN direccion VARCHAR(255) NULL
            """)
            
            connection.execute(alter_query)
            connection.commit()
            
            print("[OK] Columna 'direccion' agregada exitosamente a la tabla 'prospectos'")
            print("[INFO] La columna es de tipo VARCHAR(255) y permite valores NULL")
            return True
            
    except Exception as e:
        print(f"[ERROR] Error al ejecutar la migracion: {e}")
        return False
    finally:
        engine.dispose()

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACION: Agregar columna direccion")
    print("=" * 60)
    print()
    
    success = migrate_add_direccion()
    
    print()
    if success:
        print("[OK] Migracion completada exitosamente")
        print()
        print("Siguiente paso:")
        print("  - El campo 'direccion' aparecera en formularios de clientes ganados")
        print("  - Se normalizara a mayusculas automaticamente")
        sys.exit(0)
    else:
        print("[ERROR] La migracion fallo")
        sys.exit(1)
