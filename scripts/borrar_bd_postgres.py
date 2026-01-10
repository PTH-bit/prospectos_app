"""
Script Python para borrar todas las tablas de PostgreSQL
Ejecutar con: python borrar_bd_postgres.py
"""

from database import engine, Base
import models

def borrar_base_datos():
    print("⚠️  ADVERTENCIA: Esto eliminará TODOS los datos de PostgreSQL")
    confirmacion = input("¿Estás seguro? Escribe 'SI' para continuar: ")
    
    if confirmacion.upper() != "SI":
        print("❌ Operación cancelada")
        return
    
    print("\n🗑️  Borrando todas las tablas...")
    
    try:
        # Eliminar todas las tablas
        Base.metadata.drop_all(bind=engine)
        print("✅ Todas las tablas eliminadas")
        
        # Recrear todas las tablas (vacías)
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas recreadas (vacías)")
        
        print("\n🎉 Base de datos PostgreSQL limpia y lista!")
        print("\nAhora puedes:")
        print("1. Reiniciar el servidor")
        print("2. Crear un usuario administrador")
        print("3. Importar datos desde Excel si es necesario")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    borrar_base_datos()
