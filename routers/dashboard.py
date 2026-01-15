from fastapi import APIRouter, Request, Form, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
import database
import models
from models import TipoUsuario, EstadoProspecto
from dependencies import require_admin, get_current_user
from utils import (
    calcular_rango_fechas,
    enviar_notificacion_email
)
import io
import pandas as pd
from datetime import datetime, date, timedelta

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# ========== DASHBOARD ==========

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    periodo: str = Query("mes"),
    fecha_inicio: str = Query(None),
    fecha_fin: str = Query(None),
    db: Session = Depends(database.get_db)
):
    user = await get_current_user(request, db)

    if not user:
        return RedirectResponse(url="/", status_code=303)

    try:
        fecha_inicio_obj, fecha_fin_obj = calcular_rango_fechas(periodo, fecha_inicio, fecha_fin)

        fecha_inicio_dt = datetime.combine(fecha_inicio_obj, datetime.min.time())
        fecha_fin_dt = datetime.combine(fecha_fin_obj, datetime.max.time())

        # Initialize
        total_prospectos = prospectos_con_datos = prospectos_sin_datos = 0
        clientes_sin_asignar = clientes_asignados = destinos_count = ventas_count = 0
        prospectos_nuevos = prospectos_seguimiento = prospectos_cotizados = prospectos_ganados = prospectos_perdidos = ventas_canceladas = 0
        destinos_populares = []
        conversion_agentes = []

        if user.tipo_usuario in [TipoUsuario.ADMINISTRADOR.value, TipoUsuario.SUPERVISOR.value]:
            total_prospectos = db.query(models.Prospecto).filter(
                models.Prospecto.fecha_registro >= fecha_inicio_dt,
                models.Prospecto.fecha_registro <= fecha_fin_dt
            ).count()

            prospectos_con_datos = db.query(models.Prospecto).filter(
                models.Prospecto.tiene_datos_completos == True,
                models.Prospecto.fecha_registro >= fecha_inicio_dt,
                models.Prospecto.fecha_registro <= fecha_fin_dt
            ).count()

            prospectos_sin_datos = db.query(models.Prospecto).filter(
                models.Prospecto.tiene_datos_completos == False,
                models.Prospecto.fecha_registro >= fecha_inicio_dt,
                models.Prospecto.fecha_registro <= fecha_fin_dt
            ).count()

            clientes_sin_asignar = db.query(models.Prospecto).filter(
                models.Prospecto.estado == EstadoProspecto.NUEVO.value,
                models.Prospecto.agente_asignado_id == None,
                models.Prospecto.fecha_registro >= fecha_inicio_dt,
                models.Prospecto.fecha_registro <= fecha_fin_dt
            ).count()

            clientes_asignados = db.query(models.Prospecto).filter(
                models.Prospecto.agente_asignado_id != None,
                models.Prospecto.fecha_registro >= fecha_inicio_dt,
                models.Prospecto.fecha_registro <= fecha_fin_dt
            ).count()

            destinos_query = db.query(models.Prospecto.destino).filter(
                models.Prospecto.fecha_registro >= fecha_inicio_dt,
                models.Prospecto.fecha_registro <= fecha_fin_dt,
                models.Prospecto.destino.isnot(None),
                models.Prospecto.destino != ''
            ).distinct().all()
            destinos_count = len(destinos_query)

            ventas_count = db.query(models.Prospecto).filter(
                models.Prospecto.estado == EstadoProspecto.GANADO.value,
                models.Prospecto.fecha_registro >= fecha_inicio_dt,
                models.Prospecto.fecha_registro <= fecha_fin_dt
            ).count()

            destinos_populares = db.query(
                models.Prospecto.destino,
                func.count(models.Prospecto.id).label('count')
            ).filter(
                models.Prospecto.fecha_registro >= fecha_inicio_dt,
                models.Prospecto.fecha_registro <= fecha_fin_dt,
                models.Prospecto.destino.isnot(None),
                models.Prospecto.destino != ''
            ).group_by(models.Prospecto.destino).order_by(func.count(models.Prospecto.id).desc()).limit(5).all()

            prospectos_nuevos = db.query(models.Prospecto).filter(
                models.Prospecto.estado == EstadoProspecto.NUEVO.value,
                models.Prospecto.fecha_registro >= fecha_inicio_dt,
                models.Prospecto.fecha_registro <= fecha_fin_dt
            ).count()

            prospectos_seguimiento = db.query(models.Prospecto).filter(
                models.Prospecto.estado == EstadoProspecto.EN_SEGUIMIENTO.value,
                models.Prospecto.fecha_registro >= fecha_inicio_dt,
                models.Prospecto.fecha_registro <= fecha_fin_dt
            ).count()

            prospectos_cotizados = db.query(models.Prospecto).filter(
                models.Prospecto.estado == EstadoProspecto.COTIZADO.value,
                models.Prospecto.fecha_registro >= fecha_inicio_dt,
                models.Prospecto.fecha_registro <= fecha_fin_dt
            ).count()

            prospectos_ganados = db.query(models.Prospecto).filter(
                models.Prospecto.estado == EstadoProspecto.GANADO.value,
                models.Prospecto.fecha_registro >= fecha_inicio_dt,
                models.Prospecto.fecha_registro <= fecha_fin_dt
            ).count()

            prospectos_perdidos = db.query(models.Prospecto).filter(
                models.Prospecto.estado == EstadoProspecto.CERRADO_PERDIDO.value,
                models.Prospecto.fecha_registro >= fecha_inicio_dt,
                models.Prospecto.fecha_registro <= fecha_fin_dt
            ).count()

            ventas_canceladas = db.query(models.Prospecto).filter(
                models.Prospecto.estado == EstadoProspecto.VENTA_CANCELADA.value,
                models.Prospecto.fecha_registro >= fecha_inicio_dt,
                models.Prospecto.fecha_registro <= fecha_fin_dt
            ).count()

            conversion_agentes = []
            agentes_con_prospectos = db.query(
                models.Usuario.id,
                models.Usuario.username
            ).filter(
                models.Usuario.tipo_usuario == TipoUsuario.AGENTE.value,
                models.Usuario.activo == 1
            ).all()

            for agente in agentes_con_prospectos:
                total_agente = db.query(models.Prospecto).filter(
                    models.Prospecto.agente_asignado_id == agente.id,
                    models.Prospecto.fecha_registro >= fecha_inicio_dt,
                    models.Prospecto.fecha_registro <= fecha_fin_dt
                ).count()

                ganados_agente = db.query(models.HistorialEstado).filter(
                    models.HistorialEstado.usuario_id == agente.id,
                    models.HistorialEstado.estado_nuevo == EstadoProspecto.GANADO.value,
                    models.HistorialEstado.fecha_cambio >= fecha_inicio_dt,
                    models.HistorialEstado.fecha_cambio <= fecha_fin_dt
                ).count()

                cotizados_agente = db.query(models.EstadisticaCotizacion).filter(
                    models.EstadisticaCotizacion.agente_id == agente.id,
                    models.EstadisticaCotizacion.fecha_cotizacion >= fecha_inicio_obj,
                    models.EstadisticaCotizacion.fecha_cotizacion <= fecha_fin_obj
                ).count()

                conversion_agentes.append({
                    'id': agente.id,
                    'username': agente.username,
                    'total_prospectos': total_agente,
                    'cotizados': cotizados_agente,
                    'ganados': ganados_agente
                })

        else:
            total_prospectos = db.query(models.Prospecto).filter(
                models.Prospecto.agente_asignado_id == user.id,
                models.Prospecto.fecha_registro >= fecha_inicio_dt,
                models.Prospecto.fecha_registro <= fecha_fin_dt
            ).count()

            prospectos_con_datos = db.query(models.Prospecto).filter(
                models.Prospecto.agente_asignado_id == user.id,
                models.Prospecto.tiene_datos_completos == True,
                models.Prospecto.fecha_registro >= fecha_inicio_dt,
                models.Prospecto.fecha_registro <= fecha_fin_dt
            ).count()

            prospectos_sin_datos = db.query(models.Prospecto).filter(
                models.Prospecto.agente_asignado_id == user.id,
                models.Prospecto.tiene_datos_completos == False,
                models.Prospecto.fecha_registro >= fecha_inicio_dt,
                models.Prospecto.fecha_registro <= fecha_fin_dt
            ).count()

            clientes_asignados = db.query(models.Prospecto).filter(
                models.Prospecto.agente_asignado_id == user.id,
                models.Prospecto.fecha_registro >= fecha_inicio_dt,
                models.Prospecto.fecha_registro <= fecha_fin_dt
            ).count()

            destinos_query = db.query(models.Prospecto.destino).filter(
                models.Prospecto.agente_asignado_id == user.id,
                models.Prospecto.fecha_registro >= fecha_inicio_dt,
                models.Prospecto.fecha_registro <= fecha_fin_dt,
                models.Prospecto.destino.isnot(None),
                models.Prospecto.destino != ''
            ).distinct().all()
            destinos_count = len(destinos_query)

            ventas_count = db.query(models.HistorialEstado).filter(
                models.HistorialEstado.usuario_id == user.id,
                models.HistorialEstado.estado_nuevo == EstadoProspecto.GANADO.value,
                models.HistorialEstado.fecha_cambio >= fecha_inicio_dt,
                models.HistorialEstado.fecha_cambio <= fecha_fin_dt
            ).count()

            destinos_populares = db.query(
                models.Prospecto.destino,
                func.count(models.Prospecto.id).label('count')
            ).filter(
                models.Prospecto.agente_asignado_id == user.id,
                models.Prospecto.fecha_registro >= fecha_inicio_dt,
                models.Prospecto.fecha_registro <= fecha_fin_dt,
                models.Prospecto.destino.isnot(None),
                models.Prospecto.destino != ''
            ).group_by(models.Prospecto.destino).order_by(func.count(models.Prospecto.id).desc()).limit(5).all()

            clientes_sin_asignar = 0

            prospectos_nuevos = db.query(models.Prospecto).filter(
                models.Prospecto.agente_asignado_id == user.id,
                models.Prospecto.estado == EstadoProspecto.NUEVO.value,
                models.Prospecto.fecha_registro >= fecha_inicio_dt,
                models.Prospecto.fecha_registro <= fecha_fin_dt
            ).count()
            prospectos_seguimiento = db.query(models.HistorialEstado).filter(
                models.HistorialEstado.usuario_id == user.id,
                models.HistorialEstado.estado_nuevo == EstadoProspecto.EN_SEGUIMIENTO.value,
                models.HistorialEstado.fecha_cambio >= fecha_inicio_dt,
                models.HistorialEstado.fecha_cambio <= fecha_fin_dt
            ).count()

            prospectos_cotizados = db.query(models.EstadisticaCotizacion).filter(
                models.EstadisticaCotizacion.agente_id == user.id,
                models.EstadisticaCotizacion.fecha_cotizacion >= fecha_inicio_obj,
                models.EstadisticaCotizacion.fecha_cotizacion <= fecha_fin_obj
            ).count()

            prospectos_ganados = db.query(models.HistorialEstado).filter(
                models.HistorialEstado.usuario_id == user.id,
                models.HistorialEstado.estado_nuevo == EstadoProspecto.GANADO.value,
                models.HistorialEstado.fecha_cambio >= fecha_inicio_dt,
                models.HistorialEstado.fecha_cambio <= fecha_fin_dt
            ).count()

            prospectos_perdidos = db.query(models.HistorialEstado).filter(
                models.HistorialEstado.usuario_id == user.id,
                models.HistorialEstado.estado_nuevo == EstadoProspecto.CERRADO_PERDIDO.value,
                models.HistorialEstado.fecha_cambio >= fecha_inicio_dt,
                models.HistorialEstado.fecha_cambio <= fecha_fin_dt
            ).count()

            conversion_agentes = []

    except Exception as e:
        print(f"❌ Error grave calculando estadísticas: {e}")
        import traceback
        traceback.print_exc()
        # Initialize with default values if error
        total_prospectos = prospectos_con_datos = prospectos_sin_datos = 0
        clientes_sin_asignar = clientes_asignados = destinos_count = ventas_count = 0
        prospectos_nuevos = prospectos_seguimiento = prospectos_cotizados = prospectos_ganados = prospectos_perdidos = 0
        destinos_populares = []
        conversion_agentes = []
        fecha_inicio_obj = date.today()
        fecha_fin_obj = date.today()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "current_user": user,
        "today": date.today().strftime("%d/%m/%Y"),
        "periodo_activo": periodo,
        "fecha_inicio_activa": fecha_inicio,
        "fecha_fin_activa": fecha_fin,
        "fecha_inicio_formateada": fecha_inicio_obj.strftime("%d/%m/%Y") if fecha_inicio_obj else "",
        "fecha_fin_formateada": fecha_fin_obj.strftime("%d/%m/%Y") if fecha_fin_obj else "",
        "total_prospectos": total_prospectos,
        "prospectos_con_datos": prospectos_con_datos,
        "prospectos_sin_datos": prospectos_sin_datos,
        "clientes_sin_asignar": clientes_sin_asignar,
        "clientes_asignados": clientes_asignados,
        "destinos_count": destinos_count,
        "ventas_count": ventas_count,
        "prospectos_nuevos": prospectos_nuevos,
        "prospectos_seguimiento": prospectos_seguimiento,
        "prospectos_cotizados": prospectos_cotizados,
        "prospectos_ganados": prospectos_ganados,
        "prospectos_perdidos": prospectos_perdidos,
        "ventas_canceladas": ventas_canceladas,
        "destinos_populares": destinos_populares,
        "conversion_agentes": conversion_agentes
    })

