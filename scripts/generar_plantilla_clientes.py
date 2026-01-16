"""
Script para generar la plantilla de Excel para importación de CLIENTES (sin solicitudes)
"""
import pandas as pd
from datetime import date

# Definir las columnas de la plantilla de clientes
columnas = [
    'telefono',
    'indicativo_telefono',
    'nombre',
    'apellido',
    'correo_electronico',
    'telefono_secundario',
    'indicativo_telefono_secundario',
    'fecha_nacimiento',
    'numero_identificacion',
    'direccion',
    'agente_asignado'
]

# Crear datos de ejemplo
datos_ejemplo = [
    {
        'telefono': '3001234567',
        'indicativo_telefono': '57',
        'nombre': 'JUAN',
        'apellido': 'PEREZ',
        'correo_electronico': 'juan.perez@email.com',
        'telefono_secundario': '',
        'indicativo_telefono_secundario': '57',
        'fecha_nacimiento': '15/05/1985',
        'numero_identificacion': '1234567890',
        'direccion': 'CALLE 123 #45-67',
        'agente_asignado': 'agente1'
    },
    {
        'telefono': '3009876543',
        'indicativo_telefono': '57',
        'nombre': 'MARIA',
        'apellido': 'GONZALEZ',
        'correo_electronico': 'maria.gonzalez@email.com',
        'telefono_secundario': '3101234567',
        'indicativo_telefono_secundario': '57',
        'fecha_nacimiento': '20/08/1990',
        'numero_identificacion': '9876543210',
        'direccion': 'CARRERA 45 #12-34 APT 501',
        'agente_asignado': 'agente1'
    },
    {
        'telefono': '3157654321',
        'indicativo_telefono': '57',
        'nombre': '',  # Ejemplo: solo teléfono y agente
        'apellido': '',
        'correo_electronico': '',
        'telefono_secundario': '',
        'indicativo_telefono_secundario': '57',
        'fecha_nacimiento': '',
        'numero_identificacion': '',
        'direccion': '',
        'agente_asignado': 'agente1'
    }
]

# Crear DataFrame
df = pd.DataFrame(datos_ejemplo)

# Guardar como Excel
output_path = 'static/plantillas/plantilla_clientes.xlsx'
df.to_excel(output_path, index=False, sheet_name='Clientes')

print(f"✅ Plantilla de clientes guardada en: {output_path}")
print(f"   Columnas incluidas: {len(columnas)}")
print(f"   Filas de ejemplo: {len(datos_ejemplo)}")
print()
print("Nota importante:")
print("   - Esta plantilla es SOLO para importar CLIENTES (información de contacto)")
print("   - NO se crearán solicitudes de viaje")
print("   - El campo 'telefono' es OBLIGATORIO")
print("   - Todos los demás campos son opcionales")
print("   - Si el cliente ya existe (mismo teléfono), se actualizarán sus datos")
