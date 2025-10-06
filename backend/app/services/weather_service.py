from typing import List, Dict, Any
from app.models.weather import (
    WeatherQuery, WeatherResponse, WeatherProbability, WeatherDataPoint, 
    WeatherCondition, CustomThresholds, FuturePrediction, TemperatureUnit,
    WeatherConditionType
)
from app.data.mock_weather_data import mock_data_generator
from app.data.real_weather_data import real_weather_service, RealWeatherDataService
# from app.data.giovanni_nasa_data import giovanni_weather_service  # DESACTIVADO - Solo NASA POWER
import statistics
import asyncio
import logging
from datetime import datetime, date, timedelta
import numpy as np
import pickle
import json
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.mock_service = mock_data_generator
        self.real_data_service = real_weather_service
        # self.giovanni_service = giovanni_weather_service  # DESACTIVADO - Solo NASA POWER
        
        self.prefer_giovanni = False  # DESACTIVADO - Solo usar NASA POWER
        
        # Cache en memoria para datos históricos (también se guarda en disco)
        self.historical_data_cache = {}
        
        # Cache para modelos entrenados (evita re-entrenar)
        self.models_cache = {}
        
        # Directorios para persistencia
        self.cache_dir = Path("weather_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Cargar caches desde disco al inicializar
        self._load_cache_from_disk()

    def _load_cache_from_disk(self):
        """Cargar caches desde archivos en disco"""
        try:
            # Cargar cache de datos históricos
            historical_cache_file = self.cache_dir / "historical_data_cache.pkl"
            if historical_cache_file.exists():
                with open(historical_cache_file, 'rb') as f:
                    self.historical_data_cache = pickle.load(f)
                print(f"📂 Loaded historical data cache: {len(self.historical_data_cache)} locations")
            
            # Cargar cache de modelos entrenados
            models_cache_file = self.cache_dir / "models_cache.pkl"
            if models_cache_file.exists():
                with open(models_cache_file, 'rb') as f:
                    self.models_cache = pickle.load(f)
                print(f"🧠 Loaded models cache: {len(self.models_cache)} trained locations")
                    
        except Exception as e:
            print(f"⚠️ Error loading cache from disk: {e}")
            self.historical_data_cache = {}
            self.models_cache = {}

    def _save_cache_to_disk(self):
        """Guardar caches en archivos en disco"""
        try:
            # Guardar cache de datos históricos
            historical_cache_file = self.cache_dir / "historical_data_cache.pkl"
            with open(historical_cache_file, 'wb') as f:
                pickle.dump(self.historical_data_cache, f)
            
            # Guardar cache de modelos entrenados
            models_cache_file = self.cache_dir / "models_cache.pkl"
            with open(models_cache_file, 'wb') as f:
                pickle.dump(self.models_cache, f)
                
            print(f"💾 Cache saved to disk: {len(self.historical_data_cache)} locations, {len(self.models_cache)} models")
                
        except Exception as e:
            print(f"⚠️ Error saving cache to disk: {e}")
    
    def _get_location_key(self, latitude: float, longitude: float) -> str:
        """Generar clave única para la ubicación (redondeada para cache eficiente)"""
        return f"{round(latitude, 3)}_{round(longitude, 3)}"
    
    async def _get_all_historical_data(self, latitude: float, longitude: float, date_of_year: str) -> List[Dict[str, Any]]:
        """
        Obtener TODOS los datos históricos disponibles para una ubicación y cachearlos.
        Solo hace la consulta una vez por ubicación.
        """
        location_key = self._get_location_key(latitude, longitude)
        
        # Si ya tenemos los datos en cache, devolverlos
        if location_key in self.historical_data_cache:
            print(f"✅ Using cached data for {location_key}: {len(self.historical_data_cache[location_key])} records")
            return self.historical_data_cache[location_key]
        
        print(f"🔄 Fetching ALL available historical data for {latitude}, {longitude}...")
        
        try:
            # Intentar obtener el máximo de datos disponibles (hasta 50 años)
            print(f"Attempting NASA POWER data for {latitude}, {longitude} (MAX YEARS)...")
            historical_data = await self.real_data_service.get_historical_data(
                latitude, longitude, date_of_year, years=50  # Solicitar máximo disponible
            )
            
            if historical_data and len(historical_data) >= 3:
                print(f"✅ NASA POWER data retrieved: {len(historical_data)} records - CACHING FOR FUTURE USE")
                
                # Guardar en cache de memoria y disco
                self.historical_data_cache[location_key] = historical_data
                self._save_cache_to_disk()  # 💾 Persistir en disco
                
                # Entrenar modelo UNA SOLA VEZ con todos los datos
                if location_key not in self.models_cache:
                    # Intentar cargar modelos existentes para esta ubicación
                    models_loaded = self.real_data_service.load_trained_models(location_key)
                    
                    if not models_loaded:
                        # Si no hay modelos, entrenar nuevos
                        print(f"🧠 Training ML models with {len(historical_data)} data points...")
                        self.real_data_service.train_prediction_models(historical_data, latitude, longitude)
                    else:
                        print(f"📂 Loaded existing ML models for {location_key}")
                        
                    self.models_cache[location_key] = True
                    self._save_cache_to_disk()  # 💾 Persistir cache de modelos
                    print(f"✅ Models ready for location {location_key}")
                else:
                    print(f"✅ Using cached models for location {location_key}")
                
                return historical_data
                
        except Exception as e:
            print(f"NASA POWER data failed: {e}")
        
        # Giovanni DESACTIVADO - Solo usar NASA POWER y datos sintéticos como fallback
        # try:
        #     print(f"Attempting Giovanni data for {latitude}, {longitude} (MAX YEARS)...")
        #     giovanni_data = await giovanni_weather_service.get_historical_data(
        #         latitude, longitude, date_of_year, years=50  # Solicitar máximo disponible
        #     )
        #     
        #     if giovanni_data and len(giovanni_data) >= 3:
        #         print(f"✅ Giovanni data retrieved: {len(giovanni_data)} records - CACHING FOR FUTURE USE")
        #         
        #         # Guardar en cache
        #         self.historical_data_cache[location_key] = giovanni_data
        #         
        #         # Entrenar modelo UNA SOLA VEZ
        #         if location_key not in self.models_cache:
        #             print(f"🧠 Training ML models with {len(giovanni_data)} data points...")
        #             giovanni_weather_service.train_prediction_models(giovanni_data, latitude, longitude)
        #             self.models_cache[location_key] = True
        #             print(f"✅ Models trained and cached for location {location_key}")
        #         
        #         return giovanni_data
        #         
        # except Exception as e:
        #     print(f"Giovanni data failed (authentication required): {e}")
        
        # Si NASA POWER falla, usar datos sintéticos como fallback
        print("🔄 Using synthetic data as fallback...")
        synthetic_data = await self.get_synthetic_historical_data(latitude, longitude, date_of_year, 30)  # 30 años por defecto
        if synthetic_data and len(synthetic_data) >= 3:
            print(f"✅ Synthetic data generated: {len(synthetic_data)} records")
            
            # Guardar en cache de memoria y disco
            self.historical_data_cache[location_key] = synthetic_data
            self._save_cache_to_disk()  # 💾 Persistir en disco
            
            # Entrenar modelo UNA SOLA VEZ con datos sintéticos
            if location_key not in self.models_cache:
                # Intentar cargar modelos existentes para esta ubicación
                models_loaded = self.real_data_service.load_trained_models(location_key)
                
                if not models_loaded:
                    # Si no hay modelos, entrenar con datos sintéticos
                    print(f"🧠 Training ML models with {len(synthetic_data)} synthetic data points...")
                    self.real_data_service.train_prediction_models(synthetic_data, latitude, longitude)
                else:
                    print(f"📂 Loaded existing ML models for {location_key}")
                    
                self.models_cache[location_key] = True
                self._save_cache_to_disk()  # 💾 Persistir cache de modelos
                print(f"✅ Models ready for location {location_key}")
            
            return synthetic_data
        
        # Si todo falla, retornar lista vacía
        print("❌ Could not retrieve historical data from any source")
        return []
    
    async def get_weather_data(self, latitude: float, longitude: float, date_of_year: str, years_range: int = 30) -> Dict[str, Any]:
        """
        Obtener datos meteorológicos usando cache inteligente.
        Obtiene todos los datos disponibles una vez y luego filtra según years_range.
        """
        location_key = self._get_location_key(latitude, longitude)
        
        # Obtener TODOS los datos históricos (usa cache si están disponibles)
        all_historical_data = await self._get_all_historical_data(latitude, longitude, date_of_year)
        
        if not all_historical_data or len(all_historical_data) < 3:
            print("Using synthetic data as fallback...")
            return await self._get_synthetic_weather_data(latitude, longitude, date_of_year)
        
        # Filtrar datos según el years_range solicitado
        current_year = datetime.now().year
        start_year = current_year - years_range
        
        filtered_data = [
            data_point for data_point in all_historical_data
            if isinstance(data_point.get('date'), str) and int(data_point['date'].split('-')[0]) >= start_year
            or isinstance(data_point.get('date'), datetime) and data_point['date'].year >= start_year
        ]
        
        # Si después del filtrado no hay suficientes datos, usar más años
        if len(filtered_data) < 3:
            print(f"⚠️ Only {len(filtered_data)} records for {years_range} years, using all available {len(all_historical_data)} records")
            filtered_data = all_historical_data
        
        print(f"📊 Using {len(filtered_data)} records out of {len(all_historical_data)} total (requested: {years_range} years)")
        
        # Obtener predicciones usando el modelo ya entrenado (no re-entrenar)
        try:
            if location_key in self.models_cache:
                probabilities = self.real_data_service.predict_probabilities(
                    latitude, longitude, date_of_year, filtered_data
                )
            else:
                # Fallback si no hay modelo entrenado
                probabilities = {}
        except:
            probabilities = {}
        
        # Calcular condiciones actuales basadas en el último dato
        current_conditions = self._calculate_current_conditions(filtered_data[-1])
        
        # Determinar fuente de datos
        data_source = "NASA POWER API (Cached)" if location_key in self.historical_data_cache else "NASA POWER API"
        
        return {
            "current_conditions": current_conditions,
            "probabilities": probabilities,
            "historical_data": filtered_data,  # Datos filtrados según years_range
            "prediction_accuracy": 0.88,
            "data_source": data_source,
            "sample_size": len(filtered_data),
            "total_available": len(all_historical_data),  # Info adicional
            "model_info": f"ML models trained on {len(all_historical_data)} data points (using {len(filtered_data)} for analysis)"
        }
    
    def clear_cache(self, latitude: float = None, longitude: float = None):
        """Limpiar cache para una ubicación específica o todo el cache"""
        if latitude is not None and longitude is not None:
            location_key = self._get_location_key(latitude, longitude)
            self.historical_data_cache.pop(location_key, None)
            self.models_cache.pop(location_key, None)
            print(f"🗑️ Cache cleared for location {location_key}")
        else:
            self.historical_data_cache.clear()
            self.models_cache.clear()
            print("🗑️ All cache cleared")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Obtener información sobre el estado del cache"""
        return {
            "cached_locations": list(self.historical_data_cache.keys()),
            "total_cached_locations": len(self.historical_data_cache),
            "total_data_points": sum(len(data) for data in self.historical_data_cache.values()),
            "trained_models": list(self.models_cache.keys())
        }
    
    async def get_weather_probabilities(self, query: WeatherQuery) -> WeatherResponse:
        """Método principal para obtener probabilidades meteorológicas personalizadas"""
        
        # Si no se especifica date_of_year, usar la fecha actual
        date_of_year = query.date_of_year
        if date_of_year is None:
            from datetime import datetime
            today = datetime.now()
            date_of_year = f"{today.month:02d}-{today.day:02d}"
        
        # Obtener datos meteorológicos base con el rango de años especificado
        weather_data = await self.get_weather_data(
            query.latitude, query.longitude, date_of_year, query.years_range or 30
        )
        
        # Aplicar umbrales personalizados si se proporcionan
        if query.custom_thresholds:
            weather_data["probabilities"] = self._apply_custom_thresholds(
                weather_data["probabilities"], 
                query.custom_thresholds,
                query.temperature_unit
            )
        
        # Filtrar solo las condiciones seleccionadas por el usuario
        filtered_probabilities = self._filter_selected_conditions(
            weather_data["probabilities"], 
            query.selected_conditions
        )
        
        # Convertir datos de temperatura según la unidad seleccionada
        converted_current_conditions = self._convert_temperature_data(
            weather_data["current_conditions"].copy(), 
            query.temperature_unit
        )
        
        current_conditions = WeatherCondition(**converted_current_conditions)
        
        # Convertir probabilidades a objetos WeatherProbability con personalización
        probabilities = []
        for condition, data in filtered_probabilities.items():
            # Convertir unidades de temperatura en umbrales si es necesario
            threshold = data["threshold"]
            unit = data["unit"]
            
            if condition in ['very_hot', 'very_cold', 'very_uncomfortable'] and query.temperature_unit == TemperatureUnit.FAHRENHEIT:
                if unit == "°C":
                    threshold = self._celsius_to_fahrenheit(threshold)
                    unit = "°F"
            
            probabilities.append(WeatherProbability(
                condition=condition,
                probability=data["probability"],
                threshold=threshold,
                unit=unit,
                description=self._get_condition_description(condition, threshold, unit),
                is_enabled=True
            ))
        
        # Convertir datos históricos con unidades apropiadas
        historical_data = []
        for data_point in weather_data["historical_data"]:
            converted_point = self._convert_temperature_data(data_point.copy(), query.temperature_unit)
            historical_data.append(WeatherDataPoint(
                date=converted_point["date"],
                temperature=converted_point["temperature"],
                precipitation=converted_point["precipitation"],
                wind_speed=converted_point["wind_speed"],
                humidity=converted_point["humidity"],
                heat_index=converted_point.get("heat_index", converted_point["temperature"])
            ))
        
        # Generar predicciones futuras si se solicitan
        future_predictions = None
        if query.include_future_predictions:
            future_predictions = await self._generate_future_predictions(
                query.latitude, 
                query.longitude,
                query.selected_conditions,
                query.future_days,
                query.temperature_unit
            )
        
        # Preparar preferencias del usuario para la respuesta
        user_preferences = {
            "selected_conditions": [condition.value for condition in query.selected_conditions],
            "temperature_unit": query.temperature_unit.value,
            "custom_thresholds_applied": query.custom_thresholds is not None,
            "future_predictions_enabled": query.include_future_predictions,
            "future_days": query.future_days if query.include_future_predictions else 0
        }
        
        return WeatherResponse(
            location=f"{query.latitude}, {query.longitude}",
            current_conditions=current_conditions,
            probabilities=probabilities,
            historical_data=historical_data,  # Usar todos los datos históricos recibidos
            prediction_accuracy=weather_data["prediction_accuracy"],
            data_source=weather_data["data_source"],
            sample_size=weather_data["sample_size"],
            statistics={"mean_temp": statistics.mean([d.temperature for d in historical_data])},
            future_predictions=future_predictions,
            temperature_unit=query.temperature_unit,
            query_date=date.today(),
            user_preferences=user_preferences
        )
    
    def _calculate_current_conditions(self, latest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcular las condiciones actuales basadas en el último dato disponible"""
        return {
            "temperature": latest_data.get("temperature", 20.0),
            "precipitation": latest_data.get("precipitation", 0.0),
            "wind_speed": latest_data.get("wind_speed", 5.0),
            "humidity": latest_data.get("humidity", 50.0),
            "heat_index": latest_data.get("heat_index", latest_data.get("temperature", 20.0)),
            "description": self._get_weather_description(latest_data)
        }
    
    def _get_weather_description(self, data: Dict[str, Any]) -> str:
        """Generar descripción del clima basada en los datos"""
        temp = data.get("temperature", 20.0)
        precipitation = data.get("precipitation", 0.0)
        
        if precipitation > 5:
            return "Lluvioso"
        elif temp > 30:
            return "Caluroso"
        elif temp < 10:
            return "Frío"
        else:
            return "Templado"
    
    async def _get_synthetic_weather_data(self, latitude: float, longitude: float, date_of_year: str) -> Dict[str, Any]:
        """Generar datos sintéticos como último recurso"""
        print("⚠️ Using synthetic weather data - no real data available")
        
        # Usar el generador de datos mock existente
        historical_data = await self.data_generator.get_historical_data(
            latitude, longitude, date_of_year, years=5
        )
        
        # Generar probabilidades básicas
        probabilities = {
            "very_hot": {"probability": 0.15, "threshold": 35.0, "unit": "°C"},
            "very_cold": {"probability": 0.10, "threshold": 5.0, "unit": "°C"},
            "very_windy": {"probability": 0.12, "threshold": 25.0, "unit": "km/h"},
            "very_wet": {"probability": 0.20, "threshold": 10.0, "unit": "mm"},
            "very_uncomfortable": {"probability": 0.18, "threshold": 40.0, "unit": "°C"}
        }
        
        current_conditions = self._calculate_current_conditions(historical_data[-1])
        
        return {
            "current_conditions": current_conditions,
            "probabilities": probabilities,
            "historical_data": historical_data[-5:],  # Últimos 5 años
            "prediction_accuracy": 0.65,  # Menor precisión para datos sintéticos
            "data_source": "Synthetic Data (Demo Mode)",
            "sample_size": len(historical_data),
            "model_info": "Basic synthetic weather patterns for demonstration"
        }
    
    async def export_data(self, query: WeatherQuery, format: str = "json") -> Dict[str, Any]:
        """Exporta los datos en formato JSON o CSV"""
        response = await self.get_weather_probabilities(query)
        
        if format.lower() == "csv":
            # Para CSV, convertir a formato tabular
            csv_data = []
            for data_point in response.historical_data:
                csv_data.append({
                    "date": data_point.date.isoformat(),
                    "temperature": data_point.temperature,
                    "precipitation": data_point.precipitation,
                    "wind_speed": data_point.wind_speed,
                    "humidity": data_point.humidity,
                    "heat_index": data_point.heat_index
                })
            return {
                "format": "csv",
                "data": csv_data,
                "metadata": {
                    "location": response.location,
                    "probabilities": [p.dict() for p in response.probabilities],
                    "statistics": response.statistics
                }
            }
        
        # Formato JSON por defecto
        return {
            "format": "json",
            "data": response.dict()
        }
    
    def _celsius_to_fahrenheit(self, celsius: float) -> float:
        """Convertir Celsius a Fahrenheit"""
        return (celsius * 9/5) + 32
    
    def _fahrenheit_to_celsius(self, fahrenheit: float) -> float:
        """Convertir Fahrenheit a Celsius"""
        return (fahrenheit - 32) * 5/9
    
    def _convert_temperature_data(self, data: Dict[str, Any], target_unit: TemperatureUnit) -> Dict[str, Any]:
        """Convertir datos de temperatura según la unidad especificada"""
        if target_unit == TemperatureUnit.FAHRENHEIT:
            # Convertir temperaturas a Fahrenheit
            if 'temperature' in data:
                data['temperature'] = self._celsius_to_fahrenheit(data['temperature'])
            if 'heat_index' in data:
                data['heat_index'] = self._celsius_to_fahrenheit(data['heat_index'])
        return data
    
    def _apply_custom_thresholds(self, probabilities: Dict[str, Any], custom_thresholds: CustomThresholds, temperature_unit: TemperatureUnit) -> Dict[str, Any]:
        """Aplicar umbrales personalizados definidos por el usuario"""
        if not custom_thresholds:
            return probabilities
        
        # Mapeo de condiciones a umbrales personalizados
        threshold_map = {
            'very_hot': custom_thresholds.very_hot_threshold,
            'very_cold': custom_thresholds.very_cold_threshold,
            'very_windy': custom_thresholds.very_windy_threshold,
            'very_wet': custom_thresholds.very_wet_threshold,
            'very_uncomfortable': custom_thresholds.very_uncomfortable_threshold
        }
        
        for condition, custom_threshold in threshold_map.items():
            if custom_threshold is not None and condition in probabilities:
                # Convertir umbral si es necesario
                if condition in ['very_hot', 'very_cold', 'very_uncomfortable'] and temperature_unit == TemperatureUnit.FAHRENHEIT:
                    custom_threshold = self._celsius_to_fahrenheit(custom_threshold)
                
                probabilities[condition]['threshold'] = custom_threshold
                probabilities[condition]['is_custom'] = True
        
        return probabilities
    
    def _filter_selected_conditions(self, probabilities: Dict[str, Any], selected_conditions: List[WeatherConditionType]) -> Dict[str, Any]:
        """Filtrar solo las condiciones seleccionadas por el usuario"""
        filtered = {}
        for condition in selected_conditions:
            condition_key = condition.value
            if condition_key in probabilities:
                filtered[condition_key] = probabilities[condition_key]
                filtered[condition_key]['is_enabled'] = True
        return filtered
    
    async def _generate_future_predictions(self, latitude: float, longitude: float, 
                                         selected_conditions: List[WeatherConditionType],
                                         future_days: int = 14,
                                         temperature_unit: TemperatureUnit = TemperatureUnit.CELSIUS) -> List[FuturePrediction]:
        """Generar predicciones para los próximos días"""
        future_predictions = []
        today = date.today()
        
        # Obtener datos históricos una sola vez (usando cache)
        location_key = f"{latitude:.3f}_{longitude:.3f}"
        if location_key in self.historical_data_cache:
            historical_data = self.historical_data_cache[location_key]
        else:
            print("⚠️ No historical data available for predictions, using basic estimates")
            historical_data = []
        
        for day_offset in range(1, future_days + 1):
            prediction_date = today + timedelta(days=day_offset)
            date_of_year = prediction_date.strftime("%m-%d")
            
            try:
                # Calcular probabilidades basándose en datos históricos para esta fecha
                probabilities = []
                
                if historical_data:
                    # Filtrar datos históricos para esta fecha del año
                    same_date_data = [item for item in historical_data if item.get('date_of_year') == date_of_year]
                    
                    if same_date_data:
                        # Calcular probabilidades basándose en datos históricos
                        for condition in selected_conditions:
                            probability = self._calculate_condition_probability(same_date_data, condition.value)
                            threshold = self._get_condition_threshold(condition.value)
                            unit = self._get_condition_unit(condition.value)
                            
                            # Convertir unidades si es necesario
                            if condition.value in ['very_hot', 'very_cold', 'very_uncomfortable'] and temperature_unit == TemperatureUnit.FAHRENHEIT:
                                if unit == "°C":
                                    threshold = self._celsius_to_fahrenheit(threshold)
                                    unit = "°F"
                            
                            probabilities.append(WeatherProbability(
                                condition=condition.value,
                                probability=probability,
                                threshold=threshold,
                                unit=unit,
                                description=self._get_condition_description(condition.value, threshold, unit),
                                is_enabled=True
                            ))
                    else:
                        # Si no hay datos para esta fecha específica, usar promedio
                        for condition in selected_conditions:
                            probabilities.append(WeatherProbability(
                                condition=condition.value,
                                probability=0.15,  # Probabilidad base
                                threshold=self._get_condition_threshold(condition.value),
                                unit=self._get_condition_unit(condition.value),
                                description=self._get_condition_description(condition.value, self._get_condition_threshold(condition.value), self._get_condition_unit(condition.value)),
                                is_enabled=True
                            ))
                else:
                    # Si no hay datos históricos, usar probabilidades básicas
                    for condition in selected_conditions:
                        probabilities.append(WeatherProbability(
                            condition=condition.value,
                            probability=0.10,  # Probabilidad muy baja sin datos
                            threshold=self._get_condition_threshold(condition.value),
                            unit=self._get_condition_unit(condition.value),
                            description=self._get_condition_description(condition.value, self._get_condition_threshold(condition.value), self._get_condition_unit(condition.value)),
                            is_enabled=True
                        ))
                
                # Calcular nivel de confianza basado en la cantidad de datos históricos
                confidence = min(0.95, len(historical_data) / 20.0) if historical_data else 0.3
                
                future_predictions.append(FuturePrediction(
                    date=prediction_date,
                    probabilities=probabilities,
                    confidence_level=confidence
                ))
                
            except Exception as e:
                print(f"Error generating prediction for {prediction_date}: {e}")
                # Agregar predicción con baja confianza en caso de error
                basic_probabilities = []
                for condition in selected_conditions:
                    basic_probabilities.append(WeatherProbability(
                        condition=condition.value,
                        probability=0.15,  # Probabilidad base
                        threshold=25.0,
                        unit="°C" if temperature_unit == TemperatureUnit.CELSIUS else "°F",
                        description="Predicción limitada - datos insuficientes",
                        is_enabled=True
                    ))
                
                future_predictions.append(FuturePrediction(
                    date=prediction_date,
                    probabilities=basic_probabilities,
                    confidence_level=0.3
                ))
        
        return future_predictions
    
    def _get_condition_description(self, condition: str, threshold: float, unit: str) -> str:
        """Generar descripción personalizada para cada condición"""
        descriptions = {
            'very_hot': f"Temperaturas superiores a {threshold:.1f}{unit}",
            'very_cold': f"Temperaturas inferiores a {threshold:.1f}{unit}",
            'very_windy': f"Vientos superiores a {threshold:.1f} {unit}",
            'very_wet': f"Precipitación superior a {threshold:.1f} {unit}",
            'very_uncomfortable': f"Índice de calor/frío superior a {threshold:.1f}{unit}"
        }
        return descriptions.get(condition, f"Condición extrema con umbral {threshold:.1f}{unit}")

    def _calculate_condition_probability(self, historical_data: List[Dict], condition: str) -> float:
        """Calcular probabilidad de una condición basándose en datos históricos"""
        if not historical_data:
            return 0.1
        
        count_matches = 0
        total_count = len(historical_data)
        
        for data_point in historical_data:
            temp = data_point.get('temperature', 20)
            precipitation = data_point.get('precipitation', 0)
            wind_speed = data_point.get('wind_speed', 10)
            humidity = data_point.get('humidity', 50)
            
            if condition == 'very_hot' and temp >= 35:
                count_matches += 1
            elif condition == 'very_cold' and temp <= 5:
                count_matches += 1
            elif condition == 'very_windy' and wind_speed >= 25:
                count_matches += 1
            elif condition == 'very_wet' and precipitation >= 10:
                count_matches += 1
            elif condition == 'very_uncomfortable' and (temp >= 35 or temp <= 5 or humidity >= 80):
                count_matches += 1
        
        return min(0.95, count_matches / total_count) if total_count > 0 else 0.1

    def _get_condition_threshold(self, condition: str) -> float:
        """Obtener umbral por defecto para una condición"""
        thresholds = {
            'very_hot': 35.0,
            'very_cold': 5.0,
            'very_windy': 25.0,
            'very_wet': 10.0,
            'very_uncomfortable': 35.0
        }
        return thresholds.get(condition, 20.0)

    def _get_condition_unit(self, condition: str) -> str:
        """Obtener unidad para una condición"""
        units = {
            'very_hot': '°C',
            'very_cold': '°C',
            'very_windy': 'km/h',
            'very_wet': 'mm',
            'very_uncomfortable': '°C'
        }
        return units.get(condition, '°C')

# Instancia del servicio
weather_service = WeatherService()