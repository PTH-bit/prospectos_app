# 📝 Historial de Cambios - Sistema CRM ZARITA!

Todos los cambios notables en este proyecto serán documentados en este archivo.

---

## [2.0.0] - 2026-01-09

### ✨ Nuevas Funcionalidades

#### Sistema de Notificaciones Avanzado
- Panel de notificaciones con filtros múltiples (tipo, estado, fecha)
- Búsqueda inteligente por ID de cliente o cotización
- Creación manual de notificaciones personalizadas
- Programación de recordatorios futuros
- Registro automático en historial de interacciones

#### Gestión de Usuarios Inactivos
- Marcado de usuarios como activos/inactivos
- Reasignación automática de prospectos a "Servicio al Cliente"
- Exclusión de usuarios inactivos en estadísticas
- Indicadores visuales en la interfaz
- Usuario especial "servicio_cliente" creado automáticamente

#### Filtros de Fecha Avanzados
- Filtros de rango de fechas en Dashboard
- Filtros de rango de fechas en Panel de Prospectos
- Presets rápidos: Hoy, Esta Semana, Este Mes, Este Año
- Rango personalizado con selector de fechas
- Persistencia de filtros entre sesiones

#### Gestión de Clientes Recurrentes
- Detección automática de clientes que regresan
- Vinculación con prospecto original
- Historial completo de compras
- Indicador visual de cliente recurrente

#### Datos Completos del Cliente
- Verificación automática de datos completos
- Indicadores visuales en Dashboard y listas
- Métricas de prospectos con/sin datos completos
- Campos adicionales para clientes ganados:
  - Fecha de nacimiento
  - Número de identificación
  - Dirección
  - Fecha de compra

### 🔄 Mejoras

#### Dashboard
- Estadísticas separadas para prospectos con/sin datos completos
- Métricas de conversión mejoradas por agente
- Filtros de fecha aplicables a todas las estadísticas
- Visualización clara del periodo activo
- Exclusión automática de usuarios inactivos en estadísticas

#### Panel de Prospectos
- Paginación mejorada (configurable de 10 a 100 registros)
- Filtros combinables
- Búsqueda global en múltiples campos
- Filtros de fecha por rango
- Indicadores visuales de estado

#### Importación de Datos
- Detección automática de clientes recurrentes
- Manejo de usuarios inactivos en importación
- Validación mejorada de datos
- Normalización automática de teléfonos y emails
- Mensajes de error más descriptivos

#### Seguridad
- Soft delete en prospectos (eliminación lógica)
- Preservación de historial en reasignaciones
- Auditoría completa de cambios
- Validación de permisos mejorada

### 🗄️ Base de Datos

#### Nuevos Campos
- `prospectos.tiene_datos_completos` (Boolean)
- `prospectos.cliente_recurrente` (Boolean)
- `prospectos.prospecto_original_id` (ForeignKey)
- `prospectos.fecha_nacimiento` (Date)
- `prospectos.numero_identificacion` (String)
- `prospectos.direccion` (String)
- `prospectos.fecha_compra` (Date)
- `prospectos.fecha_eliminacion` (DateTime)
- `prospectos.agente_original_id` (ForeignKey)
- `documentos.id_documento` (String)
- `estadisticas_cotizacion.id_cotizacion` (String)
- `notificaciones.fecha_programada` (DateTime)

#### Nuevas Tablas
- `historial_estados`: Registro de cambios de estado
- `estadisticas_cotizacion`: Métricas de cotizaciones

### 🐛 Correcciones

- Corregido cálculo de estadísticas por periodo
- Corregido filtro de usuarios activos en conversión de agentes
- Mejorado manejo de fechas en múltiples formatos
- Corregida normalización de datos en importación
- Corregido cálculo de último día del mes en filtros

### 📚 Documentación

- README.md completamente actualizado
- Nuevo archivo FUNCIONES.md con documentación de API
- Nuevo archivo INSTALACION.md con guía rápida
- requirements.txt con comentarios explicativos
- Este archivo CHANGELOG.md

---

## [1.0.0] - 2025-12-10

### ✨ Funcionalidades Iniciales

#### Sistema Base
- Autenticación con sesiones
- Roles: Administrador, Supervisor, Agente
- Dashboard con estadísticas básicas
- Gestión de prospectos (CRUD completo)
- Sistema de estados de prospecto

#### Gestión de Prospectos
- Creación y edición de prospectos
- Estados: Nuevo, En Seguimiento, Cotizado, Ganado, Cerrado Perdido
- Asignación de agentes
- Historial de interacciones
- Integración con WhatsApp

#### Gestión de Documentos
- Subida de archivos
- Categorización por tipo
- Descarga de documentos
- Almacenamiento en servidor

#### Importación de Datos
- Importación de usuarios desde Excel
- Importación de prospectos desde Excel
- Plantillas predefinidas
- Validación básica de datos

#### Dashboard
- Estadísticas por estado
- Destinos más populares
- Conversión por agente
- Filtros temporales básicos

### 🗄️ Base de Datos Inicial

#### Tablas Principales
- `usuarios`: Gestión de usuarios del sistema
- `prospectos`: Información de prospectos
- `interacciones`: Historial de interacciones
- `documentos`: Gestión de archivos
- `medios_ingreso`: Catálogo de medios
- `notificaciones`: Sistema básico de notificaciones

### 🛠️ Tecnologías
- FastAPI 0.104.1
- SQLAlchemy 2.0+
- PostgreSQL / SQLite
- Jinja2 Templates
- Bootstrap 5
- Pandas para importación

---

## Formato del Changelog

Este changelog sigue el formato de [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

### Tipos de Cambios
- **✨ Nuevas Funcionalidades** - para nuevas características
- **🔄 Mejoras** - para cambios en funcionalidades existentes
- **🐛 Correcciones** - para corrección de bugs
- **🗄️ Base de Datos** - para cambios en esquema de BD
- **📚 Documentación** - para cambios en documentación
- **🔒 Seguridad** - para correcciones de seguridad
- **⚠️ Deprecado** - para funcionalidades que serán removidas
- **🗑️ Removido** - para funcionalidades removidas

---

**Desarrollado para ZARITA! Travel Agency**  
**Última actualización:** Enero 2026
