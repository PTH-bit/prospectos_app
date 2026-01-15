from fastapi import APIRouter, Request, Form, Depends, UploadFile, File, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
import shutil
import database
import models
import auth
import excel_import
import pandas as pd
import io
from datetime import datetime
from models import TipoUsuario, EstadoProspecto
from dependencies import require_admin, get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/usuarios", response_class=HTMLResponse)
async def listar_usuarios(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    filtro_estado: str = Query("activos"),  # activos, inactivos, todos
    db: Session = Depends(database.get_db),
    user: models.Usuario = Depends(require_admin)
):
    """Lista usuarios con paginación y filtro de estado"""

    # Query base
    query = db.query(models.Usuario)

    # Aplicar filtro de estado
    if filtro_estado == "activos":
        query = query.filter(models.Usuario.activo == 1)
    elif filtro_estado == "inactivos":
        query = query.filter(models.Usuario.activo == 0)
    # Si es "todos", no filtrar

    # Contar total
    total_usuarios = query.count()

    # Calcular paginación
    total_pages = (total_usuarios + limit - 1) // limit
    offset = (page - 1) * limit

    # Obtener usuarios paginados
    usuarios = query.order_by(models.Usuario.fecha_creacion.desc()).offset(offset).limit(limit).all()

    return templates.TemplateResponse("usuarios/lista.html", {
        "request": request,
        "current_user": user,
        "usuarios": usuarios,
        "tipos_usuario": [tipo.value for tipo in TipoUsuario],
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "total_usuarios": total_usuarios,
        "filtro_estado": filtro_estado
    })

@router.post("/usuarios")
async def crear_usuario(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    tipo_usuario: str = Form(...),
    db: Session = Depends(database.get_db),
    user: models.Usuario = Depends(require_admin)
):
    try:
        # Verificar si usuario ya existe
        existing_user = db.query(models.Usuario).filter(
            (models.Usuario.username == username) | (models.Usuario.email == email)
        ).first()

        if existing_user:
            return RedirectResponse(url="/usuarios?error=Usuario o email ya existen", status_code=303)

        # Crear usuario
        nuevo_usuario = models.Usuario(
            username=username,
            email=email,
            hashed_password=auth.get_password_hash(password),
            tipo_usuario=tipo_usuario
        )

        db.add(nuevo_usuario)
        db.commit()

        return RedirectResponse(url="/usuarios?success=Usuario creado correctamente", status_code=303)

    except Exception as e:
        db.rollback()
        print(f"❌ Error creating user: {e}")
        return RedirectResponse(url="/usuarios?error=Error al crear usuario", status_code=303)

@router.post("/usuarios/{usuario_id}/editar")
async def editar_usuario(
    request: Request,
    usuario_id: int,
    username: str = Form(...),
    email: str = Form(...),
    tipo_usuario: str = Form(...),
    password: str = Form(None),
    db: Session = Depends(database.get_db),
    user: models.Usuario = Depends(require_admin)
):
    try:
        usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
        if not usuario:
            return RedirectResponse(url="/usuarios?error=Usuario no encontrado", status_code=303)

        # Verificar si username/email ya existen en otros usuarios
        existing_user = db.query(models.Usuario).filter(
            (models.Usuario.username == username) | (models.Usuario.email == email)
        ).filter(models.Usuario.id != usuario_id).first()

        if existing_user:
            return RedirectResponse(url="/usuarios?error=Usuario o email ya existen", status_code=303)

        # Actualizar datos
        usuario.username = username
        usuario.email = email
        usuario.tipo_usuario = tipo_usuario

        # Actualizar contraseña si se proporcionó
        if password:
            usuario.hashed_password = auth.get_password_hash(password)

        db.commit()

        return RedirectResponse(url="/usuarios?success=Usuario actualizado correctamente", status_code=303)

    except Exception as e:
        db.rollback()
        print(f"❌ Error updating user: {e}")
        return RedirectResponse(url="/usuarios?error=Error al actualizar usuario", status_code=303)

