from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session
import database
import models
from models import TipoUsuario

# Almacenamiento simple de sesiones en memoria
# En un entorno de producción, esto debería reemplazarse por Redis o una tabla de base de datos
active_sessions = {}

async def get_current_user(request: Request, db: Session = Depends(database.get_db)):
    try:
        session_token = request.cookies.get("session_token")

        if not session_token:
            return None

        user_id = active_sessions.get(session_token)
        if not user_id:
            return None

        user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
        return user
    except Exception as e:
        print(f"❌ Error in get_current_user: {e}")
        return None

async def require_admin(user: models.Usuario = Depends(get_current_user)):
    if not user or user.tipo_usuario != TipoUsuario.ADMINISTRADOR.value:
        raise HTTPException(status_code=403, detail="No tiene permisos de administrador")
    return user
