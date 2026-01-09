"""
Script para actualizar plantilla de usuarios con ejemplo de usuario inactivo
"""

import pandas as pd
import os

# Crear directorio si no existe
os.makedirs("static/plantillas", exist_ok=True)

# Datos de ejemplo para usuarios
usuarios_data = {
    'username': ['juan_agente', 'maria_supervisor', 'pedro_admin', 'carlos_retirado'],
    'email': ['juan@agencia.com', 'maria@agencia.com', 'pedro@agencia.com', 'carlos@agencia.com'],
    'password': ['agente123', 'supervisor123', 'admin123', 'temp123'],
    'tipo_usuario': ['agente', 'supervisor', 'administrador', 'agente'],
    'activo': [1, 1, 1, 0]
}

# Crear DataFrame
df_usuarios = pd.DataFrame(usuarios_data)

# Guardar como Excel
df_usuarios.to_excel('static/plantillas/plantilla_usuarios.xlsx', index=False, sheet_name='Usuarios')

print("Plantilla de usuarios actualizada con ejemplo de usuario inactivo")
print("Archivo: static/plantillas/plantilla_usuarios.xlsx")
print("\nEjemplo de usuario inactivo:")
print("- username: carlos_retirado")
print("- activo: 0")
print("- Al importar, su email cambiara a servicioclientetravelhouse@gmail.com")
print("- Se generara password aleatorio")
print("- Sus prospectos activos se reasignaran a servicio_cliente")
