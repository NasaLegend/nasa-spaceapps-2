from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import weather, locations
from app.core.config import settings
from app.data.real_weather_data import real_weather_service
from app.data.giovanni_nasa_data import giovanni_weather_service

# Crear instancia de FastAPI
app = FastAPI(
    title="Weather Probability API with NASA Giovanni & AI",
    description="API para consultar probabilidades de condiciones climáticas usando datos reales de NASA Giovanni y modelos de Machine Learning avanzados",
    version="3.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En desarrollo permitir todo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(weather.router, prefix="/api/weather", tags=["weather"])
app.include_router(locations.router, prefix="/api/locations", tags=["locations"])

@app.get("/")
async def root():
    return {
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

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/model/info")
async def model_info():
    """Información sobre los modelos de ML y estado del sistema"""
    from app.services.weather_service import weather_service
    
    cache_info = weather_service.get_cache_info()
    
    return {
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
        "cache_status": cache_info,
        "performance": {
            "model_training": "Once per location (cached)",
            "data_fetching": "Once per location (cached)",
            "response_filtering": "Real-time based on years_range"
        }
    }

@app.delete("/api/cache/clear")
async def clear_cache(latitude: float = None, longitude: float = None):
    """Limpiar cache de datos históricos y modelos entrenados"""
    from app.services.weather_service import weather_service
    
    weather_service.clear_cache(latitude, longitude)
    
    if latitude is not None and longitude is not None:
        return {"message": f"Cache cleared for location {latitude}, {longitude}"}
    else:
        return {"message": "All cache cleared successfully"}
    # Modelos Giovanni
    giovanni_models_status = {}
    for model_name, model in giovanni_weather_service.models.items():
        giovanni_models_status[model_name] = {
            "trained": model is not None,
            "type": type(model).__name__ if model else None,
            "source": "Giovanni NASA"
        }
    
    # Modelos NASA POWER
    power_models_status = {}
    for model_name, model in real_weather_service.models.items():
        power_models_status[model_name] = {
            "trained": model is not None,
            "type": type(model).__name__ if model else None,
            "source": "NASA POWER"
        }
    
    return {
        "models": {
            "giovanni_models": giovanni_models_status,
            "power_models": power_models_status
        },
        "data_sources": {
            "primary": {
                "name": "NASA POWER",
                "description": "Datos de satélite y observación terrestre confiables",
                "url": "https://power.larc.nasa.gov/api",
                "temporal_range": "1981-presente",
                "spatial_coverage": "Global",
                "authentication": "No requerida"
            },
            "secondary": {
                "name": "NASA Giovanni Earth Data",
                "description": "Datos de observación terrestre de premium (requiere autenticación)",
                "url": "https://api.giovanni.earthdata.nasa.gov",
                "variables": list(giovanni_weather_service.variables.keys()),
                "temporal_range": "2000-presente",
                "spatial_coverage": "Global",
                "authentication": "OAuth requerida"
            },
            "fallback": {
                "name": "Synthetic Data",
                "description": "Datos sintéticos basados en patrones climáticos"
            }
        },
        "cache_info": {
            "giovanni_cache_dir": str(giovanni_weather_service.data_cache_dir),
            "giovanni_models_dir": str(giovanni_weather_service.models_dir),
            "power_cache_dir": str(real_weather_service.data_cache_dir),
            "power_models_dir": str(real_weather_service.models_dir)
        },
        "ml_features": [
            "Multi-source data integration",
            "Advanced temporal feature engineering",
            "Geospatial climate zone analysis",
            "Ensemble model predictions",
            "Automatic model retraining",
            "Quality-based data source selection"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)