import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
import os
from pathlib import Path
import pickle
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, mean_squared_error
import warnings
import urllib.parse
warnings.filterwarnings('ignore')

class GiovanniNASADataService:
    def __init__(self):
        self.data_cache_dir = Path("data_cache")
        self.models_dir = Path("models")
        self.data_cache_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        
        # Giovanni NASA API configuration
        self.giovanni_base_url = "https://api.giovanni.earthdata.nasa.gov"
        
        # Variables meteorológicas disponibles en Giovanni
        self.variables = {
            "temperature": {
                "dataset": "M2T1NXSLV_5_12_4_T2M",  # Temperatura a 2m
                "giovanni_name": "T2M"
            },
            "precipitation": {
                "dataset": "M2T1NXFLX_5_12_4_PRECTOTCORR",  # Precipitación total corregida
                "giovanni_name": "PRECTOTCORR"
            },
            "wind_speed": {
                "dataset": "M2T1NXSLV_5_12_4_U10M",  # Viento U a 10m
                "giovanni_name": "U10M"
            },
            "wind_speed_v": {
                "dataset": "M2T1NXSLV_5_12_4_V10M",  # Viento V a 10m
                "giovanni_name": "V10M"
            },
            "humidity": {
                "dataset": "M2T1NXSLV_5_12_4_QV2M",  # Humedad específica a 2m
                "giovanni_name": "QV2M"
            }
        }
        
        # Modelos de ML
        self.models = {
            'temperature_predictor': None,
            'precipitation_classifier': None,
            'wind_predictor': None,
            'humidity_predictor': None,
            'condition_classifier': None
        }
        
        self.scalers = {
            'features': StandardScaler(),
            'targets': {}
        }
        
        # Cargar modelos si existen
        self.load_trained_models()
    
    def build_giovanni_url(self, variable: str, location: tuple, time_range: tuple, endpoint: str = "timeseries") -> str:
        """
        Construye la URL para Giovanni API basándose en la estructura mostrada en la imagen
        """
        lat, lon = location
        start_time, end_time = time_range
        
        # Usar proxy-timeseries para acceso desde navegador
        if endpoint == "proxy-timeseries":
            base_url = f"{self.giovanni_base_url}/proxy-timeseries"
            params = {
                "data": variable,
                "version": "5.12.4",
                "location": f"[{lat},{lon}]",
                "time": f"{start_time}T00:00:00/{end_time}T07:30:00"
            }
        else:
            # Usar timeseries estándar con encoding URL
            base_url = f"{self.giovanni_base_url}/timeseries"
            params = {
                "data": variable,
                "version": "5.12.4",
                "location": f"%5B{lat}%2C{lon}%5D",  # URL encoded [lat,lon]
                "time": f"{start_time}T00%3A00%3A00%2F{end_time}T07%3A30%3A00"  # URL encoded time
            }
        
        # Construir URL completa
        url_parts = []
        for key, value in params.items():
            url_parts.append(f"{key}={value}")
        
        full_url = f"{base_url}?" + "&".join(url_parts)
        return full_url
    
    async def fetch_giovanni_data(self, variable: str, latitude: float, longitude: float, 
                                 start_date: str, end_date: str) -> Optional[Dict]:
        """
        Obtiene datos de Giovanni NASA API
        """
        try:
            url = self.build_giovanni_url(
                variable=variable,
                location=(latitude, longitude),
                time_range=(start_date, end_date),
                endpoint="proxy-timeseries"
            )
            
            print(f"Fetching from Giovanni: {url}")
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
                headers = {
                    'User-Agent': 'WeatherProbabilityApp/2.0',
                    'Accept': 'application/json, text/plain, */*'
                }
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self.process_giovanni_data(data, variable)
                    else:
                        print(f"Error fetching Giovanni data: {response.status}")
                        error_text = await response.text()
                        print(f"Error details: {error_text}")
                        return None
                        
        except Exception as e:
            print(f"Error in Giovanni API call: {e}")
            return None
    
    def process_giovanni_data(self, raw_data: Dict, variable: str) -> Dict:
        """
        Procesa los datos de Giovanni y los convierte a formato estándar
        """
        try:
            processed_data = []
            
            # Giovanni retorna datos en formato timeseries
            if 'data' in raw_data and isinstance(raw_data['data'], list):
                for item in raw_data['data']:
                    if 'time' in item and 'value' in item:
                        date_obj = datetime.fromisoformat(item['time'].replace('Z', '+00:00'))
                        value = item['value']
                        
                        if value is not None and value != -9999:  # Giovanni usa -9999 para missing data
                            processed_data.append({
                                'date': date_obj,
                                'variable': variable,
                                'value': value
                            })
            
            return {
                'data': processed_data,
                'source': 'NASA_Giovanni',
                'variable': variable,
                'count': len(processed_data)
            }
            
        except Exception as e:
            print(f"Error processing Giovanni data: {e}")
            return {'data': [], 'source': 'NASA_Giovanni', 'variable': variable, 'count': 0}
    
    async def get_multi_variable_data(self, latitude: float, longitude: float, 
                                    start_date: str, end_date: str) -> Dict[str, List]:
        """
        Obtiene datos de múltiples variables meteorológicas de Giovanni
        """
        all_data = {}
        
        for var_name, var_config in self.variables.items():
            print(f"Fetching {var_name} data...")
            
            giovanni_data = await self.fetch_giovanni_data(
                variable=var_config['dataset'],
                latitude=latitude,
                longitude=longitude,
                start_date=start_date,
                end_date=end_date
            )
            
            if giovanni_data and giovanni_data['data']:
                all_data[var_name] = giovanni_data['data']
                print(f"✅ {var_name}: {len(giovanni_data['data'])} points")
            else:
                print(f"❌ No data for {var_name}")
                all_data[var_name] = []
            
            # Pausa para evitar sobrecarga del servidor
            await asyncio.sleep(2)
        
        return all_data
    
    def combine_variables_data(self, multi_var_data: Dict[str, List]) -> List[Dict]:
        """
        Combina datos de múltiples variables en registros por fecha
        """
        # Crear un diccionario por fecha
        date_records = {}
        
        for var_name, var_data in multi_var_data.items():
            for record in var_data:
                date_str = record['date'].strftime('%Y-%m-%d')
                
                if date_str not in date_records:
                    date_records[date_str] = {
                        'date': record['date'],
                        'temperature': None,
                        'precipitation': None,
                        'wind_speed': None,
                        'humidity': None
                    }
                
                # Mapear variables
                if var_name == 'temperature':
                    date_records[date_str]['temperature'] = record['value'] - 273.15  # K to C
                elif var_name == 'precipitation':
                    date_records[date_str]['precipitation'] = record['value'] * 86400  # kg/m²/s to mm/day
                elif var_name == 'wind_speed':
                    # Calcular magnitud del viento si tenemos U y V
                    if 'wind_u' not in date_records[date_str]:
                        date_records[date_str]['wind_u'] = record['value']
                    else:
                        # Calcular magnitud
                        u = date_records[date_str]['wind_u']
                        v = record['value']
                        wind_speed = np.sqrt(u*u + v*v)
                        date_records[date_str]['wind_speed'] = wind_speed
                elif var_name == 'wind_speed_v':
                    date_records[date_str]['wind_v'] = record['value']
                elif var_name == 'humidity':
                    # Convertir humedad específica a humedad relativa (aproximación)
                    date_records[date_str]['humidity'] = min(100, record['value'] * 1000)
        
        # Convertir a lista y filtrar registros completos
        complete_records = []
        for date_str, record in date_records.items():
            # Calcular wind_speed si tenemos componentes U y V
            if record.get('wind_u') is not None and record.get('wind_v') is not None:
                u = record['wind_u']
                v = record['wind_v']
                record['wind_speed'] = np.sqrt(u*u + v*v)
            
            # Verificar que tenemos datos esenciales
            if (record['temperature'] is not None and 
                record['precipitation'] is not None and 
                record['wind_speed'] is not None and 
                record['humidity'] is not None):
                
                # Calcular heat index
                record['heat_index'] = self.calculate_heat_index(
                    record['temperature'], 
                    record['humidity']
                )
                
                complete_records.append(record)
        
        return complete_records
    
    def calculate_heat_index(self, temperature: float, humidity: float) -> float:
        """
        Calcula el índice de calor usando la fórmula del National Weather Service
        """
        if temperature < 27:  # 80°F
            return temperature
        
        # Conversión a Fahrenheit para el cálculo
        T = temperature * 9/5 + 32
        RH = humidity
        
        # Fórmula completa del heat index
        HI = -42.379 + 2.04901523*T + 10.14333127*RH - 0.22475541*T*RH - 0.00683783*T*T - 0.05481717*RH*RH + 0.00122874*T*T*RH + 0.00085282*T*RH*RH - 0.00000199*T*T*RH*RH
        
        # Conversión de vuelta a Celsius
        return (HI - 32) * 5/9
    
    async def get_historical_data(self, latitude: float, longitude: float, 
                                 date_of_year: str, years: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene datos históricos de Giovanni para una ubicación y fecha específica
        """
        # Calcular rango de fechas (menos años debido a limitaciones de Giovanni)
        current_year = datetime.now().year
        start_year = max(2000, current_year - years)  # Giovanni tiene datos desde ~2000
        
        # Cache key
        cache_key = f"giovanni_data_{latitude}_{longitude}_{start_year}_{current_year}.pkl"
        cache_path = self.data_cache_dir / cache_key
        
        # Intentar cargar desde cache
        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    cached_data = pickle.load(f)
                    if len(cached_data) > 0:
                        return self.filter_by_date_of_year(cached_data, date_of_year)
            except Exception as e:
                print(f"Error loading cache: {e}")
        
        # Obtener datos de Giovanni
        print(f"Fetching Giovanni data for {latitude}, {longitude} from {start_year} to {current_year}")
        
        start_date = f"{start_year}-01-01"
        end_date = f"{current_year-1}-12-31"
        
        # Obtener datos de múltiples variables
        multi_var_data = await self.get_multi_variable_data(
            latitude, longitude, start_date, end_date
        )
        
        # Combinar variables en registros por fecha
        combined_data = self.combine_variables_data(multi_var_data)
        
        # Guardar en cache
        if combined_data:
            try:
                with open(cache_path, 'wb') as f:
                    pickle.dump(combined_data, f)
                print(f"✅ Cached {len(combined_data)} records")
            except Exception as e:
                print(f"Error saving cache: {e}")
        
        return self.filter_by_date_of_year(combined_data, date_of_year)
    
    def filter_by_date_of_year(self, data: List[Dict], date_of_year: str) -> List[Dict]:
        """
        Filtra los datos para obtener solo los de la fecha específica del año
        """
        try:
            month, day = map(int, date_of_year.split('-'))
            
            filtered_data = []
            for item in data:
                date_obj = item['date'] if isinstance(item['date'], datetime) else datetime.fromisoformat(str(item['date']))
                
                # Permitir un rango de ±3 días para tener más datos
                target_date = datetime(2000, month, day)  # Año de referencia
                item_date = datetime(2000, date_obj.month, date_obj.day)
                
                days_diff = abs((item_date - target_date).days)
                if days_diff <= 3 or days_diff >= 362:  # También incluir wrap-around del año
                    filtered_data.append(item)
            
            print(f"Filtered to {len(filtered_data)} records for date {date_of_year}")
            return filtered_data
            
        except Exception as e:
            print(f"Error filtering data by date: {e}")
            return []
    
    def train_prediction_models(self, data: List[Dict], latitude: float, longitude: float):
        """
        Entrena modelos de ML con los datos históricos de Giovanni
        """
        if len(data) < 5:  # Menos datos requeridos debido a calidad superior
            print("Not enough Giovanni data to train models")
            return
        
        print(f"Training models with {len(data)} Giovanni data points...")
        
        # Preparar features
        X = self.prepare_features(data, latitude, longitude)
        
        if X.shape[0] == 0:
            print("No valid features for training")
            return
        
        # Entrenar modelos específicos para datos Giovanni
        self.train_giovanni_models(X, data)
        
        # Guardar modelos entrenados
        self.save_trained_models()
        
        print("Giovanni-based models trained and saved successfully!")
    
    def prepare_features(self, data: List[Dict], latitude: float, longitude: float) -> np.ndarray:
        """
        Prepara features mejoradas para modelos basados en Giovanni
        """
        features = []
        
        for item in data:
            date_obj = item['date'] if isinstance(item['date'], datetime) else datetime.fromisoformat(str(item['date']))
            
            # Features temporales avanzadas
            day_of_year = date_obj.timetuple().tm_yday
            month = date_obj.month
            year = date_obj.year
            
            # Features geográficas
            equator_distance = abs(latitude)
            coastal_factor = abs(longitude) % 180
            
            # Features estacionales múltiples
            seasonal_factor_1 = np.sin(2 * np.pi * day_of_year / 365.25)
            seasonal_factor_2 = np.cos(2 * np.pi * day_of_year / 365.25)
            
            # Features climáticas derivadas
            temp = item.get('temperature', 0)
            precip = item.get('precipitation', 0)
            wind = item.get('wind_speed', 0)
            humidity = item.get('humidity', 0)
            
            feature_vector = [
                latitude, longitude, equator_distance, coastal_factor,
                day_of_year, month, year, 
                seasonal_factor_1, seasonal_factor_2,
                temp, precip, wind, humidity,
                temp * humidity / 100,  # Factor de confort
                wind * temp,  # Factor de sensación térmica
                precip * humidity / 100  # Factor de humedad efectiva
            ]
            
            features.append(feature_vector)
        
        return np.array(features)
    
    def train_giovanni_models(self, X: np.ndarray, data: List[Dict]):
        """
        Entrena modelos específicamente optimizados para datos Giovanni
        """
        # Modelo para temperatura
        y_temp = [item['temperature'] for item in data]
        if len(set(y_temp)) > 1:
            self.models['temperature_predictor'] = RandomForestRegressor(
                n_estimators=200, 
                max_depth=10,
                random_state=42
            )
            self.models['temperature_predictor'].fit(X, y_temp)
        
        # Modelo para precipitación con categorías más precisas
        y_precip = [item['precipitation'] for item in data]
        if len(set(y_precip)) > 1:
            self.models['precipitation_classifier'] = GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.1,
                random_state=42
            )
            # Categorías más detalladas para precipitación
            precip_categories = []
            for p in y_precip:
                if p == 0:
                    precip_categories.append(0)  # Sin precipitación
                elif p < 2.5:
                    precip_categories.append(1)  # Llovizna
                elif p < 10:
                    precip_categories.append(2)  # Lluvia ligera
                elif p < 50:
                    precip_categories.append(3)  # Lluvia moderada
                else:
                    precip_categories.append(4)  # Lluvia intensa
            
            self.models['precipitation_classifier'].fit(X, precip_categories)
        
        # Modelo para viento
        y_wind = [item['wind_speed'] for item in data]
        if len(set(y_wind)) > 1:
            self.models['wind_predictor'] = RandomForestRegressor(
                n_estimators=150,
                max_depth=8,
                random_state=42
            )
            self.models['wind_predictor'].fit(X, y_wind)
        
        # Modelo para humedad
        y_humidity = [item['humidity'] for item in data]
        if len(set(y_humidity)) > 1:
            self.models['humidity_predictor'] = RandomForestRegressor(
                n_estimators=150,
                max_depth=8,
                random_state=42
            )
            self.models['humidity_predictor'].fit(X, y_humidity)
    
    def predict_probabilities(self, latitude: float, longitude: float, 
                            date_of_year: str, historical_data: List[Dict]) -> Dict[str, Dict]:
        """
        Predice probabilidades usando modelos entrenados con datos Giovanni
        """
        if not historical_data:
            return self.fallback_probabilities()
        
        # Calcular estadísticas con datos Giovanni de alta calidad
        temps = [item['temperature'] for item in historical_data]
        precips = [item['precipitation'] for item in historical_data]
        winds = [item['wind_speed'] for item in historical_data]
        humidities = [item['humidity'] for item in historical_data]
        heat_indices = [item.get('heat_index', item['temperature']) for item in historical_data]
        
        # Umbrales más precisos basados en datos Giovanni
        probabilities = {
            'very_hot': {
                'probability': len([t for t in temps if t > np.percentile(temps, 85)]) / len(temps),
                'threshold': np.percentile(temps, 85),
                'unit': '°C'
            },
            'very_cold': {
                'probability': len([t for t in temps if t < np.percentile(temps, 15)]) / len(temps),
                'threshold': np.percentile(temps, 15),
                'unit': '°C'
            },
            'very_windy': {
                'probability': len([w for w in winds if w > np.percentile(winds, 80)]) / len(winds),
                'threshold': np.percentile(winds, 80),
                'unit': 'm/s'
            },
            'very_wet': {
                'probability': len([p for p in precips if p > np.percentile(precips, 75)]) / len(precips),
                'threshold': np.percentile(precips, 75),
                'unit': 'mm'
            },
            'very_uncomfortable': {
                'probability': len([h for h in heat_indices if h > np.percentile(heat_indices, 80)]) / len(heat_indices),
                'threshold': np.percentile(heat_indices, 80),
                'unit': '°C'
            }
        }
        
        return probabilities
    
    def fallback_probabilities(self) -> Dict[str, Dict]:
        """
        Probabilidades por defecto cuando no hay datos Giovanni suficientes
        """
        return {
            'very_hot': {'probability': 0.15, 'threshold': 35.0, 'unit': '°C'},
            'very_cold': {'probability': 0.15, 'threshold': 0.0, 'unit': '°C'},
            'very_windy': {'probability': 0.20, 'threshold': 15.0, 'unit': 'm/s'},
            'very_wet': {'probability': 0.25, 'threshold': 10.0, 'unit': 'mm'},
            'very_uncomfortable': {'probability': 0.20, 'threshold': 32.0, 'unit': '°C'}
        }
    
    def save_trained_models(self):
        """
        Guarda los modelos entrenados
        """
        try:
            for model_name, model in self.models.items():
                if model is not None:
                    model_path = self.models_dir / f"giovanni_{model_name}.pkl"
                    joblib.dump(model, model_path)
            
            # Guardar scalers
            scaler_path = self.models_dir / "giovanni_scalers.pkl"
            joblib.dump(self.scalers, scaler_path)
            
        except Exception as e:
            print(f"Error saving Giovanni models: {e}")
    
    def load_trained_models(self):
        """
        Carga los modelos entrenados si existen
        """
        try:
            for model_name in self.models.keys():
                model_path = self.models_dir / f"giovanni_{model_name}.pkl"
                if model_path.exists():
                    self.models[model_name] = joblib.load(model_path)
            
            # Cargar scalers
            scaler_path = self.models_dir / "giovanni_scalers.pkl"
            if scaler_path.exists():
                self.scalers = joblib.load(scaler_path)
                
        except Exception as e:
            print(f"Error loading Giovanni models: {e}")

# Instancia global
giovanni_weather_service = GiovanniNASADataService()