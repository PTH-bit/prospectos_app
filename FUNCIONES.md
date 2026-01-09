# 📚 Documentación de Funciones - Sistema CRM ZARITA!

Este documento describe todas las funciones principales, endpoints de la API y su funcionalidad en el sistema CRM de gestión de prospectos.

---

## 📑 Tabla de Contenidos

1. [Funciones Auxiliares](#funciones-auxiliares)
2. [Autenticación](#autenticación)
3. [Dashboard](#dashboard)
4. [Gestión de Prospectos](#gestión-de-prospectos)
5. [Gestión de Usuarios](#gestión-de-usuarios)
6. [Notificaciones](#notificaciones)
7. [Importación de Datos](#importación-de-datos)
8. [Documentos](#documentos)
9. [Estadísticas](#estadísticas)

---

## 🔧 Funciones Auxiliares

### `enviar_notificacion_email(destinatario, asunto, cuerpo)`
**Descripción:** Envía notificaciones por correo electrónico (actualmente simulado).

**Parámetros:**
- `destinatario` (str): Email del destinatario
- `asunto` (str): Asunto del correo
- `cuerpo` (str): Contenido del mensaje

**Retorna:** `bool` - True si se envió correctamente, False en caso de error

**Uso futuro:** Configurar credenciales SMTP para envío real de emails.

---

### `parsear_fecha(fecha_str)`
**Descripción:** Parsea fechas en múltiples formatos.

**Parámetros:**
- `fecha_str` (str): Fecha en formato DD/MM/YYYY o YYYY-MM-DD

**Retorna:** `date` o `None` si hay error

**Formatos soportados:**
- DD/MM/YYYY (ejemplo: 25/12/2025)
- YYYY-MM-DD (ejemplo: 2025-12-25)

---

### `normalizar_texto_mayusculas(texto)`
**Descripción:** Normaliza texto a mayúsculas y elimina espacios extras.

**Parámetros:**
- `texto` (str): Texto a normalizar

**Retorna:** `str` o `None` si está vacío

**Ejemplo:**
```python
normalizar_texto_mayusculas("  juan pérez  ")  # "JUAN PÉREZ"
```

---

### `normalizar_numero(numero)`
**Descripción:** Limpia números removiendo espacios, guiones y símbolos.

**Parámetros:**
- `numero` (str): Número a normalizar

**Retorna:** `str` - Solo dígitos

**Ejemplo:**
```python
normalizar_numero("300-123-4567")  # "3001234567"
```

---

### `normalizar_email(email)`
**Descripción:** Normaliza emails a minúsculas y elimina espacios.

**Parámetros:**
- `email` (str): Email a normalizar

**Retorna:** `str` o `None` si está vacío

**Ejemplo:**
```python
normalizar_email("  USUARIO@EJEMPLO.COM  ")  # "usuario@ejemplo.com"
```

---

### `normalizar_fecha_input(fecha_str)`
**Descripción:** Parsea fechas de inputs HTML o formato DD/MM/YYYY.

**Parámetros:**
- `fecha_str` (str): Fecha a parsear

**Retorna:** `date` o `None`

---

### `calcular_rango_fechas(periodo, fecha_inicio, fecha_fin)`
**Descripción:** Calcula el rango de fechas según el periodo seleccionado.

**Parámetros:**
- `periodo` (str): "dia", "semana", "mes", "año", "personalizado"
- `fecha_inicio` (str): Fecha inicio personalizada (opcional)
- `fecha_fin` (str): Fecha fin personalizada (opcional)

**Retorna:** `tuple` - (fecha_inicio_dt, fecha_fin_dt)

**Periodos:**
- **dia**: Hoy
- **semana**: Lunes a domingo de la semana actual
- **mes**: Primer día al último día del mes actual
- **año**: 1 de enero al 31 de diciembre del año actual
- **personalizado**: Usa fecha_inicio y fecha_fin proporcionadas

---

## 🔐 Autenticación

### `GET /`
**Descripción:** Página de inicio de sesión.

**Retorna:** Template HTML de login

---

### `POST /login`
**Descripción:** Procesa el inicio de sesión.

**Parámetros (Form):**
- `username` (str): Nombre de usuario
- `password` (str): Contraseña

**Retorna:** 
- Redirección a `/dashboard` si es exitoso
- Template de login con error si falla

**Seguridad:**
- Verifica usuario en base de datos
- Valida contraseña con hash BCrypt
- Crea sesión con token seguro
- Cookie httponly con timeout de 30 minutos

---

### `GET /logout`
**Descripción:** Cierra la sesión del usuario.

**Retorna:** Redirección a `/`

**Acciones:**
- Elimina token de sesiones activas
- Borra cookie de sesión

---

### `get_current_user(request, db)`
**Descripción:** Obtiene el usuario actual desde la sesión.

**Parámetros:**
- `request` (Request): Objeto de solicitud
- `db` (Session): Sesión de base de datos

**Retorna:** `Usuario` o `None`

**Uso:** Dependency en endpoints protegidos

---

### `require_admin(user)`
**Descripción:** Verifica que el usuario sea administrador.

**Parámetros:**
- `user` (Usuario): Usuario actual

**Retorna:** `Usuario` si es admin

**Excepciones:** HTTPException 403 si no es admin

---

## 📊 Dashboard

### `GET /dashboard`
**Descripción:** Panel de control principal con estadísticas.

**Parámetros (Query):**
- `periodo` (str): "dia", "semana", "mes", "año", "personalizado" (default: "mes")
- `fecha_inicio` (str): Fecha inicio para periodo personalizado
- `fecha_fin` (str): Fecha fin para periodo personalizado

**Retorna:** Template HTML con estadísticas

**Estadísticas para Administradores/Supervisores:**
- Total de prospectos en el periodo
- Prospectos con datos completos vs. incompletos
- Clientes sin asignar
- Clientes asignados
- Destinos únicos registrados
- Ventas cerradas
- Prospectos por estado (Nuevos, Seguimiento, Cotizados, Ganados, Perdidos, Canceladas)
- Destinos más populares (top 5)
- Conversión por agente (total, cotizados, ganados)

**Estadísticas para Agentes:**
- Total de prospectos asignados en el periodo
- Prospectos con datos completos vs. incompletos
- Destinos únicos
- Ventas cerradas
- Prospectos por estado
- Destinos más populares

**Filtros:**
- Los filtros se aplican a `fecha_registro` de prospectos
- Las estadísticas de conversión usan `fecha_cambio` del historial

---

## 👥 Gestión de Prospectos

### `GET /prospectos`
**Descripción:** Lista de prospectos con filtros y paginación.

**Parámetros (Query):**
- `destino` (str): Filtrar por destino
- `telefono` (str): Filtrar por teléfono
- `medio_ingreso_id` (int): Filtrar por medio de ingreso
- `agente_asignado_id` (int): Filtrar por agente
- `estado` (str): Filtrar por estado
- `busqueda_global` (str): Búsqueda en nombre, teléfono, email
- `fecha_inicio` (str): Filtro de fecha inicio
- `fecha_fin` (str): Filtro de fecha fin
- `page` (int): Página actual (default: 1)
- `limit` (int): Registros por página (default: 10, max: 100)

**Retorna:** Template HTML con lista de prospectos

**Características:**
- Paginación automática
- Filtros combinables
- Búsqueda global en múltiples campos
- Ordenamiento por fecha de registro (más recientes primero)
- Agentes solo ven sus prospectos
- Admins ven todos los prospectos

---

### `GET /prospectos/nuevo`
**Descripción:** Formulario para crear nuevo prospecto.

**Retorna:** Template HTML con formulario

**Datos del formulario:**
- Información básica (nombre, apellido)
- Contacto (email, teléfonos con indicativos)
- Detalles del viaje (origen, destino, fechas, pasajeros)
- Medio de ingreso
- Observaciones

---

### `POST /prospectos/crear`
**Descripción:** Crea un nuevo prospecto.

**Parámetros (Form):**
- `nombre` (str): Nombre del prospecto
- `apellido` (str): Apellido del prospecto
- `correo_electronico` (str): Email
- `telefono` (str): Teléfono principal
- `indicativo_telefono` (str): Código de país (default: "57")
- `telefono_secundario` (str): Teléfono secundario (opcional)
- `indicativo_telefono_secundario` (str): Código de país secundario
- `ciudad_origen` (str): Ciudad de origen
- `destino` (str): Destino del viaje
- `fecha_ida` (str): Fecha de ida (YYYY-MM-DD)
- `fecha_vuelta` (str): Fecha de vuelta (YYYY-MM-DD)
- `pasajeros_adultos` (int): Número de adultos
- `pasajeros_ninos` (int): Número de niños
- `pasajeros_infantes` (int): Número de infantes
- `medio_ingreso_id` (int): ID del medio de ingreso
- `observaciones` (str): Notas adicionales

**Retorna:** Redirección a `/prospectos`

**Acciones automáticas:**
- Normalización de datos (emails, teléfonos, textos)
- Asignación del agente actual
- Estado inicial: "nuevo"
- Verificación de datos completos
- Creación de interacción inicial
- Generación de notificación de asignación

---

### `GET /prospectos/{id}`
**Descripción:** Detalle completo de un prospecto.

**Parámetros (Path):**
- `id` (int): ID del prospecto

**Retorna:** Template HTML con detalle del prospecto

**Información mostrada:**
- Datos completos del prospecto
- Historial de interacciones
- Documentos adjuntos
- Historial de cambios de estado
- Botones de WhatsApp
- Información de cliente recurrente (si aplica)

**Permisos:**
- Agentes solo ven sus prospectos
- Admins ven todos

---

### `GET /prospectos/{id}/editar`
**Descripción:** Formulario para editar prospecto.

**Parámetros (Path):**
- `id` (int): ID del prospecto

**Retorna:** Template HTML con formulario pre-llenado

---

### `POST /prospectos/{id}/actualizar`
**Descripción:** Actualiza un prospecto existente.

**Parámetros (Path):**
- `id` (int): ID del prospecto

**Parámetros (Form):** Mismos que crear prospecto

**Retorna:** Redirección a detalle del prospecto

**Acciones:**
- Normalización de datos
- Verificación de datos completos
- Registro de cambios en historial

---

### `POST /prospectos/{id}/cambiar-estado`
**Descripción:** Cambia el estado de un prospecto.

**Parámetros (Path):**
- `id` (int): ID del prospecto

**Parámetros (Form):**
- `nuevo_estado` (str): Estado destino
- `comentario` (str): Comentario del cambio (opcional)

**Retorna:** Redirección a detalle del prospecto

**Estados válidos:**
- nuevo
- en_seguimiento
- cotizado
- ganado
- cerrado_perdido
- venta_cancelada

**Acciones automáticas:**
- Registro en historial de estados
- Creación de interacción
- Si cambia a "cotizado": Registro en estadísticas de cotización
- Si cambia a "ganado": Solicita datos adicionales (fecha de compra, etc.)

---

### `POST /prospectos/{id}/agregar-interaccion`
**Descripción:** Registra una nueva interacción con el prospecto.

**Parámetros (Path):**
- `id` (int): ID del prospecto

**Parámetros (Form):**
- `tipo_interaccion` (str): Tipo de interacción
- `descripcion` (str): Descripción detallada

**Tipos de interacción:**
- llamada
- email
- whatsapp
- reunion
- otro

**Retorna:** Redirección a detalle del prospecto

---

### `POST /prospectos/{id}/reasignar`
**Descripción:** Reasigna un prospecto a otro agente (solo admins).

**Parámetros (Path):**
- `id` (int): ID del prospecto

**Parámetros (Form):**
- `nuevo_agente_id` (int): ID del nuevo agente

**Retorna:** Redirección a detalle del prospecto

**Acciones:**
- Preserva agente original si es la primera reasignación
- Crea interacción de reasignación
- Genera notificación al nuevo agente

---

### `POST /prospectos/{id}/eliminar`
**Descripción:** Elimina lógicamente un prospecto (soft delete).

**Parámetros (Path):**
- `id` (int): ID del prospecto

**Retorna:** Redirección a `/prospectos`

**Acciones:**
- Establece `fecha_eliminacion` a la fecha actual
- El prospecto se excluye de consultas normales
- Los datos se preservan para auditoría

---

## 👤 Gestión de Usuarios

### `GET /usuarios`
**Descripción:** Lista de usuarios (solo admins).

**Retorna:** Template HTML con lista de usuarios

**Información mostrada:**
- Username
- Email
- Tipo de usuario
- Estado (activo/inactivo)
- Fecha de creación

---

### `GET /usuarios/nuevo`
**Descripción:** Formulario para crear nuevo usuario (solo admins).

**Retorna:** Template HTML con formulario

---

### `POST /usuarios/crear`
**Descripción:** Crea un nuevo usuario (solo admins).

**Parámetros (Form):**
- `username` (str): Nombre de usuario único
- `email` (str): Email
- `password` (str): Contraseña
- `tipo_usuario` (str): "administrador", "supervisor", "agente"
- `activo` (int): 1 (activo) o 0 (inactivo)

**Retorna:** Redirección a `/usuarios`

**Validaciones:**
- Username único
- Email válido
- Contraseña hasheada con BCrypt

---

### `POST /usuarios/{id}/toggle-activo`
**Descripción:** Activa/desactiva un usuario (solo admins).

**Parámetros (Path):**
- `id` (int): ID del usuario

**Retorna:** Redirección a `/usuarios`

**Acciones al desactivar:**
- Marca usuario como inactivo
- Reasigna todos sus prospectos a "Servicio al Cliente"
- Excluye de estadísticas futuras
- Preserva historial

---

## 🔔 Notificaciones

### `GET /notificaciones`
**Descripción:** Panel de notificaciones del usuario.

**Parámetros (Query):**
- `tipo` (str): Filtrar por tipo
- `estado` (str): "leidas" o "no_leidas"
- `fecha_inicio` (str): Filtro de fecha inicio
- `fecha_fin` (str): Filtro de fecha fin
- `busqueda` (str): Búsqueda por ID de cliente o cotización

**Retorna:** Template HTML con notificaciones

**Tipos de notificación:**
- asignacion: Nuevo prospecto asignado
- seguimiento: Recordatorio de seguimiento
- inactividad: Alerta de prospecto inactivo

---

### `POST /notificaciones/crear`
**Descripción:** Crea una notificación manual.

**Parámetros (Form):**
- `prospecto_id` (int): ID del prospecto relacionado
- `tipo` (str): Tipo de notificación
- `mensaje` (str): Contenido de la notificación
- `fecha_programada` (str): Fecha para recordatorio (opcional)

**Retorna:** Redirección a `/notificaciones`

**Acciones:**
- Crea notificación
- Registra interacción en el prospecto
- Opcionalmente programa para fecha futura

---

### `POST /notificaciones/{id}/marcar-leida`
**Descripción:** Marca una notificación como leída.

**Parámetros (Path):**
- `id` (int): ID de la notificación

**Retorna:** JSON con status

---

### `POST /notificaciones/marcar-todas-leidas`
**Descripción:** Marca todas las notificaciones del usuario como leídas.

**Retorna:** Redirección a `/notificaciones`

---

## 📥 Importación de Datos

### `GET /importar-datos`
**Descripción:** Página de importación de datos (solo admins).

**Retorna:** Template HTML con opciones de importación

---

### `POST /importar-usuarios`
**Descripción:** Importa usuarios desde archivo Excel (solo admins).

**Parámetros (Form):**
- `archivo` (UploadFile): Archivo Excel (.xlsx)

**Retorna:** Template con resultado de importación

**Formato del Excel:**
- Columnas: username, email, password, tipo_usuario, activo
- Primera fila: encabezados
- Datos desde fila 2

**Validaciones:**
- Formato de archivo válido
- Columnas requeridas presentes
- Datos válidos en cada fila

**Resultado:**
- Número de usuarios importados exitosamente
- Lista de errores por fila
- Usuarios marcados como inactivos

---

### `POST /importar-prospectos`
**Descripción:** Importa prospectos desde archivo Excel (solo admins).

**Parámetros (Form):**
- `archivo` (UploadFile): Archivo Excel (.xlsx)

**Retorna:** Template con resultado de importación

**Formato del Excel:**
- Columnas: nombre, apellido, telefono, email, ciudad_origen, destino, fecha_ida, fecha_vuelta, pasajeros_adultos, pasajeros_ninos, pasajeros_infantes, medio_ingreso, agente_asignado, estado, observaciones
- Primera fila: encabezados
- Datos desde fila 2

**Características especiales:**
- Detección automática de clientes recurrentes (por teléfono)
- Normalización de datos
- Asignación de agentes por nombre de usuario
- Validación de medios de ingreso

**Resultado:**
- Número de prospectos importados
- Número de clientes recurrentes detectados
- Lista de errores por fila

---

### `GET /descargar-plantilla/{tipo}`
**Descripción:** Descarga plantilla Excel de ejemplo (solo admins).

**Parámetros (Path):**
- `tipo` (str): "usuarios" o "prospectos"

**Retorna:** Archivo Excel para descarga

**Ubicación de plantillas:**
- `static/plantillas/plantilla_usuarios.xlsx`
- `static/plantillas/plantilla_prospectos.xlsx`

---

## 📄 Documentos

### `POST /prospectos/{id}/subir-documento`
**Descripción:** Sube un documento relacionado con un prospecto.

**Parámetros (Path):**
- `id` (int): ID del prospecto

**Parámetros (Form):**
- `archivo` (UploadFile): Archivo a subir
- `tipo_documento` (str): Tipo de documento
- `descripcion` (str): Descripción del documento

**Tipos de documento:**
- cotizacion
- contrato
- factura_proveedor
- reserva_proveedor
- pago_cliente
- pago_proveedor
- otro

**Retorna:** Redirección a detalle del prospecto

**Acciones:**
- Guarda archivo en `uploads/`
- Genera ID único de documento
- Registra en base de datos
- Crea interacción automática

**Validaciones:**
- Tamaño máximo de archivo
- Tipos de archivo permitidos
- Usuario tiene permiso sobre el prospecto

---

### `GET /documentos/{id}/descargar`
**Descripción:** Descarga un documento.

**Parámetros (Path):**
- `id` (int): ID del documento

**Retorna:** Archivo para descarga

**Permisos:**
- Agentes solo pueden descargar documentos de sus prospectos
- Admins pueden descargar cualquier documento

---

### `POST /documentos/{id}/eliminar`
**Descripción:** Elimina un documento.

**Parámetros (Path):**
- `id` (int): ID del documento

**Retorna:** Redirección a detalle del prospecto

**Acciones:**
- Elimina archivo físico del servidor
- Elimina registro de base de datos
- Registra interacción de eliminación

---

## 📈 Estadísticas

### Modelo `EstadisticaCotizacion`
**Descripción:** Registra cada vez que un prospecto es cotizado.

**Campos:**
- `id`: ID único
- `id_cotizacion`: ID generado (COT-YYYYMMDD-XXXX)
- `agente_id`: Agente que cotizó
- `prospecto_id`: Prospecto cotizado
- `fecha_cotizacion`: Fecha de la cotización
- `fecha_registro`: Timestamp de creación

**Uso:** Métricas de conversión y productividad de agentes

---

### Modelo `HistorialEstado`
**Descripción:** Registra cada cambio de estado de un prospecto.

**Campos:**
- `id`: ID único
- `prospecto_id`: Prospecto relacionado
- `estado_anterior`: Estado previo
- `estado_nuevo`: Nuevo estado
- `usuario_id`: Usuario que realizó el cambio
- `fecha_cambio`: Timestamp del cambio
- `comentario`: Comentario opcional

**Uso:** Auditoría y métricas de conversión

---

## 🔍 Métodos de Modelos

### `Prospecto.generar_id_cliente()`
**Descripción:** Genera un ID único para el cliente.

**Formato:** CL-YYYYMMDD-XXXX

**Ejemplo:** CL-20260109-0001

---

### `Prospecto.verificar_datos_completos()`
**Descripción:** Verifica si el prospecto tiene datos completos.

**Criterios:**
- Tiene email válido, O
- Tiene fechas de viaje, O
- Tiene más de 1 pasajero, O
- Tiene destino, O
- Tiene ciudad de origen

**Retorna:** `bool`

---

### `Prospecto.get_telefono_whatsapp(telefono_principal=True)`
**Descripción:** Obtiene el teléfono completo para WhatsApp.

**Parámetros:**
- `telefono_principal` (bool): True para teléfono principal, False para secundario

**Retorna:** `str` - Teléfono con indicativo (ejemplo: "573001234567")

---

### `Prospecto.get_whatsapp_link(telefono_principal=True)`
**Descripción:** Genera el enlace de WhatsApp.

**Parámetros:**
- `telefono_principal` (bool): True para teléfono principal, False para secundario

**Retorna:** `str` - URL de WhatsApp (ejemplo: "https://wa.me/573001234567")

---

### `Documento.generar_id_documento()`
**Descripción:** Genera un ID único para el documento.

**Formato:** DOC-YYYYMMDD-XXXX

**Ejemplo:** DOC-20260109-0001

---

### `EstadisticaCotizacion.generar_id_cotizacion()`
**Descripción:** Genera un ID único para la cotización.

**Formato:** COT-YYYYMMDD-XXXX

**Ejemplo:** COT-20260109-0001

---

## 🔄 Flujo de Estados de Prospecto

```
NUEVO
  ↓
EN_SEGUIMIENTO
  ↓
COTIZADO
  ↓
GANADO / CERRADO_PERDIDO
  ↓ (solo desde GANADO)
VENTA_CANCELADA
```

**Transiciones válidas:**
- NUEVO → EN_SEGUIMIENTO
- EN_SEGUIMIENTO → COTIZADO
- COTIZADO → GANADO
- COTIZADO → CERRADO_PERDIDO
- GANADO → VENTA_CANCELADA
- Cualquier estado → CERRADO_PERDIDO (cierre manual)

---

## 🔒 Niveles de Acceso

### Administrador
- ✅ Todas las funciones
- ✅ Ver todos los prospectos
- ✅ Gestionar usuarios
- ✅ Importar datos
- ✅ Reasignar prospectos
- ✅ Ver estadísticas globales

### Supervisor
- ✅ Ver todos los prospectos
- ✅ Ver estadísticas globales
- ✅ Reasignar prospectos
- ❌ Gestionar usuarios
- ❌ Importar datos

### Agente
- ✅ Ver sus prospectos asignados
- ✅ Crear nuevos prospectos
- ✅ Editar sus prospectos
- ✅ Cambiar estados
- ✅ Subir documentos
- ✅ Ver estadísticas personales
- ❌ Ver prospectos de otros agentes
- ❌ Reasignar prospectos
- ❌ Gestionar usuarios

---

## 📝 Notas Técnicas

### Sesiones
- Almacenamiento en memoria (diccionario `active_sessions`)
- Token generado con `secrets.token_urlsafe(32)`
- Timeout de 30 minutos (1800 segundos)
- Cookie httponly para seguridad

### Base de Datos
- ORM: SQLAlchemy 2.0+
- Soporte para PostgreSQL y SQLite
- Migraciones manuales con scripts Python
- Soft delete en prospectos

### Seguridad
- Contraseñas hasheadas con BCrypt
- Validación de permisos en cada endpoint
- Escape automático en templates Jinja2
- Protección contra SQL injection vía ORM

### Performance
- Paginación en listas largas
- Índices en campos de búsqueda frecuente
- Consultas optimizadas con joins
- Carga lazy de relaciones

---

## 🚀 Próximas Funcionalidades

- [ ] Exportación de reportes a Excel/PDF
- [ ] Envío real de emails (SMTP configurado)
- [ ] Notificaciones push en navegador
- [ ] API REST completa para integraciones
- [ ] Dashboard con gráficos interactivos
- [ ] Búsqueda avanzada con filtros combinados
- [ ] Automatización de seguimientos
- [ ] Integración con calendarios
- [ ] Chat interno entre agentes
- [ ] Aplicación móvil

---

**Última actualización:** Enero 2026  
**Versión del sistema:** 2.0  
**Desarrollado para:** ZARITA! Travel Agency
