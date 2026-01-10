"""
Módulo para importar datos desde archivos Excel.
Soporta importación de usuarios y prospectos/clientes.
"""

import pandas as pd
import re
import secrets
import string
from datetime import datetime
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
from models import Usuario, Prospecto, MedioIngreso, TipoUsuario, EstadoProspecto
from auth import get_password_hash


def validar_archivo_excel(archivo) -> Tuple[bool, str]:
    """
    Valida que el archivo sea un Excel válido (.xlsx o .xls)
    
    Args:
        archivo: Archivo subido
        
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    if not archivo.filename:
        return False, "No se seleccionó ningún archivo"
    
    extension = archivo.filename.lower().split('.')[-1]
    if extension not in ['xlsx', 'xls']:
        return False, f"Formato de archivo no válido. Se esperaba .xlsx o .xls, se recibió .{extension}"
    
    return True, ""


def validar_email(email: str) -> bool:
    """
    Valida el formato de un email
    
    Args:
        email: Email a validar
        
    Returns:
        True si el email es válido, False en caso contrario
    """
    if not email or pd.isna(email):
        return False
    
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, str(email)))


def limpiar_telefono(telefono: str) -> str:
    """
    Limpia un número de teléfono removiendo caracteres especiales y espacios
    
    Args:
        telefono: Número de teléfono a limpiar
        
    Returns:
        Teléfono limpio (solo dígitos)
    """
    if not telefono or pd.isna(telefono):
        return ""
    
    # Convertir a string y remover todo excepto dígitos
    telefono_str = str(telefono).strip()
    telefono_limpio = re.sub(r'[^0-9]', '', telefono_str)
    
    return telefono_limpio


def parsear_fecha(fecha_str) -> datetime.date:
    """
    Parsea una fecha en formatos DD/MM/YYYY o YYYY-MM-DD
    
    Args:
        fecha_str: String con la fecha
        
    Returns:
        Objeto date o None si no se puede parsear
    """
    if not fecha_str or pd.isna(fecha_str):
        return None
    
    # Si ya es un objeto datetime de pandas
    if isinstance(fecha_str, pd.Timestamp):
        return fecha_str.date()
    
    fecha_str = str(fecha_str).strip()
    
    # Intentar formato DD/MM/YYYY
    try:
        return datetime.strptime(fecha_str, "%d/%m/%Y").date()
    except ValueError:
        pass
    
    # Intentar formato YYYY-MM-DD
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        pass
    
    return None


def importar_usuarios_desde_excel(archivo_path: str, db: Session) -> Dict:
    """
    Importa usuarios desde un archivo Excel.
    
    Columnas esperadas:
    - username (requerido)
    - email (requerido)
    - password (requerido)
    - tipo_usuario (requerido: administrador/supervisor/agente)
    - activo (opcional, default: 1)
    
    Args:
        archivo_path: Ruta al archivo Excel
        db: Sesión de base de datos
        
    Returns:
        Diccionario con resultados de la importación
    """
    resultado = {
        'exitosos': 0,
        'errores': [],
        'usuarios_creados': []
    }
    
    try:
        # Leer archivo Excel
        df = pd.read_excel(archivo_path)
        
        # Validar columnas requeridas
        columnas_requeridas = ['username', 'email', 'password', 'tipo_usuario']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        
        if columnas_faltantes:
            resultado['errores'].append({
                'fila': 0,
                'error': f"Columnas faltantes: {', '.join(columnas_faltantes)}"
            })
            return resultado
        
        # Procesar cada fila
        for index, row in df.iterrows():
            fila_num = index + 2  # +2 porque Excel empieza en 1 y tiene encabezado
            
            try:
                # Validar campos requeridos
                username = row.get('username')
                email = row.get('email')
                password = row.get('password')
                tipo_usuario = row.get('tipo_usuario')
                
                if pd.isna(username) or not str(username).strip():
                    resultado['errores'].append({
                        'fila': fila_num,
                        'error': 'Username es requerido'
                    })
                    continue
                
                username = str(username).strip()
                
                # Obtener campo activo ANTES de validar email
                activo = row.get('activo', 1)
                if pd.isna(activo):
                    activo = 1
                else:
                    activo = int(activo)
                
                # ✅ MANEJO DE USUARIOS INACTIVOS - Validación de email especial
                if activo == 0:
                    # Para usuarios inactivos, el email puede estar vacío
                    # Se asignará automáticamente el email de servicio al cliente
                    email = "servicioclientetravelhouse@gmail.com"
                    
                    # Generar password aleatorio si no se proporciona
                    if pd.isna(password) or not str(password).strip():
                        caracteres = string.ascii_letters + string.digits
                        password = ''.join(secrets.choice(caracteres) for _ in range(16))
                    else:
                        password = str(password).strip()
                else:
                    # Para usuarios activos, validar email normalmente
                    if pd.isna(email) or not validar_email(email):
                        resultado['errores'].append({
                            'fila': fila_num,
                            'error': 'Email inválido o faltante'
                        })
                        continue
                    
                    email = str(email).strip()
                    
                    if pd.isna(password) or not str(password).strip():
                        resultado['errores'].append({
                            'fila': fila_num,
                            'error': 'Password es requerido'
                        })
                        continue
                    
                    password = str(password).strip()
                
                if pd.isna(tipo_usuario) or not str(tipo_usuario).strip():
                    resultado['errores'].append({
                        'fila': fila_num,
                        'error': 'Tipo de usuario es requerido'
                    })
                    continue
                
                tipo_usuario = str(tipo_usuario).strip().lower()
                
                # Validar tipo de usuario
                tipos_validos = ['administrador', 'supervisor', 'agente']
                if tipo_usuario not in tipos_validos:
                    resultado['errores'].append({
                        'fila': fila_num,
                        'error': f'Tipo de usuario inválido. Debe ser: {", ".join(tipos_validos)}'
                    })
                    continue
                
                # ✅ Verificar duplicados según el tipo de usuario
                if activo == 0:
                    # Para usuarios inactivos, solo verificar username
                    # (permitir email duplicado ya que todos usan servicioclientetravelhouse@gmail.com)
                    usuario_existente = db.query(Usuario).filter(
                        Usuario.username == username
                    ).first()
                else:
                    # Para usuarios activos, verificar username Y email
                    usuario_existente = db.query(Usuario).filter(
                        (Usuario.username == username) | (Usuario.email == email)
                    ).first()
                
                if usuario_existente:
                    resultado['errores'].append({
                        'fila': fila_num,
                        'error': f'Usuario ya existe: {username}'
                    })
                    continue
                
                # Crear usuario
                nuevo_usuario = Usuario(
                    username=username,
                    email=email,
                    hashed_password=get_password_hash(password),
                    tipo_usuario=tipo_usuario,
                    activo=activo
                )
                
                db.add(nuevo_usuario)
                db.commit()
                db.refresh(nuevo_usuario)
                
                # ✅ REASIGNAR PROSPECTOS SI ES USUARIO INACTIVO
                if activo == 0:
                    # Obtener usuario de servicio al cliente
                    servicio_cliente = db.query(Usuario).filter(
                        Usuario.username == "servicio_cliente"
                    ).first()
                    
                    if servicio_cliente:
                        # Buscar prospectos activos asignados a este usuario
                        prospectos_activos = db.query(Prospecto).filter(
                            Prospecto.agente_asignado_id == nuevo_usuario.id,
                            Prospecto.estado.in_(['nuevo', 'en_seguimiento', 'cotizado'])
                        ).all()
                        
                        # Reasignar a servicio al cliente y guardar original
                        for prospecto in prospectos_activos:
                            prospecto.agente_original_id = nuevo_usuario.id
                            prospecto.agente_asignado_id = servicio_cliente.id
                        
                        db.commit()
                
                resultado['usuarios_creados'].append(nuevo_usuario)
                resultado['exitosos'] += 1
                
            except Exception as e:
                db.rollback()
                resultado['errores'].append({
                    'fila': fila_num,
                    'error': f'Error al procesar: {str(e)}'
                })
        
    except Exception as e:
        resultado['errores'].append({
            'fila': 0,
            'error': f'Error al leer archivo: {str(e)}'
        })
    
    return resultado


def importar_prospectos_desde_excel(archivo_path: str, db: Session) -> Dict:
    """
    Importa prospectos/clientes desde un archivo Excel.
    
    Columnas esperadas:
    - telefono (requerido, sin caracteres especiales ni espacios)
    - indicativo_telefono (opcional, default: "57")
    - nombre (opcional)
    - apellido (opcional)
    - correo_electronico (opcional, con validación de formato)
    - ciudad_origen (opcional)
    - destino (opcional)
    - fecha_ida (opcional, formato: DD/MM/YYYY o YYYY-MM-DD)
    - fecha_vuelta (opcional, formato: DD/MM/YYYY o YYYY-MM-DD)
    - pasajeros_adultos (opcional, default: 1)
    - pasajeros_ninos (opcional, default: 0)
    - pasajeros_infantes (opcional, default: 0)
    - medio_ingreso (opcional, nombre del medio)
    - estado (opcional, default: "nuevo")
    - observaciones (opcional)
    - comentarios (opcional, comentarios de gestión)
    - agente_asignado (opcional, username del agente)
    - fecha_nacimiento (opcional, formato: DD/MM/YYYY o YYYY-MM-DD)
    - numero_identificacion (opcional, cédula/pasaporte)
    - fecha_compra (opcional, formato: DD/MM/YYYY o YYYY-MM-DD, para ventas históricas)
    
    Si existe un prospecto con el mismo teléfono, se crea como cliente recurrente.
    
    Args:
        archivo_path: Ruta al archivo Excel
        db: Sesión de base de datos
        
    Returns:
        Diccionario con resultados de la importación
    """
    resultado = {
        'exitosos': 0,
        'errores': [],
        'prospectos_creados': [],
        'recurrentes': 0
    }
    
    try:
        # Leer archivo Excel
        df = pd.read_excel(archivo_path)
        
        # Validar columna requerida
        if 'telefono' not in df.columns:
            resultado['errores'].append({
                'fila': 0,
                'error': 'Columna "telefono" es requerida'
            })
            return resultado
        
        # Procesar cada fila
        for index, row in df.iterrows():
            fila_num = index + 2  # +2 porque Excel empieza en 1 y tiene encabezado
            
            try:
                # Validar y limpiar teléfono (requerido)
                telefono = row.get('telefono')
                
                if pd.isna(telefono) or not str(telefono).strip():
                    resultado['errores'].append({
                        'fila': fila_num,
                        'error': 'Teléfono es requerido'
                    })
                    continue
                
                telefono = limpiar_telefono(telefono)
                
                if not telefono:
                    resultado['errores'].append({
                        'fila': fila_num,
                        'error': 'Teléfono inválido (debe contener solo dígitos)'
                    })
                    continue
                
                # Indicativo de teléfono
                indicativo_telefono = row.get('indicativo_telefono', '57')
                if pd.isna(indicativo_telefono):
                    indicativo_telefono = '57'
                else:
                    indicativo_telefono = str(indicativo_telefono).strip()
                
                # Verificar si existe un prospecto con este teléfono
                prospecto_existente = db.query(Prospecto).filter(
                    Prospecto.telefono == telefono
                ).first()
                
                es_recurrente = prospecto_existente is not None
                prospecto_original_id = prospecto_existente.id if es_recurrente else None
                
                # Campos opcionales - ✅ NORMALIZAR A MAYÚSCULAS
                nombre = row.get('nombre')
                empresa_segundo_titular = None  # Inicializar
                
                if not pd.isna(nombre):
                    nombre = str(nombre).strip().upper()  # ✅ MAYÚSCULAS
                    
                    # ✅ NUEVO: Detectar separador || para empresa/segundo titular
                    if '||' in nombre:
                        partes = nombre.split('||', 1)  # Dividir solo en la primera ocurrencia
                        nombre = partes[0].strip()
                        empresa_segundo_titular = partes[1].strip() if len(partes) > 1 else None
                else:
                    nombre = None
                
                # Si no se detectó en nombre, verificar si viene en columna separada
                if not empresa_segundo_titular:
                    empresa_segundo_titular_col = row.get('empresa_segundo_titular')
                    if not pd.isna(empresa_segundo_titular_col):
                        empresa_segundo_titular = str(empresa_segundo_titular_col).strip().upper()
                
                apellido = row.get('apellido')
                if not pd.isna(apellido):
                    apellido = str(apellido).strip().upper()  # ✅ MAYÚSCULAS
                else:
                    apellido = None
                
                # Validar email si se proporciona
                correo_electronico = row.get('correo_electronico')
                if not pd.isna(correo_electronico):
                    correo_electronico = str(correo_electronico).strip()
                    if not validar_email(correo_electronico):
                        resultado['errores'].append({
                            'fila': fila_num,
                            'error': f'Email inválido: {correo_electronico}'
                        })
                        continue
                else:
                    correo_electronico = None
                
                ciudad_origen = row.get('ciudad_origen')
                if not pd.isna(ciudad_origen):
                    ciudad_origen = str(ciudad_origen).strip().upper()  # ✅ MAYÚSCULAS
                else:
                    ciudad_origen = None
                
                destino = row.get('destino')
                if not pd.isna(destino):
                    destino = str(destino).strip().upper()  # ✅ MAYÚSCULAS
                else:
                    destino = None
                
                # Fechas
                fecha_ida = parsear_fecha(row.get('fecha_ida'))
                fecha_vuelta = parsear_fecha(row.get('fecha_vuelta'))
                
                # Pasajeros
                pasajeros_adultos = row.get('pasajeros_adultos', 1)
                if pd.isna(pasajeros_adultos):
                    pasajeros_adultos = 1
                else:
                    pasajeros_adultos = int(pasajeros_adultos)
                
                pasajeros_ninos = row.get('pasajeros_ninos', 0)
                if pd.isna(pasajeros_ninos):
                    pasajeros_ninos = 0
                else:
                    pasajeros_ninos = int(pasajeros_ninos)
                
                pasajeros_infantes = row.get('pasajeros_infantes', 0)
                if pd.isna(pasajeros_infantes):
                    pasajeros_infantes = 0
                else:
                    pasajeros_infantes = int(pasajeros_infantes)
                
                # Medio de ingreso
                medio_ingreso_id = None
                medio_ingreso_nombre = row.get('medio_ingreso')
                if not pd.isna(medio_ingreso_nombre):
                    medio_ingreso_nombre = str(medio_ingreso_nombre).strip().upper()
                    medio = db.query(MedioIngreso).filter(
                        MedioIngreso.nombre == medio_ingreso_nombre
                    ).first()
                    
                    if medio:
                        medio_ingreso_id = medio.id
                    else:
                        # Crear medio de ingreso si no existe
                        nuevo_medio = MedioIngreso(nombre=medio_ingreso_nombre)
                        db.add(nuevo_medio)
                        db.commit()
                        db.refresh(nuevo_medio)
                        medio_ingreso_id = nuevo_medio.id
                
                # Estado
                estado = row.get('estado', 'nuevo')
                if pd.isna(estado):
                    estado = 'nuevo'
                else:
                    estado = str(estado).strip().lower()
                
                # Validar estado
                estados_validos = ['nuevo', 'en_seguimiento', 'cotizado', 'ganado', 'cerrado_perdido']
                if estado not in estados_validos:
                    resultado['errores'].append({
                        'fila': fila_num,
                        'error': f'Estado inválido: {estado}. Debe ser uno de: {", ".join(estados_validos)}'
                    })
                    continue
                
                # Observaciones
                observaciones = row.get('observaciones')
                if not pd.isna(observaciones):
                    observaciones = str(observaciones).strip()
                else:
                    observaciones = None
                
                # Comentarios (nuevo campo)
                comentarios = row.get('comentarios')
                if not pd.isna(comentarios):
                    # Agregar comentarios a observaciones
                    if observaciones:
                        observaciones += f"\n\nComentarios: {str(comentarios).strip()}"
                    else:
                        observaciones = f"Comentarios: {str(comentarios).strip()}"
                
                # Agente asignado
                agente_asignado_id = None
                agente_username = row.get('agente_asignado')
                if not pd.isna(agente_username):
                    agente_username = str(agente_username).strip()
                    agente = db.query(Usuario).filter(
                        Usuario.username == agente_username
                    ).first()
                    
                    if agente:
                        agente_asignado_id = agente.id
                    else:
                        resultado['errores'].append({
                            'fila': fila_num,
                            'error': f'Agente no encontrado: {agente_username} (se creará sin agente asignado)'
                        })
                
                # Campos adicionales para clientes ganados
                fecha_nacimiento = parsear_fecha(row.get('fecha_nacimiento'))
                
                numero_identificacion = row.get('numero_identificacion')
                if not pd.isna(numero_identificacion):
                    numero_identificacion = str(numero_identificacion).strip()
                else:
                    numero_identificacion = None
                
                # ✅ NUEVO: Fecha de compra (para ventas históricas)
                fecha_compra = parsear_fecha(row.get('fecha_compra'))
                # Si el estado es ganado y no hay fecha_compra, usar fecha actual
                if estado == 'ganado' and not fecha_compra:
                    from datetime import date
                    fecha_compra = date.today()
                
                # ✅ NUEVO: Dirección (para clientes ganados)
                direccion = row.get('direccion')
                if not pd.isna(direccion):
                    direccion = str(direccion).strip().upper()  # ✅ MAYÚSCULAS
                else:
                    direccion = None
                
                # ✅ NUEVO: Importar id_cliente e id_solicitud desde Excel
                id_cliente_excel = row.get('id_cliente')
                if not pd.isna(id_cliente_excel):
                    id_cliente_excel = str(id_cliente_excel).strip()
                else:
                    id_cliente_excel = None
                
                id_solicitud_excel = row.get('id_solicitud')
                if not pd.isna(id_solicitud_excel):
                    id_solicitud_excel = str(id_solicitud_excel).strip()
                    
                    # Validar que id_solicitud sea único
                    solicitud_existente = db.query(Prospecto).filter(
                        Prospecto.id_solicitud == id_solicitud_excel
                    ).first()
                    
                    if solicitud_existente:
                        resultado['errores'].append({
                            'fila': fila_num,
                            'error': f'ID Solicitud duplicado: {id_solicitud_excel} (ya existe en el sistema)'
                        })
                        continue
                else:
                    id_solicitud_excel = None
                
                # Crear prospecto
                nuevo_prospecto = Prospecto(
                    telefono=telefono,
                    indicativo_telefono=indicativo_telefono,
                    nombre=nombre,
                    apellido=apellido,
                    correo_electronico=correo_electronico,
                    ciudad_origen=ciudad_origen,
                    destino=destino,
                    fecha_ida=fecha_ida,
                    fecha_vuelta=fecha_vuelta,
                    pasajeros_adultos=pasajeros_adultos,
                    pasajeros_ninos=pasajeros_ninos,
                    pasajeros_infantes=pasajeros_infantes,
                    medio_ingreso_id=medio_ingreso_id,
                    estado=estado,
                    observaciones=observaciones,
                    agente_asignado_id=agente_asignado_id,
                    cliente_recurrente=es_recurrente,
                    prospecto_original_id=prospecto_original_id,
                    fecha_nacimiento=fecha_nacimiento,
                    numero_identificacion=numero_identificacion,
                    fecha_compra=fecha_compra,  # ✅ NUEVO
                    direccion=direccion,  # ✅ NUEVO
                    empresa_segundo_titular=empresa_segundo_titular,  # ✅ NUEVO: Empresa o segundo titular
                    id_cliente=id_cliente_excel,  # ✅ NUEVO: Asignar desde Excel si existe
                    id_solicitud=id_solicitud_excel  # ✅ NUEVO: Asignar desde Excel si existe
                )
                
                # Verificar datos completos
                nuevo_prospecto.verificar_datos_completos()
                
                db.add(nuevo_prospecto)
                db.commit()
                db.refresh(nuevo_prospecto)
                
                # ✅ Generar IDs si no se proporcionaron en Excel
                # 1. id_cliente: Reutilizar si es recurrente, sino generar
                if not nuevo_prospecto.id_cliente:
                    if es_recurrente and prospecto_existente.id_cliente:
                        nuevo_prospecto.id_cliente = prospecto_existente.id_cliente
                    else:
                        nuevo_prospecto.generar_id_cliente()
                
                # 2. id_solicitud: Siempre generar si no se proporcionó
                if not nuevo_prospecto.id_solicitud:
                    nuevo_prospecto.generar_id_solicitud()
                
                db.commit()
                
                # ✅ NUEVO: Si el estado es "ganado", generar ID de cotización
                if estado == 'ganado':
                    from models import EstadisticaCotizacion
                    
                    # Crear estadística de cotización
                    estadistica = EstadisticaCotizacion(
                        agente_id=agente_asignado_id,
                        prospecto_id=nuevo_prospecto.id,
                        fecha_cotizacion=fecha_compra  # Usar fecha_compra para históricos
                    )
                    db.add(estadistica)
                    db.commit()
                    db.refresh(estadistica)
                    
                    # Generar ID de cotización
                    estadistica.generar_id_cotizacion()
                    db.commit()
                    
                    # ✅ NUEVO: Crear notificaciones automáticas de viaje
                    if fecha_ida:
                        from main import crear_notificaciones_viaje
                        crear_notificaciones_viaje(nuevo_prospecto, db)
                
                resultado['prospectos_creados'].append(nuevo_prospecto)
                resultado['exitosos'] += 1
                
                if es_recurrente:
                    resultado['recurrentes'] += 1
                
            except Exception as e:
                db.rollback()
                resultado['errores'].append({
                    'fila': fila_num,
                    'error': f'Error al procesar: {str(e)}'
                })
        
    except Exception as e:
        resultado['errores'].append({
            'fila': 0,
            'error': f'Error al leer archivo: {str(e)}'
        })
    
    return resultado