@router.post("/usuarios/{usuario_id}/eliminar")
async def eliminar_usuario(
    request: Request,
    usuario_id: int,
    db: Session = Depends(database.get_db),
    user: models.Usuario = Depends(require_admin)
):
    try:
        # No permitir eliminar el propio usuario
        if usuario_id == user.id:
            return RedirectResponse(url="/usuarios?error=No puede eliminar su propio usuario", status_code=303)

        usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
        if not usuario:
            return RedirectResponse(url="/usuarios?error=Usuario no encontrado", status_code=303)

        db.delete(usuario)
        db.commit()

        return RedirectResponse(url="/usuarios?success=Usuario eliminado correctamente", status_code=303)

    except Exception as e:
        db.rollback()
        print(f"❌ Error deleting user: {e}")
        return RedirectResponse(url="/usuarios?error=Error al eliminar usuario", status_code=303)

@router.post("/usuarios/{usuario_id}/desactivar")
async def desactivar_usuario(
    request: Request,
    usuario_id: int,
    db: Session = Depends(database.get_db),
    user: models.Usuario = Depends(require_admin)
):
    """Desactiva un usuario y reasigna sus prospectos activos a servicio_cliente"""
    try:
        # No permitir desactivar el propio usuario
        if usuario_id == user.id:
            return RedirectResponse(url="/usuarios?error=No puede desactivar su propio usuario", status_code=303)

        usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
        if not usuario:
            return RedirectResponse(url="/usuarios?error=Usuario no encontrado", status_code=303)

        if usuario.activo == 0:
            return RedirectResponse(url="/usuarios?error=El usuario ya está inactivo", status_code=303)

        # Buscar usuario servicio_cliente
        servicio_cliente = db.query(models.Usuario).filter(
            models.Usuario.username == "servicio_cliente"
        ).first()

        if not servicio_cliente:
            return RedirectResponse(url="/usuarios?error=Usuario servicio_cliente no encontrado", status_code=303)

        # Reasignar prospectos activos
        prospectos_activos = db.query(models.Prospecto).filter(
            models.Prospecto.agente_asignado_id == usuario_id,
            models.Prospecto.estado.in_([
                EstadoProspecto.NUEVO.value,
                EstadoProspecto.EN_SEGUIMIENTO.value,
                EstadoProspecto.COTIZADO.value
            ])
        ).all()

        prospectos_reasignados = 0
        for prospecto in prospectos_activos:
            prospecto.agente_original_id = usuario_id
            prospecto.agente_asignado_id = servicio_cliente.id
            prospectos_reasignados += 1

        # Desactivar usuario
        usuario.activo = 0
        usuario.email = "servicioclientetravelhouse@gmail.com"

        db.commit()

        mensaje = f"Usuario desactivado correctamente. {prospectos_reasignados} prospectos reasignados a servicio_cliente"
        return RedirectResponse(url=f"/usuarios?success={mensaje}", status_code=303)

    except Exception as e:
        db.rollback()
        print(f"Error desactivando usuario: {e}")
        return RedirectResponse(url="/usuarios?error=Error al desactivar usuario", status_code=303)

@router.post("/usuarios/{usuario_id}/reactivar")
async def reactivar_usuario(
    request: Request,
    usuario_id: int,
    email: str = Form(...),
    db: Session = Depends(database.get_db),
    user: models.Usuario = Depends(require_admin)
):
    """Reactiva un usuario inactivo"""
    try:
        usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
        if not usuario:
            return RedirectResponse(url="/usuarios?error=Usuario no encontrado", status_code=303)

        if usuario.activo == 1:
            return RedirectResponse(url="/usuarios?error=El usuario ya está activo", status_code=303)

        # Validar que el email no esté duplicado entre usuarios activos
        email_existente = db.query(models.Usuario).filter(
            models.Usuario.email == email,
            models.Usuario.activo == 1,
            models.Usuario.id != usuario_id
        ).first()

        if email_existente:
            return RedirectResponse(url="/usuarios?error=El email ya está en uso por otro usuario activo", status_code=303)

        # Reactivar usuario
        usuario.activo = 1
        usuario.email = email

        db.commit()

        return RedirectResponse(url="/usuarios?success=Usuario reactivado correctamente", status_code=303)

    except Exception as e:
        db.rollback()
        print(f"Error reactivando usuario: {e}")
        return RedirectResponse(url="/usuarios?error=Error al reactivar usuario", status_code=303)

