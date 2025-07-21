#!/usr/bin/env python3
"""
Microservicio OCR para extracción de datos de facturas
Integración con Camunda BPMN para proceso de reembolsos
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pytesseract
from PIL import Image
import io
import re
import logging
import os
from datetime import datetime
import json
from pdf2image import convert_from_bytes

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Permitir CORS para integración con Camunda

# Configuración de Tesseract (ajustar según el sistema)
if os.name == 'nt':  # Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class InvoiceDataExtractor:
    """Clase para extraer datos específicos de facturas usando OCR"""
    
    def __init__(self):
        self.extracted_text = ""
    
    def extract_text_from_image(self, image):
        """Extrae texto de la imagen usando Tesseract OCR"""
        try:
            # Configurar Tesseract para mejor reconocimiento
            custom_config = r'--oem 3 --psm 6'
            self.extracted_text = pytesseract.image_to_string(image, config=custom_config, lang='spa+eng')
            logger.info("Texto extraído exitosamente")
            logger.debug(f"Texto OCR extraído:\n{self.extracted_text}")  # Log detallado
            if not self.extracted_text.strip():
                logger.error("El OCR no extrajo ningún texto. Verifica la calidad de la imagen o la instalación de Tesseract.")
                return False
            return True
        except Exception as e:
            logger.error(f"Error al extraer texto: {str(e)}")
            return False
    
    def extract_provider(self):
        """Extrae el nombre del proveedor"""
        lines = self.extracted_text.split('\n')
        for line in lines:
            if "razón social" in line.lower():
                return line.split(":", 1)[-1].strip()
            if "nombre comercial" in line.lower():
                return line.split(":", 1)[-1].strip()
        return "Proveedor no identificado"
    
    def extract_amount(self):
        """Extrae el monto total de la factura"""
        # Buscar línea con VALOR TOTAL USD
        match = re.search(r'VALOR TOTAL USD\s*([\d,.]+)', self.extracted_text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1).replace(',', ''))
            except ValueError:
                pass
        # Fallback anterior
        return 0.0
    
    def extract_date(self):
        """Extrae la fecha de la factura"""
        # Buscar FECHA DE EMISIÓN
        match = re.search(r'FECHA DE EMISI[ÓO]N[:\s]*([\d/-]{8,10})', self.extracted_text, re.IGNORECASE)
        if match:
            return match.group(1)
        # Fallback anterior
        return datetime.now().strftime("%Y-%m-%d")
    
    def extract_invoice_number(self):
        """Extrae el número de factura"""
        # Buscar patrones como N°: 001-008-004080008
        match = re.search(r'N[°º]?:?\s*([\d-]{8,})', self.extracted_text)
        if match:
            return match.group(1)
        # Fallback anterior
        return "N/A"
    
    def extract_ruc(self):
        """Extrae el RUC del proveedor"""
        # Buscar exactamente 13 dígitos
        ruc_candidates = re.findall(r'\b\d{13}\b', self.extracted_text)
        if ruc_candidates:
            return ruc_candidates[0]
        # Fallback anterior
        return "N/A"

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de salud del servicio"""
    return jsonify({
        "status": "healthy",
        "service": "OCR Invoice Extractor",
        "version": "1.0.0",
        "tesseract_available": True
    })

