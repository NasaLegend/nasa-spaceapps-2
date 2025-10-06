from fastapi import APIRouter
from typing import List
from app.models.location import Location

router = APIRouter()

# Ubicaciones populares predefinidas
POPULAR_LOCATIONS = [
    {
        "id": 1,
        "name": "Ciudad de México",
        "country": "México",
        "latitude": 19.433,
        "longitude": -99.133,
        "timezone": "America/Mexico_City"
    },
    {
        "id": 2,
        "name": "Madrid",
        "country": "España", 
        "latitude": 40.417,
        "longitude": -3.704,
        "timezone": "Europe/Madrid"
    },
    {
        "id": 3,
        "name": "Barcelona", 
        "country": "España",
        "latitude": 41.385,
        "longitude": 2.173,
        "timezone": "Europe/Madrid"
    },
    {
        "id": 4,
        "name": "Nueva York",
        "country": "Estados Unidos",
        "latitude": 40.714,
        "longitude": -74.006,
        "timezone": "America/New_York"
    },
    {
        "id": 5,
        "name": "Londres",
        "country": "Reino Unido",
        "latitude": 51.508,
        "longitude": -0.128,
        "timezone": "Europe/London"
    },
    {
        "id": 6,
        "name": "Tokio",
        "country": "Japón",
        "latitude": 35.676,
        "longitude": 139.650,
        "timezone": "Asia/Tokyo"
    },
    {
        "id": 7,
        "name": "París",
        "country": "Francia",
        "latitude": 48.857,
        "longitude": 2.295,
        "timezone": "Europe/Paris"
    },
    {
        "id": 8,
        "name": "São Paulo",
        "country": "Brasil",
        "latitude": -23.551,
        "longitude": -46.633,
        "timezone": "America/Sao_Paulo"
    }
]

@router.get("/popular")
async def get_popular_locations():
    """
    Obtiene la lista de ubicaciones populares predefinidas.
    
    Returns:
        Lista de ubicaciones con coordenadas y información básica
    """
    return {
        "locations": POPULAR_LOCATIONS,
        "total": len(POPULAR_LOCATIONS),
        "description": "Ubicaciones populares con modelos pre-entrenados disponibles"
    }

@router.get("/search")
async def search_locations(query: str):
    """
    Busca ubicaciones por nombre.
    
    Args:
        query: Término de búsqueda para filtrar ubicaciones
        
    Returns:
        Lista de ubicaciones que coinciden con la búsqueda
    """
    query_lower = query.lower()
    filtered_locations = [
        location for location in POPULAR_LOCATIONS
        if query_lower in location["name"].lower() or query_lower in location["country"].lower()
    ]
    
    return {
        "locations": filtered_locations,
        "total": len(filtered_locations),
        "query": query,
        "description": f"Resultados de búsqueda para '{query}'"
    }

@router.get("/by-coordinates")
async def get_location_by_coordinates(latitude: float, longitude: float, radius: float = 50.0):
    """
    Encuentra ubicaciones cercanas a las coordenadas especificadas.
    
    Args:
        latitude: Latitud de referencia
        longitude: Longitud de referencia
        radius: Radio de búsqueda en kilómetros (por defecto 50km)
        
    Returns:
        Lista de ubicaciones dentro del radio especificado
    """
    import math
    
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calcula la distancia entre dos puntos usando la fórmula de Haversine"""
        R = 6371  # Radio de la Tierra en kilómetros
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    nearby_locations = []
    for location in POPULAR_LOCATIONS:
        distance = calculate_distance(
            latitude, longitude,
            location["latitude"], location["longitude"]
        )
        
        if distance <= radius:
            location_with_distance = location.copy()
            location_with_distance["distance_km"] = round(distance, 2)
            nearby_locations.append(location_with_distance)
    
    # Ordenar por distancia
    nearby_locations.sort(key=lambda x: x["distance_km"])
    
    return {
        "locations": nearby_locations,
        "total": len(nearby_locations),
        "reference_point": {"latitude": latitude, "longitude": longitude},
        "radius_km": radius,
        "description": f"Ubicaciones dentro de {radius}km de ({latitude}, {longitude})"
    }

@router.get("/trained-models")
async def get_locations_with_trained_models():
    """
    Obtiene las ubicaciones que tienen modelos de ML entrenados disponibles.
    
    Returns:
        Lista de ubicaciones con modelos pre-entrenados
    """
    import os
    from app.core.config import settings
    
    models_dir = os.path.join(settings.PROJECT_ROOT, "models")
    trained_locations = []
    
    # Verificar qué ubicaciones tienen modelos entrenados
    for location in POPULAR_LOCATIONS:
        location_key = f"{round(location['latitude'], 3)}_{round(location['longitude'], 3)}"
        location_models_dir = os.path.join(models_dir, location_key)
        
        if os.path.exists(location_models_dir):
            # Verificar que existen los archivos de modelo necesarios
            required_models = [
                "temperature_predictor.pkl",
                "humidity_predictor.pkl", 
                "wind_predictor.pkl",
                "precipitation_classifier.pkl",
                "scalers.pkl"
            ]
            
            available_models = []
            for model_file in required_models:
                model_path = os.path.join(location_models_dir, model_file)
                if os.path.exists(model_path):
                    available_models.append(model_file)
            
            if len(available_models) >= 3:  # Al menos 3 modelos disponibles
                location_with_models = location.copy()
                location_with_models["location_key"] = location_key
                location_with_models["available_models"] = available_models
                location_with_models["model_completeness"] = len(available_models) / len(required_models)
                trained_locations.append(location_with_models)
    
    return {
        "locations": trained_locations,
        "total": len(trained_locations),
        "description": "Ubicaciones con modelos de Machine Learning pre-entrenados",
        "model_types": [
            "temperature_predictor",
            "humidity_predictor", 
            "wind_predictor",
            "precipitation_classifier",
            "scalers"
        ]
    }