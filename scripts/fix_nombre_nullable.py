"""
Script para hacer el campo 'nombre' nullable en la tabla prospectos
Solo telefono y medio_ingreso son campos obligatorios
"""
import sys
import os

# Agregar el directorio padre al path para importar database y models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database import engine, SessionLocal

def fix_nombre_nullable():
    """Altera la columna nombre para permitir valores NULL"""
    db = SessionLocal()
    
    try:
        print("🔧 Modificando columna 'nombre' para permitir valores NULL...")
        
        # Ejecutar ALTER TABLE para hacer la columna nullable
        db.execute(text("""
            ALTER TABLE prospectos 
            ALTER COLUMN nombre DROP NOT NULL;
        """))
        
        db.commit()
        print("✅ Columna 'nombre' ahora permite valores NULL")
        
    except Exception as e:
        print(f"❌ Error al modificar columna: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("SCRIPT: Hacer campo 'nombre' nullable")
    print("=" * 60)
    
    respuesta = input("¿Deseas continuar? (s/n): ")
    if respuesta.lower() == 's':
        fix_nombre_nullable()
        print("\n✅ Migración completada exitosamente")
    else:
        print("❌ Operación cancelada")