@app.route('/ocr', methods=['POST'])
def process_invoice():
    """
    Endpoint principal para procesar facturas
    Recibe: archivo de imagen (PDF/JPG/PNG)
    Retorna: JSON con datos extraídos
    """
    try:
        # Verificar que se envió un archivo
        if 'file' not in request.files:
            logger.error("No se proporcionó archivo en la petición.")
            return jsonify({
                "error": "No se proporcionó archivo",
                "status": "error"
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.error("No se seleccionó archivo.")
            return jsonify({
                "error": "No se seleccionó archivo",
                "status": "error"
            }), 400
        
        # Verificar tipo de archivo
        allowed_extensions = {'png', 'jpg', 'jpeg', 'pdf', 'tiff', 'bmp'}
        if not file.filename.lower().endswith(tuple('.' + ext for ext in allowed_extensions)):
            logger.error(f"Tipo de archivo no soportado: {file.filename}")
            return jsonify({
                "error": "Tipo de archivo no soportado",
                "status": "error"
            }), 400
        
        logger.info(f"Procesando archivo: {file.filename}")
        
        # Procesar imagen o PDF
        image = None
        if file.filename.lower().endswith('.pdf'):
            try:
                pdf_bytes = file.read()
                images = convert_from_bytes(pdf_bytes)
                if not images:
                    logger.error("No se pudo convertir el PDF a imagen.")
                    return jsonify({
                        "error": "No se pudo convertir el PDF a imagen",
                        "status": "error"
                    }), 400
                image = images[0]  # Procesar solo la primera página
                logger.info("PDF convertido a imagen exitosamente.")
            except Exception as e:
                logger.error(f"Error al convertir PDF: {str(e)}")
                return jsonify({
                    "error": "Error al convertir PDF a imagen",
                    "status": "error"
                }), 400
        else:
            try:
                image = Image.open(file.stream)
                # Convertir a RGB si es necesario
                if image.mode != 'RGB':
                    image = image.convert('RGB')
            except Exception as e:
                logger.error(f"Error al abrir imagen: {str(e)}")
                return jsonify({
                    "error": "Error al procesar imagen",
                    "status": "error"
                }), 400
        
        # Extraer datos
        extractor = InvoiceDataExtractor()
        if not extractor.extract_text_from_image(image):
            logger.error("No se pudo extraer texto de la imagen. Revisa los logs para más detalles.")
            return jsonify({
                "error": "No se pudo extraer texto de la imagen",
                "status": "error"
            }), 400
        
        # Extraer información específica
        extracted_data = {
            "proveedor": extractor.extract_provider(),
            "monto": extractor.extract_amount(),
            "fecha": extractor.extract_date(),
            "numero_factura": extractor.extract_invoice_number(),
            "ruc": extractor.extract_ruc(),
            "texto_completo": extractor.extracted_text[:500] + "..." if len(extractor.extracted_text) > 500 else extractor.extracted_text,
            "archivo_procesado": file.filename,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
        logger.info(f"Datos extraídos exitosamente: {extracted_data['proveedor']} - {extracted_data['monto']}")
        logger.debug(f"Datos extraídos completos: {json.dumps(extracted_data, ensure_ascii=False, indent=2)}")
        
        return jsonify(extracted_data)
        
    except Exception as e:
        logger.error(f"Error general en procesamiento: {str(e)}")
        return jsonify({
            "error": "Error interno del servidor",
            "status": "error"
        }), 500

@app.route('/ocr/batch', methods=['POST'])
def process_batch():
    """
    Endpoint para procesar múltiples facturas
    Recibe: lista de archivos
    Retorna: lista de resultados
    """
    try:
        files = request.files.getlist('files')
        if not files:
            return jsonify({
                "error": "No se proporcionaron archivos",
                "status": "error"
            }), 400
        
        results = []
        for file in files:
            if file.filename:
                try:
                    # Procesar cada archivo individualmente
                    image = Image.open(file.stream)
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    # Extraer datos
                    extractor = InvoiceDataExtractor()
                    if extractor.extract_text_from_image(image):
                        extracted_data = {
                            "proveedor": extractor.extract_provider(),
                            "monto": extractor.extract_amount(),
                            "fecha": extractor.extract_date(),
                            "numero_factura": extractor.extract_invoice_number(),
                            "ruc": extractor.extract_ruc(),
                            "archivo_procesado": file.filename,
                            "timestamp": datetime.now().isoformat(),
                            "status": "success"
                        }
                    else:
                        extracted_data = {
                            "error": "No se pudo extraer texto",
                            "archivo_procesado": file.filename,
                            "status": "error"
                        }
                    
                    results.append({
                        "filename": file.filename,
                        "result": extracted_data
                    })
                    
                except Exception as e:
                    logger.error(f"Error procesando {file.filename}: {str(e)}")
                    results.append({
                        "filename": file.filename,
                        "result": {
                            "error": f"Error procesando archivo: {str(e)}",
                            "status": "error"
                        }
                    })
        
        return jsonify({
            "results": results,
            "total_processed": len(results),
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Error en procesamiento por lotes: {str(e)}")
        return jsonify({
            "error": "Error en procesamiento por lotes",
            "status": "error"
        }), 500

if __name__ == '__main__':
    # Configurar puerto desde variable de entorno o usar 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"Iniciando servicio OCR en puerto {port}")
    logger.info("Endpoints disponibles:")
    logger.info("  GET  /health - Verificar estado del servicio")
    logger.info("  POST /ocr - Procesar factura individual")
    logger.info("  POST /ocr/batch - Procesar múltiples facturas")
    
    app.run(host='0.0.0.0', port=port, debug=False) 