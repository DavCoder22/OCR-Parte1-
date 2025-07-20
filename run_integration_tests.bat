@echo off
REM Script para ejecutar pruebas de integración del módulo OCR
REM Autor: David - Módulo OCR para Proceso de Reembolsos

setlocal enabledelayedexpansion

REM Colores para output
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "NC=[0m"

echo %BLUE%================================%NC%
echo %BLUE%  Pruebas de Integración OCR%NC%
echo %BLUE%================================%NC%

REM Verificar que Docker esté ejecutándose
echo %GREEN%[INFO]%NC% Verificando Docker...
docker info >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Docker no está ejecutándose. Por favor, inicia Docker Desktop.
    pause
    exit /b 1
)

REM Verificar que los servicios estén ejecutándose
echo %GREEN%[INFO]%NC% Verificando servicios...
docker-compose ps | findstr "Up" >nul
if errorlevel 1 (
    echo %YELLOW%[WARNING]%NC% Los servicios no están ejecutándose. Iniciando...
    docker-compose up -d
    
    echo %GREEN%[INFO]%NC% Esperando que los servicios estén listos...
    timeout /t 30 /nobreak >nul
)

REM Verificar que Python esté disponible
echo %GREEN%[INFO]%NC% Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Python no está instalado o no está en el PATH.
    pause
    exit /b 1
)

REM Instalar dependencias de prueba si es necesario
echo %GREEN%[INFO]%NC% Verificando dependencias...
python -c "import psycopg2, requests, PIL" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%[WARNING]%NC% Instalando dependencias de prueba...
    pip install psycopg2-binary requests pillow
)

REM Ejecutar pruebas de integración
echo %GREEN%[INFO]%NC% Ejecutando pruebas de integración...
echo.

python integration_test.py

REM Verificar resultado
if errorlevel 1 (
    echo.
    echo %RED%[ERROR]%NC% Algunas pruebas fallaron. Revisa el reporte generado.
) else (
    echo.
    echo %GREEN%[SUCCESS]%NC% Todas las pruebas pasaron exitosamente!
)

echo.
echo %GREEN%[INFO]%NC% Proceso completado.
pause 