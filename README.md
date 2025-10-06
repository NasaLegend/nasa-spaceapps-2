# 🌤️ Weather Probability App - NASA Challenge

Una aplicación web avanzada que utiliza datos meteorológicos de la NASA para predecir probabilidades climáticas y planificar eventos al aire libre.

## 🚀 Descripción del Proyecto

Este proyecto fue desarrollado como respuesta al **NASA Space Apps Challenge**, aprovechando la API **NASA POWER** para proporcionar análisis meteorológicos precisos basados en hasta 50 años de datos históricos.

### ✨ Características Principales

- 🌡️ **Análisis Predictivo**: Probabilidades de condiciones extremas (calor, frío, viento, lluvia)
- 🤖 **Machine Learning**: 5 modelos de IA entrenados (RandomForest, GradientBoosting)
- 📍 **Selector Global**: Cualquier ubicación mundial con coordenadas precisas
- 📊 **Visualizaciones**: Gráficos interactivos y métricas detalladas
- � **Exportación**: Datos en JSON/CSV para análisis posterior
- 🎯 **Eventos al Aire Libre**: Modo especializado para planificación de eventos

### 🏆 Solución al Desafío NASA

La aplicación resuelve el problema de **predicción meteorológica para eventos críticos** utilizando:
- Datos satelitales de NASA POWER (1981-2025)
- Algoritmos de ML con métricas profesionales (R², F1-Score, Cross-Validation)
- Análisis de 30+ años de historia para eventos al aire libre
- Predicciones futuras hasta 14 días

## 🛠️ Tecnologías

### Backend (Python)
- **FastAPI**: API REST moderna y rápida
- **NASA POWER API**: Datos meteorológicos satelitales
- **Scikit-learn**: 5 modelos de Machine Learning
- **Pandas/NumPy**: Procesamiento de datos meteorológicos
- **Aiohttp**: Requests asíncronos a NASA

### Frontend (React)
- **React 18**: Interfaz moderna y responsiva
- **Chart.js**: Visualizaciones meteorológicas interactivas
- **CSS Personalizado**: Tema espacial inspirado en NASA
- **Componentes Modulares**: Arquitectura escalable

### Inteligencia Artificial
- **RandomForestRegressor**: Predicción de temperatura, viento, humedad
- **GradientBoostingClassifier**: Clasificación de precipitación y condiciones extremas
- **GridSearchCV**: Optimización automática de hiperparámetros
- **Cross-Validation**: Validación robusta con 5-fold CV

## 🚀 Instalación Rápida

### Prerrequisitos
- Python 3.9+
- Node.js 16+
- npm o yarn

### 1. Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
npm start
```

### 3. Acceso
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs

## 📊 API Endpoints

### Predicciones Meteorológicas
- `GET /api/weather/probability/{lat}/{lng}` - Probabilidades para ubicación
- `POST /api/weather/probability` - Análisis personalizado
- `GET /api/weather/model-metrics/{lat}/{lng}` - Métricas de modelos ML

### Análisis Personalizado
- `GET /api/weather/analysis/{lat}/{lng}` - Análisis filtrado por métricas

## 🎯 Casos de Uso

### 🏕️ Eventos al Aire Libre
- **Bodas**: Probabilidad de lluvia y viento fuerte
- **Conciertos**: Análisis de confort térmico y condiciones extremas
- **Deportes**: Predicciones de temperatura y humedad
- **Festivales**: Planificación con 30 años de datos históricos

### 📊 Análisis Básico
- **Investigación**: Tendencias climáticas históricas
- **Agricultura**: Patrones de precipitación y temperatura
- **Turismo**: Mejores épocas para viajar

## 🧠 Modelos de IA

La aplicación incluye 5 modelos especializados:

1. **Temperature Predictor** (R² > 0.98): Predicción de temperatura
2. **Precipitation Classifier** (F1 > 0.85): Categorías de lluvia (seco, ligero, moderado, fuerte, extremo)
3. **Wind Predictor** (R² > 0.92): Velocidad del viento
4. **Humidity Predictor** (R² > 0.89): Humedad relativa
5. **Extreme Conditions Classifier** (F1 > 0.78): 6 tipos de condiciones extremas

### Métricas de Rendimiento
- **Cross-Validation**: 5-fold para robustez
- **Hyperparameter Optimization**: GridSearchCV automático
- **Feature Engineering**: Variables geográficas y estacionales
- **Model Persistence**: Modelos guardados por ubicación

## 📁 Estructura del Proyecto

```
weather-probability-app/
├── backend/
│   ├── app/
│   │   ├── api/weather.py          # Endpoints de la API
│   │   ├── data/real_weather_data.py # Servicio NASA + ML
│   │   ├── services/weather_service.py # Lógica de negocio
│   │   └── models/weather.py       # Modelos de datos
│   └── main.py                     # Aplicación FastAPI
├── frontend/
│   ├── src/
│   │   ├── components/             # Componentes React
│   │   ├── services/              # APIs y servicios
│   │   └── utils/                 # Utilidades
│   └── public/
└── README.md
```

## 🌟 Funcionalidades Destacadas

### 🎯 Personalización Avanzada
- **Umbrales Personalizados**: Define tus propios límites de temperatura, viento, etc.
- **Métricas Seleccionables**: Elige qué variables analizar
- **Unidades Configurables**: Celsius/Fahrenheit, diferentes escalas
- **Exportación Personalizada**: JSON/CSV con configuración incluida

### 🚀 Rendimiento
- **Cache Inteligente**: Datos NASA guardados localmente
- **Modelos Persistentes**: ML models guardados por ubicación
- **Requests Asíncronos**: Múltiples años de datos en paralelo
- **Optimización Automática**: Hiperparámetros ajustados por GridSearch

## 📈 Métricas y Validación

La aplicación proporciona métricas profesionales de ML:
- **RMSE**: Error cuadrático medio para regresión
- **R² Score**: Coeficiente de determinación
- **F1-Score**: Métrica balanceada para clasificación
- **Precision/Recall**: Métricas detalladas por clase
- **Cross-Validation**: Validación cruzada 5-fold
- **Feature Importance**: Importancia de variables

## 🔗 APIs Utilizadas

- **NASA POWER**: https://power.larc.nasa.gov/api/
  - 40+ años de datos satelitales
  - Cobertura global
  - Datos diarios de alta calidad
  - Variables: temperatura, precipitación, viento, humedad

## 👥 Contribución

Este proyecto demuestra la integración exitosa de:
- ✅ Datos gubernamentales (NASA)
- ✅ Machine Learning aplicado
- ✅ Interfaz web moderna
- ✅ API RESTful robusta
- ✅ Casos de uso reales

---

**Desarrollado para NASA Space Apps Challenge 2025**  
🚀 *Utilizando datos de la NASA para resolver problemas terrestres*

## API Endpoints

- `GET /api/weather/probability` - Obtener probabilidades climáticas
- `GET /api/locations/search` - Buscar ubicaciones
- `POST /api/data/export` - Exportar datos

## Estructura del Proyecto

```
weather-probability-app/
├── backend/          # API Python (FastAPI)
├── frontend/         # React App
├── docs/            # Documentación
└── docker-compose.yml
```

## Contribuir

1. Fork el repositorio
2. Crea una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

MIT License