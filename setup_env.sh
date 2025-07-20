#!/bin/bash

# Script para configurar entorno virtual para el módulo OCR
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
    echo -e "${BLUE}  Configuración de Entorno Virtual${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_header

# Verificar que Python esté instalado
print_message "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Python3 no está instalado o no está en el PATH."
    echo "Por favor, instala Python 3.8+ desde https://python.org"
    exit 1
fi

# Verificar que venv esté disponible
print_message "Verificando módulo venv..."
if ! python3 -c "import venv" &> /dev/null; then
    print_error "El módulo venv no está disponible."
    echo "Asegúrate de tener Python 3.3+ instalado."
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    print_message "Creando entorno virtual..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_error "Error al crear el entorno virtual."
        exit 1
    fi
    print_message "Entorno virtual creado exitosamente."
else
    print_warning "El entorno virtual ya existe."
fi

# Activar entorno virtual
print_message "Activando entorno virtual..."
source venv/bin/activate

# Verificar que el entorno esté activado
print_message "Verificando activación del entorno..."
if python -c "import sys; print('Entorno virtual activado:', 'venv' in sys.prefix)" 2>/dev/null; then
    print_message "Entorno virtual activado correctamente."
else
    print_error "Error al activar el entorno virtual."
    exit 1
fi

# Actualizar pip
print_message "Actualizando pip..."
python -m pip install --upgrade pip

# Instalar dependencias
print_message "Instalando dependencias..."
pip install -r requirements.txt

# Verificar instalación
print_message "Verificando instalación..."
if python -c "import flask, pytesseract, psycopg2, requests, PIL" 2>/dev/null; then
    print_message "Todas las dependencias instaladas correctamente."
else
    print_warning "Algunas dependencias no se instalaron correctamente."
    echo "Intentando instalar manualmente..."
    pip install flask flask-cors pillow pytesseract psycopg2-binary requests
fi

echo
print_message "Entorno virtual configurado exitosamente!"
echo
echo -e "${BLUE}Comandos útiles:${NC}"
echo "  Para activar el entorno: source venv/bin/activate"
echo "  Para desactivar: deactivate"
echo "  Para ejecutar pruebas: python integration_test.py"
echo "  Para ejecutar el servicio: python app.py"
echo
print_warning "Recuerda activar el entorno virtual antes de trabajar:"
echo "  source venv/bin/activate"
echo 