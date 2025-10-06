from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

class WeatherConditionType(str, Enum):
    VERY_HOT = "very_hot"
    VERY_COLD = "very_cold"
    VERY_WINDY = "very_windy"
    VERY_WET = "very_wet"
    VERY_UNCOMFORTABLE = "very_uncomfortable"

class WeatherVariable(str, Enum):
    TEMPERATURE = "temperature"
    PRECIPITATION = "precipitation"
    WIND_SPEED = "wind_speed"
    HUMIDITY = "humidity"
    HEAT_INDEX = "heat_index"

class TemperatureUnit(str, Enum):
    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"

class WeatherCondition(BaseModel):
    """Condiciones meteorológicas actuales"""
    temperature: float
    precipitation: float
    wind_speed: float
    humidity: float
    heat_index: float
    description: str

class WeatherDataPoint(BaseModel):
    date: datetime
    temperature: float
    precipitation: float
    wind_speed: float
    humidity: float
    heat_index: Optional[float] = None

class WeatherProbability(BaseModel):
    condition: str
    probability: float  # 0.0 to 1.0
    threshold: float
    unit: str
    description: Optional[str] = ""
    is_enabled: bool = True  # Nuevo: indica si el usuario quiere ver esta condición

class CustomThresholds(BaseModel):
    """Umbrales personalizados definidos por el usuario"""
    very_hot_threshold: Optional[float] = None
    very_cold_threshold: Optional[float] = None
    very_windy_threshold: Optional[float] = None
    very_wet_threshold: Optional[float] = None
    very_uncomfortable_threshold: Optional[float] = None

class WeatherQuery(BaseModel):
    latitude: float
    longitude: float
    date_of_year: Optional[str] = None  # Format: "MM-DD", usa fecha actual si no se especifica
    
    # Nuevos parámetros personalizables
    selected_conditions: List[WeatherConditionType] = [
        WeatherConditionType.VERY_HOT,
        WeatherConditionType.VERY_COLD,
        WeatherConditionType.VERY_WINDY,
        WeatherConditionType.VERY_WET,
        WeatherConditionType.VERY_UNCOMFORTABLE
    ]
    temperature_unit: TemperatureUnit = TemperatureUnit.CELSIUS
    custom_thresholds: Optional[CustomThresholds] = None
    
    # Predicciones futuras
    include_future_predictions: bool = True
    future_days: int = 14  # 2 semanas por defecto, máximo 60 días
    
    # Configuración existente
    variables: Optional[List[WeatherVariable]] = None
    years_range: Optional[int] = 30

class FuturePrediction(BaseModel):
    """Predicción para una fecha futura específica"""
    date: date
    probabilities: List[WeatherProbability]
    confidence_level: float  # 0.0 to 1.0

class WeatherResponse(BaseModel):
    location: str
    current_conditions: WeatherCondition
    probabilities: List[WeatherProbability]
    historical_data: List[WeatherDataPoint]
    prediction_accuracy: float
    data_source: str
    sample_size: int
    statistics: dict
    
    # Nuevos campos para predicciones futuras
    future_predictions: Optional[List[FuturePrediction]] = None
    temperature_unit: TemperatureUnit = TemperatureUnit.CELSIUS
    query_date: date
    
    # Información personalizada
    user_preferences: dict = {}