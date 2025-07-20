@echo off
echo ========================================
echo   Limpiando archivos para el repositorio
echo ========================================
echo.

echo 🗑️ Eliminando archivos de reportes generados...
del /q integration_test_report_*.json 2>nul
del /q camunda_integration_report_*.json 2>nul
del /q test_report_*.json 2>nul
del /q *_report_*.json 2>nul

echo 🗑️ Eliminando archivos de prueba temporales...
del /q test_*.png 2>nul
del /q test_*.jpg 2>nul
del /q test_*.jpeg 2>nul
del /q test_*.pdf 2>nul
del /q test_*.txt 2>nul
del /q test_*.tiff 2>nul
del /q test_*.bmp 2>nul

echo 🗑️ Eliminando directorios temporales...
if exist __pycache__ rmdir /s /q __pycache__ 2>nul
if exist logs rmdir /s /q logs 2>nul
if exist uploads rmdir /s /q uploads 2>nul
if exist temp rmdir /s /q temp 2>nul
if exist .cache rmdir /s /q .cache 2>nul
if exist .pytest_cache rmdir /s /q .pytest_cache 2>nul

echo 🗑️ Eliminando archivos de cache de Python...
del /q *.pyc 2>nul
del /q *.pyo 2>nul
del /q *.pyd 2>nul

echo 🗑️ Eliminando archivos temporales...
del /q *.tmp 2>nul
del /q *.temp 2>nul
del /q *.bak 2>nul
del /q *.backup 2>nul

echo 🗑️ Eliminando archivos de configuración local...
if exist .env del .env
if exist secrets.json del secrets.json
if exist config.local.json del config.local.json

echo.
echo ========================================
echo   ✅ Limpieza completada
echo ========================================
echo.
echo 📋 Archivos que se mantienen:
echo    ✅ Código fuente (.py)
echo    ✅ Configuración (.json, .sql)
echo    ✅ Documentación (.md)
echo    ✅ Scripts (.bat, .sh)
echo    ✅ Docker (Dockerfile, docker-compose.yml)
echo    ✅ Archivos de prueba (código)
echo.
echo 🚫 Archivos eliminados:
echo    ❌ Reportes generados (*_report_*.json)
echo    ❌ Archivos de prueba temporales (test_*.*)
echo    ❌ Directorios temporales (__pycache__, logs, etc.)
echo    ❌ Archivos de cache (*.pyc, *.pyo)
echo    ❌ Archivos de configuración local (.env, secrets.json)
echo.
echo 🚀 Ahora puedes hacer commit de tu repositorio:
echo    git add .
echo    git commit -m "OCR Module - Ready for Camunda integration"
echo    git push origin main
echo.
pause 