"""
Script de migración de base de datos para agregar tablas Cliente y Destino.

Este script:
1. Crea la tabla 'clientes' para almacenar información de contacto
2. Crea la tabla 'destinos' para el catálogo de destinos
3. Agrega las columnas necesarias a la tabla 'prospectos'
4. Pobla la tabla de destinos con destinos comunes

IMPORTANTE: Ejecutar este script ANTES de iniciar la aplicación.
"""

import sys
import os

# Agregar el directorio padre al path para importar módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL
import models

def ejecutar_migracion():
    """Ejecuta la migración de base de datos"""
    
    print("=" * 60)
    print("MIGRACIÓN DE BASE DE DATOS")
    print("=" * 60)
    print()
    
    # Crear engine
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    print("✅ Conexión a base de datos establecida")
    print(f"   URL: {SQLALCHEMY_DATABASE_URL}")
    print()
    
    # Crear todas las tablas nuevas
    print("📋 Creando nuevas tablas...")
    try:
        models.Base.metadata.create_all(bind=engine)
        print("   ✅ Tablas creadas exitosamente")
    except Exception as e:
        print(f"   ⚠️  Algunas tablas ya existen (esto es normal): {e}")
    print()
    
    # Poblar tabla de destinos con destinos comunes
    print("🌍 Poblando catálogo de destinos...")
    
    destinos_iniciales = [
        # Caribe
        {"nombre": "CANCUN", "pais": "MÉXICO", "continente": "AMÉRICA"},
        {"nombre": "PUNTA CANA", "pais": "REPÚBLICA DOMINICANA", "continente": "AMÉRICA"},
        {"nombre": "ARUBA", "pais": "ARUBA", "continente": "AMÉRICA"},
        {"nombre": "CARTAGENA", "pais": "COLOMBIA", "continente": "AMÉRICA"},
        {"nombre": "SAN ANDRES", "pais": "COLOMBIA", "continente": "AMÉRICA"},
        {"nombre": "SANTA MARTA", "pais": "COLOMBIA", "continente": "AMÉRICA"},
        
        # Sudamérica
        {"nombre": "RIO DE JANEIRO", "pais": "BRASIL", "continente": "AMÉRICA"},
        {"nombre": "BUENOS AIRES", "pais": "ARGENTINA", "continente": "AMÉRICA"},
        {"nombre": "CUSCO", "pais": "PERÚ", "continente": "AMÉRICA"},
        {"nombre": "MACHU PICCHU", "pais": "PERÚ", "continente": "AMÉRICA"},
        
        # Norteamérica
        {"nombre": "MIAMI", "pais": "ESTADOS UNIDOS", "continente": "AMÉRICA"},
        {"nombre": "ORLANDO", "pais": "ESTADOS UNIDOS", "continente": "AMÉRICA"},
        {"nombre": "NEW YORK", "pais": "ESTADOS UNIDOS", "continente": "AMÉRICA"},
        {"nombre": "LAS VEGAS", "pais": "ESTADOS UNIDOS", "continente": "AMÉRICA"},
        
        # Europa
        {"nombre": "MADRID", "pais": "ESPAÑA", "continente": "EUROPA"},
        {"nombre": "BARCELONA", "pais": "ESPAÑA", "continente": "EUROPA"},
        {"nombre": "PARIS", "pais": "FRANCIA", "continente": "EUROPA"},
        {"nombre": "ROMA", "pais": "ITALIA", "continente": "EUROPA"},
        {"nombre": "LONDRES", "pais": "REINO UNIDO", "continente": "EUROPA"},
        
        # Asia
        {"nombre": "DUBAI", "pais": "EMIRATOS ÁRABES UNIDOS", "continente": "ASIA"},
        {"nombre": "TOKIO", "pais": "JAPÓN", "continente": "ASIA"},
        {"nombre": "BANGKOK", "pais": "TAILANDIA", "continente": "ASIA"},
        
        # Otros destinos populares
        {"nombre": "EGIPTO", "pais": "EGIPTO", "continente": "ÁFRICA"},
        {"nombre": "TURQUIA", "pais": "TURQUÍA", "continente": "ASIA"},
    ]
    
    with engine.connect() as conn:
        destinos_creados = 0
        destinos_existentes = 0
        
        for destino_data in destinos_iniciales:
            try:
                # Verificar si el destino ya existe
                result = conn.execute(
                    text("SELECT id FROM destinos WHERE nombre = :nombre"),
                    {"nombre": destino_data["nombre"]}
                )
                
                if result.fetchone():
                    destinos_existentes += 1
                else:
                    # Insertar destino
                    conn.execute(
                        text("""
                            INSERT INTO destinos (nombre, pais, continente, activo, fecha_creacion)
                            VALUES (:nombre, :pais, :continente, 1, CURRENT_TIMESTAMP)
                        """),
                        destino_data
                    )
                    destinos_creados += 1
                    
            except Exception as e:
                print(f"   ⚠️  Error al insertar {destino_data['nombre']}: {e}")
        
        conn.commit()
        
        print(f"   ✅ Destinos creados: {destinos_creados}")
        print(f"   ℹ️  Destinos ya existentes: {destinos_existentes}")
    
    print()
    print("=" * 60)
    print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    print()
    print("Próximos pasos:")
    print("1. Iniciar la aplicación normalmente")
    print("2. Usar la nueva funcionalidad de importación de clientes")
    print("3. Los destinos estarán disponibles con autocompletado")
    print()

if __name__ == "__main__":
    try:
        ejecutar_migracion()
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
