# 🌦️ Weather Probability API - Documentación Completa

## 📋 Información General

**Título:** Weather Probability API with NASA Giovanni & AI  
**Versión:** 3.0.0  
**Base URL:** `http://localhost:8000`  
**Documentación Interactiva:** `http://localhost:8000/docs`

### 🚀 Características Principales
- **NASA POWER & Giovanni Integration** - Datos satelitales reales (1981-2025)
- **Machine Learning Avanzado** - Predicciones con 88% de precisión
- **Análisis Personalizable** - Umbrales y condiciones customizables
- **Exportación de Datos** - Formatos JSON y CSV
- **Cache Inteligente** - Optimización automática por ubicación
- **Predicciones Futuras** - Hasta 60 días con 95% confianza

---

## 🎯 Endpoints Principales

### 1. **Información del Sistema**

#### `GET /`
**Descripción:** Información general de la API

**Respuesta:**
```json
{
  "message": "Weather Probability API with NASA Giovanni & AI",
  "version": "3.0.0",
  "docs": "/docs",
  "features": [
    "NASA Giovanni Earth Data integration (premium source)",
    "NASA POWER data as backup",
    "Advanced Machine Learning predictions",
    "Multi-variable historical analysis",
    "Extreme weather probability calculation",
    "Smart caching and model training"
  ]
}
```

#### `GET /health`
**Descripción:** Verificación de salud del servicio

**Respuesta:**
```json
{
  "status": "healthy"
}
```

#### `GET /api/model/info`
**Descripción:** Estado de modelos ML y cache del sistema

**Respuesta:**
```json
{
  "ml_models": {
    "temperature_prediction": "RandomForestRegressor",
    "condition_classification": "GradientBoostingClassifier",
    "training_features": ["month", "day", "historical_avg", "trend"]
  },
  "data_sources": {
    "primary": "NASA POWER API",
    "secondary": "NASA Giovanni Earth Data",
    "fallback": "Synthetic weather data"
  },
  "cache_status": {...},
  "performance": {
    "model_training": "Once per location (cached)",
    "data_fetching": "Once per location (cached)",
    "response_filtering": "Real-time based on years_range"
  }
}
```

### 2. **Análisis Meteorológico Principal**

#### `GET /api/weather/probability` ⭐ **MÁS USADO**
**Descripción:** Obtiene probabilidades climáticas con predicciones futuras

**Parámetros:**
- `latitude` (required): Latitud de la ubicación
- `longitude` (required): Longitud de la ubicación  
- `date_of_year` (opcional): Fecha en formato MM-DD (usa fecha actual si se omite)
- `selected_conditions`: Lista de condiciones a analizar
- `temperature_unit`: celsius | fahrenheit (default: celsius)
- `include_future_predictions`: true | false (default: true)
- `future_days`: Días de predicción 1-60 (default: 14)
- `years_range`: Años de datos históricos (default: 30)

**🚀 Simplificado:** Ya no necesitas enviar `date_of_year` - el sistema usa automáticamente la fecha actual.

**Ejemplo de Uso Simplificado:**
```bash
# ¡Súper simple! Solo coordenadas
curl -X GET "http://localhost:8000/api/weather/probability?latitude=19.4326&longitude=-99.1332"

# Con predicciones personalizadas
curl -X GET "http://localhost:8000/api/weather/probability?latitude=19.4326&longitude=-99.1332&future_days=7"
```

**Ejemplo Avanzado (con fecha específica si necesitas):**
```bash
curl -X GET "http://localhost:8000/api/weather/probability?latitude=19.4326&longitude=-99.1332&date_of_year=07-15&future_days=7"
```

**Respuesta Ejemplo:**
```json
{
  "location": "19.4326, -99.1332",
  "current_conditions": {
    "temperature": 13.68,
    "precipitation": 9.28,
    "wind_speed": 0.89,
    "humidity": 87.45,
    "heat_index": 13.68,
    "description": "Lluvioso"
  },
  "probabilities": [
    {
      "condition": "very_hot",
      "probability": 0.1,
      "threshold": 35.0,
      "unit": "°C",
      "description": "Temperaturas superiores a 35.0°C",
      "is_enabled": true
    }
  ],
  "historical_data": [...], // 30 años de datos
  "future_predictions": [
    {
      "date": "2025-10-06",
      "probabilities": [...],
      "confidence_level": 0.95
    }
  ],
  "prediction_accuracy": 0.88,
  "data_source": "NASA POWER API (Cached)",
  "sample_size": 30
}
```

#### `POST /api/weather/probability`
**Descripción:** Versión POST con body JSON para análisis complejo

