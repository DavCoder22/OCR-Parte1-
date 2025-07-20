@echo off
echo ========================================
echo   Desplegando OCR API a Docker Hub
echo ========================================

REM Configurar variables
set DOCKER_USERNAME=malquinaguirre98
set IMAGE_NAME=ocr-invoice-extractor
set VERSION=1.0.0

echo.
echo [INFO] Construyendo imagen Docker...
docker build -t %IMAGE_NAME%:latest .

echo.
echo [INFO] Etiquetando imagen para Docker Hub...
docker tag %IMAGE_NAME%:latest %DOCKER_USERNAME%/%IMAGE_NAME%:latest
docker tag %IMAGE_NAME%:latest %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%

echo.
echo [INFO] Subiendo imagen a Docker Hub...
docker push %DOCKER_USERNAME%/%IMAGE_NAME%:latest
docker push %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%

echo.
echo ========================================
echo   ¡Despliegue Completado!
echo ========================================
echo.
echo 📋 Información para el equipo de Camunda:
echo.
echo 🐳 Imagen Docker Hub:
echo    %DOCKER_USERNAME%/%IMAGE_NAME%:latest
echo    %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%
echo.
echo 🚀 Comando para ejecutar:
echo    docker run -d -p 5000:5000 --name ocr-service %DOCKER_USERNAME%/%IMAGE_NAME%:latest
echo.
echo 🌐 URL de la API:
echo    http://localhost:5000
echo.
echo 📚 Endpoints disponibles:
echo    GET  http://localhost:5000/health
echo    POST http://localhost:5000/ocr
echo    POST http://localhost:5000/ocr/batch
echo.
echo 📄 Documentación: README_CAMUNDA_INTEGRATION.md
echo.
pause 