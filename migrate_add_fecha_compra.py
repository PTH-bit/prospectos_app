"""
Script de migración para agregar la columna fecha_compra a la tabla prospectos
"""
from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL
import sys

def migrate_add_fecha_compra():
    """Agregar columna fecha_compra a la tabla prospectos"""
    
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    try:
        with engine.connect() as connection:
            # Verificar si la columna ya existe
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='prospectos' AND column_name='fecha_compra'
            """)
            
            result = connection.execute(check_query)
            exists = result.fetchone()
            
            if exists:
                print("[INFO] La columna 'fecha_compra' ya existe en la tabla 'prospectos'")
                return True
            
            # Agregar la columna fecha_compra
            alter_query = text("""
                ALTER TABLE prospectos 
                ADD COLUMN fecha_compra DATE NULL
            """)
            
            connection.execute(alter_query)
            connection.commit()
            
            print("[OK] Columna 'fecha_compra' agregada exitosamente a la tabla 'prospectos'")
            print("[INFO] La columna es de tipo DATE y permite valores NULL")
            return True
            
    except Exception as e:
        print(f"[ERROR] Error al ejecutar la migracion: {e}")
        return False
    finally:
        engine.dispose()

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACION: Agregar columna fecha_compra")
    print("=" * 60)
    print()
    
    success = migrate_add_fecha_compra()
    
    print()
    if success:
        print("[OK] Migracion completada exitosamente")
        print()
        print("Siguiente paso:")
        print("  - Puedes importar datos con la columna 'fecha_compra'")
        print("  - Los prospectos marcados como 'ganado' registraran automaticamente la fecha")
        sys.exit(0)
    else:
        print("[ERROR] La migracion fallo")
        sys.exit(1)