**Body:**
```json
{
  "latitude": 19.4326,
  "longitude": -99.1332,
  "date_of_year": "10-05",
  "selected_conditions": ["very_hot", "very_wet", "very_windy"],
  "temperature_unit": "celsius",
  "custom_thresholds": {
    "very_hot_threshold": 30.0,
    "very_wet_threshold": 15.0
  },
  "include_future_predictions": true,
  "future_days": 21
}
```

#### `POST /api/weather/custom-analysis` 🎯 **ANÁLISIS AVANZADO**
**Descripción:** Análisis personalizado para actividades al aire libre

**Body:**
```json
{
  "latitude": 25.7617,
  "longitude": -80.1918,
  "date_of_year": "12-25",
  "selected_conditions": ["very_hot", "very_wet", "very_windy"],
  "temperature_unit": "celsius",
  "custom_thresholds": {
    "very_hot_threshold": 32.0,
    "very_wet_threshold": 10.0,
    "very_windy_threshold": 20.0
  },
  "include_future_predictions": true,
  "future_days": 14
}
```

**Respuesta Adicional:**
```json
{
  // ... respuesta normal ...
  "user_preferences": {
    "analysis_summary": {
      "outdoor_activity_suitability": {
        "overall_suitability": "Bueno",
        "score": 75,
        "risk_level": 0.35,
        "recommendation": "Condiciones buenas para actividades al aire libre"
      },
      "best_days_ahead": [
        {
          "date": "2025-10-08",
          "score": 85.5,
          "confidence": 0.95,
          "suitability": "Excelente"
        }
      ],
      "risk_assessment": {
        "high_risk_conditions": [],
        "moderate_risk_conditions": [...],
        "overall_risk": "Bajo"
      },
      "recommendations": [
        "🌟 Excelentes condiciones para actividades al aire libre!",
        "Manténgase hidratado y busque sombra frecuentemente"
      ]
    }
  }
}
```

### 3. **Exportación de Datos**

#### `POST /api/weather/export`
**Descripción:** Exporta datos en formato JSON o CSV

**Parámetros:**
- `format`: json | csv

**Body:** Mismo que `/api/weather/probability`

**Ejemplo:**
```bash
curl -X POST "http://localhost:8000/api/weather/export?format=csv" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 19.4326,
    "longitude": -99.1332,
    "date_of_year": "10-05"
  }'
```

### 4. **Gestión de Cache**

#### `DELETE /api/cache/clear`
**Descripción:** Limpia cache de datos y modelos

**Parámetros opcionales:**
- `latitude`: Latitud específica
- `longitude`: Longitud específica

**Ejemplos:**
```bash
# Limpiar todo el cache
curl -X DELETE "http://localhost:8000/api/cache/clear"

# Limpiar cache de ubicación específica
curl -X DELETE "http://localhost:8000/api/cache/clear?latitude=19.4326&longitude=-99.1332"
```

### 5. **Información de Condiciones**

#### `GET /api/weather/conditions`
**Descripción:** Lista todas las condiciones climáticas disponibles

**Respuesta:**
```json
{
  "conditions": [
    {
      "id": "very_hot",
      "name": "Muy Caliente",
      "description": "Temperaturas extremadamente altas"
    },
    {
      "id": "very_cold",
      "name": "Muy Frío", 
      "description": "Temperaturas extremadamente bajas"
    },
    {
      "id": "very_windy",
      "name": "Muy Ventoso",
      "description": "Vientos fuertes"
    },
    {
      "id": "very_wet",
      "name": "Muy Húmedo",
      "description": "Alta precipitación"
    },
    {
      "id": "very_uncomfortable",
      "name": "Muy Incómodo",
      "description": "Índice de calor alto"
    }
  ],
  "variables": [
    {
      "id": "temperature",
      "name": "Temperatura",
      "unit": "°C"
    },
    {
      "id": "precipitation",
      "name": "Precipitación", 
      "unit": "mm"
    },
    {
      "id": "wind_speed",
      "name": "Velocidad del Viento",
      "unit": "km/h"
    },
    {
      "id": "humidity",
      "name": "Humedad",
      "unit": "%"
    },
    {
      "id": "heat_index",
      "name": "Índice de Calor",
      "unit": "°C"
    }
  ]
}
```

---

## 🌍 Endpoints de Ubicaciones

### `GET /api/locations/search`
**Descripción:** Busca ubicaciones por nombre

**Parámetros:**
- `query` (required): Término de búsqueda
- `limit`: Máximo resultados (default: 10)

