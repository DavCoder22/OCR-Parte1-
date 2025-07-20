#!/usr/bin/env python3
"""
Integración con Camunda BPMN para el proceso de reembolsos
Microservicio OCR - Parte 1 del proceso
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CamundaOCRIntegration:
    """Clase para integrar el microservicio OCR con Camunda BPMN"""
    
    def __init__(self, camunda_url: str = "http://localhost:8080", ocr_url: str = "http://localhost:5000"):
        self.camunda_url = camunda_url
        self.ocr_url = ocr_url
        self.headers = {
            'Content-Type': 'application/json'
        }
    
    def deploy_process(self, bpmn_file_path: str) -> Optional[str]:
        """
        Despliega el proceso BPMN en Camunda
        """
        try:
            with open(bpmn_file_path, 'rb') as file:
                files = {
                    'file': (bpmn_file_path, file, 'application/xml')
                }
                response = requests.post(
                    f"{self.camunda_url}/engine-rest/deployment/create",
                    files=files
                )
            
            if response.status_code == 200:
                deployment_data = response.json()
                deployment_id = deployment_data['id']
                logger.info(f"Proceso desplegado exitosamente. ID: {deployment_id}")
                return deployment_id
            else:
                logger.error(f"Error al desplegar proceso: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error al desplegar proceso: {str(e)}")
            return None
    
    def start_process_instance(self, process_key: str, variables: Dict[str, Any] = None) -> Optional[str]:
        """
        Inicia una instancia del proceso
        """
        try:
            payload = {
                "variables": variables or {}
            }
            
            response = requests.post(
                f"{self.camunda_url}/engine-rest/process-definition/key/{process_key}/start",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                instance_data = response.json()
                instance_id = instance_data['id']
                logger.info(f"Instancia de proceso iniciada. ID: {instance_id}")
                return instance_id
            else:
                logger.error(f"Error al iniciar proceso: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error al iniciar proceso: {str(e)}")
            return None
    
    def process_ocr_task(self, task_id: str, invoice_file_path: str) -> bool:
        """
        Procesa una tarea OCR específica
        """
        try:
            # 1. Procesar factura con OCR
            with open(invoice_file_path, 'rb') as file:
                files = {'file': file}
                ocr_response = requests.post(f"{self.ocr_url}/ocr", files=files, timeout=30)
            
            if ocr_response.status_code != 200:
                logger.error(f"Error en OCR: {ocr_response.status_code}")
                return False
            
            ocr_data = ocr_response.json()
            
            # 2. Completar tarea en Camunda con datos extraídos
            task_payload = {
                "variables": {
                    "proveedor": {
                        "value": ocr_data.get('proveedor', ''),
                        "type": "String"
                    },
                    "monto": {
                        "value": ocr_data.get('monto', 0.0),
                        "type": "Double"
                    },
                    "fecha_factura": {
                        "value": ocr_data.get('fecha', ''),
                        "type": "String"
                    },
                    "numero_factura": {
                        "value": ocr_data.get('numero_factura', ''),
                        "type": "String"
                    },
                    "ruc_proveedor": {
                        "value": ocr_data.get('ruc', ''),
                        "type": "String"
                    },
                    "ocr_status": {
                        "value": "completed",
                        "type": "String"
                    },
                    "ocr_timestamp": {
                        "value": datetime.now().isoformat(),
                        "type": "String"
                    }
                }
            }
            
            response = requests.post(
                f"{self.camunda_url}/engine-rest/task/{task_id}/complete",
                headers=self.headers,
                json=task_payload
            )
            
            if response.status_code == 204:
                logger.info(f"Tarea OCR completada exitosamente. Task ID: {task_id}")
                return True
            else:
                logger.error(f"Error al completar tarea: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error al procesar tarea OCR: {str(e)}")
            return False
    
    def get_user_tasks(self, process_instance_id: str = None) -> list:
        """
        Obtiene las tareas de usuario disponibles
        """
        try:
            url = f"{self.camunda_url}/engine-rest/task"
            if process_instance_id:
                url += f"?processInstanceId={process_instance_id}"
            
            response = requests.get(url)
            
            if response.status_code == 200:
                tasks = response.json()
                logger.info(f"Tareas encontradas: {len(tasks)}")
                return tasks
            else:
                logger.error(f"Error al obtener tareas: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error al obtener tareas: {str(e)}")
            return []
    
    def get_ocr_tasks(self, process_instance_id: str = None) -> list:
        """
        Obtiene específicamente las tareas OCR
        """
        tasks = self.get_user_tasks(process_instance_id)
        ocr_tasks = [task for task in tasks if 'ocr' in task.get('name', '').lower()]
        return ocr_tasks

def create_sample_bpmn_process() -> str:
    """
    Crea un archivo BPMN de ejemplo para el proceso de reembolsos
    """
    bpmn_content = '''<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" 
                  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" 
                  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" 
                  xmlns:di="http://www.omg.org/spec/DD/20100524/DI" 
                  xmlns:camunda="http://camunda.org/schema/1.0/bpmn" 
                  id="Definitions_1" 
                  targetNamespace="http://bpmn.io/schema/bpmn">
  
  <bpmn:process id="Process_Reembolso" name="Proceso de Reembolso" isExecutable="true">
    
    <bpmn:startEvent id="StartEvent_1" name="Inicio Solicitud">
      <bpmn:outgoing>Flow_1</bpmn:outgoing>
    </bpmn:startEvent>
    
    <bpmn:userTask id="Task_OCR" name="Procesar Factura OCR" camunda:assignee="david">
      <bpmn:incoming>Flow_1</bpmn:incoming>
      <bpmn:outgoing>Flow_2</bpmn:outgoing>
    </bpmn:userTask>
    
    <bpmn:serviceTask id="Task_Validar" name="Validar Datos" camunda:class="com.example.ValidationService">
      <bpmn:incoming>Flow_2</bpmn:incoming>
      <bpmn:outgoing>Flow_3</bpmn:outgoing>
    </bpmn:serviceTask>
    
    <bpmn:exclusiveGateway id="Gateway_1" name="¿Datos Válidos?">
      <bpmn:incoming>Flow_3</bpmn:incoming>
      <bpmn:outgoing>Flow_4</bpmn:outgoing>
      <bpmn:outgoing>Flow_5</bpmn:outgoing>
    </bpmn:exclusiveGateway>
    
    <bpmn:userTask id="Task_Aprobar" name="Aprobar Reembolso" camunda:assignee="manager">
      <bpmn:incoming>Flow_4</bpmn:incoming>
      <bpmn:outgoing>Flow_6</bpmn:outgoing>
    </bpmn:userTask>
    
    <bpmn:endEvent id="EndEvent_1" name="Reembolso Aprobado">
      <bpmn:incoming>Flow_6</bpmn:incoming>
    </bpmn:endEvent>
    
    <bpmn:endEvent id="EndEvent_2" name="Reembolso Rechazado">
      <bpmn:incoming>Flow_5</bpmn:incoming>
    </bpmn:endEvent>
    
    <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="Task_OCR" />
    <bpmn:sequenceFlow id="Flow_2" sourceRef="Task_OCR" targetRef="Task_Validar" />
    <bpmn:sequenceFlow id="Flow_3" sourceRef="Task_Validar" targetRef="Gateway_1" />
    <bpmn:sequenceFlow id="Flow_4" sourceRef="Gateway_1" targetRef="Task_Aprobar" />
    <bpmn:sequenceFlow id="Flow_5" sourceRef="Gateway_1" targetRef="EndEvent_2" />
    <bpmn:sequenceFlow id="Flow_6" sourceRef="Task_Aprobar" targetRef="EndEvent_1" />
    
  </bpmn:process>
  
</bpmn:definitions>'''
    
    # Guardar archivo BPMN
    bpmn_file_path = "proceso_reembolso.bpmn"
    with open(bpmn_file_path, 'w', encoding='utf-8') as f:
        f.write(bpmn_content)
    
    return bpmn_file_path

def main():
    """
    Función principal para demostrar la integración
    """
    print("🔧 Integración Camunda - Microservicio OCR")
    print("=" * 50)
    
    # Crear instancia de integración
    integration = CamundaOCRIntegration()
    
    # 1. Crear archivo BPMN de ejemplo
    print("\n📋 Creando archivo BPMN de ejemplo...")
    bpmn_file = create_sample_bpmn_process()
    print(f"✅ Archivo BPMN creado: {bpmn_file}")
    
    # 2. Desplegar proceso (requiere Camunda ejecutándose)
    print("\n🚀 Desplegando proceso en Camunda...")
    deployment_id = integration.deploy_process(bpmn_file)
    
    if deployment_id:
        print(f"✅ Proceso desplegado. Deployment ID: {deployment_id}")
        
        # 3. Iniciar instancia de proceso
        print("\n🎯 Iniciando instancia de proceso...")
        instance_id = integration.start_process_instance("Process_Reembolso")
        
        if instance_id:
            print(f"✅ Instancia iniciada. Instance ID: {instance_id}")
            
            # 4. Obtener tareas OCR
            print("\n📋 Buscando tareas OCR...")
            ocr_tasks = integration.get_ocr_tasks(instance_id)
            
            if ocr_tasks:
                print(f"✅ Tareas OCR encontradas: {len(ocr_tasks)}")
                for task in ocr_tasks:
                    print(f"   - Task ID: {task['id']}, Name: {task['name']}")
            else:
                print("⚠️  No se encontraron tareas OCR")
        else:
            print("❌ Error al iniciar instancia de proceso")
    else:
        print("❌ Error al desplegar proceso")
        print("💡 Asegúrate de que Camunda esté ejecutándose en http://localhost:8080")
    
    print("\n📚 Documentación de integración:")
    print("   - El microservicio OCR está disponible en: http://localhost:5000")
    print("   - Endpoints disponibles:")
    print("     * POST /ocr - Procesar factura individual")
    print("     * POST /ocr/batch - Procesar múltiples facturas")
    print("     * GET /health - Verificar estado del servicio")
    print("   - Variables de proceso disponibles:")
    print("     * proveedor, monto, fecha_factura, numero_factura, ruc_proveedor")

if __name__ == "__main__":
    main() 