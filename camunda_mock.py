#!/usr/bin/env python3
"""
Mock de Camunda para pruebas de integración
Simula las respuestas de Camunda sin necesidad de tenerlo instalado
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class CamundaMock:
    """Mock de Camunda para pruebas de integración"""
    
    def __init__(self):
        self.processes = {}
        self.tasks = []
        self.deployments = {}
        self.instances = {}
        self.task_counter = 1
        self.instance_counter = 1
        self.deployment_counter = 1
    
    def deploy_process(self, bpmn_file_path: str) -> str:
        """Simula el despliegue de un proceso BPMN"""
        deployment_id = f"mock-deployment-{self.deployment_counter}"
        self.deployment_counter += 1
        
        self.deployments[deployment_id] = {
            "id": deployment_id,
            "name": "Mock Process Deployment",
            "source": bpmn_file_path,
            "deploymentTime": datetime.now().isoformat(),
            "processDefinitions": [
                {
                    "id": "Process_Reembolso:1:mock",
                    "key": "Process_Reembolso",
                    "name": "Proceso de Reembolso",
                    "version": 1
                }
            ]
        }
        
        logger.info(f"Mock: Proceso desplegado exitosamente. ID: {deployment_id}")
        return deployment_id
    
    def start_process_instance(self, process_key: str, variables: Dict[str, Any] = None) -> str:
        """Simula el inicio de una instancia de proceso"""
        instance_id = f"mock-instance-{self.instance_counter}"
        self.instance_counter += 1
        
        self.instances[instance_id] = {
            "id": instance_id,
            "processDefinitionId": f"{process_key}:1:mock",
            "processDefinitionKey": process_key,
            "startTime": datetime.now().isoformat(),
            "variables": variables or {},
            "status": "running"
        }
        
        # Crear tarea OCR automáticamente
        task_id = f"mock-task-{self.task_counter}"
        self.task_counter += 1
        
        task = {
            "id": task_id,
            "name": "Procesar Factura OCR",
            "processInstanceId": instance_id,
            "assignee": "david",
            "created": datetime.now().isoformat(),
            "formKey": None,
            "variables": {}
        }
        
        self.tasks.append(task)
        
        logger.info(f"Mock: Instancia de proceso iniciada. ID: {instance_id}")
        return instance_id
    
    def get_user_tasks(self, process_instance_id: str = None) -> List[Dict[str, Any]]:
        """Simula la obtención de tareas de usuario"""
        if process_instance_id:
            tasks = [task for task in self.tasks if task.get("processInstanceId") == process_instance_id]
        else:
            tasks = self.tasks.copy()
        
        logger.info(f"Mock: Tareas encontradas: {len(tasks)}")
        return tasks
    
    def get_ocr_tasks(self, process_instance_id: str = None) -> List[Dict[str, Any]]:
        """Simula la obtención de tareas OCR específicas"""
        all_tasks = self.get_user_tasks(process_instance_id)
        ocr_tasks = [task for task in all_tasks if 'ocr' in task.get('name', '').lower()]
        return ocr_tasks
    
    def complete_task(self, task_id: str, variables: Dict[str, Any] = None) -> bool:
        """Simula la completación de una tarea"""
        # Encontrar la tarea
        task_index = None
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                task_index = i
                break
        
        if task_index is None:
            logger.error(f"Mock: Tarea {task_id} no encontrada")
            return False
        
        # Actualizar variables de la tarea
        if variables:
            self.tasks[task_index]["variables"] = variables
        
        # Remover la tarea completada
        completed_task = self.tasks.pop(task_index)
        
        # Actualizar instancia de proceso
        instance_id = completed_task["processInstanceId"]
        if instance_id in self.instances:
            self.instances[instance_id]["variables"].update(variables or {})
        
        logger.info(f"Mock: Tarea {task_id} completada exitosamente")
        return True
    
    def get_process_variables(self, instance_id: str) -> Dict[str, Any]:
        """Simula la obtención de variables de proceso"""
        if instance_id in self.instances:
            return self.instances[instance_id].get("variables", {})
        return {}
    
    def get_version_info(self) -> Dict[str, Any]:
        """Simula la información de versión de Camunda"""
        return {
            "version": "7.20.0-mock",
            "edition": "Community",
            "buildTime": datetime.now().isoformat()
        }

# Instancia global del mock
camunda_mock = CamundaMock() 