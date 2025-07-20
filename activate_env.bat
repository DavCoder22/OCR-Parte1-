@echo off
REM Script para activar el entorno virtual del módulo OCR
REM Autor: David - Módulo OCR para Proceso de Reembolsos

echo ================================
echo   Activando Entorno Virtual OCR
echo ================================

REM Verificar que el entorno virtual existe
if not exist "venv" (
    echo [ERROR] El entorno virtual no existe.
    echo Ejecuta setup_env.bat primero para crear el entorno.
    pause
    exit /b 1
)

REM Activar entorno virtual
echo [INFO] Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar activación
python -c "import sys; print('Entorno virtual activado:', 'venv' in sys.prefix)" 2>nul
if errorlevel 1 (
    echo [ERROR] Error al activar el entorno virtual.
    pause
    exit /b 1
)

echo [SUCCESS] Entorno virtual activado correctamente!
echo.
echo Comandos disponibles:
echo   python app.py                    - Ejecutar servicio OCR
echo   python test_ocr.py               - Ejecutar pruebas básicas
echo   python integration_test.py       - Ejecutar pruebas de integración
echo   python camunda_integration.py    - Ejemplos de integración Camunda
echo   deactivate                       - Desactivar entorno virtual
echo.
echo [INFO] El entorno virtual está listo para usar. 