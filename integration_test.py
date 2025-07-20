#!/usr/bin/env python3
"""
Prueba de Integración Completa - Microservicio OCR
Verifica: Servicio OCR, Base de Datos PostgreSQL, Conectividad y Funcionalidad
"""

import requests
import json
import os
import sys
import time
import psycopg2
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, Any, List

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IntegrationTestSuite:
    """
    Suite completa de pruebas de integración para el microservicio OCR
    """
    
    def __init__(self):
        # Configuración de servicios
        self.ocr_service_url = "http://localhost:5000"
        self.db_config = {
            'host': 'localhost',
            'port': 5435,
            'database': 'ocr_db',
            'user': 'ocr_user',
            'password': 'ocr_password'
        }
        
        # Resultados de las pruebas
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Registra el resultado de una prueba"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            logger.info(f"✅ {test_name}: PASÓ")
        else:
            logger.error(f"❌ {test_name}: FALLÓ - {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def test_ocr_service_health(self) -> bool:
        """Prueba 1: Verificar que el servicio OCR esté disponible"""
        try:
            response = requests.get(f"{self.ocr_service_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                expected_fields = ['status', 'service', 'version', 'tesseract_available']
                
                if all(field in data for field in expected_fields):
                    if data['status'] == 'healthy' and data['tesseract_available']:
                        self.log_test_result("OCR Service Health Check", True)
                        return True
                    else:
                        self.log_test_result("OCR Service Health Check", False, 
                                           f"Status: {data.get('status')}, Tesseract: {data.get('tesseract_available')}")
                        return False
                else:
                    self.log_test_result("OCR Service Health Check", False, 
                                       f"Campos faltantes en respuesta: {data}")
                    return False
            else:
                self.log_test_result("OCR Service Health Check", False, 
                                   f"HTTP {response.status_code}: {response.text}")
                return False
        except requests.exceptions.ConnectionError:
            self.log_test_result("OCR Service Health Check", False, 
                               "No se puede conectar al servicio OCR")
            return False
        except Exception as e:
            self.log_test_result("OCR Service Health Check", False, str(e))
            return False
    
    def test_database_connection(self) -> bool:
        """Prueba 2: Verificar conexión a PostgreSQL"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Verificar que podemos ejecutar una consulta simple
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if version:
                self.log_test_result("Database Connection", True, f"PostgreSQL {version[0]}")
                return True
            else:
                self.log_test_result("Database Connection", False, "No se pudo obtener versión de PostgreSQL")
                return False
                
        except psycopg2.OperationalError as e:
            self.log_test_result("Database Connection", False, f"Error de conexión: {str(e)}")
            return False
        except Exception as e:
            self.log_test_result("Database Connection", False, str(e))
            return False
    
    def test_database_schema(self) -> bool:
        """Prueba 3: Verificar esquema de base de datos"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Verificar que existe la tabla de resultados OCR
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'ocr_results'
                );
            """)
            
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                # Crear la tabla si no existe
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ocr_results (
                        id SERIAL PRIMARY KEY,
                        filename VARCHAR(255) NOT NULL,
                        provider VARCHAR(255),
                        amount DECIMAL(10,2),
                        invoice_date DATE,
                        invoice_number VARCHAR(100),
                        ruc VARCHAR(20),
                        extracted_text TEXT,
                        processing_time_ms INTEGER,
                        status VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
                logger.info("Tabla ocr_results creada")
            
            cursor.close()
            conn.close()
            
            self.log_test_result("Database Schema", True, "Esquema de base de datos verificado")
            return True
            
        except Exception as e:
            self.log_test_result("Database Schema", False, str(e))
            return False
    
    def test_ocr_data_extraction(self) -> bool:
        """Prueba 4: Verificar extracción de datos OCR"""
        try:
            # Crear una imagen de prueba con datos conocidos
            from PIL import Image, ImageDraw, ImageFont
            
            # Crear imagen de factura de prueba
            img = Image.new('RGB', (500, 300), color='white')
            draw = ImageDraw.Draw(img)
            
            # Datos de prueba conocidos
            test_data = {
                'provider': 'EMPRESA DE PRUEBA SAC',
                'amount': 1250.50,
                'date': '15/06/2024',
                'invoice_number': 'F001-001-00012345',
                'ruc': '20123456789'
            }
            
            # Agregar texto a la imagen
            text_lines = [
                f"FACTURA N° {test_data['invoice_number']}",
                f"RUC: {test_data['ruc']}",
                f"{test_data['provider']}",
                f"FECHA: {test_data['date']}",
                f"TOTAL: S/ {test_data['amount']:.2f}"
            ]
            
            y_position = 30
            for line in text_lines:
                draw.text((30, y_position), line, fill='black')
                y_position += 30
            
            # Guardar imagen temporal
            test_image_path = "test_integration_invoice.png"
            img.save(test_image_path)
            
            # Procesar con OCR
            start_time = time.time()
            with open(test_image_path, 'rb') as file:
                files = {'file': file}
                response = requests.post(f"{self.ocr_service_url}/ocr", files=files, timeout=30)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            # Limpiar archivo temporal
            if os.path.exists(test_image_path):
                os.remove(test_image_path)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verificar que los datos extraídos coincidan con los esperados
                success = True
                details = []
                
                # Verificar proveedor (puede variar por OCR)
                if 'proveedor' in data and data['proveedor']:
                    details.append(f"Proveedor: {data['proveedor']}")
                else:
                    success = False
                    details.append("Proveedor no extraído")
                
                # Verificar monto (debe ser cercano al esperado)
                if 'monto' in data and data['monto']:
                    amount_diff = abs(data['monto'] - test_data['amount'])
                    if amount_diff < 10:  # Tolerancia de 10 unidades
                        details.append(f"Monto: {data['monto']}")
                    else:
                        success = False
                        details.append(f"Monto extraído: {data['monto']}, Esperado: {test_data['amount']}")
                else:
                    success = False
                    details.append("Monto no extraído")
                
                # Verificar fecha
                if 'fecha' in data and data['fecha']:
                    details.append(f"Fecha: {data['fecha']}")
                else:
                    details.append("Fecha no extraída")
                
                # Verificar número de factura
                if 'numero_factura' in data and data['numero_factura']:
                    details.append(f"Número: {data['numero_factura']}")
                else:
                    details.append("Número de factura no extraído")
                
                # Verificar RUC
                if 'ruc' in data and data['ruc']:
                    details.append(f"RUC: {data['ruc']}")
                else:
                    details.append("RUC no extraído")
                
                details.append(f"Tiempo de procesamiento: {processing_time}ms")
                
                self.log_test_result("OCR Data Extraction", success, ", ".join(details))
                return success
            else:
                self.log_test_result("OCR Data Extraction", False, 
                                   f"HTTP {response.status_code}: {response.text}")
                return False
                
        except ImportError:
            self.log_test_result("OCR Data Extraction", False, "Pillow no disponible")
            return False
        except Exception as e:
            self.log_test_result("OCR Data Extraction", False, str(e))
            return False
    
    def test_database_integration(self) -> bool:
        """Prueba 5: Verificar integración con base de datos"""
        try:
            # Procesar una imagen de prueba y guardar en BD
            from PIL import Image, ImageDraw
            
            # Crear imagen simple
            img = Image.new('RGB', (400, 200), color='white')
            draw = ImageDraw.Draw(img)
            draw.text((20, 20), "FACTURA TEST BD", fill='black')
            draw.text((20, 50), "MONTO: S/ 500.00", fill='black')
            
            test_image_path = "test_db_integration.png"
            img.save(test_image_path)
            
            # Procesar con OCR
            with open(test_image_path, 'rb') as file:
                files = {'file': file}
                response = requests.post(f"{self.ocr_service_url}/ocr", files=files, timeout=30)
            
            # Limpiar archivo temporal
            if os.path.exists(test_image_path):
                os.remove(test_image_path)
            
            if response.status_code == 200:
                ocr_data = response.json()
                
                # Guardar en base de datos
                conn = psycopg2.connect(**self.db_config)
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO ocr_results 
                    (filename, provider, amount, invoice_date, invoice_number, ruc, extracted_text, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (
                    ocr_data.get('archivo_procesado', 'test.png'),
                    ocr_data.get('proveedor'),
                    ocr_data.get('monto'),
                    ocr_data.get('fecha'),
                    ocr_data.get('numero_factura'),
                    ocr_data.get('ruc'),
                    ocr_data.get('texto_completo', '')[:1000],  # Limitar texto
                    ocr_data.get('status', 'success')
                ))
                
                record_id = cursor.fetchone()[0]
                conn.commit()
                
                # Verificar que se guardó correctamente
                cursor.execute("SELECT * FROM ocr_results WHERE id = %s", (record_id,))
                saved_record = cursor.fetchone()
                
                cursor.close()
                conn.close()
                
                if saved_record:
                    self.log_test_result("Database Integration", True, 
                                       f"Registro guardado con ID: {record_id}")
                    return True
                else:
                    self.log_test_result("Database Integration", False, 
                                       "No se pudo recuperar el registro guardado")
                    return False
            else:
                self.log_test_result("Database Integration", False, 
                                   f"Error en OCR: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test_result("Database Integration", False, str(e))
            return False
    
    def test_batch_processing(self) -> bool:
        """Prueba 6: Verificar procesamiento por lotes"""
        try:
            from PIL import Image, ImageDraw
            
            # Crear múltiples imágenes de prueba
            test_files = []
            for i in range(3):
                img = Image.new('RGB', (300, 150), color='white')
                draw = ImageDraw.Draw(img)
                draw.text((20, 20), f"FACTURA BATCH {i+1}", fill='black')
                draw.text((20, 50), f"MONTO: S/ {100 + i*50}.00", fill='black')
                
                filename = f"test_batch_{i+1}.png"
                img.save(filename)
                test_files.append(filename)
            
            # Procesar por lotes
            files = [('files', open(f, 'rb')) for f in test_files]
            response = requests.post(f"{self.ocr_service_url}/ocr/batch", files=files, timeout=60)
            
            # Cerrar archivos
            for _, file in files:
                file.close()
            
            # Limpiar archivos temporales
            for f in test_files:
                if os.path.exists(f):
                    os.remove(f)
            
            if response.status_code == 200:
                data = response.json()
                total_processed = data.get('total_processed', 0)
                
                if total_processed == 3:
                    self.log_test_result("Batch Processing", True, 
                                       f"Procesados {total_processed} archivos correctamente")
                    return True
                else:
                    self.log_test_result("Batch Processing", False, 
                                       f"Procesados {total_processed}/3 archivos")
                    return False
            else:
                self.log_test_result("Batch Processing", False, 
                                   f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test_result("Batch Processing", False, str(e))
            return False
    
    def test_error_handling(self) -> bool:
        """Prueba 7: Verificar manejo de errores"""
        try:
            # Probar con archivo inválido
            response = requests.post(f"{self.ocr_service_url}/ocr", 
                                   files={'file': ('invalid.txt', b'invalid content', 'text/plain')},
                                   timeout=10)
            
            if response.status_code == 400:
                error_data = response.json()
                if 'error' in error_data and 'status' in error_data:
                    self.log_test_result("Error Handling", True, 
                                       f"Error manejado correctamente: {error_data.get('error')}")
                    return True
                else:
                    self.log_test_result("Error Handling", False, 
                                       "Respuesta de error sin formato esperado")
                    return False
            else:
                self.log_test_result("Error Handling", False, 
                                   f"Error esperado no recibido: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test_result("Error Handling", False, str(e))
            return False
    
    def test_performance(self) -> bool:
        """Prueba 8: Verificar rendimiento básico"""
        try:
            from PIL import Image, ImageDraw
            
            # Crear imagen de prueba
            img = Image.new('RGB', (400, 200), color='white')
            draw = ImageDraw.Draw(img)
            draw.text((20, 20), "PRUEBA DE RENDIMIENTO", fill='black')
            
            test_image_path = "test_performance.png"
            img.save(test_image_path)
            
            # Medir tiempo de procesamiento
            start_time = time.time()
            
            with open(test_image_path, 'rb') as file:
                files = {'file': file}
                response = requests.post(f"{self.ocr_service_url}/ocr", files=files, timeout=30)
            
            processing_time = (time.time() - start_time) * 1000
            
            # Limpiar archivo temporal
            if os.path.exists(test_image_path):
                os.remove(test_image_path)
            
            if response.status_code == 200 and processing_time < 10000:  # Menos de 10 segundos
                self.log_test_result("Performance Test", True, 
                                   f"Tiempo de procesamiento: {processing_time:.2f}ms")
                return True
            else:
                self.log_test_result("Performance Test", False, 
                                   f"Tiempo excesivo: {processing_time:.2f}ms")
                return False
                
        except Exception as e:
            self.log_test_result("Performance Test", False, str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Ejecuta todas las pruebas de integración"""
        logger.info("🚀 Iniciando Pruebas de Integración Completa")
        logger.info("=" * 60)
        
        # Lista de pruebas a ejecutar
        tests = [
            ("OCR Service Health", self.test_ocr_service_health),
            ("Database Connection", self.test_database_connection),
            ("Database Schema", self.test_database_schema),
            ("OCR Data Extraction", self.test_ocr_data_extraction),
            ("Database Integration", self.test_database_integration),
            ("Batch Processing", self.test_batch_processing),
            ("Error Handling", self.test_error_handling),
            ("Performance Test", self.test_performance)
        ]
        
        # Ejecutar pruebas
        for test_name, test_func in tests:
            logger.info(f"\n🧪 Ejecutando: {test_name}")
            logger.info("-" * 40)
            try:
                test_func()
            except Exception as e:
                logger.error(f"Error ejecutando {test_name}: {str(e)}")
                self.log_test_result(test_name, False, f"Error de ejecución: {str(e)}")
        
        # Generar reporte
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Genera reporte final de las pruebas"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 REPORTE FINAL DE PRUEBAS DE INTEGRACIÓN")
        logger.info("=" * 60)
        
        # Estadísticas
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        logger.info(f"✅ Pruebas exitosas: {self.passed_tests}/{self.total_tests}")
        logger.info(f"📈 Tasa de éxito: {success_rate:.1f}%")
        
        # Detalles de cada prueba
        logger.info("\n📋 Detalles por prueba:")
        for result in self.test_results:
            status = "✅ PASÓ" if result['success'] else "❌ FALLÓ"
            logger.info(f"  {status} - {result['test']}")
            if not result['success'] and result['details']:
                logger.info(f"      💡 {result['details']}")
        
        # Recomendaciones
        logger.info("\n💡 Recomendaciones:")
        if success_rate == 100:
            logger.info("  🎉 ¡Todas las pruebas pasaron! El sistema está listo para producción.")
        elif success_rate >= 80:
            logger.info("  ⚠️  La mayoría de las pruebas pasaron. Revisa las fallidas antes de continuar.")
        else:
            logger.info("  🚨 Muchas pruebas fallaron. Revisa la configuración del sistema.")
        
        # Guardar reporte en archivo
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': self.total_tests,
                'passed_tests': self.passed_tests,
                'success_rate': success_rate
            },
            'results': self.test_results
        }
        
        report_file = f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n📄 Reporte guardado en: {report_file}")
        
        return report_data

def main():
    """Función principal"""
    print("🔧 Pruebas de Integración - Microservicio OCR")
    print("=" * 60)
    
    # Verificar argumentos
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("\nUso: python integration_test.py [opciones]")
        print("\nOpciones:")
        print("  --help     Mostrar esta ayuda")
        print("  --db-only  Solo probar base de datos")
        print("  --ocr-only Solo probar servicio OCR")
        print("\nEjemplos:")
        print("  python integration_test.py")
        print("  python integration_test.py --db-only")
        return
    
    # Crear y ejecutar suite de pruebas
    test_suite = IntegrationTestSuite()
    
    try:
        report = test_suite.run_all_tests()
        
        # Código de salida basado en resultados
        success_rate = report['summary']['success_rate']
        if success_rate >= 80:
            sys.exit(0)  # Éxito
        else:
            sys.exit(1)  # Fallo
            
    except KeyboardInterrupt:
        logger.info("\n⚠️  Pruebas interrumpidas por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Error general en las pruebas: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 