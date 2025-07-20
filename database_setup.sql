-- Script de configuración de base de datos para el módulo OCR
-- Autor: David - Módulo OCR para Proceso de Reembolsos

-- Crear base de datos
CREATE DATABASE ocr_db;

-- Conectar a la base de datos
\c ocr_db;

-- Crear usuario para el módulo OCR
CREATE USER ocr_user WITH PASSWORD 'ocr_password';

-- Otorgar permisos al usuario
GRANT ALL PRIVILEGES ON DATABASE ocr_db TO ocr_user;
GRANT CONNECT ON DATABASE ocr_db TO ocr_user;

-- Crear tabla para almacenar resultados de OCR
CREATE TABLE IF NOT EXISTS ocr_results (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    provider VARCHAR(255),
    amount DECIMAL(10,2),
    invoice_date DATE,
    invoice_number VARCHAR(100),
    ruc VARCHAR(20),
    extracted_text TEXT,
    processing_time_ms INTEGER,
    status VARCHAR(50) DEFAULT 'success',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear tabla para logs de procesamiento
CREATE TABLE IF NOT EXISTS ocr_logs (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255),
    operation VARCHAR(100),
    status VARCHAR(50),
    error_message TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear tabla para configuración del sistema
CREATE TABLE IF NOT EXISTS ocr_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar configuración inicial
INSERT INTO ocr_config (config_key, config_value, description) VALUES
('tesseract_language', 'spa+eng', 'Idiomas para Tesseract OCR'),
('max_file_size_mb', '10', 'Tamaño máximo de archivo en MB'),
('processing_timeout_seconds', '30', 'Timeout para procesamiento OCR'),
('batch_size', '10', 'Tamaño de lote para procesamiento'),
('enable_logging', 'true', 'Habilitar logging detallado')
ON CONFLICT (config_key) DO NOTHING;

-- Crear índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_ocr_results_filename ON ocr_results(filename);
CREATE INDEX IF NOT EXISTS idx_ocr_results_provider ON ocr_results(provider);
CREATE INDEX IF NOT EXISTS idx_ocr_results_date ON ocr_results(invoice_date);
CREATE INDEX IF NOT EXISTS idx_ocr_results_status ON ocr_results(status);
CREATE INDEX IF NOT EXISTS idx_ocr_results_created_at ON ocr_results(created_at);

CREATE INDEX IF NOT EXISTS idx_ocr_logs_filename ON ocr_logs(filename);
CREATE INDEX IF NOT EXISTS idx_ocr_logs_status ON ocr_logs(status);
CREATE INDEX IF NOT EXISTS idx_ocr_logs_created_at ON ocr_logs(created_at);

-- Otorgar permisos en las tablas
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ocr_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ocr_user;

-- Crear función para actualizar timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Crear triggers para actualizar timestamps
CREATE TRIGGER update_ocr_results_updated_at 
    BEFORE UPDATE ON ocr_results 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ocr_config_updated_at 
    BEFORE UPDATE ON ocr_config 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Crear vistas útiles para reportes
CREATE OR REPLACE VIEW ocr_summary AS
SELECT 
    DATE(created_at) as processing_date,
    COUNT(*) as total_processed,
    COUNT(CASE WHEN status = 'success' THEN 1 END) as successful,
    COUNT(CASE WHEN status = 'error' THEN 1 END) as failed,
    AVG(processing_time_ms) as avg_processing_time_ms,
    SUM(amount) as total_amount
FROM ocr_results 
GROUP BY DATE(created_at)
ORDER BY processing_date DESC;

CREATE OR REPLACE VIEW ocr_provider_stats AS
SELECT 
    provider,
    COUNT(*) as total_invoices,
    AVG(amount) as avg_amount,
    SUM(amount) as total_amount,
    MIN(created_at) as first_invoice,
    MAX(created_at) as last_invoice
FROM ocr_results 
WHERE provider IS NOT NULL
GROUP BY provider
ORDER BY total_invoices DESC;

-- Crear función para limpiar logs antiguos
CREATE OR REPLACE FUNCTION cleanup_old_logs(days_to_keep INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM ocr_logs 
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '1 day' * days_to_keep;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Crear función para obtener estadísticas del sistema
CREATE OR REPLACE FUNCTION get_ocr_stats()
RETURNS TABLE(
    total_processed BIGINT,
    successful_processed BIGINT,
    failed_processed BIGINT,
    success_rate DECIMAL(5,2),
    avg_processing_time_ms DECIMAL(10,2),
    total_amount DECIMAL(15,2),
    last_processed TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_processed,
        COUNT(CASE WHEN status = 'success' THEN 1 END)::BIGINT as successful_processed,
        COUNT(CASE WHEN status = 'error' THEN 1 END)::BIGINT as failed_processed,
        ROUND(
            (COUNT(CASE WHEN status = 'success' THEN 1 END)::DECIMAL / COUNT(*)::DECIMAL) * 100, 
            2
        ) as success_rate,
        ROUND(AVG(processing_time_ms), 2) as avg_processing_time_ms,
        COALESCE(SUM(amount), 0) as total_amount,
        MAX(created_at) as last_processed
    FROM ocr_results;
END;
$$ LANGUAGE plpgsql;

-- Otorgar permisos en las funciones
GRANT EXECUTE ON FUNCTION cleanup_old_logs(INTEGER) TO ocr_user;
GRANT EXECUTE ON FUNCTION get_ocr_stats() TO ocr_user;

-- Comentarios para documentación
COMMENT ON TABLE ocr_results IS 'Almacena los resultados del procesamiento OCR de facturas';
COMMENT ON TABLE ocr_logs IS 'Registra logs de operaciones del sistema OCR';
COMMENT ON TABLE ocr_config IS 'Configuración del sistema OCR';
COMMENT ON VIEW ocr_summary IS 'Resumen diario de procesamiento OCR';
COMMENT ON VIEW ocr_provider_stats IS 'Estadísticas por proveedor';
COMMENT ON FUNCTION cleanup_old_logs(INTEGER) IS 'Limpia logs antiguos del sistema';
COMMENT ON FUNCTION get_ocr_stats() IS 'Obtiene estadísticas generales del sistema OCR';

-- Verificar que todo se creó correctamente
SELECT 'Base de datos OCR configurada correctamente' as status;
SELECT COUNT(*) as total_tables FROM information_schema.tables WHERE table_schema = 'public';
SELECT COUNT(*) as total_views FROM information_schema.views WHERE table_schema = 'public';
SELECT COUNT(*) as total_functions FROM information_schema.routines WHERE routine_schema = 'public'; 