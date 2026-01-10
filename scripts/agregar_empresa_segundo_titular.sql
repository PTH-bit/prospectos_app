-- =====================================================
-- Script: Agregar campo empresa_segundo_titular
-- Descripción: Agrega columna para almacenar nombre de 
--              empresa o segundo titular del cliente
-- Fecha: 2026-01-10
-- =====================================================

-- 1. Agregar columna empresa_segundo_titular
ALTER TABLE prospectos 
ADD COLUMN empresa_segundo_titular VARCHAR(255);

-- 2. Crear índice para búsquedas (opcional pero recomendado)
CREATE INDEX idx_empresa_segundo_titular 
ON prospectos(empresa_segundo_titular);

-- 3. Verificar que la columna se agregó correctamente
SELECT column_name, data_type, character_maximum_length, is_nullable
FROM information_schema.columns
WHERE table_name = 'prospectos' 
  AND column_name = 'empresa_segundo_titular';

-- Resultado esperado:
-- column_name                 | data_type        | character_maximum_length | is_nullable
-- empresa_segundo_titular     | character varying| 255                      | YES

COMMIT;
