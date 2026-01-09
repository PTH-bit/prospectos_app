# Instrucciones para agentes AI (Copilot)

Breve: este repositorio es una aplicación monolítica en FastAPI para gestionar prospectos (ZARITA!). Aquí están las decisiones y patrones esenciales para ser productivo rápidamente.

- **Arquitectura**: backend en `main.py` (FastAPI + Jinja2), modelos en `models.py` (SQLAlchemy), DB en `database.py` (SQLite). Plantillas Jinja2 en `templates/`, estáticos en `static/` y archivos subidos en `uploads/`.
- **Punto de entrada**: `main.py` — la mayoría de rutas y lógica de UI/negocio residen aquí.

- **Autenticación**: simple, basada en `auth.py` (PassLib + JWT helpers). La app usa sesiones en memoria (`active_sessions` en `main.py`) y cookies `session_token`. Nota: `SECRET_KEY` en `auth.py` es estático y debe cambiarse en producción.

- **Modelos y enums**: ver `models.py` para `TipoUsuario` (administrador/supervisor/agente) y `EstadoProspecto` (nuevo, seguimiento, cotizado, ganado, perdido). Respeta estos valores al filtrar o crear estados.

- **Patrones de base de datos**: `database.create_tables()` crea tablas; `database.check_and_migrate()` / `migrate_database()` realizan alteraciones simples vía PRAGMA/ALTER. Para cambios estructurales preferir migraciones controladas: revisar `migrate_database()` antes de ejecutar.

- **Convenciones del código**:
  - Rutas devuelven `TemplateResponse` para vistas (Jinja2). Sigue el patrón de obtener `user = await get_current_user(request, db)` y redirigir si es `None`.
  - Paginación en listados: query params `page` y `limit` (ver `/prospectos`). Implementa nuevos listados con los mismos parámetros.
  - Filtros por defecto: `/prospectos` aplica filtros por rol (agente vs admin). Mantén compatibilidad con esa lógica al cambiar queries.
  - Validaciones de formulario se hacen en endpoints con `Form(...)` y redirecciones a la vista con mensajes en query string (p. ej. `?error=...`).

- **Flujos importantes** (ejemplos):
  - Login: `POST /login` (formulario, crea cookie `session_token`).
  - Dashboard: `GET /dashboard` admite `periodo`, `fecha_inicio`, `fecha_fin`.
  - Listar prospectos: `GET /prospectos` con filtros `estado`, `agente_asignado_id`, `busqueda_global`, `page`, `limit`.
  - Crear prospecto: `POST /prospectos` valida indicativos y detecta clientes duplicados por teléfono.

- **Migración y datos de prueba**:
  - Iniciar app local: `uvicorn main:app --reload`.
  - Crear datos de prueba: `python generar_datos_prueba.py`.
  - DB: archivo `prospectos.db` en la raíz del proyecto; `database.reset_database()` es para desarrollo.

- **Cosas a tener en cuenta para cambios automatizados**:
  - `active_sessions` es almacenamiento en memoria — tests o workers múltiples requieren cambiar esta estrategia.
  - Evitar cambios que rompan los nombres de enums (`TipoUsuario`, `EstadoProspecto`) sin actualizar todas las queries.
  - Las plantillas Jinja2 consumen variables con nombres específicos (ej. `prospectos`, `current_user`, `page`, `total_pages`). Mantener esos nombres para no romper vistas.

- **Dónde añadir código nuevo**:
  - Para cambios rápidos: añadir rutas en `main.py` siguiendo el estilo existente.
  - Si el cambio crece, separar en módulos nuevos y registrar routers en `main.py` (mantener misma inyección `Depends(database.get_db)`).

- **Pruebas y calidad**:
  - No hay test suite incluida. Al agregar tests, usar `pytest` y un SQLite en memoria (`sqlite:///:memory:`) o crear un fixture que utilice `database.SessionLocal` apuntando a una DB temporal.

- **Seguridad y producción**:
  - Reemplazar `SECRET_KEY` y manejar contraseñas/credenciales con variables de entorno.
  - Revisar envíos de email: `enviar_notificacion_email` en `main.py` es un stub, implementar con credenciales seguras si se activa.

Si algo no queda claro o quieres que adapte las instrucciones (por ejemplo, añadir ejemplos de endpoints concretos o mapeos de plantillas), dime qué sección ampliar.