# ========== NOTIFICACIONES ==========

def check_inactivity(db: Session):
    """Verifica prospectos nuevos sin gestión por más de 4 horas"""
    limite = datetime.now() - timedelta(hours=4)

    prospectos_inactivos = db.query(models.Prospecto).filter(
        models.Prospecto.estado == EstadoProspecto.NUEVO.value,
        models.Prospecto.fecha_registro <= limite
    ).all()

    count = 0
    for p in prospectos_inactivos:
        existe_alerta = db.query(models.Notificacion).filter(
            models.Notificacion.prospecto_id == p.id,
            models.Notificacion.tipo == "inactividad",
            models.Notificacion.fecha_creacion >= datetime.now() - timedelta(hours=24)
        ).first()

        if not existe_alerta:
            destinatarios = []
            if p.agente_asignado_id:
                destinatarios.append(p.agente_asignado_id)
            else:
                admins = db.query(models.Usuario).filter(
                    models.Usuario.tipo_usuario.in_([TipoUsuario.ADMINISTRADOR.value, TipoUsuario.SUPERVISOR.value])
                ).all()
                destinatarios = [u.id for u in admins]

            for uid in destinatarios:
                notificacion = models.Notificacion(
                    usuario_id=uid,
                    prospecto_id=p.id,
                    tipo="inactividad",
                    mensaje=f"⚠️ Prospecto inactivo > 4h: {p.nombre} {p.apellido or ''}",
                    email_enviado=False
                )
                db.add(notificacion)
                count += 1

    db.commit()
    return count

