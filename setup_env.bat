@echo off
REM Script para configurar entorno virtual para el módulo OCR
REM Autor: David - Módulo OCR para Proceso de Reembolsos

setlocal enabledelayedexpansion

REM Colores para output
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "NC=[0m"

echo %BLUE%================================%NC%
echo %BLUE%  Configuración de Entorno Virtual%NC%
echo %BLUE%================================%NC%

REM Verificar que Python esté instalado
echo %GREEN%[INFO]%NC% Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Python no está instalado o no está en el PATH.
    echo Por favor, instala Python 3.8+ desde https://python.org
    pause
    exit /b 1
)

REM Verificar que venv esté disponible
echo %GREEN%[INFO]%NC% Verificando módulo venv...
python -c "import venv" >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR]%NC% El módulo venv no está disponible.
    echo Asegúrate de tener Python 3.3+ instalado.
    pause
    exit /b 1
)

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo %GREEN%[INFO]%NC% Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo %RED%[ERROR]%NC% Error al crear el entorno virtual.
        pause
        exit /b 1
    )
    echo %GREEN%[SUCCESS]%NC% Entorno virtual creado exitosamente.
) else (
    echo %YELLOW%[INFO]%NC% El entorno virtual ya existe.
)

REM Activar entorno virtual
echo %GREEN%[INFO]%NC% Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar que el entorno esté activado
echo %GREEN%[INFO]%NC% Verificando activación del entorno...
python -c "import sys; print('Entorno virtual activado:', 'venv' in sys.prefix)" 2>nul
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Error al activar el entorno virtual.
    pause
    exit /b 1
)

REM Actualizar pip
echo %GREEN%[INFO]%NC% Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias
echo %GREEN%[INFO]%NC% Instalando dependencias...
pip install -r requirements.txt

REM Verificar instalación
echo %GREEN%[INFO]%NC% Verificando instalación...
python -c "import flask, pytesseract, psycopg2, requests, PIL" 2>nul
if errorlevel 1 (
    echo %YELLOW%[WARNING]%NC% Algunas dependencias no se instalaron correctamente.
    echo Intentando instalar manualmente...
    pip install flask flask-cors pillow pytesseract psycopg2-binary requests
) else (
    echo %GREEN%[SUCCESS]%NC% Todas las dependencias instaladas correctamente.
)

echo.
echo %GREEN%[SUCCESS]%NC% Entorno virtual configurado exitosamente!
echo.
echo %BLUE%Comandos útiles:%NC%
echo   Para activar el entorno: venv\Scripts\activate.bat
echo   Para desactivar: deactivate
echo   Para ejecutar pruebas: python integration_test.py
echo   Para ejecutar el servicio: python app.py
echo.
echo %YELLOW%[NOTA]%NC% Recuerda activar el entorno virtual antes de trabajar:
echo   venv\Scripts\activate.bat
echo.
pause 