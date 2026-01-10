"""
Script de migración: Agregar id_solicitud y modificar id_cliente

Este script:
1. Agrega la columna id_solicitud a la tabla prospectos
2. Elimina la restricción UNIQUE de id_cliente
3. Genera id_solicitud para todos los registros existentes
4. Agrupa prospectos por teléfono y asigna el mismo id_cliente a registros del mismo cliente

IMPORTANTE: Hacer backup de la base de datos antes de ejecutar
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL
from datetime import datetime

def migrar_ids():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    with engine.connect() as conn:
        print("🔄 Iniciando migración de IDs...")
        
        # 1. Agregar columna id_solicitud
        print("\n1️⃣ Agregando columna id_solicitud...")
        try:
            conn.execute(text("""
                ALTER TABLE prospectos 
                ADD COLUMN IF NOT EXISTS id_solicitud VARCHAR(20) UNIQUE;
            """))
            conn.commit()
            print("✅ Columna id_solicitud agregada")
        except Exception as e:
            print(f"⚠️ Error al agregar columna (puede que ya exista): {e}")
        
        # 2. Eliminar restricción UNIQUE de id_cliente
        print("\n2️⃣ Modificando restricción de id_cliente...")
        try:
            # Primero obtener el nombre de la restricción
            result = conn.execute(text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'prospectos' 
                AND constraint_type = 'UNIQUE' 
                AND constraint_name LIKE '%id_cliente%';
            """))
            constraint = result.fetchone()
            
            if constraint:
                constraint_name = constraint[0]
                conn.execute(text(f"ALTER TABLE prospectos DROP CONSTRAINT {constraint_name};"))
                conn.commit()
                print(f"✅ Restricción UNIQUE eliminada de id_cliente ({constraint_name})")
            else:
                print("ℹ️ No se encontró restricción UNIQUE en id_cliente")
        except Exception as e:
            print(f"⚠️ Error al modificar restricción: {e}")
        
        # 3. Agregar índice a id_cliente (para búsquedas rápidas)
        print("\n3️⃣ Agregando índice a id_cliente...")
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_prospectos_id_cliente 
                ON prospectos(id_cliente);
            """))
            conn.commit()
            print("✅ Índice agregado a id_cliente")
        except Exception as e:
            print(f"⚠️ Error al agregar índice: {e}")
        
        # 4. Generar id_solicitud para registros existentes
        print("\n4️⃣ Generando id_solicitud para registros existentes...")
        try:
            # Obtener todos los prospectos sin id_solicitud
            result = conn.execute(text("""
                SELECT id, fecha_registro 
                FROM prospectos 
                WHERE id_solicitud IS NULL 
                ORDER BY id;
            """))
            prospectos = result.fetchall()
            
            print(f"📊 Encontrados {len(prospectos)} registros sin id_solicitud")
            
            for prospecto in prospectos:
                prospecto_id = prospecto[0]
                fecha_registro = prospecto[1]
                
                # Generar id_solicitud basado en la fecha de registro
                timestamp = fecha_registro.strftime("%Y%m%d")
                id_solicitud = f"SOL-{timestamp}-{prospecto_id:04d}"
                
                conn.execute(text("""
                    UPDATE prospectos 
                    SET id_solicitud = :id_solicitud 
                    WHERE id = :prospecto_id;
                """), {"id_solicitud": id_solicitud, "prospecto_id": prospecto_id})
            
            conn.commit()
            print(f"✅ Generados {len(prospectos)} id_solicitud")
        except Exception as e:
            print(f"❌ Error al generar id_solicitud: {e}")
            conn.rollback()
            return False
        
        # 5. Agrupar prospectos por teléfono y reutilizar id_cliente
        print("\n5️⃣ Agrupando prospectos por teléfono y reutilizando id_cliente...")
        try:
            # Obtener grupos de prospectos con el mismo teléfono
            result = conn.execute(text("""
                SELECT telefono, MIN(id) as primer_id, COUNT(*) as total
                FROM prospectos
                WHERE telefono IS NOT NULL AND telefono != ''
                GROUP BY telefono
                HAVING COUNT(*) > 1
                ORDER BY MIN(id);
            """))
            grupos = result.fetchall()
            
            print(f"📊 Encontrados {len(grupos)} clientes con múltiples registros")
            
            for grupo in grupos:
                telefono = grupo[0]
                primer_id = grupo[1]
                total = grupo[2]
                
                # Obtener el id_cliente del primer registro
                result_cliente = conn.execute(text("""
                    SELECT id_cliente 
                    FROM prospectos 
                    WHERE id = :primer_id;
                """), {"primer_id": primer_id})
                id_cliente_original = result_cliente.fetchone()[0]
                
                if id_cliente_original:
                    # Actualizar todos los registros con el mismo teléfono
                    conn.execute(text("""
                        UPDATE prospectos 
                        SET id_cliente = :id_cliente 
                        WHERE telefono = :telefono AND id != :primer_id;
                    """), {
                        "id_cliente": id_cliente_original, 
                        "telefono": telefono, 
                        "primer_id": primer_id
                    })
                    print(f"  ♻️ Cliente {id_cliente_original}: {total} registros agrupados")
            
            conn.commit()
            print(f"✅ Agrupación completada")
        except Exception as e:
            print(f"❌ Error al agrupar prospectos: {e}")
            conn.rollback()
            return False
        
        print("\n✅ Migración completada exitosamente!")
        
        # Mostrar resumen
        print("\n📊 RESUMEN:")
        result = conn.execute(text("SELECT COUNT(*) FROM prospectos;"))
        total_prospectos = result.fetchone()[0]
        
        result = conn.execute(text("SELECT COUNT(DISTINCT id_cliente) FROM prospectos WHERE id_cliente IS NOT NULL;"))
        total_clientes = result.fetchone()[0]
        
        result = conn.execute(text("SELECT COUNT(*) FROM prospectos WHERE id_solicitud IS NOT NULL;"))
        total_solicitudes = result.fetchone()[0]
        
        print(f"  Total prospectos: {total_prospectos}")
        print(f"  Total clientes únicos: {total_clientes}")
        print(f"  Total solicitudes: {total_solicitudes}")
        
        return True

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACIÓN: Agregar id_solicitud y modificar id_cliente")
    print("=" * 60)
    print("\n⚠️  ADVERTENCIA: Este script modificará la estructura de la base de datos")
    print("⚠️  Asegúrate de tener un backup antes de continuar\n")
    
    respuesta = input("¿Deseas continuar? (si/no): ")
    
    if respuesta.lower() in ['si', 's', 'yes', 'y']:
        if migrar_ids():
            print("\n🎉 Migración completada con éxito!")
        else:
            print("\n❌ La migración falló. Revisa los errores anteriores.")
    else:
        print("\n❌ Migración cancelada por el usuario")