@router.get("/api/notificaciones/check-inactivity")
async def api_check_inactivity(
    db: Session = Depends(database.get_db)
):
    try:
        count = check_inactivity(db)
        return {"status": "ok", "alertas_generadas": count}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/notificaciones", response_class=HTMLResponse)
async def ver_notificaciones(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    filtro_agente_id: str = Query(None),
    filtro_tipo: str = Query(None),
    filtro_estado: str = Query(None),
    fecha_inicio: str = Query(None),
    fecha_fin: str = Query(None),
    db: Session = Depends(database.get_db)
):
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    check_inactivity(db)

    query = db.query(models.Notificacion)

    if user.tipo_usuario == TipoUsuario.AGENTE.value:
        query = query.filter(models.Notificacion.usuario_id == user.id)
    elif filtro_agente_id and filtro_agente_id != "todos":
        query = query.filter(models.Notificacion.usuario_id == int(filtro_agente_id))

    if filtro_tipo and filtro_tipo != "todos":
        query = query.filter(models.Notificacion.tipo == filtro_tipo)

    if filtro_estado:
        if filtro_estado == "pendientes":
            query = query.filter(models.Notificacion.leida == False)
        elif filtro_estado == "leidas":
            query = query.filter(models.Notificacion.leida == True)
        elif filtro_estado == "vencidas":
            query = query.filter(
                models.Notificacion.leida == False,
                models.Notificacion.fecha_programada.isnot(None),
                models.Notificacion.fecha_programada < datetime.now()
            )
        elif filtro_estado == "proximas":
            query = query.filter(
                models.Notificacion.leida == False,
                models.Notificacion.fecha_programada.isnot(None),
                models.Notificacion.fecha_programada > datetime.now()
            )
    else:
        query = query.filter(models.Notificacion.leida == False)

    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, "%d/%m/%Y")
            query = query.filter(models.Notificacion.fecha_creacion >= fecha_inicio_dt)
        except ValueError:
            pass

    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, "%d/%m/%Y")
            fecha_fin_dt = fecha_fin_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(models.Notificacion.fecha_creacion <= fecha_fin_dt)
        except ValueError:
            pass

    total_notificaciones = query.count()

    total_pages = (total_notificaciones + limit - 1) // limit
    offset = (page - 1) * limit

    notificaciones = query.order_by(models.Notificacion.fecha_creacion.desc()).offset(offset).limit(limit).all()

    for n in notificaciones:
        if n.fecha_programada:
            delta = n.fecha_programada - datetime.now()
            dias = delta.days
            horas, resto = divmod(delta.seconds, 3600)
            minutos, _ = divmod(resto, 60)

            if delta.total_seconds() > 0:
                if dias > 0:
                    n.tiempo_restante_str = f"{dias}d {horas}h"
                else:
                    n.tiempo_restante_str = f"{horas}h {minutos}m"
                n.es_tarde = False
            else:
                n.tiempo_restante_str = "Vencida"
                n.es_tarde = True
        else:
            delta = datetime.now() - n.fecha_creacion
            dias = delta.days
            horas, resto = divmod(delta.seconds, 3600)
            n.tiempo_restante_str = f"Hace {dias}d {horas}h" if dias > 0 else f"Hace {horas}h"
            n.es_tarde = False

    agentes = []
    if user.tipo_usuario in [TipoUsuario.ADMINISTRADOR.value, TipoUsuario.SUPERVISOR.value]:
        agentes = db.query(models.Usuario).filter(
            models.Usuario.tipo_usuario == TipoUsuario.AGENTE.value,
            models.Usuario.activo == 1
        ).all()

    prospectos_activos = []
    if user.tipo_usuario == TipoUsuario.AGENTE.value:
        prospectos_activos = db.query(models.Prospecto).filter(
            models.Prospecto.agente_asignado_id == user.id,
            models.Prospecto.estado.in_(['nuevo', 'en_seguimiento', 'cotizado'])
        ).order_by(models.Prospecto.nombre).limit(50).all()
    else:
        prospectos_activos = db.query(models.Prospecto).filter(
            models.Prospecto.estado.in_(['nuevo', 'en_seguimiento', 'cotizado'])
        ).order_by(models.Prospecto.nombre).limit(100).all()

    return templates.TemplateResponse("notificaciones.html", {
        "request": request,
        "current_user": user,
        "notificaciones": notificaciones,
        "agentes": agentes,
        "filtro_agente_id": filtro_agente_id,
        "filtro_tipo": filtro_tipo,
        "filtro_estado": filtro_estado,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "prospectos_activos": prospectos_activos,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "total_notificaciones": total_notificaciones
    })

