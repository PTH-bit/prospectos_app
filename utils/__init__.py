"""
Módulo de utilidades para el CRM ZARITA!
Contiene funciones auxiliares para normalización, fechas y emails.
"""

from .date_utils import parsear_fecha, calcular_rango_fechas, normalizar_fecha_input
from .normalization import (
    normalizar_texto_mayusculas,
    normalizar_numero,
    normalizar_email
)
from .email_utils import enviar_notificacion_email

__all__ = [
    'parsear_fecha',
    'calcular_rango_fechas',
    'normalizar_fecha_input',
    'normalizar_texto_mayusculas',
    'normalizar_numero',
    'normalizar_email',
    'enviar_notificacion_email'
]
