# Weather Probability App - Versión 2.0 con IA y Datos Reales

Esta aplicación ahora utiliza **datos reales de la NASA** y **modelos de Machine Learning** para proporcionar predicciones meteorológicas precisas basadas en datos históricos.

## 🚀 Nuevas Funcionalidades

### 🌍 Datos Reales de NASA POWER
- **Fuente**: NASA POWER API - Datos meteorológicos globales
- **Cobertura**: Datos históricos desde 1981 hasta la actualidad
- **Variables**: Temperatura, precipitación, velocidad del viento, humedad
- **Resolución**: Datos diarios para cualquier ubicación del mundo

### 🤖 Inteligencia Artificial
- **Modelos ML**: Random Forest y Gradient Boosting
- **Predicciones**: Probabilidades de condiciones extremas
- **Entrenamiento automático**: Los modelos se entrenan con datos reales
- **Fallback inteligente**: Datos sintéticos si no hay datos reales disponibles

### 📊 Análisis Avanzado
- **Condiciones analizadas**:
  - 🔥 Muy caliente (>90% percentil histórico)
  - ❄️ Muy frío (<10% percentil histórico)  
  - 💨 Muy ventoso (>85% percentil histórico)
  - 🌧️ Muy húmedo (>80% percentil histórico)
  - 🥵 Muy incómodo (índice de calor >85% percentil)

## 🛠️ Configuración e Instalación

### Opción 1: Script Automático (Recomendado)
```bash
# En Windows
python setup_real_data.py

# En Linux/Mac
chmod +x setup_real_data.sh
./setup_real_data.sh
```

### Opción 2: Instalación Manual
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Crear directorios
mkdir data_cache models logs

# 3. Configurar variables de entorno
# Crear archivo .env con las configuraciones necesarias

# 4. Ejecutar servidor
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📡 APIs y Fuentes de Datos

### NASA POWER API
- **URL**: https://power.larc.nasa.gov/api/
- **Acceso**: Gratuito, sin API key requerida
- **Límites**: 10 requests/minuto (implementado rate limiting)
- **Datos**: 40+ años de observaciones meteorológicas globales

### OpenWeatherMap (Opcional)
- **URL**: https://openweathermap.org/api
- **Acceso**: Requiere API key gratuita
- **Uso**: Datos adicionales y validación

## 🔧 Configuración

### Variables de Entorno (.env)
```env
# Aplicación
DEBUG=True
USE_REAL_DATA=True

# APIs
OPENWEATHER_API_KEY=tu_api_key_aqui
NASA_POWER_ENABLED=True

# Machine Learning
ML_ENABLED=True
AUTO_RETRAIN=True

# Logging
LOG_LEVEL=INFO
```

## 📈 Modelos de Machine Learning

### Modelos Implementados
1. **Predictor de Temperatura**: Random Forest Regressor
2. **Clasificador de Precipitación**: Gradient Boosting Classifier  
3. **Predictor de Viento**: Random Forest Regressor
4. **Predictor de Humedad**: Random Forest Regressor
5. **Clasificador de Condiciones**: Multi-class classifier

### Features Utilizadas
- Coordenadas geográficas (lat/lon)
- Distancia al ecuador
- Factor costero
- Día del año y factores estacionales
- Variables meteorológicas históricas
- Tendencias temporales

### Entrenamiento
- **Automático**: Los modelos se reentrenan con nuevos datos
- **Validación**: Cross-validation y métricas de precisión
- **Persistencia**: Modelos guardados en disco para reutilización

## 🗂️ Estructura de Datos

### Cache Inteligente
```
data_cache/
├── weather_data_[lat]_[lon]_[year_start]_[year_end].pkl
├── location_metadata.json
└── cache_index.json
```

### Modelos Entrenados
```
models/
├── temperature_predictor.pkl
├── precipitation_classifier.pkl
├── wind_predictor.pkl
├── humidity_predictor.pkl
├── condition_classifier.pkl
└── scalers.pkl
```

## 🔍 Endpoints Disponibles

### Datos Meteorológicos
- `POST /api/weather/probabilities` - Obtener probabilidades
- `POST /api/weather/export` - Exportar datos (JSON/CSV)

### Información del Sistema
- `GET /api/model/info` - Estado de modelos ML
- `GET /health` - Estado del servidor
- `GET /` - Información general

### Ejemplo de Respuesta
```json
{
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "data_source": "real_nasa_power",
    "data_points": 150,
    "years_analyzed": 30
  },
  "probabilities": [
    {
      "condition": "very_hot",
      "probability": 0.23,
      "threshold_value": 32.5,
      "unit": "°C"
    }
  ]
}
```

## 🚀 Uso del Sistema

### 1. Datos Reales Automáticos
El sistema automáticamente:
- Obtiene datos de NASA POWER para la ubicación solicitada
- Entrena modelos ML con los datos históricos
- Calcula probabilidades basadas en análisis estadístico y ML
- Guarda resultados en cache para consultas futuras

### 2. Fallback Inteligente
Si no hay datos reales disponibles:
- Utiliza datos sintéticos basados en patrones climáticos
- Mantiene funcionalidad completa
- Indica claramente la fuente de datos

### 3. Optimizaciones
- **Cache**: Evita descargas repetidas
- **Rate Limiting**: Respeta límites de APIs
- **Compresión**: Datos eficientemente almacenados
- **Async**: Operaciones no bloqueantes

## 📊 Métricas y Monitoreo

### Logs del Sistema
```
logs/
├── weather_ml.log      # Logs de ML y datos
├── api_requests.log    # Logs de API calls
└── error.log          # Logs de errores
```

### Métricas Disponibles
- Precisión de modelos ML
- Tiempo de respuesta de APIs
- Uso de cache
- Cobertura de datos reales

## 🔮 Próximas Mejoras

- [ ] Integración con más fuentes de datos (ECMWF, NOAA)
- [ ] Modelos de Deep Learning (LSTM, CNN)
- [ ] Predicciones de cambio climático
- [ ] API de alertas meteorológicas
- [ ] Dashboard de métricas en tiempo real
- [ ] Soporte para datos de satélite

## 🐛 Troubleshooting

### Problemas Comunes

1. **Error de conexión NASA POWER**
   - Verificar conexión a internet
   - Comprobar logs en `logs/weather_ml.log`
   - El sistema automáticamente usa fallback

2. **Modelos no entrenan**
   - Verificar que hay suficientes datos (mínimo 10 puntos)
   - Revisar logs de ML
   - Verificar permisos de escritura en `models/`

3. **Cache corrupto**
   - Eliminar archivos en `data_cache/`
   - Reiniciar servidor

### Logs de Debug
```bash
# Ver logs en tiempo real
tail -f logs/weather_ml.log

# Verificar estado de modelos
curl http://localhost:8000/api/model/info
```

## 📞 Soporte

Para problemas o sugerencias:
1. Revisar logs del sistema
2. Verificar configuración en `.env`
3. Comprobar conectividad a APIs
4. Consultar documentación en `/docs`

---

**¡Disfruta de predicciones meteorológicas precisas con datos reales de la NASA y Machine Learning!** 🌤️🤖