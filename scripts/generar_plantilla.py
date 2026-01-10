"""
Script para generar la plantilla de Excel actualizada con la columna fecha_compra
"""
import pandas as pd
from datetime import date

# Definir las columnas de la plantilla
columnas = [
    'id_cliente',  # ✅ NUEVO: ID del cliente (se reutiliza)
    'id_solicitud',  # ✅ NUEVO: ID de la solicitud (único por caso)
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
    'numero_identificacion',
    'fecha_compra',  # NUEVA COLUMNA
    'direccion',  # NUEVA COLUMNA
    'empresa_segundo_titular'  # ✅ NUEVO: Empresa o segundo titular
]

# Crear datos de ejemplo
datos_ejemplo = [
    {
        'id_cliente': '',  # ✅ Vacío: Se genera automáticamente
        'id_solicitud': '',  # ✅ Vacío: Se genera automáticamente
        'telefono': '3001234567',
        'indicativo_telefono': '57',
        'nombre': 'Juan',  # O puede usar: 'JUAN PEREZ||EMPRESA XYZ' para auto-parsear
        'apellido': 'Perez',
        'correo_electronico': 'juan.perez@email.com',
        'ciudad_origen': 'Bogota',
        'destino': 'Cancun',
        'fecha_ida': '15/02/2026',
        'fecha_vuelta': '22/02/2026',
        'pasajeros_adultos': 2,
        'pasajeros_ninos': 1,
        'pasajeros_infantes': 0,
        'medio_ingreso': 'REDES',
        'estado': 'nuevo',
        'observaciones': 'Cliente interesado en paquete todo incluido',
        'comentarios': '',
        'agente_asignado': 'agente1',
        'fecha_nacimiento': '15/05/1985',
        'numero_identificacion': '1234567890',
        'fecha_compra': '',  # Vacio para prospectos nuevos
        'direccion': '',  # Vacio para prospectos nuevos
        'empresa_segundo_titular': ''  # ✅ NUEVO: Empresa o segundo titular (o usar || en nombre)
    },
    {
        'id_cliente': 'CL-20250105-0001',  # ✅ Ejemplo de ID existente
        'id_solicitud': 'SOL-20250105-0001',  # ✅ Ejemplo de ID existente
        'telefono': '3009876543',
        'indicativo_telefono': '57',
        'nombre': 'MARIA GONZALEZ||VIAJES COLOMBIA SAS',  # ✅ Ejemplo con separador ||
        'apellido': 'Gonzalez',
        'correo_electronico': 'maria.gonzalez@email.com',
        'ciudad_origen': 'Medellin',
        'destino': 'Cartagena',
        'fecha_ida': '10/01/2025',
        'fecha_vuelta': '15/01/2025',
        'pasajeros_adultos': 2,
        'pasajeros_ninos': 0,
        'pasajeros_infantes': 0,
        'medio_ingreso': 'REFERIDO',
        'estado': 'ganado',
        'observaciones': 'Venta historica - Ya viajo',
        'comentarios': 'Cliente satisfecho',
        'agente_asignado': 'agente1',
        'fecha_nacimiento': '20/08/1990',
        'numero_identificacion': '9876543210',
        'fecha_compra': '05/01/2025',  # Fecha historica de la venta
        'direccion': 'CALLE 123 #45-67 APT 801',  # Direccion del cliente ganado
        'empresa_segundo_titular': ''  # Se parseará automáticamente desde nombre
    }
]

# Crear DataFrame
df = pd.DataFrame(datos_ejemplo)

# Guardar como Excel
output_path = 'static/plantillas/plantilla_prospectos.xlsx'
df.to_excel(output_path, index=False, sheet_name='Prospectos')

print(f"[OK] Plantilla actualizada guardada en: {output_path}")
print(f"Columnas incluidas: {len(columnas)}")
print(f"Filas de ejemplo: {len(datos_ejemplo)}")
print("\nNota importante:")
print("   - La columna 'fecha_compra' es OPCIONAL")
print("   - Solo se usa para importar ventas historicas en estado 'ganado'")
print("   - Si el estado es 'ganado' y no hay fecha_compra, se usa la fecha actual")
print("   - Para prospectos nuevos, dejar vacio")