@router.post("/notificaciones/{notificacion_id}/leer")
async def marcar_notificacion_leida(
    notificacion_id: int,
    db: Session = Depends(database.get_db),
    request: Request = None
):
    notif = db.query(models.Notificacion).filter(models.Notificacion.id == notificacion_id).first()
    if notif:
        notif.leida = True
        db.commit()

    return RedirectResponse(url="/notificaciones", status_code=303)

@router.get("/api/notificaciones/pendientes")
async def obtener_notificaciones_pendientes(
    request: Request,
    db: Session = Depends(database.get_db)
):
    user = await get_current_user(request, db)
    if not user:
        return JSONResponse(content={"notificaciones": []})

    ahora = datetime.now()

    notificaciones = db.query(models.Notificacion).filter(
        models.Notificacion.usuario_id == user.id,
        models.Notificacion.leida == False,
        models.Notificacion.fecha_programada.isnot(None),
        models.Notificacion.fecha_programada <= ahora
    ).order_by(models.Notificacion.fecha_programada.asc()).all()

    resultado = []
    for n in notificaciones:
        prospecto_nombre = "N/A"
        if n.prospecto:
            prospecto_nombre = f"{n.prospecto.nombre} {n.prospecto.apellido or ''}".strip()

        resultado.append({
            "id": n.id,
            "mensaje": n.mensaje,
            "tipo": n.tipo,
            "prospecto_id": n.prospecto_id,
            "fecha_programada": n.fecha_programada.strftime("%d/%m/%Y %H:%M"),
            "prospecto_nombre": prospecto_nombre
        })

    return JSONResponse(content={"notificaciones": resultado})

