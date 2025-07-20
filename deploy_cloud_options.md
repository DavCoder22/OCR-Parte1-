# ☁️ Opciones de Despliegue en la Nube

## 🎯 Objetivo
Hacer que tu API OCR esté disponible públicamente para que el equipo de Camunda pueda usarla sin configurar el entorno local.

## 🐳 Opción 1: Docker Hub (Recomendado)

### Ventajas:
- ✅ Gratuito
- ✅ Fácil de usar
- ✅ No requiere configuración de servidor
- ✅ El equipo solo necesita Docker

### Pasos:
1. **Subir imagen a Docker Hub:**
   ```bash
   # Ejecutar el script
   deploy_to_dockerhub.bat
   ```

2. **El equipo de Camunda ejecuta:**
   ```bash
   docker run -d -p 5000:5000 --name ocr-service malquinaguirre98/ocr-invoice-extractor:latest
   ```

3. **API disponible en:**
   ```
   http://localhost:5000
   ```

## ☁️ Opción 2: Heroku (Gratuito)

### Configuración:
1. Crear cuenta en Heroku
2. Instalar Heroku CLI
3. Crear `Procfile`:
   ```
   web: python app.py
   ```

4. Desplegar:
   ```bash
   heroku create ocr-invoice-api
   git push heroku main
   ```

5. **API disponible en:**
   ```
   https://ocr-invoice-api.herokuapp.com
   ```

## ☁️ Opción 3: Railway (Gratuito)

### Configuración:
1. Conectar repositorio GitHub
2. Configurar variables de entorno
3. Desplegar automáticamente

### API disponible en:
```
https://ocr-api-production.up.railway.app
```

## ☁️ Opción 4: Render (Gratuito)

### Configuración:
1. Conectar repositorio GitHub
2. Configurar como Web Service
3. Puerto: 5000

### API disponible en:
```
https://ocr-invoice-api.onrender.com
```

## ☁️ Opción 5: Google Cloud Run

### Configuración:
1. Crear proyecto en Google Cloud
2. Habilitar Cloud Run
3. Desplegar con Docker

### API disponible en:
```
https://ocr-api-xxxxx-uc.a.run.app
```

## 📋 Comparación de Opciones

| Opción | Costo | Facilidad | Velocidad | Recomendación |
|--------|-------|-----------|-----------|---------------|
| Docker Hub | Gratis | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **Mejor opción** |
| Heroku | Gratis | ⭐⭐⭐⭐ | ⭐⭐⭐ | Buena alternativa |
| Railway | Gratis | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Excelente |
| Render | Gratis | ⭐⭐⭐⭐ | ⭐⭐⭐ | Buena |
| Google Cloud | Pago | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Para producción |

## 🎯 Recomendación Final

### Para tu caso específico:

**1. Docker Hub** (Primera opción)
- ✅ Más fácil para el equipo de Camunda
- ✅ No requiere configuración de servidor
- ✅ Solo necesitan Docker instalado

**2. Railway** (Segunda opción)
- ✅ Despliegue automático desde GitHub
- ✅ URL pública directa
- ✅ Muy fácil de configurar

## 🚀 Instrucciones para el Equipo de Camunda

### Con Docker Hub:
```bash
# 1. Instalar Docker (si no lo tienen)
# 2. Ejecutar el contenedor
docker run -d -p 5000:5000 --name ocr-service malquinaguirre98/ocr-invoice-extractor:latest

# 3. Verificar que funciona
curl http://localhost:5000/health

# 4. Usar en Camunda
# URL: http://localhost:5000
```

### Con Railway/Heroku:
```bash
# 1. Usar directamente la URL pública
# 2. No necesitan instalar nada
# 3. API disponible inmediatamente

# URL: https://ocr-api-production.up.railway.app
```

## 📞 Información de Contacto

- **Desarrollador:** David
- **Email:** david@company.com
- **Documentación:** README_CAMUNDA_INTEGRATION.md
- **Repositorio:** [GitHub URL]
- **Docker Hub:** malquinaguirre98/ocr-invoice-extractor 