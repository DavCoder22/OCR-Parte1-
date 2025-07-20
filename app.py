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
            return True
        except Exception as e:
            logger.error(f"Error al extraer texto: {str(e)}")
            return False
    
    def extract_provider(self):
        """Extrae el nombre del proveedor"""
        # Buscar patrones comunes de proveedores
        lines = self.extracted_text.split('\n')
        for line in lines[:10]:  # Buscar en las primeras líneas
            line = line.strip()
            if len(line) > 3 and not re.match(r'^\d', line):
                # Excluir líneas que empiecen con números
                return line
        return "Proveedor no identificado"
    
    def extract_amount(self):
        """Extrae el monto total de la factura"""
        # Buscar patrones específicos de montos con mejor prioridad
        amount_patterns = [
            # Patrones más específicos primero
            r'TOTAL[:\s]*S/\.?\s*([\d,]+\.?\d*)',
            r'TOTAL[:\s]*\$?\s*([\d,]+\.?\d*)',
            r'MONTO[:\s]*S/\.?\s*([\d,]+\.?\d*)',
            r'MONTO[:\s]*\$?\s*([\d,]+\.?\d*)',
            r'IMPORTE[:\s]*S/\.?\s*([\d,]+\.?\d*)',
            r'IMPORTE[:\s]*\$?\s*([\d,]+\.?\d*)',
            r'SUBTOTAL[:\s]*S/\.?\s*([\d,]+\.?\d*)',
            r'SUBTOTAL[:\s]*\$?\s*([\d,]+\.?\d*)',
            r'PAGAR[:\s]*S/\.?\s*([\d,]+\.?\d*)',
            r'PAGAR[:\s]*\$?\s*([\d,]+\.?\d*)',
            r'PAGO[:\s]*S/\.?\s*([\d,]+\.?\d*)',
            r'PAGO[:\s]*\$?\s*([\d,]+\.?\d*)',
            # Patrones con decimales específicos
            r'S/\.?\s*([\d,]+\.\d{2})',
            r'\$\s*([\d,]+\.\d{2})',
            r'USD\s*([\d,]+\.\d{2})',
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, self.extracted_text, re.IGNORECASE)
            if match:
                amount = match.group(1).replace(',', '')
                try:
                    amount_float = float(amount)
                    # Validar que sea un monto razonable y no un año
                    if 1 <= amount_float <= 100000 and amount_float != 2024 and amount_float != 2023 and amount_float != 2025:
                        return amount_float
                except ValueError:
                    continue
        
        # Buscar números con formato de moneda (más específico)
        currency_patterns = [
            r'S/\.?\s*([\d,]+\.?\d*)',
            r'\$\s*([\d,]+\.?\d*)',
            r'USD\s*([\d,]+\.?\d*)',
        ]
        
        for pattern in currency_patterns:
            matches = re.findall(pattern, self.extracted_text, re.IGNORECASE)
            for match in matches:
                amount = match.replace(',', '')
                try:
                    amount_float = float(amount)
                    # Validar que sea un monto razonable, no un número de factura, y no un año
                    if (10 <= amount_float <= 100000 and 
                        amount_float != int(amount_float) and 
                        amount_float not in [2024, 2023, 2025, 2026]):
                        return amount_float
                except ValueError:
                    continue
        
        # Buscar números que parezcan montos (excluyendo números de factura y años)
        # Buscar líneas que contengan palabras relacionadas con dinero
        money_keywords = ['total', 'monto', 'importe', 'pagar', 'pago', 'subtotal', 'suma']
        lines = self.extracted_text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            # Verificar si la línea contiene palabras relacionadas con dinero
            if any(keyword in line_lower for keyword in money_keywords):
                # Buscar números en esa línea
                numbers = re.findall(r'[\d,]+\.?\d*', line)
                for num in numbers:
                    num_clean = num.replace(',', '')
                    try:
                        amount = float(num_clean)
                        # Excluir años y números de factura
                        if (10 <= amount <= 100000 and 
                            amount not in [2024, 2023, 2025, 2026] and
                            (amount != int(amount) or amount < 10000)):
                            return amount
                    except ValueError:
                        continue
        
        # Último recurso: buscar números grandes pero excluir números de factura y años
        numbers = re.findall(r'[\d,]+\.?\d*', self.extracted_text)
        valid_amounts = []
        for num in numbers:
            num_clean = num.replace(',', '')
            try:
                amount = float(num_clean)
                # Excluir números que parecen ser números de factura o años
                if (10 <= amount <= 100000 and 
                    amount not in [2024, 2023, 2025, 2026] and
                    (amount != int(amount) or amount < 10000)):
                    valid_amounts.append(amount)
            except ValueError:
                continue
        
        # Retornar el monto más alto que no sea un número de factura o año
        if valid_amounts:
            return max(valid_amounts)
        
        return 0.0
    
    def extract_date(self):
        """Extrae la fecha de la factura"""
        # Buscar patrones de fecha
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
            r'FECHA[:\s]*(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, self.extracted_text)
            if match:
                try:
                    if len(match.group(3)) == 2:
                        year = '20' + match.group(3)
                    else:
                        year = match.group(3)
                    
                    month = match.group(2).zfill(2)
                    day = match.group(1).zfill(2)
                    
                    return f"{year}-{month}-{day}"
                except:
                    continue
        
        return datetime.now().strftime("%Y-%m-%d")
    
    def extract_invoice_number(self):
        """Extrae el número de factura"""
        # Buscar patrones de números de factura
        invoice_patterns = [
            r'FACTURA[:\s]*N°?\s*([A-Z0-9-]+)',
            r'FACTURA[:\s]*#\s*([A-Z0-9-]+)',
            r'BOLETA[:\s]*N°?\s*([A-Z0-9-]+)',
            r'COMPROBANTE[:\s]*N°?\s*([A-Z0-9-]+)',
            r'N°?\s*([A-Z0-9-]{6,})',
        ]
        
        for pattern in invoice_patterns:
            match = re.search(pattern, self.extracted_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "N/A"
    
    def extract_ruc(self):
        """Extrae el RUC del proveedor"""
        # Buscar RUC (11 dígitos en Perú)
        ruc_pattern = r'RUC[:\s]*(\d{11})'
        match = re.search(ruc_pattern, self.extracted_text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Buscar cualquier secuencia de 11 dígitos
        ruc_candidates = re.findall(r'\d{11}', self.extracted_text)
        if ruc_candidates:
            return ruc_candidates[0]
        
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
            return jsonify({
                "error": "No se proporcionó archivo",
                "status": "error"
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "error": "No se seleccionó archivo",
                "status": "error"
            }), 400
        
        # Verificar tipo de archivo
        allowed_extensions = {'png', 'jpg', 'jpeg', 'pdf', 'tiff', 'bmp'}
        if not file.filename.lower().endswith(tuple('.' + ext for ext in allowed_extensions)):
            return jsonify({
                "error": "Tipo de archivo no soportado",
                "status": "error"
            }), 400
        
        logger.info(f"Procesando archivo: {file.filename}")
        
        # Procesar imagen
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