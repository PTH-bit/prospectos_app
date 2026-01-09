"""
Script para ejecutar la migración de soft delete
Ejecutar con: python ejecutar_migracion_soft_delete.py
"""

from database import engine

def ejecutar_migracion():
    print("Ejecutando migración: Agregar columna fecha_eliminacion...")
    
    with engine.connect() as conn:
        try:
            # Agregar columna
            conn.execute("""
                ALTER TABLE prospectos 
                ADD COLUMN IF NOT EXISTS fecha_eliminacion TIMESTAMP;
            """)
            print("✅ Columna fecha_eliminacion agregada")
            
            # Crear índice
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_prospectos_fecha_eliminacion 
                ON prospectos(fecha_eliminacion);
            """)
            print("✅ Índice creado")
            
            conn.commit()
            print("\n🎉 Migración completada exitosamente!")
            
        except Exception as e:
            print(f"❌ Error en la migración: {e}")
            conn.rollback()

if __name__ == "__main__":
    ejecutar_migracion()
