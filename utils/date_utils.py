"""
Utilidades para manejo de fechas en el CRM ZARITA!
"""

from datetime import datetime, date, timedelta
from typing import Optional


def parsear_fecha(fecha_str: str) -> Optional[date]:
    """Helper para parsear fechas en formatos DD/MM/YYYY o YYYY-MM-DD"""
    if not fecha_str:
        return None
    try:
        return datetime.strptime(fecha_str, "%d/%m/%Y").date()
    except ValueError:
        try:
            return datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            print(f"⚠️ Error parseando fecha: {fecha_str}")
            return None


def normalizar_fecha_input(fecha_str: str) -> Optional[date]:
    """Parsea fecha de input HTML (YYYY-MM-DD) o DD/MM/YYYY a objeto date."""
    if not fecha_str or not str(fecha_str).strip():
        return None
    fecha_str = str(fecha_str).strip()
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        try:
            return datetime.strptime(fecha_str, "%d/%m/%Y").date()
        except ValueError:
            print(f"⚠️ Error parseando fecha: {fecha_str}")
            return None


def calcular_rango_fechas(periodo: str, fecha_inicio: str = None, fecha_fin: str = None):
    """Calcula el rango de fechas según el periodo seleccionado"""
    hoy = date.today()
    
    fecha_inicio_obj = hoy
    fecha_fin_obj = hoy

    if periodo == "personalizado" and fecha_inicio and fecha_fin:
        # Usar fechas personalizadas
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, "%d/%m/%Y").date()
            fecha_fin_obj = datetime.strptime(fecha_fin, "%d/%m/%Y").date()
        except ValueError:
            # Si hay error en el formato, usar mes actual por defecto
            print("⚠️ Error en formato de fecha personalizada, usando mes actual")
            pass
    
    elif periodo == "dia":
        # Hoy
        fecha_inicio_obj = hoy
        fecha_fin_obj = hoy
    elif periodo == "semana":
        # Esta semana (lunes a domingo)
        fecha_inicio_obj = hoy - timedelta(days=hoy.weekday())
        fecha_fin_obj = fecha_inicio_obj + timedelta(days=6)
    elif periodo == "año":
        # Este año
        fecha_inicio_obj = date(hoy.year, 1, 1)
        fecha_fin_obj = date(hoy.year, 12, 31)
    else:
        # Mes actual (por defecto)
        fecha_inicio_obj = date(hoy.year, hoy.month, 1)
        if hoy.month == 12:
            fecha_fin_obj = date(hoy.year + 1, 1, 1) - timedelta(days=1)
        else:
            fecha_fin_obj = date(hoy.year, hoy.month + 1, 1) - timedelta(days=1)
    
    # Convertir a datetime con horas inicio/fin del día
    fecha_inicio_dt = datetime.combine(fecha_inicio_obj, datetime.min.time())
    fecha_fin_dt = datetime.combine(fecha_fin_obj, datetime.max.time())
    
    return fecha_inicio_dt, fecha_fin_dt
