# ✈️ ZARITA! - Sistema CRM de Gestión de Prospectos

Bienvenido a **ZARITA!**, un sistema CRM completo diseñado para optimizar la gestión de prospectos y clientes en agencias de viajes. Este sistema permite realizar un seguimiento detallado de cada oportunidad de venta, desde el primer contacto hasta el cierre, facilitando la colaboración entre agentes y supervisores.

---

## 🚀 Características Principales

### 📊 Dashboard Interactivo
- **Vista General en Tiempo Real:** Resumen de prospectos por estado (Nuevos, Seguimiento, Cotizados, Ganados, Perdidos, Ventas Canceladas)
- **KPIs Avanzados:** 
  - Conversión por agente con métricas de cotizaciones y ventas
  - Destinos más solicitados
  - Prospectos con datos completos vs. incompletos
  - Clientes sin asignar y asignados
- **Filtros Temporales Avanzados:** 
  - Presets rápidos: Hoy, Esta Semana, Este Mes, Este Año
  - Rango de fechas personalizado
  - Persistencia de filtros entre sesiones

### 👥 Gestión de Prospectos
- **Pipeline de Ventas Completo:** Estados definidos con transiciones controladas
- **Asignación Inteligente de Leads:** 
  - Distribución manual o automática
  - Filtro de prospectos "Nuevos" sin asignar
  - Reasignación con preservación del agente original
- **Gestión de Clientes Recurrentes:**
  - Identificación automática de clientes que regresan
  - Vinculación con prospecto original
  - Historial completo de compras
- **Datos Completos del Cliente:**
  - Información de contacto (teléfonos con indicativos internacionales)
  - Detalles del viaje (origen, destino, fechas, pasajeros)
  - Información adicional para clientes ganados (fecha de nacimiento, identificación, dirección)
- **Integración con WhatsApp:** Enlaces directos para iniciar conversaciones con teléfonos principal y secundario

### 📝 Seguimiento y Documentación
- **Bitácora de Interacciones:** 
  - Registro automático de cambios de estado
  - Notas de llamadas, correos y mensajes
  - Historial completo con usuario y fecha
- **Gestión de Documentos:**
  - Carga de cotizaciones, contratos, facturas, reservas
  - IDs únicos para cada documento
  - Categorización por tipo de documento
  - Almacenamiento seguro en servidor
- **Sistema de Notificaciones:**
  - Alertas de asignación de prospectos
  - Recordatorios de seguimiento
  - Notificaciones de inactividad
  - Panel de notificaciones con filtros avanzados
  - Creación manual de notificaciones personalizadas

### 🔔 Panel de Notificaciones Avanzado
- **Filtros Múltiples:**
  - Por tipo (asignación, seguimiento, inactividad)
  - Por estado (leídas/no leídas)
  - Por rango de fechas
- **Búsqueda Inteligente:**
  - Por ID de cliente
  - Por ID de cotización
  - Por nombre de prospecto
- **Creación Manual de Notificaciones:**
  - Asociadas a prospectos específicos
  - Programación de recordatorios futuros
  - Registro automático en historial de interacciones

### 🛡️ Roles y Seguridad
- **Administrador/Supervisor:** 
  - Acceso total a métricas y estadísticas globales
  - Reasignación de leads
  - Gestión de usuarios (activos/inactivos)
  - Importación masiva de datos
  - Visualización de todos los prospectos
- **Agente:** 
  - Vista enfocada en prospectos asignados
  - Estadísticas personales
  - Herramientas de venta diaria
  - Gestión de seguimiento y documentos

### 👤 Gestión de Usuarios
- **Usuarios Activos e Inactivos:**
  - Marcado de usuarios como inactivos
  - Reasignación automática de prospectos a "Servicio al Cliente"
  - Exclusión de usuarios inactivos en estadísticas
  - Indicadores visuales en la interfaz
- **Importación desde Excel:**
  - Actualización masiva de usuarios
  - Detección automática de usuarios inactivos
  - Generación de contraseñas aleatorias

### 📥 Importación de Datos
- **Importación de Usuarios:**
  - Plantilla Excel predefinida
  - Validación de datos
  - Manejo de usuarios existentes
  - Gestión de usuarios inactivos
- **Importación de Prospectos:**
  - Plantilla Excel con todos los campos
  - Detección de clientes recurrentes
  - Normalización automática de datos
  - Validación de teléfonos y emails
  - Asignación automática de agentes

### 🔍 Búsqueda y Filtros Avanzados
- **Panel de Prospectos:**
  - Filtros por estado, destino, agente, medio de ingreso
  - Búsqueda global por nombre, teléfono, email
  - Filtros de fecha (rango personalizado)
  - Paginación configurable
  - Exportación de resultados
