from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos PostgreSQL
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Producto24*")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "prospectos_crm")

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Crear todas las tablas en la base de datos"""
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas correctamente")

def reset_database():
    """Eliminar y recrear todas las tablas (solo para desarrollo)"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos reiniciada")

def migrate_database():
    """Migrar base de datos - PostgreSQL maneja esto automáticamente con SQLAlchemy"""
    print("✅ PostgreSQL: Las migraciones se manejan con SQLAlchemy automáticamente")

def agregar_columnas_faltantes():
    """Agregar columnas faltantes a tablas existentes"""
    with engine.connect() as conn:
        try:
            # Verificar y agregar cliente_id a prospectos
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='prospectos' AND column_name='cliente_id'
            """))
            
            if not result.fetchone():
                print("📝 Agregando columna 'cliente_id' a prospectos...")
                conn.execute(text("""
                    ALTER TABLE prospectos 
                    ADD COLUMN cliente_id INTEGER
                """))
                conn.execute(text("""
                    ALTER TABLE prospectos 
                    ADD CONSTRAINT fk_prospectos_cliente 
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
                """))
                conn.commit()
                print("   ✅ Columna 'cliente_id' agregada")
            
            # Verificar y agregar destino_id a prospectos
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='prospectos' AND column_name='destino_id'
            """))
            
            if not result.fetchone():
                print("📝 Agregando columna 'destino_id' a prospectos...")
                conn.execute(text("""
                    ALTER TABLE prospectos 
                    ADD COLUMN destino_id INTEGER
                """))
                conn.execute(text("""
                    ALTER TABLE prospectos 
                    ADD CONSTRAINT fk_prospectos_destino 
                    FOREIGN KEY (destino_id) REFERENCES destinos(id)
                """))
                conn.commit()
                print("   ✅ Columna 'destino_id' agregada")
                
        except Exception as e:
            print(f"⚠️  Error al agregar columnas: {e}")
            conn.rollback()

def poblar_destinos_iniciales():
    """Poblar catálogo de destinos con destinos comunes"""
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
        
        # Otros
        {"nombre": "EGIPTO", "pais": "EGIPTO", "continente": "ÁFRICA"},
        {"nombre": "TURQUIA", "pais": "TURQUÍA", "continente": "ASIA"},
    ]
    
    with engine.connect() as conn:
        destinos_creados = 0
        
        for destino_data in destinos_iniciales:
            try:
                result = conn.execute(
                    text("SELECT id FROM destinos WHERE nombre = :nombre"),
                    {"nombre": destino_data["nombre"]}
                )
                
                if not result.fetchone():
                    conn.execute(
                        text("""
                            INSERT INTO destinos (nombre, pais, continente, activo, fecha_creacion)
                            VALUES (:nombre, :pais, :continente, 1, CURRENT_TIMESTAMP)
                        """),
                        destino_data
                    )
                    destinos_creados += 1
                    
            except Exception as e:
                print(f"⚠️  Error al insertar destino {destino_data['nombre']}: {e}")
        
        if destinos_creados > 0:
            conn.commit()
            print(f"✅ {destinos_creados} destinos iniciales agregados al catálogo")

def inicializar_base_datos():
    """
    Inicialización automática de la base de datos.
    Se ejecuta al iniciar la aplicación.
    """
    print("\n" + "="*60)
    print("🔧 INICIALIZANDO BASE DE DATOS")
    print("="*60)
    
    try:
        # 1. Crear todas las tablas
        print("\n1️⃣ Creando tablas...")
        create_tables()
        
        # 2. Agregar columnas faltantes
        print("\n2️⃣ Verificando columnas...")
        agregar_columnas_faltantes()
        
        # 3. Poblar destinos iniciales
        print("\n3️⃣ Poblando catálogo de destinos...")
        poblar_destinos_iniciales()
        
        print("\n" + "="*60)
        print("✅ INICIALIZACIÓN COMPLETADA")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERROR EN INICIALIZACIÓN")
        print("="*60)
        print(f"Error: {e}\n")
        return False

def check_and_migrate():
    """Verificar y ejecutar migración si es necesario"""
    return inicializar_base_datos()
