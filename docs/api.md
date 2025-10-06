# API Documentation

## Endpoints Overview

### Weather Endpoints

#### POST /api/weather/probability
Obtiene las probabilidades de condiciones climáticas para una consulta específica.

**Request Body:**
```json
{
  "latitude": 40.4168,
  "longitude": -3.7038,
  "date_of_year": "07-15",
  "variables": ["temperature", "precipitation", "wind_speed", "humidity"],
  "years_range": 30
}
```

**Response:**
```json
{
  "location": {
    "latitude": 40.4168,
    "longitude": -3.7038,
    "climate_zone": "temperate"
  },
  "date_of_year": "07-15",
  "probabilities": [
    {
      "condition": "very_hot",
      "probability": 0.25,
      "threshold_value": 35.2,
      "unit": "°C"
    }
  ],
  "historical_data": [...],
  "statistics": {...}
}
```

#### GET /api/weather/probability
Versión GET del endpoint de probabilidades.

**Parameters:**
- `latitude` (float): Latitud de la ubicación
- `longitude` (float): Longitud de la ubicación  
- `date_of_year` (string): Fecha en formato MM-DD
- `years_range` (int, optional): Años de datos históricos (default: 30)

#### POST /api/weather/export
Exporta datos meteorológicos en formato JSON o CSV.

**Parameters:**
- `format` (string): "json" o "csv"

**Request Body:** Mismo que `/probability`

#### GET /api/weather/conditions
Obtiene las condiciones climáticas disponibles y variables meteorológicas.

**Response:**
```json
{
  "conditions": [
    {
      "id": "very_hot",
      "name": "Muy Caliente",
      "description": "Temperaturas extremadamente altas"
    }
  ],
  "variables": [
    {
      "id": "temperature",
      "name": "Temperatura",
      "unit": "°C"
    }
  ]
}
```

### Location Endpoints

#### GET /api/locations/search
Busca ubicaciones por nombre.

**Parameters:**
- `query` (string): Término de búsqueda
- `limit` (int, optional): Máximo número de resultados (default: 10)

**Response:**
```json
{
  "locations": [
    {
      "latitude": 40.4168,
      "longitude": -3.7038,
      "name": "Madrid",
      "country": "España"
    }
  ],
  "total": 1
}
```

#### GET /api/locations/coordinates
Obtiene información de ubicación por coordenadas.

**Parameters:**
- `latitude` (float): Latitud
- `longitude` (float): Longitud

#### GET /api/locations/popular
Obtiene una lista de ubicaciones populares.

## Error Handling

Todos los endpoints pueden devolver los siguientes errores:

- `400 Bad Request`: Parámetros inválidos
- `404 Not Found`: Recurso no encontrado
- `500 Internal Server Error`: Error interno del servidor

**Error Response Format:**
```json
{
  "detail": "Descripción del error"
}
```

## Rate Limiting

Currently no rate limiting is implemented, but it's recommended for production use.

## Authentication

Currently no authentication is required, but it should be implemented for production use.