#!/bin/bash

# Script de inicio para el microservicio OCR
# Autor: David - Módulo OCR para Proceso de Reembolsos

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con colores
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Microservicio OCR - Inicio${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Función para verificar prerrequisitos
check_prerequisites() {
    print_message "Verificando prerrequisitos..."
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado. Por favor, instala Docker primero."
        exit 1
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose no está instalado. Por favor, instala Docker Compose primero."
        exit 1
    fi
    
    # Verificar que Docker esté ejecutándose
    if ! docker info &> /dev/null; then
        print_error "Docker no está ejecutándose. Por favor, inicia Docker."
        exit 1
    fi
    
    print_message "Prerrequisitos verificados correctamente."
}

# Función para construir la imagen
build_image() {
    print_message "Construyendo imagen Docker..."
    
    if docker-compose build; then
        print_message "Imagen construida exitosamente."
    else
        print_error "Error al construir la imagen."
        exit 1
    fi
}

# Función para iniciar el servicio
start_service() {
    print_message "Iniciando servicio OCR..."
    
    if docker-compose up -d; then
        print_message "Servicio iniciado exitosamente."
    else
        print_error "Error al iniciar el servicio."
        exit 1
    fi
}

# Función para verificar el estado del servicio
check_service_status() {
    print_message "Verificando estado del servicio..."
    
    # Esperar un momento para que el servicio se inicie
    sleep 5
    
    # Verificar que el contenedor esté ejecutándose
    if docker-compose ps | grep -q "Up"; then
        print_message "Contenedor ejecutándose correctamente."
    else
        print_error "El contenedor no está ejecutándose."
        exit 1
    fi
    
    # Verificar health check
    if curl -f http://localhost:5000/health &> /dev/null; then
        print_message "Health check exitoso."
        print_message "Servicio OCR disponible en http://localhost:5000"
    else
        print_warning "Health check falló. El servicio puede estar iniciándose..."
        print_message "Esperando 10 segundos más..."
        sleep 10
        
        if curl -f http://localhost:5000/health &> /dev/null; then
            print_message "Health check exitoso después del retraso."
        else
            print_error "El servicio no responde. Revisa los logs con: docker-compose logs ocr-service"
            exit 1
        fi
    fi
}

# Función para mostrar información del servicio
show_service_info() {
    echo ""
    print_message "Información del servicio:"
    echo "  URL del servicio: http://localhost:5000"
    echo "  Health check: http://localhost:5000/health"
    echo "  Endpoint OCR: http://localhost:5000/ocr"
    echo "  Endpoint batch: http://localhost:5000/ocr/batch"
    echo ""
    print_message "Comandos útiles:"
    echo "  Ver logs: docker-compose logs -f ocr-service"
    echo "  Detener servicio: docker-compose down"
    echo "  Reiniciar servicio: docker-compose restart"
    echo "  Ejecutar pruebas: python test_ocr.py"
    echo ""
}

# Función para ejecutar pruebas
run_tests() {
    print_message "¿Deseas ejecutar las pruebas automáticas? (y/n)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_message "Ejecutando pruebas..."
        
        # Verificar que Python esté disponible
        if command -v python &> /dev/null; then
            # Instalar dependencias de prueba si es necesario
            if ! python -c "import requests, PIL" &> /dev/null; then
                print_warning "Instalando dependencias de prueba..."
                pip install requests pillow
            fi
            
            # Ejecutar pruebas
            if python test_ocr.py; then
                print_message "Pruebas ejecutadas exitosamente."
            else
                print_warning "Algunas pruebas fallaron. Revisa la salida anterior."
            fi
        else
            print_warning "Python no está disponible. No se pueden ejecutar las pruebas automáticas."
        fi
    fi
}

# Función para mostrar logs
show_logs() {
    print_message "¿Deseas ver los logs del servicio? (y/n)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_message "Mostrando logs (Ctrl+C para salir)..."
        docker-compose logs -f ocr-service
    fi
}

# Función principal
main() {
    print_header
    
    # Verificar argumentos de línea de comandos
    case "${1:-}" in
        "build")
            check_prerequisites
            build_image
            ;;
        "start")
            check_prerequisites
            start_service
            check_service_status
            show_service_info
            ;;
        "test")
            run_tests
            ;;
        "logs")
            show_logs
            ;;
        "stop")
            print_message "Deteniendo servicio..."
            docker-compose down
            print_message "Servicio detenido."
            ;;
        "restart")
            print_message "Reiniciando servicio..."
            docker-compose restart
            print_message "Servicio reiniciado."
            ;;
        "status")
            print_message "Estado del servicio:"
            docker-compose ps
            ;;
        "help"|"-h"|"--help")
            echo "Uso: $0 [comando]"
            echo ""
            echo "Comandos disponibles:"
            echo "  build   - Construir la imagen Docker"
            echo "  start   - Iniciar el servicio (comando por defecto)"
            echo "  stop    - Detener el servicio"
            echo "  restart - Reiniciar el servicio"
            echo "  status  - Mostrar estado del servicio"
            echo "  test    - Ejecutar pruebas automáticas"
            echo "  logs    - Mostrar logs del servicio"
            echo "  help    - Mostrar esta ayuda"
            echo ""
            echo "Ejemplos:"
            echo "  $0 start    # Iniciar servicio"
            echo "  $0 test     # Ejecutar pruebas"
            echo "  $0 logs     # Ver logs"
            ;;
        *)
            # Comando por defecto: build + start
            check_prerequisites
            build_image
            start_service
            check_service_status
            show_service_info
            run_tests
            ;;
    esac
}

# Ejecutar función principal
main "$@" 