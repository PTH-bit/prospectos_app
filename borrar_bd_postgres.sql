"""
Script para borrar todas las tablas de PostgreSQL y recrear la base de datos limpia
ADVERTENCIA: Esto eliminará TODOS los datos
"""

-- ========================================
-- PASO 1: ELIMINAR TODAS LAS TABLAS
-- ========================================

-- Eliminar tablas en orden inverso de dependencias
DROP TABLE IF EXISTS notificaciones CASCADE;
DROP TABLE IF EXISTS historial_estados CASCADE;
DROP TABLE IF EXISTS estadisticas_cotizacion CASCADE;
DROP TABLE IF EXISTS documentos CASCADE;
DROP TABLE IF EXISTS interacciones CASCADE;
DROP TABLE IF EXISTS prospectos CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;
DROP TABLE IF EXISTS medios_ingreso CASCADE;

-- ========================================
-- CONFIRMACIÓN
-- ========================================

-- Verificar que no queden tablas
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- Si el resultado está vacío, la base de datos está limpia
