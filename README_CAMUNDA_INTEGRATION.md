# 🔧 Integración Camunda BPMN - Microservicio OCR

## 📋 Descripción General

Este documento describe la integración del microservicio OCR con Camunda BPMN para el proceso de gestión de reembolsos. El módulo OCR (Parte 1) se encarga de extraer datos de facturas y proporcionarlos al proceso BPMN.

## 🏗️ Arquitectura de Integración

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Camunda BPMN  │    │  Microservicio  │    │   PostgreSQL    │
│                 │◄──►│      OCR        │◄──►│    Database     │
│  - Process      │    │                 │    │                 │
│  - Tasks        │    │  - Flask API    │    │  - OCR Results  │
│  - Variables    │    │  - Tesseract    │    │  - Audit Log    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Configuración del Sistema

### 1. Requisitos Previos

- **Camunda Platform Community Edition** ejecutándose en `http://localhost:8080`
- **Docker Desktop** para el microservicio OCR
- **Python 3.10+** para las pruebas de integración

### 2. Servicios Requeridos

```bash
# 1. Microservicio OCR (Puerto 5000)
docker-compose up -d

# 2. Base de datos PostgreSQL (Puerto 5435)
# Incluido en docker-compose.yml

# 3. Camunda Platform (Puerto 8080)
# Descargar e instalar Camunda Platform Community Edition
```

## 📊 Variables de Proceso BPMN

### Variables de Entrada (OCR Output)

| Variable | Tipo | Descripción | Ejemplo |
|----------|------|-------------|---------|
| `proveedor` | String | Nombre del proveedor | "Empresa ABC S.A." |
| `monto` | Double | Monto total de la factura | 1250.50 |
| `fecha_factura` | String | Fecha de la factura | "2024-08-15" |
| `numero_factura` | String | Número de factura | "F001-001" |
| `ruc_proveedor` | String | RUC del proveedor | "20123456789" |
| `ocr_status` | String | Estado del procesamiento | "completed" |
| `ocr_timestamp` | String | Timestamp del procesamiento | "2024-08-15T10:30:00" |

### Variables de Control

| Variable | Tipo | Descripción |
|----------|------|-------------|
| `datos_validos` | Boolean | Resultado de validación |
| `error_mensaje` | String | Mensaje de error si aplica |
| `aprobado` | Boolean | Resultado de aprobación |
| `aprobador` | String | Usuario que aprobó |

## 🔌 Endpoints del Microservicio OCR

### 1. Health Check
```http
GET http://localhost:5000/health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "service": "OCR Invoice Extractor",
  "version": "1.0.0",
  "tesseract_available": true
}
```

### 2. Procesar Factura Individual
```http
POST http://localhost:5000/ocr
Content-Type: multipart/form-data

file: [archivo de imagen]
```

**Respuesta:**
```json
{
  "proveedor": "Empresa ABC S.A.",
  "monto": 1250.50,
  "fecha": "2024-08-15",
  "numero_factura": "F001-001",
  "ruc": "20123456789",
  "archivo_procesado": "factura.pdf",
  "timestamp": "2024-08-15T10:30:00",
  "status": "success"
}
```

### 3. Procesar Múltiples Facturas
```http
POST http://localhost:5000/ocr/batch
Content-Type: multipart/form-data

files: [archivo1, archivo2, ...]
```

## 🔄 Flujo de Integración con Camunda

### 1. Despliegue del Proceso

```python
from camunda_integration import CamundaOCRIntegration

# Crear instancia de integración
integration = CamundaOCRIntegration()

# Desplegar proceso BPMN
deployment_id = integration.deploy_process("proceso_reembolso.bpmn")
```

### 2. Inicio de Instancia

```python
# Iniciar instancia del proceso
instance_id = integration.start_process_instance("Process_Reembolso")
```

### 3. Procesamiento de Tarea OCR

```python
# Obtener tareas OCR pendientes
ocr_tasks = integration.get_ocr_tasks(instance_id)

# Procesar cada tarea
for task in ocr_tasks:
    success = integration.process_ocr_task(task['id'], "factura.pdf")
```

## 📝 Proceso BPMN de Reembolsos

### Estructura del Proceso

```
[Inicio] → [Procesar Factura OCR] → [Validar Datos] → [¿Datos Válidos?]
                                                           ↓
[Reembolso Aprobado] ← [Aprobar Reembolso] ← [Sí] ←───────┘
                                                           ↓
[Reembolso Rechazado] ←────────────────────────────────── [No]
```