@router.get("/api/buscar-prospecto-por-id")
async def buscar_prospecto_por_id(
    id: str = Query(...),
    db: Session = Depends(database.get_db),
    request: Request = None
):
    user = await get_current_user(request, db)
    if not user:
        return JSONResponse(content={"success": False, "error": "No autenticado"})

    try:
        prospecto = None

        if id.startswith('CL-'):
            prospecto = db.query(models.Prospecto).filter(
                models.Prospecto.id_cliente == id
            ).first()
        elif id.startswith('COT-'):
            cotizacion = db.query(models.EstadisticaCotizacion).filter(
                models.EstadisticaCotizacion.id_cotizacion == id
            ).first()
            if cotizacion:
                prospecto = cotizacion.prospecto
        else:
            try:
                prospecto_id = int(id)
                prospecto = db.query(models.Prospecto).filter(
                    models.Prospecto.id == prospecto_id
                ).first()
            except ValueError:
                pass

        if prospecto:
            if user.tipo_usuario == TipoUsuario.AGENTE.value:
                if prospecto.agente_asignado_id != user.id:
                    return JSONResponse(content={
                        "success": False,
                        "error": "No tienes permisos para ver este prospecto"
                    })

            return JSONResponse(content={
                "success": True,
                "prospecto": {
                    "id": prospecto.id,
                    "id_cliente": prospecto.id_cliente,
                    "nombre": prospecto.nombre,
                    "apellido": prospecto.apellido or "",
                    "destino": prospecto.destino or ""
                }
            })
        else:
            return JSONResponse(content={
                "success": False,
                "error": "Prospecto no encontrado"
            })

    except Exception as e:
        print(f"Error buscando prospecto: {e}")
        return JSONResponse(content={
            "success": False,
            "error": "Error en la búsqueda"
        })