- **Identificadores Únicos:**
  - ID de Cliente (CL-YYYYMMDD-XXXX)
  - ID de Documento (DOC-YYYYMMDD-XXXX)
  - ID de Cotización (COT-YYYYMMDD-XXXX)

### 🗑️ Soft Delete
- **Eliminación Lógica:**
  - Los prospectos no se eliminan físicamente
  - Fecha de eliminación registrada
  - Posibilidad de recuperación
  - Exclusión automática de consultas normales

---

## 🛠️ Tecnologías Utilizadas

- **Backend:** Python 3.9+ con [FastAPI](https://fastapi.tiangolo.com/)
- **Base de Datos:** PostgreSQL con SQLAlchemy ORM
- **Frontend:** HTML5, Jinja2 Templates, Bootstrap 5, JavaScript
- **Servidor:** Uvicorn (ASGI)
- **Procesamiento de Datos:** Pandas, OpenPyXL
- **Autenticación:** Passlib, BCrypt, Python-JOSE
- **Variables de Entorno:** Python-dotenv

---

## 🔧 Instalación y Configuración

### Requisitos Previos
- Python 3.9 o superior
- PostgreSQL 12 o superior
- pip (gestor de paquetes de Python)

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/prospectos_app.git
cd prospectos_app
```

### 2. Crear Entorno Virtual (Recomendado)
```bash
# En Windows
python -m venv venv
.\venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos

#### Opción A: Usar PostgreSQL (Recomendado para producción)
1. Crear base de datos PostgreSQL:
```bash
python crear_db_postgres.py
```

2. Configurar archivo `.env`:
```env
DATABASE_URL=postgresql://usuario:contraseña@localhost/prospectos_db
```

#### Opción B: Usar SQLite (Para desarrollo)
El sistema creará automáticamente `prospectos.db` si no existe configuración de PostgreSQL.

### 5. Inicializar Datos
En el primer inicio, el sistema creará automáticamente:
- **Usuario Administrador:** `admin` / `admin123`
- **Usuario Agente de Prueba:** `agente1` / `agente123`
- **Usuario Servicio al Cliente:** `servicio_cliente` / `servicio123`
- **Medios de Ingreso:** REDES, TEL TRAVEL, RECOMPRA, REFERIDO, FIDELIZACION

> **⚠️ IMPORTANTE:** Cambia la contraseña del administrador después del primer inicio.

### 6. Ejecutar la Aplicación
```bash
uvicorn main:app --reload
```

La aplicación estará disponible en: `http://127.0.0.1:8000`

Para producción (sin reload):
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📖 Guía de Uso

### Para Administradores

#### 1. Primer Inicio
1. Accede a `http://127.0.0.1:8000`
2. Inicia sesión con `admin` / `admin123`
3. Cambia tu contraseña en el perfil

#### 2. Importar Usuarios
1. Ve a **"Importar Datos"** en el menú
2. Descarga la plantilla de usuarios
3. Completa la plantilla con los datos de tus agentes
4. Sube el archivo Excel
5. Revisa el resumen de importación

**Campos de la plantilla de usuarios:**
- `username`: Nombre de usuario único
- `email`: Correo electrónico
- `password`: Contraseña (se encriptará automáticamente)
- `tipo_usuario`: administrador, supervisor, o agente
- `activo`: 1 (activo) o 0 (inactivo)

#### 3. Importar Prospectos
1. Ve a **"Importar Datos"** en el menú
2. Descarga la plantilla de prospectos
3. Completa la plantilla con los datos
4. Sube el archivo Excel
5. Revisa el resumen (exitosos, errores, recurrentes)

**Campos principales de la plantilla de prospectos:**
- Información básica: nombre, apellido, teléfono, email
- Detalles del viaje: origen, destino, fechas, pasajeros
- Asignación: agente_asignado, medio_ingreso
- Estado: nuevo, en_seguimiento, cotizado, ganado, cerrado_perdido

#### 4. Gestionar Usuarios Inactivos
1. Importa usuarios con `activo = 0`
2. El sistema automáticamente:
   - Reasigna sus prospectos a "Servicio al Cliente"
   - Los excluye de estadísticas
   - Mantiene su historial intacto

### Para Agentes

#### 1. Dashboard Personal
- Visualiza tus estadísticas personales
- Filtra por periodo (hoy, semana, mes, año)
- Revisa tus KPIs de conversión

#### 2. Gestión de Prospectos
1. **Crear Nuevo Prospecto:**
   - Clic en "➕ Nuevo Prospecto"
   - Completa el formulario
   - Guarda

2. **Ver Detalle:**
   - Clic en "📋" en la lista
   - Revisa información completa
   - Accede a historial e interacciones

3. **Registrar Seguimiento:**
   - En el detalle del prospecto
   - Clic en "Agregar Interacción"
   - Selecciona tipo y describe la interacción

4. **Cambiar Estado:**
   - En el detalle del prospecto
   - Selecciona nuevo estado
   - Agrega comentario (opcional)
   - Guarda

5. **Subir Documentos:**
   - En el detalle del prospecto
   - Clic en "Subir Documento"
   - Selecciona tipo y archivo
   - Agrega descripción

#### 3. Notificaciones
1. Clic en el ícono de campana 🔔
2. Revisa notificaciones pendientes
3. Filtra por tipo o estado
4. Marca como leídas
5. Crea notificaciones manuales para recordatorios

#### 4. Contacto con Clientes
- Usa los botones de WhatsApp para contacto directo
- Los enlaces se generan automáticamente con el indicativo correcto

---

## 📂 Estructura del Proyecto

```text
prospectos_app/
├── main.py                                    # Aplicación principal FastAPI
├── models.py                                  # Modelos de base de datos (SQLAlchemy)
├── database.py                                # Configuración de conexión a BD
├── auth.py                                    # Lógica de autenticación y hashing
├── excel_import.py                            # Lógica de importación desde Excel
├── requirements.txt                           # Dependencias del proyecto
├── .env                                       # Variables de entorno (no en git)
├── .gitignore                                 # Archivos ignorados por git
│
├── templates/                                 # Plantillas HTML (Jinja2)
│   ├── base.html                              # Layout principal
│   ├── login.html                             # Página de inicio de sesión
│   ├── dashboard.html                         # Panel de control
│   ├── prospectos.html                        # Lista de prospectos
│   ├── prospecto_detalle.html                 # Detalle de prospecto
│   ├── prospecto_form.html                    # Formulario de prospecto
│   ├── notificaciones.html                    # Panel de notificaciones
│   ├── importar_datos.html                    # Importación de datos
│   └── ...
│
├── static/                                    # Archivos estáticos
│   ├── css/
│   │   └── styles.css                         # Estilos personalizados
│   ├── js/
│   │   └── scripts.js                         # Scripts JavaScript
│   ├── img/                                   # Imágenes
│   └── plantillas/                            # Plantillas Excel
│       ├── plantilla_usuarios.xlsx
│       └── plantilla_prospectos.xlsx
│
├── uploads/                                   # Documentos subidos (no en git)
│
├── scripts de migración/                      # Scripts de utilidad
│   ├── crear_db_postgres.py                   # Crear BD PostgreSQL
│   ├── borrar_bd_postgres.py                  # Eliminar BD PostgreSQL
│   ├── migrar_datos_sqlite_postgres.py        # Migrar de SQLite a PostgreSQL
│   ├── generar_plantilla.py                   # Generar plantillas Excel
│   ├── actualizar_plantilla_prospectos.py     # Actualizar plantilla
│   ├── actualizar_plantilla_usuarios.py       # Actualizar plantilla
│   ├── verificar_usuarios_inactivos.py        # Verificar usuarios inactivos
│   └── ...
│
└── prospectos.db                              # Base de datos SQLite (desarrollo)
```

---

## 🗄️ Estructura de Base de Datos

### Tablas Principales

#### `usuarios`
- `id`: ID único
- `username`: Nombre de usuario (único)
- `email`: Correo electrónico
- `hashed_password`: Contraseña encriptada
- `tipo_usuario`: administrador, supervisor, agente
- `activo`: 1 (activo) o 0 (inactivo)
- `fecha_creacion`: Fecha de creación

#### `prospectos`
- `id`: ID único
- `id_cliente`: ID de cliente (CL-YYYYMMDD-XXXX)
- `nombre`, `apellido`: Información básica
- `correo_electronico`, `telefono`, `telefono_secundario`: Contacto
- `indicativo_telefono`, `indicativo_telefono_secundario`: Códigos de país
- `ciudad_origen`, `destino`: Información de viaje
- `fecha_ida`, `fecha_vuelta`: Fechas de viaje
- `pasajeros_adultos`, `pasajeros_ninos`, `pasajeros_infantes`: Pasajeros
- `medio_ingreso_id`: Cómo llegó el prospecto
- `observaciones`: Notas adicionales
- `fecha_registro`: Fecha de creación
- `agente_asignado_id`: Agente actual
- `agente_original_id`: Primer agente asignado
- `estado`: Estado actual del prospecto
- `tiene_datos_completos`: Boolean
- `cliente_recurrente`: Boolean
- `prospecto_original_id`: Referencia a prospecto original
- `fecha_nacimiento`, `numero_identificacion`, `direccion`: Datos adicionales
- `fecha_compra`: Fecha de cierre de venta
- `fecha_eliminacion`: Soft delete

#### `interacciones`
- `id`: ID único
- `prospecto_id`: Prospecto relacionado
- `usuario_id`: Usuario que registró
- `tipo_interaccion`: Tipo de interacción
- `descripcion`: Descripción detallada
- `fecha_creacion`: Fecha y hora
- `estado_anterior`, `estado_nuevo`: Cambios de estado

#### `documentos`
- `id`: ID único
- `id_documento`: ID de documento (DOC-YYYYMMDD-XXXX)
- `prospecto_id`: Prospecto relacionado
- `usuario_id`: Usuario que subió
- `nombre_archivo`: Nombre del archivo
- `tipo_documento`: cotizacion, contrato, factura_proveedor, etc.
- `ruta_archivo`: Ruta en servidor
- `fecha_subida`: Fecha de carga
- `descripcion`: Descripción

#### `notificaciones`
- `id`: ID único
- `usuario_id`: Usuario destinatario
- `prospecto_id`: Prospecto relacionado
- `tipo`: asignacion, inactividad, seguimiento
- `mensaje`: Contenido de la notificación
- `fecha_creacion`: Fecha de creación
- `fecha_programada`: Fecha programada (recordatorios)
- `leida`: Boolean
- `email_enviado`: Boolean

#### `estadisticas_cotizacion`
- `id`: ID único
- `id_cotizacion`: ID de cotización (COT-YYYYMMDD-XXXX)
- `agente_id`: Agente que cotizó
- `prospecto_id`: Prospecto cotizado
- `fecha_cotizacion`: Fecha de cotización
- `fecha_registro`: Fecha de registro

#### `historial_estados`
- `id`: ID único
- `prospecto_id`: Prospecto relacionado
- `estado_anterior`, `estado_nuevo`: Transición de estado
- `usuario_id`: Usuario que cambió
- `fecha_cambio`: Fecha del cambio
- `comentario`: Comentario opcional

#### `medios_ingreso`
- `id`: ID único
- `nombre`: Nombre del medio (REDES, TEL TRAVEL, etc.)
- `activo`: 1 (activo) o 0 (inactivo)

---

## 🔐 Seguridad

- **Autenticación:** Sistema de sesiones con tokens seguros
- **Contraseñas:** Encriptación con BCrypt
- **Sesiones:** Timeout de 30 minutos
- **Validación:** Validación de datos en backend
- **SQL Injection:** Protección mediante ORM SQLAlchemy
- **XSS:** Escape automático en templates Jinja2

---

## 🚀 Despliegue en Producción

### Consideraciones
1. **Base de Datos:** Usar PostgreSQL en lugar de SQLite
2. **Variables de Entorno:** Configurar `.env` con credenciales seguras
3. **HTTPS:** Usar certificados SSL/TLS
4. **Servidor:** Usar Nginx como proxy reverso
5. **Proceso:** Usar supervisor o systemd para mantener la aplicación corriendo

### Ejemplo de configuración Nginx
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📝 Mantenimiento

### Backups
```bash
# PostgreSQL
pg_dump prospectos_db > backup_$(date +%Y%m%d).sql

# SQLite
cp prospectos.db backups/prospectos_$(date +%Y%m%d).db
```

### Logs
Los logs se imprimen en consola. Para producción, redirigir a archivo:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 >> logs/app.log 2>&1
```

---

## 🐛 Solución de Problemas

### Error de conexión a base de datos
- Verifica que PostgreSQL esté corriendo
- Revisa las credenciales en `.env`
- Verifica que la base de datos exista

### Error al importar Excel
- Verifica que el archivo tenga el formato correcto
- Revisa que las columnas coincidan con la plantilla
- Verifica que no haya caracteres especiales en los datos

### Sesión expirada
- Las sesiones expiran después de 30 minutos
- Vuelve a iniciar sesión

---

## 📞 Soporte

Para soporte técnico o reportar problemas:
- Email: soporte@zarita.com
- Documentación: [Wiki del proyecto]

---

## 📄 Licencia

Este proyecto es propiedad de **ZARITA! Travel Agency**.

---

## 👥 Créditos

Desarrollado para **ZARITA! Travel Agency**  
Versión: 2.0  
Última actualización: Enero 2026
