"""
Script para actualizar la plantilla de Excel de prospectos
Agrega las columnas: fecha_nacimiento y numero_identificacion
"""
import pandas as pd
import os

# Ruta de la plantilla
plantilla_path = "static/plantillas/plantilla_prospectos.xlsx"

try:
    # Leer la plantilla existente
    df = pd.read_excel(plantilla_path)
    
    print(f"Columnas actuales: {list(df.columns)}")
    
    # Verificar si las columnas ya existen
    columnas_nuevas = []
    
    if 'fecha_nacimiento' not in df.columns:
        df['fecha_nacimiento'] = None
        columnas_nuevas.append('fecha_nacimiento')
    
    if 'numero_identificacion' not in df.columns:
        df['numero_identificacion'] = None
        columnas_nuevas.append('numero_identificacion')
    
    if columnas_nuevas:
        # Guardar la plantilla actualizada
        df.to_excel(plantilla_path, index=False)
        print(f"\n✓ Plantilla actualizada exitosamente")
        print(f"✓ Columnas agregadas: {', '.join(columnas_nuevas)}")
        print(f"\nColumnas finales: {list(df.columns)}")
    else:
        print("\n- Las columnas ya existen en la plantilla")
    
except FileNotFoundError:
    print(f"ERROR: No se encontró la plantilla en {plantilla_path}")
    print("\nCreando nueva plantilla con todas las columnas...")
    
    # Crear plantilla desde cero
    columnas = [
        'telefono',
        'indicativo_telefono',
        'nombre',
        'apellido',
        'correo_electronico',
        'ciudad_origen',
        'destino',
        'fecha_ida',
        'fecha_vuelta',
        'pasajeros_adultos',
        'pasajeros_ninos',
        'pasajeros_infantes',
        'medio_ingreso',
        'estado',
        'observaciones',
        'comentarios',
        'agente_asignado',
        'fecha_nacimiento',
        'numero_identificacion'
    ]
    
    # Crear DataFrame vacío con las columnas
    df_nuevo = pd.DataFrame(columns=columnas)
    
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(plantilla_path), exist_ok=True)
    
    # Guardar plantilla
    df_nuevo.to_excel(plantilla_path, index=False)
    print(f"✓ Plantilla creada en {plantilla_path}")
    print(f"✓ Columnas: {columnas}")

except Exception as e:
    print(f"ERROR: {e}")
