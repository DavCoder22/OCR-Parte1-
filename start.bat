@echo off
REM Script de inicio para el microservicio OCR en Windows
REM Autor: David - Módulo OCR para Proceso de Reembolsos

setlocal enabledelayedexpansion

REM Colores para output (Windows 10+)
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "NC=[0m"

REM Función para imprimir mensajes con colores
:print_message
echo %GREEN%[INFO]%NC% %~1
goto :eof

:print_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:print_error
echo %RED%[ERROR]%NC% %~1
goto :eof

:print_header
echo %BLUE%================================%NC%
echo %BLUE%  Microservicio OCR - Inicio%NC%
echo %BLUE%================================%NC%
goto :eof

REM Función para verificar prerrequisitos
:check_prerequisites
call :print_message "Verificando prerrequisitos..."

REM Verificar Docker
docker --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Docker no está instalado. Por favor, instala Docker Desktop primero."
    exit /b 1
)

REM Verificar Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Docker Compose no está instalado. Por favor, instala Docker Compose primero."
    exit /b 1
)

REM Verificar que Docker esté ejecutándose
docker info >nul 2>&1
if errorlevel 1 (
    call :print_error "Docker no está ejecutándose. Por favor, inicia Docker Desktop."
    exit /b 1
)

call :print_message "Prerrequisitos verificados correctamente."
goto :eof

REM Función para construir la imagen
:build_image
call :print_message "Construyendo imagen Docker..."

docker-compose build
if errorlevel 1 (
    call :print_error "Error al construir la imagen."
    exit /b 1
)

call :print_message "Imagen construida exitosamente."
goto :eof

REM Función para iniciar el servicio
:start_service
call :print_message "Iniciando servicio OCR..."

docker-compose up -d
if errorlevel 1 (
    call :print_error "Error al iniciar el servicio."
    exit /b 1
)

call :print_message "Servicio iniciado exitosamente."
goto :eof

REM Función para verificar el estado del servicio
:check_service_status
call :print_message "Verificando estado del servicio..."

REM Esperar un momento para que el servicio se inicie
timeout /t 5 /nobreak >nul

REM Verificar que el contenedor esté ejecutándose
docker-compose ps | findstr "Up" >nul
if errorlevel 1 (
    call :print_error "El contenedor no está ejecutándose."
    exit /b 1
)

call :print_message "Contenedor ejecutándose correctamente."

REM Verificar health check
curl -f http://localhost:5000/health >nul 2>&1
if errorlevel 1 (
    call :print_warning "Health check falló. El servicio puede estar iniciándose..."
    call :print_message "Esperando 10 segundos más..."
    timeout /t 10 /nobreak >nul
    
    curl -f http://localhost:5000/health >nul 2>&1
    if errorlevel 1 (
        call :print_error "El servicio no responde. Revisa los logs con: docker-compose logs ocr-service"
        exit /b 1
    )
)

call :print_message "Health check exitoso."
call :print_message "Servicio OCR disponible en http://localhost:5000"
goto :eof

REM Función para mostrar información del servicio
:show_service_info
echo.
call :print_message "Información del servicio:"
echo   URL del servicio: http://localhost:5000
echo   Health check: http://localhost:5000/health
echo   Endpoint OCR: http://localhost:5000/ocr
echo   Endpoint batch: http://localhost:5000/ocr/batch
echo.
call :print_message "Comandos útiles:"
echo   Ver logs: docker-compose logs -f ocr-service
echo   Detener servicio: docker-compose down
echo   Reiniciar servicio: docker-compose restart
echo   Ejecutar pruebas: python test_ocr.py
echo.
goto :eof

REM Función para ejecutar pruebas
:run_tests
call :print_message "¿Deseas ejecutar las pruebas automáticas? (y/n)"
set /p response=

if /i "%response%"=="y" (
    call :print_message "Ejecutando pruebas..."
    
    REM Verificar que Python esté disponible
    python --version >nul 2>&1
    if errorlevel 1 (
        call :print_warning "Python no está disponible. No se pueden ejecutar las pruebas automáticas."
        goto :eof
    )
    
    REM Instalar dependencias de prueba si es necesario
    python -c "import requests, PIL" >nul 2>&1
    if errorlevel 1 (
        call :print_warning "Instalando dependencias de prueba..."
        pip install requests pillow
    )
    
    REM Ejecutar pruebas
    python test_ocr.py
    if errorlevel 1 (
        call :print_warning "Algunas pruebas fallaron. Revisa la salida anterior."
    ) else (
        call :print_message "Pruebas ejecutadas exitosamente."
    )
)
goto :eof

REM Función para mostrar logs
:show_logs
call :print_message "¿Deseas ver los logs del servicio? (y/n)"
set /p response=

if /i "%response%"=="y" (
    call :print_message "Mostrando logs (Ctrl+C para salir)..."
    docker-compose logs -f ocr-service
)
goto :eof

REM Función principal
:main
call :print_header

REM Verificar argumentos de línea de comandos
if "%1"=="build" (
    call :check_prerequisites
    call :build_image
    goto :end
)

if "%1"=="start" (
    call :check_prerequisites
    call :start_service
    call :check_service_status
    call :show_service_info
    goto :end
)

if "%1"=="test" (
    call :run_tests
    goto :end
)

if "%1"=="logs" (
    call :show_logs
    goto :end
)

if "%1"=="stop" (
    call :print_message "Deteniendo servicio..."
    docker-compose down
    call :print_message "Servicio detenido."
    goto :end
)

if "%1"=="restart" (
    call :print_message "Reiniciando servicio..."
    docker-compose restart
    call :print_message "Servicio reiniciado."
    goto :end
)

if "%1"=="status" (
    call :print_message "Estado del servicio:"
    docker-compose ps
    goto :end
)

if "%1"=="help" (
    echo Uso: %0 [comando]
    echo.
    echo Comandos disponibles:
    echo   build   - Construir la imagen Docker
    echo   start   - Iniciar el servicio (comando por defecto)
    echo   stop    - Detener el servicio
    echo   restart - Reiniciar el servicio
    echo   status  - Mostrar estado del servicio
    echo   test    - Ejecutar pruebas automáticas
    echo   logs    - Mostrar logs del servicio
    echo   help    - Mostrar esta ayuda
    echo.
    echo Ejemplos:
    echo   %0 start    # Iniciar servicio
    echo   %0 test     # Ejecutar pruebas
    echo   %0 logs     # Ver logs
    goto :end
)

if "%1"=="-h" (
    goto :help
)

if "%1"=="--help" (
    goto :help
)

REM Comando por defecto: build + start
call :check_prerequisites
call :build_image
call :start_service
call :check_service_status
call :show_service_info
call :run_tests

:end
echo.
call :print_message "Proceso completado."
pause
exit /b 0

:help
echo Uso: %0 [comando]
echo.
echo Comandos disponibles:
echo   build   - Construir la imagen Docker
echo   start   - Iniciar el servicio (comando por defecto)
echo   stop    - Detener el servicio
echo   restart - Reiniciar el servicio
echo   status  - Mostrar estado del servicio
echo   test    - Ejecutar pruebas automáticas
echo   logs    - Mostrar logs del servicio
echo   help    - Mostrar esta ayuda
echo.
echo Ejemplos:
echo   %0 start    # Iniciar servicio
echo   %0 test     # Ejecutar pruebas
echo   %0 logs     # Ver logs
goto :end 