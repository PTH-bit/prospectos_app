"""
Script para migrar datos de SQLite a PostgreSQL
"""
import sqlite3
import psycopg2
from datetime import datetime
import sys

# Configuración
SQLITE_DB = "prospectos.db"
PG_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "Producto24*",
    "database": "prospectos_crm"
}

# Tablas a migrar (en orden de dependencias)
TABLES = [
    "medios_ingreso",
    "usuarios",
    "prospectos",
    "interacciones",
    "documentos",
    "viajes"
]

def migrate_data():
    """Migrar datos de SQLite a PostgreSQL"""
    try:
        # Conectar a SQLite
        print("Conectando a SQLite...")
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        # Conectar a PostgreSQL
        print("Conectando a PostgreSQL...")
        pg_conn = psycopg2.connect(**PG_CONFIG)
        pg_cursor = pg_conn.cursor()
        
        total_registros = 0
        
        for table in TABLES:
            print(f"\nMigrando tabla: {table}")
            
            try:
                # Leer datos de SQLite
                sqlite_cursor.execute(f"SELECT * FROM {table}")
                rows = sqlite_cursor.fetchall()
                
                if not rows:
                    print(f"  - Tabla {table} vacía, saltando...")
                    continue
                
                # Obtener nombres de columnas
                columns = [description[0] for description in sqlite_cursor.description]
                
                # Preparar query de inserción
                placeholders = ','.join(['%s'] * len(columns))
                columns_str = ','.join(columns)
                insert_query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
                
                # Insertar datos en PostgreSQL
                count = 0
                for row in rows:
                    try:
                        pg_cursor.execute(insert_query, tuple(row))
                        count += 1
                    except Exception as e:
                        print(f"  ! Error en fila: {e}")
                        continue
                
                pg_conn.commit()
                total_registros += count
                print(f"  ✓ {count} registros migrados")
                
            except sqlite3.OperationalError as e:
                print(f"  - Tabla {table} no existe en SQLite: {e}")
                continue
            except Exception as e:
                print(f"  ! Error migrando {table}: {e}")
                pg_conn.rollback()
                continue
        
        # Cerrar conexiones
        sqlite_cursor.close()
        sqlite_conn.close()
        pg_cursor.close()
        pg_conn.close()
        
        print(f"\n{'='*50}")
        print(f"MIGRACIÓN COMPLETADA")
        print(f"Total de registros migrados: {total_registros}")
        print(f"{'='*50}")
        
        return True
        
    except Exception as e:
        print(f"\nERROR CRÍTICO: {e}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("MIGRACIÓN DE DATOS: SQLite -> PostgreSQL")
    print("="*50)
    
    success = migrate_data()
    sys.exit(0 if success else 1)
