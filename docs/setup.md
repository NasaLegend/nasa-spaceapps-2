# Guía de Instalación y Configuración

## Requisitos del Sistema

### Backend (Python)
- Python 3.9 o superior
- pip (gestor de paquetes de Python)

### Frontend (React)
- Node.js 16 o superior
- npm o yarn

### Opcional
- Docker y Docker Compose (para deployment con contenedores)

## Instalación Local

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd weather-probability-app
```

### 2. Configurar el Backend

#### Crear entorno virtual
```bash
cd backend
python -m venv venv

# En Windows
venv\Scripts\activate

# En macOS/Linux
source venv/bin/activate
```

#### Instalar dependencias
```bash
pip install -r requirements.txt
```

#### Ejecutar el servidor
```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en: http://localhost:8000

### 3. Configurar el Frontend

#### Instalar dependencias
```bash
cd frontend
npm install
```

#### Configurar variables de entorno
Crear archivo `.env` en la carpeta `frontend`:
```env
REACT_APP_API_URL=http://localhost:8000
```

#### Ejecutar la aplicación
```bash
npm start
```

La aplicación estará disponible en: http://localhost:3000

## Instalación con Docker

### Opción 1: Docker Compose (Recomendado)
```bash
docker-compose up --build
```

### Opción 2: Contenedores individuales

#### Backend
```bash
cd backend
docker build -t weather-api .
docker run -p 8000:8000 weather-api
```

#### Frontend
```bash
cd frontend
docker build -t weather-frontend .
docker run -p 3000:3000 weather-frontend
```

## Configuración de Desarrollo

### Backend
1. **Configurar variables de entorno** (opcional):
   - Crear archivo `.env` en la carpeta `backend`
   - Configurar variables como `DEBUG=True`

2. **Ejecutar tests**:
   ```bash
   cd backend
   pytest
   ```

### Frontend
1. **Configurar proxy** (ya configurado en package.json):
   ```json
   "proxy": "http://localhost:8000"
   ```

2. **Ejecutar tests**:
   ```bash
   cd frontend
   npm test
   ```

## Configuración de Producción

### Variables de Entorno

#### Backend
```env
DEBUG=False
ALLOWED_HOSTS=["https://your-domain.com"]
```

#### Frontend
```env
REACT_APP_API_URL=https://your-api-domain.com
```

### Deployment

#### Backend (FastAPI)
- Usar servidor ASGI como Gunicorn con Uvicorn workers
- Configurar proxy reverso (Nginx)
- Configurar HTTPS

#### Frontend (React)
- Build para producción: `npm run build`
- Servir archivos estáticos con servidor web (Nginx, Apache)
- Configurar HTTPS y compresión

## Troubleshooting

### Problemas Comunes

1. **Puerto 8000 ocupado**:
   ```bash
   uvicorn app.main:app --port 8001
   ```

2. **Problemas de CORS**:
   - Verificar configuración en `backend/app/core/config.py`
   - Añadir URL del frontend a `ALLOWED_HOSTS`

3. **Dependencias no encontradas**:
   ```bash
   # Backend
   pip install --upgrade pip
   pip install -r requirements.txt

   # Frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Error de importación de Chart.js**:
   ```bash
   npm install chart.js react-chartjs-2
   ```

### Logs y Debugging

#### Backend
- Los logs aparecen en la consola donde ejecutas uvicorn
- Para más detalle: `uvicorn app.main:app --log-level debug`

#### Frontend
- Usar DevTools del navegador
- Consola de errores: F12 → Console

## Estructura de Datos

### Datos Fake
La aplicación usa datos simulados generados dinámicamente. Para usar datos reales:

1. Implementar conectores a APIs de NASA
2. Configurar base de datos para cache
3. Actualizar `mock_weather_data.py` con datos reales

### Formato de Fechas
- Input: "MM-DD" (ej: "07-15" para 15 de julio)
- Los datos históricos cubren los últimos 30 años por defecto