@router.post("/notificaciones/crear")
async def crear_notificacion_manual(
    request: Request,
    mensaje: str = Form(...),
    fecha_programada: str = Form(...),
    prospecto_id: int = Form(None),
    db: Session = Depends(database.get_db)
):
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    try:
        fecha_prog = datetime.strptime(fecha_programada, "%Y-%m-%dT%H:%M")

        if fecha_prog <= datetime.now():
            return RedirectResponse(
                url="/notificaciones?error=La fecha debe ser futura",
                status_code=303
            )

        notificacion = models.Notificacion(
            usuario_id=user.id,
            prospecto_id=prospecto_id if prospecto_id else None,
            tipo="seguimiento",
            mensaje=mensaje,
            fecha_programada=fecha_prog,
            leida=False,
            email_enviado=False
        )

        db.add(notificacion)

        if prospecto_id:
            prospecto = db.query(models.Prospecto).filter(
                models.Prospecto.id == prospecto_id
            ).first()

            if prospecto:
                fecha_formateada = fecha_prog.strftime("%d/%m/%Y a las %H:%M")

                interaccion = models.Interaccion(
                    prospecto_id=prospecto_id,
                    usuario_id=user.id,
                    tipo_interaccion="sistema",
                    descripcion=f"📅 Contacto programado para {fecha_formateada}\n{mensaje}",
                    estado_anterior=prospecto.estado,
                    estado_nuevo=prospecto.estado
                )

                db.add(interaccion)

        db.commit()

        return RedirectResponse(
            url="/notificaciones?success=Recordatorio creado correctamente",
            status_code=303
        )

    except ValueError as e:
        return RedirectResponse(
            url="/notificaciones?error=Formato de fecha inválido",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        print(f"Error creando notificación: {e}")
        return RedirectResponse(
            url="/notificaciones?error=Error al crear recordatorio",
            status_code=303
        )

# ========== OTROS ENDPOINTS ==========

@router.get("/busqueda_ids", response_class=HTMLResponse)
async def buscar_por_id(
    request: Request,
    tipo_id: str = Query("cliente"),
    valor_id: str = Query(None),
    db: Session = Depends(database.get_db)
):
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    resultados = []
    tipo_busqueda = ""

    if valor_id:
        valor_id = valor_id.upper().strip()

        if tipo_id == "cliente":
            resultados = db.query(models.Prospecto).filter(
                models.Prospecto.id_cliente.ilike(f"%{valor_id}%")
            ).all()
            tipo_busqueda = f"Clientes con ID: {valor_id}"

        elif tipo_id == "solicitud":
            resultados = db.query(models.Prospecto).filter(
                models.Prospecto.id_solicitud.ilike(f"%{valor_id}%")
            ).all()
            tipo_busqueda = f"Solicitudes con ID: {valor_id}"

        elif tipo_id == "cotizacion":
            estadisticas = db.query(models.EstadisticaCotizacion).filter(
                models.EstadisticaCotizacion.id_cotizacion.ilike(f"%{valor_id}%")
            ).all()
            for stats in estadisticas:
                prospecto = db.query(models.Prospecto).filter(
                    models.Prospecto.id == stats.prospecto_id
                ).first()
                if prospecto:
                    resultados.append(prospecto)
            tipo_busqueda = f"Cotizaciones con ID: {valor_id}"

        elif tipo_id == "documento":
            documentos = db.query(models.Documento).filter(
                models.Documento.id_documento.ilike(f"%{valor_id}%")
            ).all()
            for doc in documentos:
                prospecto = db.query(models.Prospecto).filter(
                    models.Prospecto.id == doc.prospecto_id
                ).first()
                if prospecto:
                    resultados.append(prospecto)
            tipo_busqueda = f"Documentos con ID: {valor_id}"

    return templates.TemplateResponse("busqueda_ids.html", {
        "request": request,
        "current_user": user,
        "resultados": resultados,
        "tipo_busqueda": tipo_busqueda,
        "tipo_id_activo": tipo_id,
        "valor_id_buscado": valor_id
    })

@router.get("/estadisticas/cotizaciones", response_class=HTMLResponse)
async def estadisticas_cotizaciones(
    request: Request,
    periodo: str = Query("mes"),
    fecha_inicio: str = Query(None),
    fecha_fin: str = Query(None),
    agente_id: str = Query(None),
    db: Session = Depends(database.get_db)
):
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    try:
        fecha_inicio_dt, fecha_fin_dt = calcular_rango_fechas(periodo, fecha_inicio, fecha_fin)
        fecha_inicio_obj = fecha_inicio_dt.date()
        fecha_fin_obj = fecha_fin_dt.date()

        query = db.query(
            models.EstadisticaCotizacion,
            models.Usuario.username
        ).join(
            models.Usuario, models.EstadisticaCotizacion.agente_id == models.Usuario.id
        ).filter(
            models.EstadisticaCotizacion.fecha_cotizacion >= fecha_inicio_obj,
            models.EstadisticaCotizacion.fecha_cotizacion <= fecha_fin_obj
        )

        if agente_id and agente_id != "todos":
            query = query.filter(models.EstadisticaCotizacion.agente_id == int(agente_id))
        elif user.tipo_usuario == TipoUsuario.AGENTE.value:
            query = query.filter(models.EstadisticaCotizacion.agente_id == user.id)

        estadisticas = query.add_columns(
            models.Prospecto.id.label('prospecto_id'),
            models.Prospecto.nombre,
            models.Prospecto.apellido,
            models.Prospecto.telefono
        ).join(
            models.Prospecto, models.EstadisticaCotizacion.prospecto_id == models.Prospecto.id
        ).order_by(
            models.EstadisticaCotizacion.fecha_cotizacion.desc(),
            models.Usuario.username
        ).all()

        resumen_agentes = db.query(
            models.Usuario.id,
            models.Usuario.username,
            func.count(models.EstadisticaCotizacion.id).label('total')
        ).join(
            models.EstadisticaCotizacion, models.EstadisticaCotizacion.agente_id == models.Usuario.id
        ).filter(
            models.EstadisticaCotizacion.fecha_cotizacion >= fecha_inicio_obj,
            models.EstadisticaCotizacion.fecha_cotizacion <= fecha_fin_obj
        )

        if user.tipo_usuario == TipoUsuario.AGENTE.value:
            resumen_agentes = resumen_agentes.filter(models.EstadisticaCotizacion.agente_id == user.id)

        resumen_agentes = resumen_agentes.group_by(models.Usuario.id, models.Usuario.username).all()

        agentes = db.query(models.Usuario).filter(
            models.Usuario.tipo_usuario == TipoUsuario.AGENTE.value,
            models.Usuario.activo == 1
        ).all()

        return templates.TemplateResponse("estadisticas_cotizaciones.html", {
            "request": request,
            "current_user": user,
            "estadisticas": estadisticas,
            "resumen_agentes": resumen_agentes,
            "agentes": agentes,
            "periodo_activo": periodo,
            "fecha_inicio_activa": fecha_inicio,
            "fecha_fin_activa": fecha_fin,
            "agente_id_activo": agente_id,
            "fecha_inicio_formateada": fecha_inicio_obj.strftime("%d/%m/%Y"),
            "fecha_fin_formateada": fecha_fin_obj.strftime("%d/%m/%Y")
        })

    except Exception as e:
        print(f"❌ Error en estadísticas: {e}")
        return RedirectResponse(url="/dashboard?error=Error al cargar estadísticas", status_code=303)

def generar_excel_estadisticas(stats, periodo, fecha_inicio, fecha_fin, filename="dashboard_export.xlsx"):
    """
    Genera archivo Excel con estadísticas del dashboard
    """
    try:
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Hoja 1: Resumen General
            resumen_data = {
                'Métrica': [
                    'Periodo',
                    'Fecha Inicio',
                    'Fecha Fin',
                    '',
                    'Total Prospectos',
                    'Prospectos con Datos Completos',
                    'Prospectos sin Datos',
                    'Clientes Sin Asignar',
                    'Clientes Asignados',
                    'Destinos Únicos',
                    'Ventas Cerradas',
                    '',
                    'Prospectos Nuevos',
                    'En Seguimiento',
                    'Cotizados',
                    'Ganados',
                    'Perdidos',
                    'Ventas Canceladas'
                ],
                'Valor': [
                    periodo.title(),
                    fecha_inicio.strftime("%d/%m/%Y"),
                    fecha_fin.strftime("%d/%m/%Y"),
                    '',
                    stats.get('total_prospectos', 0),
                    stats.get('prospectos_con_datos', 0),
                    stats.get('prospectos_sin_datos', 0),
                    stats.get('clientes_sin_asignar', 0),
                    stats.get('clientes_asignados', 0),
                    stats.get('destinos_count', 0),
                    stats.get('ventas_count', 0),
                    '',
                    stats.get('prospectos_nuevos', 0),
                    stats.get('prospectos_seguimiento', 0),
                    stats.get('prospectos_cotizados', 0),
                    stats.get('prospectos_ganados', 0),
                    stats.get('prospectos_perdidos', 0),
                    stats.get('ventas_canceladas', 0)
                ]
            }
            df_resumen = pd.DataFrame(resumen_data)
            df_resumen.to_excel(writer, sheet_name='Resumen General', index=False)

            # Hoja 2: Por Estado
            estados_data = {
                'Estado': ['Nuevo', 'En Seguimiento', 'Cotizado', 'Ganado', 'Perdido', 'Venta Cancelada'],
                'Cantidad': [
                    stats.get('prospectos_nuevos', 0),
                    stats.get('prospectos_seguimiento', 0),
                    stats.get('prospectos_cotizados', 0),
                    stats.get('prospectos_ganados', 0),
                    stats.get('prospectos_perdidos', 0),
                    stats.get('ventas_canceladas', 0)
                ]
            }
            df_estados = pd.DataFrame(estados_data)
            df_estados.to_excel(writer, sheet_name='Por Estado', index=False)

            # Hoja 3: Por Agente
            if stats.get('conversion_agentes'):
                agentes_data = []
                for agente in stats['conversion_agentes']:
                    agentes_data.append({
                        'Agente': agente['username'],
                        'Total Prospectos': agente['total_prospectos'],
                        'Cotizados': agente['cotizados'],
                        'Ganados': agente['ganados'],
                        'Tasa Conversión': f"{(agente['ganados'] / agente['total_prospectos'] * 100) if agente['total_prospectos'] > 0 else 0:.1f}%"
                    })
                df_agentes = pd.DataFrame(agentes_data)
                df_agentes.to_excel(writer, sheet_name='Por Agente', index=False)

            # Hoja 4: Destinos Populares
            if stats.get('destinos_populares'):
                destinos_data = []
                for destino, count in stats['destinos_populares']:
                    destinos_data.append({
                        'Destino': destino,
                        'Cantidad': count
                    })
                df_destinos = pd.DataFrame(destinos_data)
                df_destinos.to_excel(writer, sheet_name='Destinos Populares', index=False)

            # Aplicar formato a todas las hojas
            from openpyxl.styles import Font, PatternFill, Alignment
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_font = Font(color="FFFFFF", bold=True)

            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]

                # Formato de encabezados
                for cell in worksheet[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center", vertical="center")

                # Auto-ajustar columnas
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 40)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

        output.seek(0)
        return output

    except Exception as e:
        print(f"❌ Error generando Excel de estadísticas: {e}")
        import traceback
        traceback.print_exc()
        return None