@router.post("/importar-usuarios")
async def importar_usuarios(
    request: Request,
    archivo: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    user: models.Usuario = Depends(require_admin)
):
    """Procesa la importación de usuarios desde Excel"""
    try:
        # Validar archivo
        es_valido, mensaje_error = excel_import.validar_archivo_excel(archivo)
        if not es_valido:
            return templates.TemplateResponse("importar_datos.html", {
                "request": request,
                "current_user": user,
                "resultado_usuarios": {
                    "exitosos": 0,
                    "errores": [{"fila": 0, "error": mensaje_error}]
                }
            })

        # Guardar archivo temporalmente
        temp_path = f"uploads/temp_{archivo.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(archivo.file, buffer)

        # Importar usuarios
        resultado = excel_import.importar_usuarios_desde_excel(temp_path, db)

        # Eliminar archivo temporal
        os.remove(temp_path)

        return templates.TemplateResponse("importar_datos.html", {
            "request": request,
            "current_user": user,
            "resultado_usuarios": resultado
        })

    except Exception as e:
        return templates.TemplateResponse("importar_datos.html", {
            "request": request,
            "current_user": user,
            "resultado_usuarios": {
                "exitosos": 0,
                "errores": [{"fila": 0, "error": f"Error procesando archivo: {str(e)}"}]
            }
        })

def generar_excel_usuarios(usuarios, filename="usuarios_export.xlsx"):
    """
    Genera archivo Excel con lista de usuarios del sistema
    """
    try:
        data = []
        for u in usuarios:
            # Contar prospectos asignados
            prospectos_count = len([p for p in u.prospectos if p.fecha_eliminacion is None]) if hasattr(u, 'prospectos') else 0

            data.append({
                'ID': u.id,
                'Username': u.username,
                'Email': u.email,
                'Tipo Usuario': u.tipo_usuario.title(),
                'Estado': 'Activo' if u.activo else 'Inactivo',
                'Fecha Creación': u.fecha_creacion.strftime("%d/%m/%Y %H:%M"),
                'Prospectos Asignados': prospectos_count
            })

        df = pd.DataFrame(data)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Usuarios', index=False)

            workbook = writer.book
            worksheet = writer.sheets['Usuarios']

            from openpyxl.styles import Font, PatternFill, Alignment
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_font = Font(color="FFFFFF", bold=True)

            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")

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

            worksheet.auto_filter.ref = worksheet.dimensions

        output.seek(0)
        return output

    except Exception as e:
        print(f"❌ Error generando Excel de usuarios: {e}")
        import traceback
        traceback.print_exc()
        return None

@router.get("/exportar/usuarios")
async def exportar_usuarios(
    request: Request,
    db: Session = Depends(database.get_db),
    user: models.Usuario = Depends(require_admin)
):
    """Exporta lista de usuarios a Excel (solo admins)"""
    try:
        # Obtener todos los usuarios
        usuarios = db.query(models.Usuario).order_by(models.Usuario.fecha_creacion.desc()).all()

        # Generar Excel
        excel_file = generar_excel_usuarios(usuarios)

        if not excel_file:
            raise HTTPException(status_code=500, detail="Error generando archivo Excel")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"usuarios_{timestamp}.xlsx"

        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        print(f"❌ Error exportando usuarios: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error al exportar usuarios")
