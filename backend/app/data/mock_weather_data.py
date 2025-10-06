import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any

# Datos fake para simular datos históricos de la NASA
class MockWeatherDataGenerator:
    def __init__(self):
        self.base_patterns = {
            # Patrones de temperatura por ubicación (aproximado)
            "temperature": {
                "tropical": {"mean": 28, "std": 5, "seasonal_amplitude": 3},
                "temperate": {"mean": 15, "std": 10, "seasonal_amplitude": 15},
                "desert": {"mean": 25, "std": 12, "seasonal_amplitude": 20},
                "arctic": {"mean": -5, "std": 8, "seasonal_amplitude": 25}
            },
            # Patrones de precipitación
            "precipitation": {
                "tropical": {"mean": 8, "std": 12, "seasonal_factor": 1.5},
                "temperate": {"mean": 3, "std": 6, "seasonal_factor": 1.2},
                "desert": {"mean": 0.5, "std": 2, "seasonal_factor": 0.8},
                "arctic": {"mean": 1, "std": 3, "seasonal_factor": 0.5}
            },
            # Patrones de viento
            "wind_speed": {
                "tropical": {"mean": 15, "std": 8},
                "temperate": {"mean": 12, "std": 6},
                "desert": {"mean": 18, "std": 10},
                "arctic": {"mean": 20, "std": 12}
            },
            # Patrones de humedad
            "humidity": {
                "tropical": {"mean": 80, "std": 15},
                "temperate": {"mean": 65, "std": 20},
                "desert": {"mean": 30, "std": 15},
                "arctic": {"mean": 70, "std": 18}
            }
        }
    
    def get_climate_zone(self, latitude: float) -> str:
        """Determina la zona climática basada en la latitud"""
        abs_lat = abs(latitude)
        if abs_lat < 23.5:
            return "tropical"
        elif abs_lat < 60:
            return "temperate"
        elif abs_lat < 70:
            return "arctic"
        else:
            return "arctic"
    
    def generate_historical_data(self, latitude: float, longitude: float, 
                               date_of_year: str, years: int = 30) -> List[Dict[str, Any]]:
        """Genera datos históricos fake para una ubicación y fecha específica"""
        climate_zone = self.get_climate_zone(latitude)
        month, day = map(int, date_of_year.split('-'))
        
        historical_data = []
        current_year = datetime.now().year
        
        for year in range(current_year - years, current_year):
            try:
                date = datetime(year, month, day)
                
                # Calcular factores estacionales
                day_of_year = date.timetuple().tm_yday
                seasonal_factor = np.sin(2 * np.pi * day_of_year / 365.25)
                
                # Temperatura con variación estacional
                temp_pattern = self.base_patterns["temperature"][climate_zone]
                temperature = (temp_pattern["mean"] + 
                             seasonal_factor * temp_pattern["seasonal_amplitude"] +
                             np.random.normal(0, temp_pattern["std"]))
                
                # Precipitación
                precip_pattern = self.base_patterns["precipitation"][climate_zone]
                precipitation = max(0, np.random.exponential(precip_pattern["mean"]) * 
                                  precip_pattern["seasonal_factor"])
                
                # Viento
                wind_pattern = self.base_patterns["wind_speed"][climate_zone]
                wind_speed = max(0, np.random.normal(wind_pattern["mean"], wind_pattern["std"]))
                
                # Humedad
                humidity_pattern = self.base_patterns["humidity"][climate_zone]
                humidity = np.clip(np.random.normal(humidity_pattern["mean"], 
                                                  humidity_pattern["std"]), 0, 100)
                
                # Índice de calor (heat index)
                heat_index = self.calculate_heat_index(temperature, humidity)
                
                historical_data.append({
                    "date": date,
                    "temperature": round(temperature, 2),
                    "precipitation": round(precipitation, 2),
                    "wind_speed": round(wind_speed, 2),
                    "humidity": round(humidity, 2),
                    "heat_index": round(heat_index, 2)
                })
                
            except ValueError:
                # Manejar fechas inválidas como 29 de febrero en años no bisiestos
                continue
        
        return historical_data
    
    def calculate_heat_index(self, temperature: float, humidity: float) -> float:
        """Calcula el índice de calor simplificado"""
        if temperature < 27:
            return temperature
        
        # Fórmula simplificada del heat index
        hi = (temperature + humidity) * 0.7 + (temperature - 20) * 0.3
        return hi
    
    def calculate_probabilities(self, historical_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calcula las probabilidades de condiciones extremas"""
        df = pd.DataFrame(historical_data)
        
        probabilities = {}
        
        # Muy caliente (temperatura > percentil 90)
        temp_threshold = np.percentile(df['temperature'], 90)
        probabilities['very_hot'] = {
            'probability': (df['temperature'] > temp_threshold).mean(),
            'threshold': temp_threshold,
            'unit': '°C'
        }
        
        # Muy frío (temperatura < percentil 10)
        cold_threshold = np.percentile(df['temperature'], 10)
        probabilities['very_cold'] = {
            'probability': (df['temperature'] < cold_threshold).mean(),
            'threshold': cold_threshold,
            'unit': '°C'
        }
        
        # Muy ventoso (viento > percentil 85)
        wind_threshold = np.percentile(df['wind_speed'], 85)
        probabilities['very_windy'] = {
            'probability': (df['wind_speed'] > wind_threshold).mean(),
            'threshold': wind_threshold,
            'unit': 'km/h'
        }
        
        # Muy húmedo (precipitación > percentil 80)
        precip_threshold = np.percentile(df['precipitation'], 80)
        probabilities['very_wet'] = {
            'probability': (df['precipitation'] > precip_threshold).mean(),
            'threshold': precip_threshold,
            'unit': 'mm'
        }
        
        # Muy incómodo (heat index > percentil 85)
        heat_threshold = np.percentile(df['heat_index'], 85)
        probabilities['very_uncomfortable'] = {
            'probability': (df['heat_index'] > heat_threshold).mean(),
            'threshold': heat_threshold,
            'unit': '°C'
        }
        
        return probabilities

# Instancia global para usar en los servicios
mock_data_generator = MockWeatherDataGenerator()