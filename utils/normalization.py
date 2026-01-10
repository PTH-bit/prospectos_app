"""
Utilidades para normalización de datos en el CRM ZARITA!
"""

import re
from typing import Optional


def normalizar_texto_mayusculas(texto: str) -> Optional[str]:
    """Convierte texto a mayúsculas y elimina espacios extras. Retorna None si vacío."""
    if not texto or not str(texto).strip():
        return None
    return str(texto).strip().upper()


def normalizar_numero(numero: str) -> str:
    """Remueve espacios, guiones y símbolos de números. Solo deja dígitos."""
    if not numero:
        return ""
    return re.sub(r'[^0-9]', '', str(numero))


def normalizar_email(email: str) -> Optional[str]:
    """Normaliza email a minúsculas y elimina espacios."""
    if not email or not str(email).strip():
        return None
    return str(email).strip().lower()