@router.get("/exportar/dashboard")
async def exportar_dashboard(
    request: Request,
    periodo: str = Query("mes"),
    fecha_inicio: str = Query(None),
    fecha_fin: str = Query(None),
    db: Session = Depends(database.get_db),
    user: models.Usuario = Depends(require_admin)
):
    try:
        fecha_inicio_obj, fecha_fin_obj = calcular_rango_fechas(periodo, fecha_inicio, fecha_fin)

        fecha_inicio_dt = datetime.combine(fecha_inicio_obj, datetime.min.time())
        fecha_fin_dt = datetime.combine(fecha_fin_obj, datetime.max.time())

        stats = {}

        stats['total_prospectos'] = db.query(models.Prospecto).filter(
            models.Prospecto.fecha_registro >= fecha_inicio_dt,
            models.Prospecto.fecha_registro <= fecha_fin_dt
        ).count()

        stats['prospectos_con_datos'] = db.query(models.Prospecto).filter(
            models.Prospecto.tiene_datos_completos == True,
            models.Prospecto.fecha_registro >= fecha_inicio_dt,
            models.Prospecto.fecha_registro <= fecha_fin_dt
        ).count()

        stats['prospectos_sin_datos'] = db.query(models.Prospecto).filter(
            models.Prospecto.tiene_datos_completos == False,
            models.Prospecto.fecha_registro >= fecha_inicio_dt,
            models.Prospecto.fecha_registro <= fecha_fin_dt
        ).count()

        stats['clientes_sin_asignar'] = db.query(models.Prospecto).filter(
            models.Prospecto.estado == EstadoProspecto.NUEVO.value,
            models.Prospecto.agente_asignado_id == None,
            models.Prospecto.fecha_registro >= fecha_inicio_dt,
            models.Prospecto.fecha_registro <= fecha_fin_dt
        ).count()

        stats['clientes_asignados'] = db.query(models.Prospecto).filter(
            models.Prospecto.agente_asignado_id != None,
            models.Prospecto.fecha_registro >= fecha_inicio_dt,
            models.Prospecto.fecha_registro <= fecha_fin_dt
        ).count()

        destinos_query = db.query(models.Prospecto.destino).filter(
            models.Prospecto.fecha_registro >= fecha_inicio_dt,
            models.Prospecto.fecha_registro <= fecha_fin_dt,
            models.Prospecto.destino.isnot(None),
            models.Prospecto.destino != ''
        ).distinct().all()
        stats['destinos_count'] = len(destinos_query)

        stats['ventas_count'] = db.query(models.Prospecto).filter(
            models.Prospecto.estado == EstadoProspecto.GANADO.value,
            models.Prospecto.fecha_registro >= fecha_inicio_dt,
            models.Prospecto.fecha_registro <= fecha_fin_dt
        ).count()

        stats['prospectos_nuevos'] = db.query(models.Prospecto).filter(
            models.Prospecto.estado == EstadoProspecto.NUEVO.value,
            models.Prospecto.fecha_registro >= fecha_inicio_dt,
            models.Prospecto.fecha_registro <= fecha_fin_dt
        ).count()

        stats['prospectos_seguimiento'] = db.query(models.Prospecto).filter(
            models.Prospecto.estado == EstadoProspecto.EN_SEGUIMIENTO.value,
            models.Prospecto.fecha_registro >= fecha_inicio_dt,
            models.Prospecto.fecha_registro <= fecha_fin_dt
        ).count()

        stats['prospectos_cotizados'] = db.query(models.Prospecto).filter(
            models.Prospecto.estado == EstadoProspecto.COTIZADO.value,
            models.Prospecto.fecha_registro >= fecha_inicio_dt,
            models.Prospecto.fecha_registro <= fecha_fin_dt
        ).count()

        stats['prospectos_ganados'] = db.query(models.Prospecto).filter(
            models.Prospecto.estado == EstadoProspecto.GANADO.value,
            models.Prospecto.fecha_registro >= fecha_inicio_dt,
            models.Prospecto.fecha_registro <= fecha_fin_dt
        ).count()

        stats['prospectos_perdidos'] = db.query(models.Prospecto).filter(
            models.Prospecto.estado == EstadoProspecto.CERRADO_PERDIDO.value,
            models.Prospecto.fecha_registro >= fecha_inicio_dt,
            models.Prospecto.fecha_registro <= fecha_fin_dt
        ).count()

        stats['ventas_canceladas'] = db.query(models.Prospecto).filter(
            models.Prospecto.estado == EstadoProspecto.VENTA_CANCELADA.value,
            models.Prospecto.fecha_registro >= fecha_inicio_dt,
            models.Prospecto.fecha_registro <= fecha_fin_dt
        ).count()

        stats['destinos_populares'] = db.query(
            models.Prospecto.destino,
            func.count(models.Prospecto.id).label('count')
        ).filter(
            models.Prospecto.fecha_registro >= fecha_inicio_dt,
            models.Prospecto.fecha_registro <= fecha_fin_dt,
            models.Prospecto.destino.isnot(None),
            models.Prospecto.destino != ''
        ).group_by(models.Prospecto.destino).order_by(func.count(models.Prospecto.id).desc()).limit(10).all()

        conversion_agentes = []
        agentes = db.query(models.Usuario).filter(
            models.Usuario.tipo_usuario == TipoUsuario.AGENTE.value,
            models.Usuario.activo == 1
        ).all()

        for agente in agentes:
            total_agente = db.query(models.Prospecto).filter(
                models.Prospecto.agente_asignado_id == agente.id,
                models.Prospecto.fecha_registro >= fecha_inicio_dt,
                models.Prospecto.fecha_registro <= fecha_fin_dt
            ).count()

            ganados_agente = db.query(models.HistorialEstado).filter(
                models.HistorialEstado.usuario_id == agente.id,
                models.HistorialEstado.estado_nuevo == EstadoProspecto.GANADO.value,
                models.HistorialEstado.fecha_cambio >= fecha_inicio_dt,
                models.HistorialEstado.fecha_cambio <= fecha_fin_dt
            ).count()

            cotizados_agente = db.query(models.EstadisticaCotizacion).filter(
                models.EstadisticaCotizacion.agente_id == agente.id,
                models.EstadisticaCotizacion.fecha_cotizacion >= fecha_inicio_obj,
                models.EstadisticaCotizacion.fecha_cotizacion <= fecha_fin_obj
            ).count()

            conversion_agentes.append({
                'username': agente.username,
                'total_prospectos': total_agente,
                'cotizados': cotizados_agente,
                'ganados': ganados_agente
            })

        stats['conversion_agentes'] = conversion_agentes

        excel_file = generar_excel_estadisticas(stats, periodo, fecha_inicio_obj, fecha_fin_obj)

        if not excel_file:
            raise HTTPException(status_code=500, detail="Error generando archivo Excel")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dashboard_{timestamp}.xlsx"

        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        print(f"❌ Error exportando dashboard: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error al exportar estadísticas")

