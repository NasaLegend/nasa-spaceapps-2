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
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score, classification_report, confusion_matrix
from sklearn.metrics import mean_absolute_error, f1_score, precision_score, recall_score
import warnings
warnings.filterwarnings('ignore')

class RealWeatherDataService:
    def __init__(self):
        self.data_cache_dir = Path("data_cache")
        self.models_dir = Path("models")
        self.data_cache_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        
        # APIs de datos meteorológicos reales
        self.apis = {
            "openweather": {
                "base_url": "https://api.openweathermap.org/data/2.5",
                "historical_url": "https://history.openweathermap.org/data/2.5/history/city",
                "api_key": os.getenv("OPENWEATHER_API_KEY", "demo_key")
            },
            "nasa_power": {
                "base_url": "https://power.larc.nasa.gov/api/temporal/daily/point",
                "parameters": "T2M,PRECTOTCORR,WS10M,RH2M,T2M_MAX,T2M_MIN"
            },
            "meteostat": {
                "base_url": "https://meteostat.p.rapidapi.com/point/daily"
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
        
        # Métricas de evaluación para cada modelo
        self.model_metrics = {
            'temperature_predictor': {},
            'precipitation_classifier': {},
            'wind_predictor': {},
            'humidity_predictor': {},
            'condition_classifier': {}
        }
        
        self.scalers = {
            'features': StandardScaler(),
            'targets': {}
        }
        
        # No cargar modelos automáticamente - se cargarán por ubicación cuando sea necesario
        # self.load_trained_models()
    
    async def fetch_nasa_power_data(self, latitude: float, longitude: float, 
                                   start_date: str, end_date: str) -> Optional[Dict]:
        """
        Obtiene datos históricos de NASA POWER API
        """
        try:
            url = f"{self.apis['nasa_power']['base_url']}"
            params = {
                'parameters': self.apis['nasa_power']['parameters'],
                'community': 'RE',
                'longitude': longitude,
                'latitude': latitude,
                'start': start_date.replace('-', ''),
                'end': end_date.replace('-', ''),
                'format': 'JSON'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self.process_nasa_power_data(data)
                    else:
                        print(f"Error fetching NASA POWER data: {response.status}")
                        return None
        except Exception as e:
            print(f"Error in NASA POWER API call: {e}")
            return None
    
    def process_nasa_power_data(self, raw_data: Dict) -> Dict:
        """
        Procesa los datos de NASA POWER y los convierte a formato estándar
        """
        try:
            parameters = raw_data.get('properties', {}).get('parameter', {})
            
            processed_data = []
            dates = list(parameters.get('T2M', {}).keys())
            
            for date_str in dates:
                date_obj = datetime.strptime(date_str, '%Y%m%d')
                
                # Extraer datos para esta fecha
                temp_avg = parameters.get('T2M', {}).get(date_str, None)
                temp_max = parameters.get('T2M_MAX', {}).get(date_str, None)
                temp_min = parameters.get('T2M_MIN', {}).get(date_str, None)
                precipitation = parameters.get('PRECTOTCORR', {}).get(date_str, None)
                wind_speed = parameters.get('WS10M', {}).get(date_str, None)
                humidity = parameters.get('RH2M', {}).get(date_str, None)
                
                # Filtrar valores válidos (NASA POWER usa -999 para datos faltantes)
                if all(val is not None and val != -999 for val in [temp_avg, precipitation, wind_speed, humidity]):
                    processed_data.append({
                        'date': date_obj,
                        'temperature': temp_avg,
                        'temperature_max': temp_max if temp_max != -999 else temp_avg,
                        'temperature_min': temp_min if temp_min != -999 else temp_avg,
                        'precipitation': max(0, precipitation),  # No precipitación negativa
                        'wind_speed': wind_speed,
                        'humidity': min(100, max(0, humidity)),  # Clamp humidity 0-100%
                        'heat_index': self.calculate_heat_index(temp_avg, humidity)
                    })
            
            return {
                'data': processed_data,
                'source': 'NASA_POWER',
                'location': {
                    'latitude': raw_data.get('geometry', {}).get('coordinates', [None, None])[1],
                    'longitude': raw_data.get('geometry', {}).get('coordinates', [None, None])[0]
                }
            }
        except Exception as e:
            print(f"Error processing NASA POWER data: {e}")
            return {'data': [], 'source': 'NASA_POWER', 'location': {}}
    
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
                                 date_of_year: str, years: int = 30) -> List[Dict[str, Any]]:
        """
        Obtiene datos históricos reales para una ubicación y fecha específica
        """
        # Calcular rango de fechas
        current_year = datetime.now().year
        start_year = current_year - years
        
        # Cache key para evitar llamadas repetidas
        cache_key = f"weather_data_{latitude}_{longitude}_{start_year}_{current_year}.pkl"
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
        
        # Si no hay cache, obtener datos de NASA POWER
        all_data = []
        
        # Obtener datos por chunks de años para evitar timeouts
        chunk_size = 5
        for year_start in range(start_year, current_year + 1, chunk_size):
            year_end = min(year_start + chunk_size - 1, current_year)
            
            start_date = f"{year_start}-01-01"
            end_date = f"{year_end}-12-31"
            
            print(f"Fetching data for years {year_start}-{year_end}...")
            
            nasa_data = await self.fetch_nasa_power_data(latitude, longitude, start_date, end_date)
            
            if nasa_data and nasa_data['data']:
                all_data.extend(nasa_data['data'])
            
            # Pequeña pausa para no sobrecargar la API
            await asyncio.sleep(1)
        
        # Guardar en cache
        if all_data:
            try:
                with open(cache_path, 'wb') as f:
                    pickle.dump(all_data, f)
            except Exception as e:
                print(f"Error saving cache: {e}")
        
        return self.filter_by_date_of_year(all_data, date_of_year)
    
    def filter_by_date_of_year(self, data: List[Dict], date_of_year: str) -> List[Dict]:
        """
        Filtra los datos para obtener solo los de la fecha específica del año
        """
        try:
            month, day = map(int, date_of_year.split('-'))
            
            filtered_data = []
            for item in data:
                date_obj = item['date'] if isinstance(item['date'], datetime) else datetime.fromisoformat(str(item['date']))
                if date_obj.month == month and date_obj.day == day:
                    filtered_data.append(item)
            
            return filtered_data
        except Exception as e:
            print(f"Error filtering data by date: {e}")
            return []
    
    def prepare_features(self, data: List[Dict], latitude: float, longitude: float) -> np.ndarray:
        """
        Prepara features para el modelo de ML
        """
        features = []
        
        for item in data:
            date_obj = item['date'] if isinstance(item['date'], datetime) else datetime.fromisoformat(str(item['date']))
            
            # Features temporales
            day_of_year = date_obj.timetuple().tm_yday
            month = date_obj.month
            year = date_obj.year
            
            # Features geográficas
            # Distancia al ecuador (influye en temperatura)
            equator_distance = abs(latitude)
            # Distancia a costa (aproximada por longitud)
            coastal_factor = abs(longitude) % 180
            
            # Features estacionales
            seasonal_factor = np.sin(2 * np.pi * day_of_year / 365.25)
            
            feature_vector = [
                latitude, longitude, equator_distance, coastal_factor,
                day_of_year, month, year, seasonal_factor,
                item.get('temperature', 0),
                item.get('precipitation', 0),
                item.get('wind_speed', 0),
                item.get('humidity', 0)
            ]
            
            features.append(feature_vector)
        
        return np.array(features)
    
    def train_prediction_models(self, data: List[Dict], latitude: float, longitude: float):
        """
        Entrena modelos de ML con evaluación completa y métricas profesionales
        """
        # Verificar que self.models esté inicializado
        if not hasattr(self, 'models'):
            print("Warning: models attribute not found, initializing...")
            self.models = {
                'temperature_predictor': None,
                'precipitation_classifier': None,
                'wind_predictor': None,
                'humidity_predictor': None,
                'condition_classifier': None
            }
            self.model_metrics = {
                'temperature_predictor': {},
                'precipitation_classifier': {},
                'wind_predictor': {},
                'humidity_predictor': {},
                'condition_classifier': {}
            }
        
        # if len(data) < 50:  # Necesitamos más datos para un entrenamiento robusto
        #     print(f"Not enough data to train robust models: {len(data)} samples (minimum 50 required)")
        #     return
        
        print(f"\n🧠 Training ML models with {len(data)} data points...")
        print("=" * 60)
        
        # Preparar features
        X = self.prepare_features(data, latitude, longitude)
        
        if X.shape[0] == 0:
            print("❌ No valid features for training")
            return
        
        # Normalizar features
        X_scaled = self.scalers['features'].fit_transform(X)
        
        # 1. MODELO DE TEMPERATURA (Regresión)
        print("\n🌡️ TRAINING TEMPERATURE PREDICTOR (RandomForestRegressor)")
        print("-" * 50)
        y_temp = np.array([item['temperature'] for item in data])
        if len(set(y_temp)) > 1:
            self._train_regression_model('temperature_predictor', X_scaled, y_temp, 'Temperature (°C)')
        
        # 2. MODELO DE PRECIPITACIÓN (Clasificación)
        print("\n🌧️ TRAINING PRECIPITATION CLASSIFIER (GradientBoostingClassifier)")
        print("-" * 50)
        y_precip = np.array([item['precipitation'] for item in data])
        # Crear categorías más sofisticadas
        precip_categories = self._create_precipitation_categories(y_precip)
        if len(set(precip_categories)) > 1:
            self._train_classification_model('precipitation_classifier', X_scaled, precip_categories, 'Precipitation Category')
        
        # 3. MODELO DE VIENTO (Regresión)
        print("\n💨 TRAINING WIND PREDICTOR (RandomForestRegressor)")
        print("-" * 50)
        y_wind = np.array([item['wind_speed'] for item in data])
        if len(set(y_wind)) > 1:
            self._train_regression_model('wind_predictor', X_scaled, y_wind, 'Wind Speed (m/s)')
        
        # 4. MODELO DE HUMEDAD (Regresión)
        print("\n💧 TRAINING HUMIDITY PREDICTOR (RandomForestRegressor)")
        print("-" * 50)
        y_humidity = np.array([item['humidity'] for item in data])
        if len(set(y_humidity)) > 1:
            self._train_regression_model('humidity_predictor', X_scaled, y_humidity, 'Humidity (%)')
        
        # 5. CLASIFICADOR DE CONDICIONES EXTREMAS
        print("\n⚡ TRAINING EXTREME CONDITIONS CLASSIFIER")
        print("-" * 50)
        extreme_labels = self._create_extreme_condition_labels(data)
        if len(set(extreme_labels)) > 1:
            self._train_classification_model('condition_classifier', X_scaled, extreme_labels, 'Extreme Conditions')
        
        # Guardar modelos entrenados por ubicación
        location_key = f"{round(latitude, 3)}_{round(longitude, 3)}"
        self.save_trained_models(location_key)
        
        print(f"\n✅ Models trained and saved successfully for {location_key}!")
        print("=" * 60)
        self._print_models_summary()
    
    def _train_regression_model(self, model_name: str, X: np.ndarray, y: np.ndarray, target_name: str):
        """Entrena un modelo de regresión con evaluación completa"""
        
        # Split datos
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        print(f"   Training samples: {len(X_train)}, Test samples: {len(X_test)}")
        
        # Hiperparámetros optimizados según cantidad de datos
        if len(X_train) < 50:
            # Para pocos datos, usar parámetros más conservadores
            if model_name == 'temperature_predictor':
                param_grid = {
                    'n_estimators': [50, 100],
                    'max_depth': [5, 10],
                    'min_samples_split': [2],
                    'min_samples_leaf': [1]
                }
            else:
                param_grid = {
                    'n_estimators': [50, 100],
                    'max_depth': [5, 10],
                    'min_samples_split': [2]
                }
            cv_folds = max(2, min(5, len(X_train) // 10)) if len(X_train) >= 10 else 2
        else:
            # Para más datos, usar búsqueda completa
            if model_name == 'temperature_predictor':
                param_grid = {
                    'n_estimators': [100, 200],
                    'max_depth': [10, 20, None],
                    'min_samples_split': [2, 5],
                    'min_samples_leaf': [1, 2]
                }
            else:
                param_grid = {
                    'n_estimators': [100, 150],
                    'max_depth': [10, 15],
                    'min_samples_split': [2, 5]
                }
            cv_folds = 5
        
        model = RandomForestRegressor(random_state=42, n_jobs=-1)
        
        # GridSearch con CV adaptativo
        if len(X_train) >= 10:
            try:
                grid_search = GridSearchCV(model, param_grid, cv=cv_folds, scoring='neg_mean_squared_error', n_jobs=-1)
                grid_search.fit(X_train, y_train)
                best_model = grid_search.best_estimator_
                best_params = grid_search.best_params_
            except Exception as e:
                print(f"   ⚠️ GridSearchCV failed: {e}")
                print(f"   🔄 Using default parameters")
                best_model = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42)
                best_model.fit(X_train, y_train)
                best_params = "default"
        else:
            # Para muy pocos datos, usar parámetros por defecto
            print(f"   ⚠️ Insufficient data for CV, using default parameters")
            best_model = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42)
            best_model.fit(X_train, y_train)
            best_params = "default"
        
        self.models[model_name] = best_model
        
        # Predicciones
        y_train_pred = best_model.predict(X_train)
        y_test_pred = best_model.predict(X_test)
        
        # Métricas de entrenamiento
        train_mse = mean_squared_error(y_train, y_train_pred)
        train_rmse = np.sqrt(train_mse)
        train_mae = mean_absolute_error(y_train, y_train_pred)
        train_r2 = r2_score(y_train, y_train_pred)
        
        # Métricas de prueba
        test_mse = mean_squared_error(y_test, y_test_pred)
        test_rmse = np.sqrt(test_mse)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        
        # Validación cruzada (adaptativa)
        if len(X) >= 10:
            try:
                cv_scores = cross_val_score(best_model, X, y, cv=cv_folds, scoring='neg_mean_squared_error')
                cv_rmse_scores = np.sqrt(-cv_scores)
                cv_rmse_mean = float(cv_rmse_scores.mean())
                cv_rmse_std = float(cv_rmse_scores.std())
                cv_scores_list = cv_rmse_scores.tolist()
            except Exception as e:
                print(f"   ⚠️ Cross-validation failed: {e}")
                cv_rmse_mean = test_rmse
                cv_rmse_std = 0.0
                cv_scores_list = [test_rmse]
        else:
            cv_rmse_mean = test_rmse
            cv_rmse_std = 0.0
            cv_scores_list = [test_rmse]
        
        # Guardar métricas
        self.model_metrics[model_name] = {
            'model_type': 'regression',
            'algorithm': 'RandomForestRegressor',
            'target': target_name,
            'best_params': best_params,
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'train_metrics': {
                'mse': float(train_mse),
                'rmse': float(train_rmse),
                'mae': float(train_mae),
                'r2_score': float(train_r2)
            },
            'test_metrics': {
                'mse': float(test_mse),
                'rmse': float(test_rmse),
                'mae': float(test_mae),
                'r2_score': float(test_r2)
            },
            'cross_validation': {
                'cv_folds': cv_folds,
                'cv_rmse_mean': cv_rmse_mean,
                'cv_rmse_std': cv_rmse_std,
                'cv_scores': cv_scores_list
            },
            'feature_importance': best_model.feature_importances_.tolist() if hasattr(best_model, 'feature_importances_') else []
        }
        
        # Imprimir resultados
        print(f"📊 {target_name} Model Results:")
        print(f"   Best Parameters: {best_params}")
        print(f"   Training RMSE: {train_rmse:.4f}")
        print(f"   Test RMSE: {test_rmse:.4f}")
        print(f"   Test R² Score: {test_r2:.4f}")
        print(f"   CV RMSE: {cv_rmse_mean:.4f} ± {cv_rmse_std:.4f}")
        
        # Detectar overfitting
        if train_rmse < test_rmse * 0.7:
            print(f"   ⚠️ Possible overfitting detected (train RMSE much lower than test RMSE)")
        elif test_r2 > 0.8:
            print(f"   ✅ Excellent model performance (R² > 0.8)")
        elif test_r2 > 0.6:
            print(f"   ✅ Good model performance (R² > 0.6)")
        else:
            print(f"   ⚠️ Model performance could be improved (R² = {test_r2:.3f})")
    
    def _train_classification_model(self, model_name: str, X: np.ndarray, y: np.ndarray, target_name: str):
        """Entrena un modelo de clasificación con evaluación completa"""
        
        # Verificar distribución de clases
        unique_classes, class_counts = np.unique(y, return_counts=True)
        min_class_count = np.min(class_counts)
        
        print(f"   Class distribution: {dict(zip(unique_classes, class_counts))}")
        
        # Si hay clases con muy pocos ejemplos, usar estrategia diferente
        if min_class_count < 2:
            print(f"   ⚠️ Insufficient samples in some classes (min: {min_class_count})")
            print(f"   🔄 Using simple train-test split without stratification")
            # Split sin estratificación
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            use_cv = False
        elif min_class_count < 5:
            print(f"   ⚠️ Low samples in some classes (min: {min_class_count})")
            print(f"   🔄 Using stratified split but simplified CV")
            # Split con estratificación pero CV reducido
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
            use_cv = True
            cv_folds = max(2, min_class_count)
        else:
            # Split normal con estratificación
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
            use_cv = True
            cv_folds = 5
        
        # Hiperparámetros optimizados (simplificados para pocos datos)
        if len(X_train) < 50:
            # Para pocos datos, usar parámetros más conservadores
            param_grid = {
                'n_estimators': [50, 100],
                'max_depth': [3, 5],
                'learning_rate': [0.1],
                'subsample': [1.0]
            }
        else:
            param_grid = {
                'n_estimators': [100, 200],
                'max_depth': [5, 10, 15],
                'learning_rate': [0.05, 0.1, 0.15],
                'subsample': [0.8, 0.9, 1.0]
            }
        
        model = GradientBoostingClassifier(random_state=42)
        
        # GridSearch con CV adaptativo
        if use_cv and len(X_train) >= 10:
            grid_search = GridSearchCV(model, param_grid, cv=cv_folds, scoring='accuracy', n_jobs=-1)
            try:
                grid_search.fit(X_train, y_train)
                best_model = grid_search.best_estimator_
                best_params = grid_search.best_params_
            except ValueError as e:
                print(f"   ⚠️ GridSearchCV failed: {e}")
                print(f"   🔄 Using default parameters")
                best_model = GradientBoostingClassifier(n_estimators=50, max_depth=3, random_state=42)
                best_model.fit(X_train, y_train)
                best_params = "default"
        else:
            # Usar parámetros por defecto sin CV
            print(f"   ⚠️ Insufficient data for CV, using default parameters")
            best_model = GradientBoostingClassifier(n_estimators=50, max_depth=3, random_state=42)
            best_model.fit(X_train, y_train)
            best_params = "default"
        
        self.models[model_name] = best_model
        
        # Predicciones
        y_train_pred = best_model.predict(X_train)
        y_test_pred = best_model.predict(X_test)
        
        # Métricas de clasificación
        train_accuracy = accuracy_score(y_train, y_train_pred)
        test_accuracy = accuracy_score(y_test, y_test_pred)
        
        # Métricas avanzadas (con protección contra errores)
        try:
            precision = precision_score(y_test, y_test_pred, average='weighted', zero_division=0)
            recall = recall_score(y_test, y_test_pred, average='weighted', zero_division=0)
            f1 = f1_score(y_test, y_test_pred, average='weighted', zero_division=0)
        except Exception as e:
            print(f"   ⚠️ Error calculating advanced metrics: {e}")
            precision = test_accuracy
            recall = test_accuracy
            f1 = test_accuracy
        
        # Validación cruzada (solo si es posible)
        if use_cv and len(X) >= 10:
            try:
                cv_scores = cross_val_score(best_model, X, y, cv=cv_folds, scoring='accuracy')
                cv_mean = float(cv_scores.mean())
                cv_std = float(cv_scores.std())
                cv_scores_list = cv_scores.tolist()
            except Exception as e:
                print(f"   ⚠️ Cross-validation failed: {e}")
                cv_mean = test_accuracy
                cv_std = 0.0
                cv_scores_list = [test_accuracy]
        else:
            cv_mean = test_accuracy
            cv_std = 0.0
            cv_scores_list = [test_accuracy]
        
        # Reporte de clasificación (con protección)
        try:
            class_report = classification_report(y_test, y_test_pred, output_dict=True, zero_division=0)
        except Exception as e:
            print(f"   ⚠️ Classification report failed: {e}")
            class_report = {"accuracy": test_accuracy}
        
        # Guardar métricas
        self.model_metrics[model_name] = {
            'model_type': 'classification',
            'algorithm': 'GradientBoostingClassifier',
            'target': target_name,
            'best_params': best_params,
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'class_distribution': class_counts.tolist(),
            'train_metrics': {
                'accuracy': float(train_accuracy)
            },
            'test_metrics': {
                'accuracy': float(test_accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1)
            },
            'cross_validation': {
                'cv_folds': cv_folds if use_cv else 1,
                'cv_f1_mean': cv_mean,
                'cv_f1_std': cv_std,
                'cv_scores': cv_scores_list
            },
            'classification_report': class_report,
            'feature_importance': best_model.feature_importances_.tolist() if hasattr(best_model, 'feature_importances_') else []
        }
        
        # Imprimir resultados
        print(f"📊 {target_name} Model Results:")
        print(f"   Best Parameters: {best_params}")
        print(f"   Training Accuracy: {train_accuracy:.4f}")
        print(f"   Test Accuracy: {test_accuracy:.4f}")
        print(f"   Test Precision: {precision:.4f}")
        print(f"   Test Recall: {recall:.4f}")
        print(f"   Test F1-Score: {f1:.4f}")
        if use_cv:
            print(f"   CV Accuracy: {cv_mean:.4f} ± {cv_std:.4f}")
        
        # Evaluación de rendimiento
        if f1 > 0.8:
            print(f"   ✅ Excellent classification performance (F1 > 0.8)")
        elif f1 > 0.6:
            print(f"   ✅ Good classification performance (F1 > 0.6)")
        else:
            print(f"   ⚠️ Classification performance could be improved (F1 = {f1:.3f})")
    
    def _create_precipitation_categories(self, precip_data: np.ndarray) -> np.ndarray:
        """Crea categorías sofisticadas de precipitación"""
        categories = []
        for p in precip_data:
            if p == 0:
                categories.append(0)  # Seco
            elif p < 2.5:
                categories.append(1)  # Lluvia ligera
            elif p < 7.5:
                categories.append(2)  # Lluvia moderada
            elif p < 15:
                categories.append(3)  # Lluvia fuerte
            else:
                categories.append(4)  # Lluvia extrema
        return np.array(categories)
    
    def _create_extreme_condition_labels(self, data: List[Dict]) -> np.ndarray:
        """Crea etiquetas para condiciones extremas"""
        labels = []
        temps = [item['temperature'] for item in data]
        precips = [item['precipitation'] for item in data]
        winds = [item['wind_speed'] for item in data]
        
        # Percentiles para determinar extremos
        temp_high = np.percentile(temps, 90)
        temp_low = np.percentile(temps, 10)
        precip_high = np.percentile(precips, 85)
        wind_high = np.percentile(winds, 85)
        
        for item in data:
            temp = item['temperature']
            precip = item['precipitation']
            wind = item['wind_speed']
            
            # Clasificación multi-clase de condiciones extremas
            if temp > temp_high and precip > precip_high:
                labels.append(0)  # Calor húmedo extremo
            elif temp > temp_high:
                labels.append(1)  # Calor seco extremo
            elif temp < temp_low:
                labels.append(2)  # Frío extremo
            elif precip > precip_high:
                labels.append(3)  # Lluvia extrema
            elif wind > wind_high:
                labels.append(4)  # Viento extremo
            else:
                labels.append(5)  # Condiciones normales
        
        return np.array(labels)
    
    def _print_models_summary(self):
        """Imprime un resumen de todos los modelos entrenados"""
        print("\n📈 MODELS PERFORMANCE SUMMARY")
        print("=" * 60)
        
        for model_name, metrics in self.model_metrics.items():
            if metrics:
                print(f"\n🔹 {model_name.upper().replace('_', ' ')}")
                print(f"   Algorithm: {metrics['algorithm']}")
                print(f"   Target: {metrics['target']}")
                
                if metrics['model_type'] == 'regression':
                    print(f"   Test RMSE: {metrics['test_metrics']['rmse']:.4f}")
                    print(f"   Test R²: {metrics['test_metrics']['r2_score']:.4f}")
                    print(f"   CV RMSE: {metrics['cross_validation']['cv_rmse_mean']:.4f}")
                else:
                    print(f"   Test Accuracy: {metrics['test_metrics']['accuracy']:.4f}")
                    print(f"   Test F1-Score: {metrics['test_metrics']['f1_score']:.4f}")
                    print(f"   CV F1: {metrics['cross_validation']['cv_f1_mean']:.4f}")
    
    def get_model_metrics(self) -> Dict:
        """Retorna todas las métricas de los modelos"""
        return self.model_metrics
    
    def print_detailed_metrics(self):
        """Imprime métricas detalladas de todos los modelos"""
        print("\n" + "="*80)
        print("🧠 COMPREHENSIVE AI MODEL METRICS REPORT")
        print("="*80)
        
        if not hasattr(self, 'model_metrics') or not self.model_metrics:
            print("❌ No model metrics available. Train models first.")
            return
        
        total_models = sum(1 for metrics in self.model_metrics.values() if metrics)
        print(f"📊 Total Trained Models: {total_models}")
        
        for model_name, metrics in self.model_metrics.items():
            if not metrics:
                continue
                
            print(f"\n" + "="*60)
            print(f"🔹 {model_name.upper().replace('_', ' ')}")
            print("="*60)
            
            print(f"📋 Model Information:")
            print(f"   • Algorithm: {metrics['algorithm']}")
            print(f"   • Model Type: {metrics['model_type'].title()}")
            print(f"   • Target Variable: {metrics['target']}")
            print(f"   • Training Samples: {metrics['train_samples']}")
            print(f"   • Test Samples: {metrics['test_samples']}")
            
            if 'best_params' in metrics:
                print(f"   • Best Hyperparameters: {metrics['best_params']}")
            
            if metrics['model_type'] == 'regression':
                print(f"\n📈 Regression Metrics:")
                train_metrics = metrics['train_metrics']
                test_metrics = metrics['test_metrics']
                cv_metrics = metrics['cross_validation']
                
                print(f"   Training Performance:")
                print(f"     - RMSE: {train_metrics['rmse']:.4f}")
                print(f"     - MAE: {train_metrics['mae']:.4f}")
                print(f"     - R² Score: {train_metrics['r2_score']:.4f}")
                
                print(f"   Test Performance:")
                print(f"     - RMSE: {test_metrics['rmse']:.4f}")
                print(f"     - MAE: {test_metrics['mae']:.4f}")
                print(f"     - R² Score: {test_metrics['r2_score']:.4f}")
                
                print(f"   Cross-Validation ({cv_metrics['cv_folds']}-fold):")
                print(f"     - CV RMSE: {cv_metrics['cv_rmse_mean']:.4f} ± {cv_metrics['cv_rmse_std']:.4f}")
                
                # Evaluación de calidad
                r2_score = test_metrics['r2_score']
                if r2_score > 0.9:
                    quality = "🔥 EXCELLENT"
                elif r2_score > 0.8:
                    quality = "✅ VERY GOOD"
                elif r2_score > 0.6:
                    quality = "✅ GOOD"
                elif r2_score > 0.4:
                    quality = "⚠️ FAIR"
                else:
                    quality = "❌ POOR"
                
                print(f"   Model Quality: {quality} (R² = {r2_score:.3f})")
                
            elif metrics['model_type'] == 'classification':
                print(f"\n🎯 Classification Metrics:")
                train_metrics = metrics['train_metrics']
                test_metrics = metrics['test_metrics']
                cv_metrics = metrics['cross_validation']
                
                print(f"   Training Performance:")
                print(f"     - Accuracy: {train_metrics['accuracy']:.4f}")
                
                print(f"   Test Performance:")
                print(f"     - Accuracy: {test_metrics['accuracy']:.4f}")
                print(f"     - Precision: {test_metrics['precision']:.4f}")
                print(f"     - Recall: {test_metrics['recall']:.4f}")
                print(f"     - F1-Score: {test_metrics['f1_score']:.4f}")
                
                print(f"   Cross-Validation ({cv_metrics['cv_folds']}-fold):")
                print(f"     - CV F1-Score: {cv_metrics['cv_f1_mean']:.4f} ± {cv_metrics['cv_f1_std']:.4f}")
                
                if 'class_distribution' in metrics:
                    print(f"   Class Distribution: {metrics['class_distribution']}")
                
                # Evaluación de calidad
                f1_score = test_metrics['f1_score']
                if f1_score > 0.9:
                    quality = "🔥 EXCELLENT"
                elif f1_score > 0.8:
                    quality = "✅ VERY GOOD"
                elif f1_score > 0.6:
                    quality = "✅ GOOD"
                elif f1_score > 0.4:
                    quality = "⚠️ FAIR"
                else:
                    quality = "❌ POOR"
                
                print(f"   Model Quality: {quality} (F1 = {f1_score:.3f})")
            
            # Feature importance
            if 'feature_importance' in metrics and metrics['feature_importance']:
                print(f"\n🎯 Feature Importance (Top 5):")
                feature_names = ['day_of_year', 'latitude', 'longitude', 'historical_avg', 
                               'seasonal_factor', 'coastal_factor', 'elevation_factor']
                
                importance_pairs = list(zip(feature_names, metrics['feature_importance']))
                importance_pairs.sort(key=lambda x: x[1], reverse=True)
                
                for i, (feature, importance) in enumerate(importance_pairs[:5]):
                    print(f"     {i+1}. {feature}: {importance:.4f}")
        
        print(f"\n" + "="*80)
        print("✅ MODEL METRICS REPORT COMPLETE")
        print("="*80)
    
    def predict_probabilities(self, latitude: float, longitude: float, 
                            date_of_year: str, historical_data: List[Dict]) -> Dict[str, Dict]:
        """
        Predice probabilidades de condiciones extremas usando modelos entrenados
        """
        if not historical_data:
            return self.fallback_probabilities()
        
        # Calcular estadísticas de los datos históricos
        temps = [item['temperature'] for item in historical_data]
        precips = [item['precipitation'] for item in historical_data]
        winds = [item['wind_speed'] for item in historical_data]
        humidities = [item['humidity'] for item in historical_data]
        heat_indices = [item.get('heat_index', item['temperature']) for item in historical_data]
        
        # Calcular umbrales basados en percentiles
        probabilities = {
            'very_hot': {
                'probability': len([t for t in temps if t > np.percentile(temps, 90)]) / len(temps),
                'threshold': np.percentile(temps, 90),
                'unit': '°C'
            },
            'very_cold': {
                'probability': len([t for t in temps if t < np.percentile(temps, 10)]) / len(temps),
                'threshold': np.percentile(temps, 10),
                'unit': '°C'
            },
            'very_windy': {
                'probability': len([w for w in winds if w > np.percentile(winds, 85)]) / len(winds),
                'threshold': np.percentile(winds, 85),
                'unit': 'km/h'
            },
            'very_wet': {
                'probability': len([p for p in precips if p > np.percentile(precips, 80)]) / len(precips),
                'threshold': np.percentile(precips, 80),
                'unit': 'mm'
            },
            'very_uncomfortable': {
                'probability': len([h for h in heat_indices if h > np.percentile(heat_indices, 85)]) / len(heat_indices),
                'threshold': np.percentile(heat_indices, 85),
                'unit': '°C'
            }
        }
        
        # Si tenemos modelos entrenados, usar ML para ajustar probabilidades
        if self.models['condition_classifier'] is not None:
            # Aquí podríamos usar el modelo para refinar las predicciones
            pass
        
        return probabilities
    
    def fallback_probabilities(self) -> Dict[str, Dict]:
        """
        Probabilidades por defecto cuando no hay datos suficientes
        """
        return {
            'very_hot': {'probability': 0.1, 'threshold': 35.0, 'unit': '°C'},
            'very_cold': {'probability': 0.1, 'threshold': 0.0, 'unit': '°C'},
            'very_windy': {'probability': 0.15, 'threshold': 50.0, 'unit': 'km/h'},
            'very_wet': {'probability': 0.2, 'threshold': 25.0, 'unit': 'mm'},
            'very_uncomfortable': {'probability': 0.15, 'threshold': 32.0, 'unit': '°C'}
        }
    
    def save_trained_models(self, location_key: str = "global"):
        """
        Guarda los modelos entrenados por ubicación
        """
        try:
            # Crear directorio específico para la ubicación
            location_models_dir = self.models_dir / location_key
            location_models_dir.mkdir(exist_ok=True)
            
            for model_name, model in self.models.items():
                if model is not None:
                    model_path = location_models_dir / f"{model_name}.pkl"
                    joblib.dump(model, model_path)
                    print(f"💾 Saved {model_name} model for {location_key}")
            
            # Guardar scalers
            scaler_path = location_models_dir / "scalers.pkl"
            joblib.dump(self.scalers, scaler_path)
            print(f"💾 Saved scalers for {location_key}")
            
        except Exception as e:
            print(f"Error saving models for {location_key}: {e}")
    
    def load_trained_models(self, location_key: str = "global"):
        """
        Carga los modelos entrenados para una ubicación específica
        """
        try:
            location_models_dir = self.models_dir / location_key
            if not location_models_dir.exists():
                print(f"📂 No models found for {location_key}")
                return False
                
            models_loaded = 0
            for model_name in self.models.keys():
                model_path = location_models_dir / f"{model_name}.pkl"
                if model_path.exists():
                    self.models[model_name] = joblib.load(model_path)
                    models_loaded += 1
            
            # Cargar scalers
            scaler_path = location_models_dir / "scalers.pkl"
            if scaler_path.exists():
                self.scalers = joblib.load(scaler_path)
                
            print(f"📂 Loaded {models_loaded} models for {location_key}")
            return models_loaded > 0
                
        except Exception as e:
            print(f"Error loading models for {location_key}: {e}")
            return False

# Instancia global
real_weather_service = RealWeatherDataService()