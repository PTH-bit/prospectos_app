"""
Script de migración para agregar columnas cliente_id y destino_id a la tabla prospectos.

Este script agrega las columnas necesarias a la tabla existente sin perder datos.
"""

import sys
import os

# Agregar el directorio padre al path para importar módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL

def agregar_columnas_a_prospectos():
    """Agrega las columnas cliente_id y destino_id a la tabla prospectos"""
    
    print("=" * 60)
    print("MIGRACIÓN: Agregar Columnas a Prospectos")
    print("=" * 60)
    print()
    
    # Crear engine
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    print("✅ Conexión a base de datos establecida")
    print()
    
    with engine.connect() as conn:
        try:
            # Verificar si la columna cliente_id ya existe
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='prospectos' AND column_name='cliente_id'
            """))
            
            if result.fetchone():
                print("ℹ️  La columna 'cliente_id' ya existe en la tabla prospectos")
            else:
                print("📝 Agregando columna 'cliente_id' a la tabla prospectos...")
                conn.execute(text("""
                    ALTER TABLE prospectos 
                    ADD COLUMN cliente_id INTEGER
                """))
                
                # Agregar foreign key
                conn.execute(text("""
                    ALTER TABLE prospectos 
                    ADD CONSTRAINT fk_prospectos_cliente 
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
                """))
                print("   ✅ Columna 'cliente_id' agregada exitosamente")
            
            # Verificar si la columna destino_id ya existe
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='prospectos' AND column_name='destino_id'
            """))
            
            if result.fetchone():
                print("ℹ️  La columna 'destino_id' ya existe en la tabla prospectos")
            else:
                print("📝 Agregando columna 'destino_id' a la tabla prospectos...")
                conn.execute(text("""
                    ALTER TABLE prospectos 
                    ADD COLUMN destino_id INTEGER
                """))
                
                # Agregar foreign key
                conn.execute(text("""
                    ALTER TABLE prospectos 
                    ADD CONSTRAINT fk_prospectos_destino 
                    FOREIGN KEY (destino_id) REFERENCES destinos(id)
                """))
                print("   ✅ Columna 'destino_id' agregada exitosamente")
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error al agregar columnas: {e}")
            raise
    
    print()
    print("=" * 60)
    print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    print()
    print("Las columnas 'cliente_id' y 'destino_id' están disponibles en la tabla prospectos")
    print()

if __name__ == "__main__":
    try:
        agregar_columnas_a_prospectos()
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERROR EN LA MIGRACIÓN")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)
