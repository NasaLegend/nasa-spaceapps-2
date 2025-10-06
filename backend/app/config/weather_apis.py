# Configuración para APIs de datos meteorológicos reales

# OpenWeatherMap API (requiere registro gratuito)
# Obtener API key en: https://openweathermap.org/api
OPENWEATHER_API_KEY = "tu_api_key_aqui"

# NASA POWER API (gratuita, sin API key requerida)
# Documentación: https://power.larc.nasa.gov/docs/
NASA_POWER_ENABLED = True

# Configuración de cache
CACHE_DURATION_DAYS = 30  # Días para mantener datos en cache
MAX_CACHE_SIZE_MB = 500   # Tamaño máximo del cache en MB

# Configuración de modelos ML
MODEL_RETRAIN_THRESHOLD = 100  # Mínimo de datos nuevos para reentrenar
MODEL_ACCURACY_THRESHOLD = 0.7  # Precisión mínima aceptable

# Configuración de APIs alternativas
APIS_CONFIG = {
    "nasa_power": {
        "enabled": True,
        "priority": 1,
        "rate_limit": 10,  # requests per minute
        "timeout": 30,
        "retry_attempts": 3
    },
    "openweather": {
        "enabled": False,  # Requiere API key
        "priority": 2,
        "rate_limit": 60,
        "timeout": 10,
        "retry_attempts": 2
    }
}

# Configuración de entrenamiento de modelos
ML_CONFIG = {
    "min_data_points": 30,
    "test_size": 0.2,
    "random_state": 42,
    "cross_validation_folds": 5,
    "feature_selection": True,
    "hyperparameter_tuning": False  # Deshabilitado por velocidad
}

# Configuración de logging
LOGGING_CONFIG = {
    "level": "INFO",
    "file": "weather_ml.log",
    "max_file_size_mb": 10,
    "backup_count": 3
}