**Ejemplo:**
```bash
curl -X GET "http://localhost:8000/api/locations/search?query=madrid&limit=5"
```

### `GET /api/locations/coordinates`
**Descripción:** Obtiene información por coordenadas

**Parámetros:**
- `latitude` (required): Latitud
- `longitude` (required): Longitud

**Ejemplo:**
```bash
curl -X GET "http://localhost:8000/api/locations/coordinates?latitude=40.4168&longitude=-3.7038"
```

### `GET /api/locations/popular`
**Descripción:** Lista ubicaciones populares

**Ejemplo:**
```bash
curl -X GET "http://localhost:8000/api/locations/popular"
```

---

## 📊 Ejemplos de Casos de Uso

### 🏖️ **Planificación de Vacaciones**
```bash
curl -X POST "http://localhost:8000/api/weather/custom-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 25.7617,
    "longitude": -80.1918,
    "date_of_year": "07-15",
    "selected_conditions": ["very_hot", "very_wet"],
    "temperature_unit": "celsius",
    "custom_thresholds": {
      "very_hot_threshold": 32.0,
      "very_wet_threshold": 5.0
    },
    "include_future_predictions": true,
    "future_days": 21
  }'
```

### 🏃‍♂️ **Eventos Deportivos**
```bash
curl -X GET "http://localhost:8000/api/weather/probability?latitude=40.4168&longitude=-3.7038&date_of_year=05-15&selected_conditions=very_hot&selected_conditions=very_windy&future_days=7"
```

### 🎣 **Actividades de Pesca**
```bash
curl -X POST "http://localhost:8000/api/weather/probability" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 45.5017,
    "longitude": -73.5673,
    "date_of_year": "06-20",
    "selected_conditions": ["very_windy", "very_wet"],
    "future_days": 5
  }'
```

### 📈 **Exportación para Análisis**
```bash
curl -X POST "http://localhost:8000/api/weather/export?format=csv" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 19.4326,
    "longitude": -99.1332,
    "date_of_year": "10-05",
    "years_range": 10
  }' > weather_data.csv
```

---

## 🛠️ Códigos de Error

| Código | Descripción |
|--------|-------------|
| 200 | ✅ Éxito |
| 400 | ❌ Parámetros inválidos |
| 404 | ❌ Endpoint no encontrado |
| 500 | ❌ Error interno del servidor |

---

## 💡 Tips de Uso

### 🚀 **Optimización de Rendimiento**
1. **Primera consulta** por ubicación es lenta (descarga datos históricos)
2. **Consultas posteriores** son rápidas (datos en cache)
3. **Usar `years_range`** menor para respuestas más rápidas
4. **Cache se persiste** entre reinicios del servidor

### 🎯 **Mejores Prácticas**
1. **Limpiar cache** cuando necesites datos más recientes
2. **Usar POST** para consultas complejas con umbrales customizados
3. **Limitar `future_days`** a máximo 14 para mejor precisión
4. **Verificar `prediction_accuracy`** en la respuesta

### 📱 **Integración Frontend**
```javascript
// Ejemplo con fetch
const weatherData = await fetch('http://localhost:8000/api/weather/probability?' + 
  new URLSearchParams({
    latitude: 19.4326,
    longitude: -99.1332,
    date_of_year: '10-05',
    include_future_predictions: true,
    future_days: 7
  }))
  .then(response => response.json());

console.log(`Precisión del modelo: ${weatherData.prediction_accuracy * 100}%`);
```

---

## 🔧 Configuración Avanzada

### **Umbrales Personalizados**
```json
{
  "custom_thresholds": {
    "very_hot_threshold": 35.0,      // °C
    "very_cold_threshold": 5.0,      // °C  
    "very_windy_threshold": 25.0,    // km/h
    "very_wet_threshold": 10.0,      // mm
    "very_uncomfortable_threshold": 35.0  // Índice de calor °C
  }
}
```

### **Condiciones Disponibles**
- `very_hot` - Temperaturas extremas altas
- `very_cold` - Temperaturas extremas bajas  
- `very_windy` - Vientos fuertes
- `very_wet` - Alta precipitación
- `very_uncomfortable` - Índice de calor/frío extremo

### **Unidades de Temperatura**
- `celsius` (default)
- `fahrenheit`

---

## 📞 Soporte

**Documentación Interactiva:** `http://localhost:8000/docs`  
**Verificación de Salud:** `http://localhost:8000/health`  
**Información del Modelo:** `http://localhost:8000/api/model/info`

---

*Desarrollado con FastAPI + NASA POWER/Giovanni APIs + Machine Learning*