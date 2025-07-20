#!/usr/bin/env python3
"""
Script de prueba para el microservicio OCR
Permite probar la funcionalidad de extracción de datos de facturas
"""

import requests
import json
import os
import sys
from pathlib import Path

# URL base del servicio OCR
BASE_URL = "http://localhost:5000"

def test_health_check():
    """Prueba el endpoint de salud del servicio"""
    print("🔍 Probando health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check exitoso: {data}")
            return True
        else:
            print(f"❌ Health check falló: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servicio OCR")
        print("   Asegúrate de que el servicio esté ejecutándose en http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error en health check: {str(e)}")
        return False

def test_ocr_with_file(file_path):
    """Prueba el procesamiento OCR con un archivo específico"""
    print(f"🔍 Probando OCR con archivo: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ Archivo no encontrado: {file_path}")
        return False
    
    try:
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(f"{BASE_URL}/ocr", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ OCR exitoso!")
            print("📊 Datos extraídos:")
            print(f"   Proveedor: {data.get('proveedor', 'N/A')}")
            print(f"   Monto: {data.get('monto', 'N/A')}")
            print(f"   Fecha: {data.get('fecha', 'N/A')}")
            print(f"   Número de factura: {data.get('numero_factura', 'N/A')}")
            print(f"   RUC: {data.get('ruc', 'N/A')}")
            print(f"   Estado: {data.get('status', 'N/A')}")
            return True
        else:
            print(f"❌ OCR falló: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en OCR: {str(e)}")
        return False

def test_ocr_with_sample_data():
    """Prueba el OCR con datos de ejemplo (simulado)"""
    print("🔍 Probando OCR con datos simulados...")
    
    # Crear una imagen de prueba simple (esto es solo para demostración)
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # Crear una imagen de prueba con texto
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Agregar texto de factura de ejemplo
        text_lines = [
            "FACTURA N° 001-001-00012345",
            "RUC: 20123456789",
            "PROVEEDOR EJEMPLO SAC",
            "FECHA: 15/06/2024",
            "TOTAL: S/ 150.00"
        ]
        
        y_position = 20
        for line in text_lines:
            draw.text((20, y_position), line, fill='black')
            y_position += 25
        
        # Guardar imagen temporal
        test_image_path = "test_invoice.png"
        img.save(test_image_path)
        
        # Probar OCR con la imagen generada
        success = test_ocr_with_file(test_image_path)
        
        # Limpiar archivo temporal
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
        
        return success
        
    except ImportError:
        print("❌ Pillow no disponible para generar imagen de prueba")
        return False
    except Exception as e:
        print(f"❌ Error generando imagen de prueba: {str(e)}")
        return False

def test_batch_processing():
    """Prueba el procesamiento por lotes"""
    print("🔍 Probando procesamiento por lotes...")
    
    try:
        # Crear múltiples imágenes de prueba
        from PIL import Image, ImageDraw
        
        test_files = []
        for i in range(2):
            img = Image.new('RGB', (300, 150), color='white')
            draw = ImageDraw.Draw(img)
            draw.text((20, 20), f"FACTURA TEST {i+1}", fill='black')
            draw.text((20, 50), f"MONTO: S/ {100 + i*50}.00", fill='black')
            
            filename = f"test_batch_{i+1}.png"
            img.save(filename)
            test_files.append(filename)
        
        # Probar procesamiento por lotes
        files = [('files', open(f, 'rb')) for f in test_files]
        response = requests.post(f"{BASE_URL}/ocr/batch", files=files)
        
        # Cerrar archivos
        for _, file in files:
            file.close()
        
        # Limpiar archivos temporales
        for f in test_files:
            if os.path.exists(f):
                os.remove(f)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Procesamiento por lotes exitoso: {data.get('total_processed', 0)} archivos procesados")
            return True
        else:
            print(f"❌ Procesamiento por lotes falló: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en procesamiento por lotes: {str(e)}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del microservicio OCR")
    print("=" * 50)
    
    # Verificar que el servicio esté disponible
    if not test_health_check():
        print("\n❌ El servicio OCR no está disponible")
        print("   Ejecuta: docker-compose up ocr-service")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # Pruebas individuales
    tests = [
        ("Health Check", test_health_check),
        ("OCR con datos simulados", test_ocr_with_sample_data),
        ("Procesamiento por lotes", test_batch_processing),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        if test_func():
            passed += 1
        print("-" * 30)
    
    # Resumen
    print(f"\n📊 Resumen de pruebas:")
    print(f"   ✅ Exitosas: {passed}/{total}")
    print(f"   ❌ Fallidas: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron!")
    else:
        print("⚠️  Algunas pruebas fallaron")
    
    # Instrucciones adicionales
    print(f"\n📝 Para probar con archivos reales:")
    print(f"   python test_ocr.py <ruta_del_archivo>")
    
    # Si se proporciona un archivo como argumento, probarlo
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print(f"\n🔍 Probando archivo proporcionado: {file_path}")
        test_ocr_with_file(file_path)

if __name__ == "__main__":
    main() 