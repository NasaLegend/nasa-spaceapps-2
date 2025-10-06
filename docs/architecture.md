# Arquitectura del Sistema

## Visión General

La aplicación Weather Probability App está diseñada con una arquitectura de microservicios separando claramente el frontend (React) del backend (FastAPI), permitiendo escalabilidad y mantenimiento independiente de cada componente.

## Arquitectura de Alto Nivel

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐
│                 │ ────────────── │                 │
│   React App     │                │   FastAPI       │
│   (Frontend)    │ ←────────────── │   (Backend)     │
│                 │    JSON Data    │                 │
└─────────────────┘                └─────────────────┘
         │                                    │
         │                                    │
         ▼                                    ▼
┌─────────────────┐                ┌─────────────────┐
│   Static Files  │                │   Data Layer    │
│   (Build)       │                │   (Mock/NASA)   │
└─────────────────┘                └─────────────────┘
```

## Backend Architecture (FastAPI)

### Estructura en Capas

```
app/
├── main.py              # Entry point & FastAPI app
├── api/                 # API endpoints (Controllers)
│   ├── weather.py       # Weather-related endpoints
│   └── locations.py     # Location-related endpoints
├── services/            # Business logic layer
│   ├── weather_service.py
│   └── ml_service.py
├── models/              # Data models (Pydantic)
│   ├── weather.py
│   └── location.py
├── core/                # Configuration & utilities
│   └── config.py
└── data/                # Data access layer
    └── mock_weather_data.py
```

### Principios de Diseño

1. **Separation of Concerns**: Cada capa tiene responsabilidades específicas
2. **Dependency Injection**: Servicios inyectados como dependencias
3. **Type Safety**: Uso extensivo de Pydantic para validación
4. **Async/Await**: Operaciones asíncronas para mejor performance

### Componentes Principales

#### API Layer
- **Responsabilidad**: Validación de entrada, serialización/deserialización
- **Tecnología**: FastAPI routers
- **Patrones**: RESTful endpoints, OpenAPI documentation

#### Service Layer
- **Responsabilidad**: Lógica de negocio, cálculos de probabilidades
- **Tecnología**: Python, NumPy, Pandas
- **Patrones**: Service pattern, Strategy pattern para diferentes algoritmos

#### Data Layer
- **Responsabilidad**: Acceso a datos (mock/NASA APIs)
- **Tecnología**: Pandas para manipulación de datos
- **Patrones**: Repository pattern, Data generation

## Frontend Architecture (React)

### Estructura de Componentes

```
src/
├── components/          # React components
│   ├── Dashboard/       # Main dashboard
│   ├── LocationPicker/  # Location selection
│   ├── WeatherChart/    # Data visualization
│   ├── ProbabilityDisplay/
│   └── DataExport/
├── services/            # API communication
│   ├── api.js          # Axios configuration
│   └── weatherService.js
├── utils/               # Utility functions
│   ├── dateUtils.js
│   └── chartUtils.js
└── styles/              # Global styles
```

### Principios de Diseño

1. **Component Composition**: Componentes reutilizables y composables
2. **State Management**: Estado local con hooks de React
3. **Separation of Concerns**: Separación de lógica de UI y datos
4. **Responsive Design**: Mobile-first approach

### Componentes Principales

#### Dashboard
- **Responsabilidad**: Orquestación de componentes, gestión de estado global
- **Tecnología**: React hooks (useState, useEffect)
- **Patrones**: Container/Presentational components

#### Services
- **Responsabilidad**: Comunicación con API, manejo de errores
- **Tecnología**: Axios, Promise handling
- **Patrones**: Service layer, Error boundary

#### Visualization
- **Responsabilidad**: Gráficos interactivos, estadísticas
- **Tecnología**: Chart.js, React-ChartJS-2
- **Patrones**: Chart configuration factory, Data transformation

## Flujo de Datos

### Consulta de Probabilidades

```
1. User Input (Location + Date)
   ↓
2. LocationPicker → Dashboard (state update)
   ↓
3. Dashboard → weatherService.getWeatherProbabilities()
   ↓
4. API Request → /api/weather/probability
   ↓
5. WeatherService.get_weather_probabilities()
   ↓
6. MockDataGenerator.generate_historical_data()
   ↓
7. Statistical Analysis & Probability Calculation
   ↓
8. JSON Response → Frontend
   ↓
9. ProbabilityDisplay + WeatherChart (render)
```

### Exportación de Datos

```
1. User Click Export
   ↓
2. DataExport → weatherService.exportWeatherData()
   ↓
3. API Request → /api/weather/export
   ↓
4. Data Processing (JSON/CSV format)
   ↓
5. File Download (Browser)
```

## Modelos de Datos

### Weather Query
```python
{
  "latitude": float,
  "longitude": float,
  "date_of_year": str,  # "MM-DD"
  "variables": List[str],
  "years_range": int
}
```

### Weather Response
```python
{
  "location": dict,
  "date_of_year": str,
  "probabilities": List[WeatherProbability],
  "historical_data": List[WeatherDataPoint],
  "statistics": dict
}
```

## Patrones de Diseño Utilizados

### Backend
- **Factory Pattern**: Para generación de datos mock
- **Service Pattern**: Para lógica de negocio
- **Repository Pattern**: Para acceso a datos (futuro)
- **Dependency Injection**: Para servicios

### Frontend
- **Observer Pattern**: React state updates
- **Strategy Pattern**: Chart configurations
- **Factory Pattern**: Chart utilities
- **Composite Pattern**: Component composition

## Consideraciones de Escalabilidad

### Backend
- **Caching**: Redis para datos frecuentemente consultados
- **Database**: PostgreSQL para datos históricos reales
- **Message Queue**: Celery para procesamiento asíncrono
- **Load Balancing**: Múltiples instancias FastAPI

### Frontend
- **Code Splitting**: Lazy loading de componentes
- **Memoization**: React.memo para optimización
- **CDN**: Para assets estáticos
- **State Management**: Redux para aplicaciones complejas

## Seguridad

### Backend
- **CORS**: Configuración restrictiva para producción
- **Rate Limiting**: Prevención de abuso de API
- **Input Validation**: Pydantic models
- **Authentication**: JWT tokens (futuro)

### Frontend
- **XSS Protection**: Sanitización de inputs
- **HTTPS**: Comunicación segura
- **Environment Variables**: Configuración segura

## Monitoreo y Observabilidad

### Métricas Propuestas
- Response time por endpoint
- Error rates
- Active users
- Data export frequency

### Logging
- Structured logging (JSON)
- Error tracking (Sentry)
- Performance monitoring (APM)

## Deployment

### Desarrollo
- Local development servers
- Docker Compose para ambiente completo

### Producción
- Containerización con Docker
- Orchestration con Kubernetes
- CI/CD pipelines
- Infrastructure as Code (Terraform)