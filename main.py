import os
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import database
import models
from models import TipoUsuario
import auth
from routers import auth as auth_router
from routers import users as users_router
from routers import prospects as prospects_router
from routers import dashboard as dashboard_router
from dependencies import active_sessions

app = FastAPI(title="Sistema de Prospectos")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Include Routers
app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(prospects_router.router)
app.include_router(dashboard_router.router)

@app.on_event("startup")
def startup():
    database.check_and_migrate()
    db = next(database.get_db())
    try:
        # Crear medios de ingreso por defecto
        medios = ["REDES", "TEL TRAVEL", "RECOMPRA", "REFERIDO", "FIDELIZACION"]
        for medio in medios:
            if not db.query(models.MedioIngreso).filter(models.MedioIngreso.nombre == medio).first():
                db.add(models.MedioIngreso(nombre=medio))
        
        # Crear usuario administrador por defecto
        if not db.query(models.Usuario).filter(models.Usuario.username == "admin").first():
            admin_user = models.Usuario(
                username="admin",
                email="admin@empresa.com",
                hashed_password=auth.get_password_hash("admin123"),
                tipo_usuario=TipoUsuario.ADMINISTRADOR.value
            )
            db.add(admin_user)
        
        # Crear un agente de prueba
        if not db.query(models.Usuario).filter(models.Usuario.username == "agente1").first():
            agente_user = models.Usuario(
                username="agente1",
                email="agente1@empresa.com",
                hashed_password=auth.get_password_hash("agente123"),
                tipo_usuario=TipoUsuario.AGENTE.value
            )
            db.add(agente_user)
        
        # Crear usuario de Servicio al Cliente
        if not db.query(models.Usuario).filter(models.Usuario.username == "servicio_cliente").first():
            servicio_user = models.Usuario(
                username="servicio_cliente",
                email="servicioclientetravelhouse@gmail.com",
                hashed_password=auth.get_password_hash("servicio123"),
                tipo_usuario=TipoUsuario.AGENTE.value,
                activo=1
            )
            db.add(servicio_user)
        
        db.commit()
        print("Datos iniciales creados correctamente")
        print("Usuario admin: admin / admin123")
        print("Usuario agente: agente1 / agente123")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error inicializando datos: {e}")
    finally:
        db.close()

@app.get("/health")
async def health_check(db: Session = Depends(database.get_db)):
    try:
        user_count = db.query(models.Usuario).count()
        prospecto_count = db.query(models.Prospecto).count()
        return {
            "status": "healthy",
            "database": "connected", 
            "users_count": user_count,
            "prospectos_count": prospecto_count,
            "active_sessions": len(active_sessions)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
