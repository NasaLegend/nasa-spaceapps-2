from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
from app.models.weather import (
    WeatherQuery, WeatherResponse, WeatherConditionType, 
    TemperatureUnit, CustomThresholds
)
from app.services.weather_service import weather_service, WeatherService

router = APIRouter()

@router.post("/probability", response_model=WeatherResponse)
async def get_weather_probability(query: WeatherQuery):
    """
    Obtiene las probabilidades de condiciones climáticas específicas
    para una ubicación y fecha determinada con personalización completa.
    
    Características nuevas:
    - Selección personalizada de condiciones a analizar
    - Unidades de temperatura (Celsius/Fahrenheit) 
    - Umbrales personalizados
    - Predicciones futuras (hasta 2 semanas)
    """
    try:
        result = await weather_service.get_weather_probabilities(query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/probability/{latitude}/{longitude}")
async def get_weather_probability(
    latitude: float, 
    longitude: float,
    date_of_year: Optional[int] = None
):
    """
    Obtiene la probabilidad del clima para coordenadas específicas
    
    Args:
        latitude: Latitud (-90 a 90)
        longitude: Longitud (-180 a 180)  
        date_of_year: Día del año (1-365, opcional - usa fecha actual si no se proporciona)
    
    Returns:
        Probabilidad del clima con predicciones de ML
    """
    
    # Si no se proporciona fecha, usar el día actual del año
    if date_of_year is None:
        today = datetime.now()
        date_of_year = today.timetuple().tm_yday
    
    try:
        weather_service_instance = WeatherService()
        result = await weather_service_instance.get_weather_probability(latitude, longitude, date_of_year)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/probability-simple")
async def post_weather_probability_simple(query: WeatherQuery):
    """
    Obtiene la probabilidad del clima usando POST
    """
    # Si no se proporciona fecha, usar el día actual del año
    date_of_year = query.date_of_year
    if date_of_year is None:
        today = datetime.now()
        date_of_year = today.timetuple().tm_yday
    
    try:
        weather_service_instance = WeatherService()
        result = await weather_service_instance.get_weather_probability(
            query.latitude, 
            query.longitude, 
            date_of_year
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-metrics/{latitude}/{longitude}")
async def get_model_metrics(latitude: float, longitude: float):
    """
    Obtiene las métricas detalladas de los modelos de ML para una ubicación específica
    
    Args:
        latitude: Latitud (-90 a 90)
        longitude: Longitud (-180 a 180)
    
    Returns:
        Métricas completas de todos los modelos entrenados para esa ubicación
    """
    try:
        from app.data.real_weather_data import RealWeatherDataService
        
        weather_data_service = RealWeatherDataService()
        
        # Cargar modelos para esta ubicación
        location_key = f"{round(latitude, 3)}_{round(longitude, 3)}"
        models_loaded = weather_data_service.load_trained_models(location_key)
        
        if not models_loaded:
            raise HTTPException(
                status_code=404, 
                detail=f"No trained models found for location {latitude}, {longitude}. Train models first by making a prediction request."
            )
        
        # Obtener métricas
        metrics = weather_data_service.get_model_metrics()
        
        if not metrics or not any(metrics.values()):
            raise HTTPException(
                status_code=404, 
                detail="No model metrics available. Models need to be retrained."
            )
        
        # Agregar información adicional
        total_models = sum(1 for m in metrics.values() if m)
        
        return {
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "location_key": location_key
            },
            "summary": {
                "total_models": total_models,
                "models_available": list(metrics.keys()),
                "all_models_trained": all(metrics.values())
            },
            "metrics": metrics,
            "interpretation": {
                "regression_models": [k for k, v in metrics.items() if v and v.get('model_type') == 'regression'],
                "classification_models": [k for k, v in metrics.items() if v and v.get('model_type') == 'classification'],
                "best_performing": _get_best_performing_models(metrics)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving model metrics: {str(e)}")

def _get_best_performing_models(metrics: dict) -> dict:
    """Identifica los modelos con mejor rendimiento"""
    best_models = {
        "best_regression": None,
        "best_classification": None
    }
    
    best_r2 = -1
    best_f1 = -1
    
    for model_name, model_metrics in metrics.items():
        if not model_metrics:
            continue
            
        if model_metrics.get('model_type') == 'regression':
            r2_score = model_metrics.get('test_metrics', {}).get('r2_score', -1)
            if r2_score > best_r2:
                best_r2 = r2_score
                best_models["best_regression"] = {
                    "model": model_name,
                    "r2_score": r2_score,
                    "rmse": model_metrics.get('test_metrics', {}).get('rmse', 'N/A')
                }
        
        elif model_metrics.get('model_type') == 'classification':
            f1_score = model_metrics.get('test_metrics', {}).get('f1_score', -1)
            if f1_score > best_f1:
                best_f1 = f1_score
                best_models["best_classification"] = {
                    "model": model_name,
                    "f1_score": f1_score,
                    "accuracy": model_metrics.get('test_metrics', {}).get('accuracy', 'N/A')
                }
    
    return best_models

@router.get("/analysis/{latitude}/{longitude}")
async def get_custom_analysis(
    latitude: float,
    longitude: float, 
    metrics: str = "temperature,precipitation,wind_speed",
    format: str = "json"
):
    """
    Obtiene análisis personalizado del clima
    """
    metrics_list = [m.strip() for m in metrics.split(",")]
    
    try:
        weather_service_instance = WeatherService()
        
        # Usar fecha actual
        today = datetime.now()
        date_of_year = today.timetuple().tm_yday
        
        result = await weather_service_instance.get_weather_probability(latitude, longitude, date_of_year)
        
        # Filtrar métricas solicitadas
        filtered_result = {}
        if "temperature" in metrics_list and "temperature" in result:
            filtered_result["temperature"] = result["temperature"]
        if "precipitation" in metrics_list and "precipitation" in result:
            filtered_result["precipitation"] = result["precipitation"]
        if "wind_speed" in metrics_list and "wind_speed" in result:
            filtered_result["wind_speed"] = result["wind_speed"]
        if "humidity" in metrics_list and "humidity" in result:
            filtered_result["humidity"] = result["humidity"]
        
        # Agregar metadatos
        filtered_result["metadata"] = {
            "location": {"latitude": latitude, "longitude": longitude},
            "date_of_year": date_of_year,
            "requested_metrics": metrics_list,
            "format": format
        }
        
        return filtered_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/custom-analysis")
async def custom_weather_analysis(
    latitude: float,
    longitude: float,
    selected_conditions: List[WeatherConditionType],
    date_of_year: Optional[str] = None,
    temperature_unit: TemperatureUnit = TemperatureUnit.CELSIUS,
    custom_thresholds: Optional[CustomThresholds] = None,
    include_future_predictions: bool = True,
    future_days: int = 14  # máximo 60 días
):
    """
    Análisis meteorológico completamente personalizado para eventos al aire libre.
    
    Perfecto para planificar:
    - Vacaciones
    - Caminatas en senderos  
    - Pesca en lagos
    - Eventos deportivos
    - Cualquier actividad al aire libre
    """
    try:
        # Si no se especifica date_of_year, usar la fecha actual
        if date_of_year is None:
            today = datetime.now()
            date_of_year = f"{today.month:02d}-{today.day:02d}"
            
        query = WeatherQuery(
            latitude=latitude,
            longitude=longitude,
            date_of_year=date_of_year,
            selected_conditions=selected_conditions,
            temperature_unit=temperature_unit,
            custom_thresholds=custom_thresholds,
            include_future_predictions=include_future_predictions,
            future_days=min(future_days, 60)
        )
        
        result = await weather_service.get_weather_probabilities(query)
        
        # Agregar información adicional para análisis personalizado
        analysis_summary = {
            "outdoor_activity_suitability": _calculate_activity_suitability(result.probabilities),
            "best_days_ahead": _find_best_future_days(result.future_predictions) if result.future_predictions else [],
            "risk_assessment": _assess_weather_risks(result.probabilities),
            "recommendations": _generate_recommendations(result.probabilities, selected_conditions)
        }
        
        # Agregar resumen al response
        result.user_preferences["analysis_summary"] = analysis_summary
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/export")
async def export_weather_data(
    query: WeatherQuery,
    format: str = Query("json", description="Formato de exportación: json o csv")
):
    """
    Exporta los datos meteorológicos en formato JSON o CSV.
    """
    try:
        if format.lower() not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Formato debe ser 'json' o 'csv'")
        
        result = await weather_service.export_data(query, format)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conditions")
async def get_available_conditions():
    """
    Obtiene la lista de condiciones climáticas disponibles.
    """
    return {
        "conditions": [
            {"id": "very_hot", "name": "Muy Caliente", "description": "Temperaturas extremadamente altas"},
            {"id": "very_cold", "name": "Muy Frío", "description": "Temperaturas extremadamente bajas"},
            {"id": "very_windy", "name": "Muy Ventoso", "description": "Vientos fuertes"},
            {"id": "very_wet", "name": "Muy Húmedo", "description": "Alta precipitación"},
            {"id": "very_uncomfortable", "name": "Muy Incómodo", "description": "Índice de calor alto"}
        ],
        "variables": [
            {"id": "temperature", "name": "Temperatura", "unit": "°C"},
            {"id": "precipitation", "name": "Precipitación", "unit": "mm"},
            {"id": "wind_speed", "name": "Velocidad del Viento", "unit": "km/h"},
            {"id": "humidity", "name": "Humedad", "unit": "%"},
            {"id": "heat_index", "name": "Índice de Calor", "unit": "°C"}
        ]
    }

# Funciones helper para análisis personalizado
def _calculate_activity_suitability(probabilities: List) -> dict:
    """Calcula la idoneidad para actividades al aire libre"""
    # Calcular riesgo promedio basado en todas las probabilidades
    total_risk = sum(prob.probability for prob in probabilities)
    avg_risk = total_risk / len(probabilities) if probabilities else 0
    
    if avg_risk < 0.2:
        suitability = "Excelente"
        score = 95
    elif avg_risk < 0.4:
        suitability = "Bueno"
        score = 75
    elif avg_risk < 0.6:
        suitability = "Moderado"
        score = 55
    elif avg_risk < 0.8:
        suitability = "Precaución"
        score = 35
    else:
        suitability = "No recomendado"
        score = 15
    
    return {
        "overall_suitability": suitability,
        "score": score,
        "risk_level": avg_risk,
        "recommendation": f"Condiciones {suitability.lower()} para actividades al aire libre"
    }

def _find_best_future_days(future_predictions: List) -> List[dict]:
    """Encuentra los mejores días en las predicciones futuras"""
    if not future_predictions:
        return []
    
    # Calcular score para cada día
    day_scores = []
    for prediction in future_predictions:
        total_risk = sum(prob.probability for prob in prediction.probabilities)
        avg_risk = total_risk / len(prediction.probabilities) if prediction.probabilities else 0
        score = (1 - avg_risk) * prediction.confidence_level * 100
        
        day_scores.append({
            "date": prediction.date.isoformat(),
            "score": score,
            "confidence": prediction.confidence_level,
            "risk_level": avg_risk,
            "suitability": "Excelente" if score > 80 else "Bueno" if score > 60 else "Moderado"
        })
    
    # Ordenar por score y retornar los 5 mejores
    day_scores.sort(key=lambda x: x["score"], reverse=True)
    return day_scores[:5]

def _assess_weather_risks(probabilities: List) -> dict:
    """Evalúa los riesgos meteorológicos específicos"""
    risks = {
        "high_risk_conditions": [],
        "moderate_risk_conditions": [],
        "low_risk_conditions": [],
        "overall_risk": "Bajo"
    }
    
    high_risk_count = 0
    moderate_risk_count = 0
    
    for prob in probabilities:
        risk_item = {
            "condition": prob.condition,
            "probability": prob.probability,
            "threshold": prob.threshold,
            "unit": prob.unit
        }
        
        if prob.probability > 0.7:
            risks["high_risk_conditions"].append(risk_item)
            high_risk_count += 1
        elif prob.probability > 0.4:
            risks["moderate_risk_conditions"].append(risk_item)
            moderate_risk_count += 1
        else:
            risks["low_risk_conditions"].append(risk_item)
    
    # Determinar riesgo general
    if high_risk_count > 0:
        risks["overall_risk"] = "Alto"
    elif moderate_risk_count > 2:
        risks["overall_risk"] = "Moderado"
    elif moderate_risk_count > 0:
        risks["overall_risk"] = "Bajo-Moderado"
    
    return risks

def _generate_recommendations(probabilities: List, selected_conditions: List) -> List[str]:
    """Genera recomendaciones basadas en las condiciones analizadas"""
    recommendations = []
    
    # Recomendaciones específicas por condición
    condition_advice = {
        "very_hot": {
            "high": "Evite actividades al aire libre durante las horas más calurosas (10 AM - 4 PM)",
            "moderate": "Manténgase hidratado y busque sombra frecuentemente",
            "low": "Condiciones de temperatura favorables"
        },
        "very_cold": {
            "high": "Use ropa térmica adecuada y limite el tiempo de exposición",
            "moderate": "Vista en capas y proteja extremidades del frío",
            "low": "Temperaturas cómodas para actividades al aire libre"
        },
        "very_windy": {
            "high": "Evite actividades en altura o cerca del agua. Asegure objetos sueltos",
            "moderate": "Tome precauciones adicionales y esté atento a ráfagas",
            "low": "Vientos ligeros, condiciones estables"
        },
        "very_wet": {
            "high": "Postponga actividades al aire libre o planifique refugios",
            "moderate": "Lleve equipo impermeable y esté preparado para lluvia",
            "low": "Tiempo seco esperado"
        },
        "very_uncomfortable": {
            "high": "Considere actividades en interiores o con climatización",
            "moderate": "Tome descansos frecuentes y manténgase hidratado",
            "low": "Condiciones de confort adecuadas"
        }
    }
    
    for prob in probabilities:
        condition = prob.condition
        if condition in condition_advice:
            if prob.probability > 0.6:
                recommendations.append(condition_advice[condition]["high"])
            elif prob.probability > 0.3:
                recommendations.append(condition_advice[condition]["moderate"])
            else:
                recommendations.append(condition_advice[condition]["low"])
    
    # Recomendación general
    avg_risk = sum(prob.probability for prob in probabilities) / len(probabilities) if probabilities else 0
    if avg_risk < 0.3:
        recommendations.insert(0, "🌟 Excelentes condiciones para actividades al aire libre!")
    elif avg_risk < 0.6:
        recommendations.insert(0, "⚠️ Condiciones moderadas - tome precauciones normales")
    else:
        recommendations.insert(0, "⛔ Condiciones adversas - considere postponer actividades al aire libre")
    
    return recommendations