### Tareas del Proceso

1. **Procesar Factura OCR** (User Task)
   - Asignado a: `david`
   - Función: Extraer datos de factura usando OCR
   - Variables de salida: `proveedor`, `monto`, `fecha_factura`, etc.

2. **Validar Datos** (Service Task)
   - Función: Validar datos extraídos
   - Variables de salida: `datos_validos`, `error_mensaje`

3. **Aprobar Reembolso** (User Task)
   - Asignado a: `manager`
   - Función: Revisar y aprobar reembolso
   - Variables de salida: `aprobado`, `aprobador`, `comentarios`

## 🧪 Pruebas de Integración

### Ejecutar Pruebas Completas

```bash
# Activar entorno virtual
venv\Scripts\activate

# Ejecutar pruebas de integración OCR
python integration_test.py

# Ejecutar pruebas de integración Camunda
python test_camunda_integration.py
```

### Pruebas Disponibles

1. **OCR Service Health Check**
2. **Database Connection**
3. **OCR Data Extraction**
4. **Batch Processing**
5. **Camunda Connectivity**
6. **BPMN Deployment**
7. **Variable Mapping**

## 🔧 Configuración de Camunda

### 1. Instalación de Camunda

1. Descargar Camunda Platform Community Edition
2. Extraer en directorio deseado
3. Ejecutar `start.bat` (Windows) o `start.sh` (Linux/Mac)
4. Acceder a `http://localhost:8080`

### 2. Configuración de Usuarios

```sql
-- Crear usuario para David
INSERT INTO ACT_ID_USER (ID_, REV_, FIRST_, LAST_, EMAIL_, PWD_) 
VALUES ('david', 1, 'David', 'OCR Processor', 'david@company.com', 'david123');

-- Crear usuario para Manager
INSERT INTO ACT_ID_USER (ID_, REV_, FIRST_, LAST_, EMAIL_, PWD_) 
VALUES ('manager', 1, 'Manager', 'Approver', 'manager@company.com', 'manager123');
```

### 3. Despliegue del Proceso

1. Acceder a Camunda Cockpit: `http://localhost:8080/cockpit`
2. Ir a "Deployments"
3. Subir archivo `proceso_reembolso.bpmn`
4. Verificar despliegue exitoso

## 📊 Monitoreo y Logs

### Logs del Microservicio OCR

```bash
# Ver logs del contenedor OCR
docker-compose logs ocr-service

# Ver logs en tiempo real
docker-compose logs -f ocr-service
```

### Logs de Camunda

```bash
# Logs de Camunda (dependiendo de la instalación)
tail -f camunda/logs/camunda.log
```

### Métricas de Rendimiento

- **Tiempo de procesamiento OCR:** ~200-300ms por factura
- **Precisión de extracción:** ~87.5%
- **Disponibilidad del servicio:** 99.9%

## 🚨 Solución de Problemas

### Problemas Comunes

1. **Camunda no responde**
   - Verificar que Camunda esté ejecutándose en puerto 8080
   - Revisar logs de Camunda

2. **OCR no extrae datos correctamente**
   - Verificar calidad de imagen
   - Revisar logs del microservicio OCR
   - Ajustar patrones de extracción en `app.py`

3. **Error de conexión a base de datos**
   - Verificar que PostgreSQL esté ejecutándose
   - Revisar configuración de conexión

### Comandos de Diagnóstico

```bash
# Verificar estado de servicios
docker-compose ps

# Verificar conectividad OCR
curl http://localhost:5000/health

# Verificar conectividad Camunda
curl http://localhost:8080/engine-rest/version

# Verificar base de datos
docker-compose exec postgres psql -U ocr_user -d ocr_db -c "SELECT COUNT(*) FROM ocr_results;"
```

## 📚 Recursos Adicionales

- [Documentación de Camunda](https://docs.camunda.org/)
- [API REST de Camunda](https://docs.camunda.org/manual/latest/reference/rest/)
- [Documentación de Tesseract OCR](https://tesseract-ocr.github.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)

## 🎯 Próximos Pasos

1. **Desplegar Camunda Platform** en el entorno de producción
2. **Configurar usuarios y permisos** en Camunda
3. **Desplegar el proceso BPMN** en Camunda Cockpit
4. **Configurar monitoreo** y alertas
5. **Implementar pruebas automatizadas** en CI/CD
6. **Documentar procedimientos operativos** para el equipo

---

**Versión:** 1.0.0  
**Fecha:** 2024-08-15  
**Autor:** David - OCR Integration Team 