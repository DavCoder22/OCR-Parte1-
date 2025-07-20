# 📦 Archivos que SÍ deben incluirse en el Repositorio

## 🎯 Archivos Esenciales del Proyecto

### 📄 Código Principal
- ✅ `app.py` - Servicio OCR principal
- ✅ `camunda_integration.py` - Integración con Camunda
- ✅ `camunda_mock.py` - Mock para pruebas
- ✅ `test_camunda_integration.py` - Pruebas de integración
- ✅ `integration_test.py` - Pruebas del servicio OCR
- ✅ `demo_complete_integration.py` - Demostración completa

### 🐳 Docker y Contenedores
- ✅ `Dockerfile` - Configuración de Docker
- ✅ `docker-compose.yml` - Orquestación de servicios
- ✅ `.dockerignore` - Archivos a ignorar en Docker

### 📋 Configuración
- ✅ `requirements.txt` - Dependencias de Python
- ✅ `camunda_config.json` - Configuración de Camunda
- ✅ `database_setup.sql` - Script de base de datos

### 📚 Documentación
- ✅ `README.md` - Documentación principal
- ✅ `README_CAMUNDA_INTEGRATION.md` - Documentación de integración
- ✅ `FOR_CAMUNDA_TEAM.md` - Guía para el equipo de Camunda
- ✅ `deploy_cloud_options.md` - Opciones de despliegue

### 🚀 Scripts de Inicio
- ✅ `start.bat` / `start.sh` - Scripts de inicio
- ✅ `setup_env.bat` / `setup_env.sh` - Configuración de entorno
- ✅ `activate_env.bat` - Activación de entorno virtual
- ✅ `quick_start.bat` - Inicio rápido para Camunda
- ✅ `deploy_to_dockerhub.bat` - Despliegue a Docker Hub

### 🧪 Pruebas
- ✅ `test_ocr.py` - Pruebas unitarias de OCR
- ✅ `run_tests_with_env.bat` - Ejecución de pruebas
- ✅ `run_integration_tests.bat` - Pruebas de integración

### 📁 Archivos de Proceso BPMN
- ✅ `test_process.bpmn` - Proceso de ejemplo para Camunda

## 🚫 Archivos que NO deben incluirse

### 📊 Reportes Generados
- ❌ `integration_test_report_*.json`
- ❌ `camunda_integration_report_*.json`
- ❌ `test_report_*.json`
- ❌ `*_report_*.json`

### 🗂️ Directorios Temporales
- ❌ `__pycache__/`
- ❌ `venv/`
- ❌ `logs/`
- ❌ `uploads/`
- ❌ `temp/`

### 🔐 Archivos de Configuración Local
- ❌ `.env`
- ❌ `secrets.json`
- ❌ `config.local.json`

### 📸 Archivos de Prueba
- ❌ `test_*.png`
- ❌ `test_*.jpg`
- ❌ `test_*.pdf`
- ❌ `test_*.txt`

## 📋 Checklist antes de hacer commit

### ✅ Verificar que incluyes:
- [ ] Todos los archivos de código fuente
- [ ] Archivos de configuración (sin secretos)
- [ ] Documentación completa
- [ ] Scripts de inicio y configuración
- [ ] Archivos Docker
- [ ] Archivos de pruebas (código, no reportes)

### ✅ Verificar que NO incluyes:
- [ ] Archivos de reportes generados
- [ ] Entorno virtual (`venv/`)
- [ ] Archivos de cache (`__pycache__/`)
- [ ] Logs y archivos temporales
- [ ] Archivos de configuración con secretos
- [ ] Archivos de prueba generados

## 🚀 Comandos útiles para verificar

### Ver archivos que se van a incluir:
```bash
git status
```

### Ver archivos ignorados:
```bash
git status --ignored
```

### Verificar que no hay archivos sensibles:
```bash
git diff --cached
```

## 📦 Estructura final del repositorio

```
OCR(Parte1)/
├── 📄 app.py
├── 📄 camunda_integration.py
├── 📄 camunda_mock.py
├── 📄 test_camunda_integration.py
├── 📄 integration_test.py
├── 📄 demo_complete_integration.py
├── 📄 Dockerfile
├── 📄 docker-compose.yml
├── 📄 requirements.txt
├── 📄 camunda_config.json
├── 📄 database_setup.sql
├── 📄 README.md
├── 📄 README_CAMUNDA_INTEGRATION.md
├── 📄 FOR_CAMUNDA_TEAM.md
├── 📄 deploy_cloud_options.md
├── 📄 start.bat
├── 📄 start.sh
├── 📄 setup_env.bat
├── 📄 setup_env.sh
├── 📄 activate_env.bat
├── 📄 quick_start.bat
├── 📄 deploy_to_dockerhub.bat
├── 📄 test_ocr.py
├── 📄 run_tests_with_env.bat
├── 📄 run_integration_tests.bat
├── 📄 test_process.bpmn
├── 📄 .gitignore
├── 📄 .dockerignore
└── 📄 INCLUDE_IN_REPO.md
```

---

**🎉 ¡Tu repositorio estará limpio y listo para compartir con el equipo!** 