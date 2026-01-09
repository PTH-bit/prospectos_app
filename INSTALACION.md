# 🚀 Guía Rápida de Instalación - Sistema CRM ZARITA!

Esta guía te ayudará a poner en marcha el sistema CRM en pocos minutos.

---

## ⚡ Instalación Rápida (5 minutos)

### 1. Requisitos Previos
Asegúrate de tener instalado:
- ✅ Python 3.9 o superior
- ✅ pip (gestor de paquetes)
- ✅ PostgreSQL 12+ (opcional, recomendado para producción)

### 2. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/prospectos_app.git
cd prospectos_app
```

### 3. Crear Entorno Virtual
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar Base de Datos

#### Opción A: SQLite (Desarrollo - Más Rápido)
No requiere configuración adicional. El sistema creará automáticamente `prospectos.db`.

#### Opción B: PostgreSQL (Producción - Recomendado)
```bash
# Crear base de datos
python crear_db_postgres.py

# Crear archivo .env
echo DATABASE_URL=postgresql://usuario:contraseña@localhost/prospectos_db > .env
```

### 6. Iniciar la Aplicación
```bash
uvicorn main:app --reload
```

### 7. Acceder al Sistema
Abre tu navegador en: `http://127.0.0.1:8000`

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`

> ⚠️ **IMPORTANTE:** Cambia la contraseña del administrador después del primer inicio.

---

## 📋 Checklist de Instalación

- [ ] Python 3.9+ instalado
- [ ] Repositorio clonado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas
- [ ] Base de datos configurada
- [ ] Aplicación iniciada
- [ ] Acceso al sistema verificado
- [ ] Contraseña de admin cambiada

---

## 🔧 Configuración Adicional

### Cambiar Puerto
```bash
uvicorn main:app --reload --port 8080
```

### Acceso desde Red Local
```bash
uvicorn main:app --reload --host 0.0.0.0
```

### Producción (Sin Reload)
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📥 Importar Datos Iniciales

### 1. Importar Usuarios
1. Inicia sesión como admin
2. Ve a **"Importar Datos"**
3. Descarga la plantilla de usuarios
4. Completa con tus datos
5. Sube el archivo

### 2. Importar Prospectos
1. Ve a **"Importar Datos"**
2. Descarga la plantilla de prospectos
3. Completa con tus datos
4. Sube el archivo

---

## 🐛 Solución de Problemas Comunes

### Error: "Module not found"
```bash
# Asegúrate de tener el entorno virtual activado
pip install -r requirements.txt
```

### Error: "Port already in use"
```bash
# Cambia el puerto
uvicorn main:app --reload --port 8080
```

### Error: "Database connection failed"
```bash
# Verifica que PostgreSQL esté corriendo
# O usa SQLite (no requiere configuración)
```

### Error: "Permission denied"
```bash
# Windows: Ejecuta como administrador
# Linux/Mac: Usa sudo si es necesario
```

---

## 📞 Soporte

Si tienes problemas:
1. Revisa la [Documentación Completa](README.md)
2. Consulta la [Documentación de Funciones](FUNCIONES.md)
3. Contacta a soporte: soporte@zarita.com

---

## ✅ Próximos Pasos

Después de la instalación:
1. ✅ Cambia la contraseña del administrador
2. ✅ Crea usuarios para tu equipo
3. ✅ Importa tus datos existentes
4. ✅ Configura los medios de ingreso
5. ✅ Comienza a gestionar prospectos

---

**¡Listo para comenzar!** 🎉

Para más información, consulta el [README completo](README.md).
