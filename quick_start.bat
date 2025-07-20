@echo off
echo ========================================
echo   OCR API - Inicio Rápido
echo ========================================
echo.
echo 🎯 Este script inicia el servicio OCR para Camunda
echo.

REM Verificar si Docker está instalado
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Docker no está instalado
    echo.
    echo 📥 Descargar Docker Desktop desde:
    echo    https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

echo ✅ Docker detectado
echo.

REM Verificar si la imagen existe localmente
docker images | findstr "ocr-invoice-extractor" >nul 2>&1
if %errorlevel% neq 0 (
    echo 📥 Descargando imagen OCR desde Docker Hub...
    docker pull malquinaguirre98/ocr-invoice-extractor:latest
    if %errorlevel% neq 0 (
        echo ❌ ERROR: No se pudo descargar la imagen
        echo.
        echo 🔧 Soluciones:
        echo    1. Verificar conexión a internet
        echo    2. Verificar que Docker esté ejecutándose
        echo    3. Contactar al desarrollador
        echo.
        pause
        exit /b 1
    )
) else (
    echo ✅ Imagen OCR encontrada localmente
)

echo.

REM Detener contenedor si ya está ejecutándose
docker stop ocr-service >nul 2>&1
docker rm ocr-service >nul 2>&1

echo 🚀 Iniciando servicio OCR...
docker run -d -p 5000:5000 --name ocr-service malquinaguirre98/ocr-invoice-extractor:latest

if %errorlevel% neq 0 (
    echo ❌ ERROR: No se pudo iniciar el servicio
    pause
    exit /b 1
)

echo.
echo ⏳ Esperando que el servicio esté listo...
timeout /t 5 /nobreak >nul

REM Verificar que el servicio esté funcionando
echo 🔍 Verificando servicio...
curl -s http://localhost:5000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ⏳ Servicio aún iniciando, esperando...
    timeout /t 10 /nobreak >nul
    curl -s http://localhost:5000/health >nul 2>&1
)

echo.
echo ========================================
echo   ✅ ¡Servicio OCR Iniciado!
echo ========================================
echo.
echo 🌐 URL de la API: http://localhost:5000
echo.
echo 📚 Endpoints disponibles:
echo    GET  http://localhost:5000/health
echo    POST http://localhost:5000/ocr
echo    POST http://localhost:5000/ocr/batch
echo.
echo 🔧 Para Camunda:
echo    - Usar URL: http://localhost:5000
echo    - Método: POST
echo    - Content-Type: multipart/form-data
echo    - Campo: file
echo.
echo 📊 Para verificar que funciona:
echo    curl http://localhost:5000/health
echo.
echo 🛑 Para detener el servicio:
echo    docker stop ocr-service
echo.
echo 📄 Documentación completa: README_CAMUNDA_INTEGRATION.md
echo.
echo ========================================
pause 