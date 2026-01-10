"""
Script para crear la base de datos PostgreSQL
"""
import psycopg2
from psycopg2 import sql
import sys

try:
    # Conectar a PostgreSQL
    print("Conectando a PostgreSQL...")
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="Producto24*",
        database="postgres"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Verificar si existe
    cursor.execute("SELECT 1 FROM pg_database WHERE datname='prospectos_crm'")
    exists = cursor.fetchone()
    
    if exists:
        print("OK: Base de datos 'prospectos_crm' ya existe")
    else:
        # Crear base de datos
        cursor.execute("CREATE DATABASE prospectos_crm")
        print("OK: Base de datos 'prospectos_crm' creada exitosamente")
    
    cursor.close()
    conn.close()
    sys.exit(0)
    
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
