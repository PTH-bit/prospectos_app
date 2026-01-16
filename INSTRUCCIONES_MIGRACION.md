# 🚀 Guía de Inicio Rápido

## ✅ Inicialización Automática

La aplicación ahora se **auto-inicializa** completamente al arrancar por primera vez. No necesitas ejecutar scripts manualmente.

### Al Iniciar la Aplicación

```powershell
python main.py
```

**La aplicación automáticamente:**
1. ✅ Crea todas las tablas necesarias (`clientes`, `destinos`, `prospectos`, etc.)
2. ✅ Agrega columnas faltantes (`cliente_id`, `destino_id`)
3. ✅ Pobla 25 destinos iniciales en el catálogo

---

## 📁 Estructura de Archivos

### Scripts (en `scripts/`)
- `migrar_db.py` - Script manual de migración (opcional)
- `agregar_columnas_prospectos.py` - Script manual para columnas (opcional)
- `generar_plantilla.py` - Genera plantilla de prospectos
- `generar_plantilla_clientes.py` - Genera plantilla de clientes

### Plantillas Excel (se generan en `static/plantillas/`)
```powershell
# Generar plantillas (ejecutar una vez)
python scripts\generar_plantilla.py
python scripts\generar_plantilla_clientes.py
```

---

## 🎯 Nuevas Funcionalidades

### 1. Importar Solo Clientes
- Descarga: `/descargar-plantilla/clientes`
- Importa: Solo teléfono + agente (sin crear solicitudes)
- Actualiza clientes existentes automáticamente

### 2. Importar Prospectos con Destinos Inteligentes
- El sistema busca destinos similares (70% umbral)
- Ejemplo: "PUJ" → "PUNTA CANA" (automático)
- Previene duplicados

### 3. Panel de Gestión de Destinos
- URL: `/destinos` (solo admin)
- Crear, editar, fusionar destinos
- Ver prospectos por destino

### 4. Autocompletado de Destinos
- Funciona en formularios de crear/editar
- Sugiere destinos mientras escribes
- Usa catálogo de 25 destinos

---

## 🔧 Configuración Inicial

### Primera Vez

1. **Inicia la aplicación**
   ```powershell
   python main.py
   ```

2. **Genera plantillas Excel**
   ```powershell
   python scripts\generar_plantilla.py
   python scripts\generar_plantilla_clientes.py
   ```

3. **¡Listo!** Todo está configurado automáticamente

---

## 📊 Catálogo de Destinos Pre-cargados

**Caribe**: Cancún, Punta Cana, Aruba, Cartagena, San Andrés, Santa Marta

**Sudamérica**: Río de Janeiro, Buenos Aires, Cusco, Machu Picchu

**Norteamérica**: Miami, Orlando, New York, Las Vegas

**Europa**: Madrid, Barcelona, París, Roma, Londres

**Asia**: Dubai, Tokio, Bangkok

**Otros**: Egipto, Turquía

---

## 🆘 Solución de Problemas

### Error: "Columna no existe"
- **Solución**: Reinicia la aplicación. La auto-inicialización corregirá el problema.

### Destinos Duplicados
- **Solución**: Ve a `/destinos` y usa "Fusionar Destinos"

### Plantillas No Generadas
- **Solución**: Ejecuta manualmente:
  ```powershell
  python scripts\generar_plantilla.py
  python scripts\generar_plantilla_clientes.py
  ```

---

## 📝 Notas Importantes

- ✅ **No se pierde información**: Los campos antiguos se mantienen por compatibilidad
- ✅ **Búsqueda inteligente**: Detecta automáticamente destinos similares
- ✅ **Métricas corregidas**: Dashboard muestra estado actual (no histórico)
- ✅ **Scripts opcionales**: Solo si necesitas ejecutar algo manualmente

---

## 🎉 ¡Todo Listo!

La aplicación está completamente configurada para:
- Importar clientes sin solicitudes
- Gestionar catálogo de destinos
- Prevenir duplicados automáticamente
- Fusionar destinos manualmente cuando sea necesario