@router.get("/clientes/historial", response_class=HTMLResponse)
async def historial_cliente(
    request: Request,
    busqueda: str = Query(None),
    telefono: str = Query(None),
    fecha_busqueda: str = Query(None),
    db: Session = Depends(database.get_db)
):
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    cliente_principal = None
    prospectos = []

    query = db.query(models.Prospecto)

    filtros = []

    if busqueda:
        term = f"%{busqueda}%"
        filtros.append(or_(
            models.Prospecto.telefono.ilike(term),
            models.Prospecto.telefono_secundario.ilike(term),
            models.Prospecto.correo_electronico.ilike(term),
            models.Prospecto.nombre.ilike(term),
            models.Prospecto.apellido.ilike(term)
        ))

    if telefono:
        filtros.append(or_(
            models.Prospecto.telefono == telefono,
            models.Prospecto.telefono_secundario == telefono
        ))

    if fecha_busqueda:
        try:
            fecha_dt = datetime.strptime(fecha_busqueda, "%d/%m/%Y").date()
            fecha_inicio = datetime.combine(fecha_dt, datetime.min.time())
            fecha_fin = datetime.combine(fecha_dt, datetime.max.time())
            filtros.append(and_(
                models.Prospecto.fecha_registro >= fecha_inicio,
                models.Prospecto.fecha_registro <= fecha_fin
            ))
        except ValueError:
            pass

    if filtros:
        query = query.filter(and_(*filtros))
        prospectos = query.order_by(models.Prospecto.fecha_registro.desc()).all()

        if prospectos:
            cliente_principal = prospectos[0]

    return templates.TemplateResponse("historial_cliente.html", {
        "request": request,
        "current_user": user,
        "cliente": cliente_principal,
        "prospectos": prospectos,
        "busqueda_activa": busqueda or telefono,
        "fecha_activa": fecha_busqueda
    })
