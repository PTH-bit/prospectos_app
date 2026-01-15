from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import secrets
import database
import models
import auth
from dependencies import active_sessions, get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    user = db.query(models.Usuario).filter(models.Usuario.username == username).first()
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Usuario no encontrado"
        })

    if not auth.verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Contraseña incorrecta"
        })

    session_token = secrets.token_urlsafe(32)
    active_sessions[session_token] = user.id

    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=1800,
        path="/"
    )

    return response

@router.get("/logout")
async def logout(request: Request):
    session_token = request.cookies.get("session_token")
    if session_token and session_token in active_sessions:
        del active_sessions[session_token]

    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_token")
    return response

@router.get("/check-auth")
async def check_auth(request: Request, db: Session = Depends(database.get_db)):
    user = await get_current_user(request, db)
    if user:
        return {
            "authenticated": True,
            "user": user.username,
            "user_type": user.tipo_usuario,
            "active_sessions": len(active_sessions)
        }
    else:
        return {
            "authenticated": False,
            "active_sessions": len(active_sessions)
        }
