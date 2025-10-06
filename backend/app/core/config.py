from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Weather Probability API"
    VERSION: str = "3.0"
    API_V1_STR: str = "/api"
    
    # CORS
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3001",
        "*"  # Para desarrollo - remover en producción
    ]
    
    # Database (si necesitamos una más adelante)
    DATABASE_URL: str = "sqlite:///./weather_app.db"
    
    # Configuración de la aplicación
    DEBUG: bool = True
    USE_REAL_DATA: bool = True
    
    # APIs de datos meteorológicos
    NASA_POWER_ENABLED: bool = True
    GIOVANNI_ENABLED: bool = False
    
    # Configuración de ML
    ML_ENABLED: bool = True
    CACHE_ENABLED: bool = True
    
    class Config:
        env_file = None  # Desactivar .env temporalmente
        extra = "ignore"  # Ignorar variables adicionales

settings = Settings()