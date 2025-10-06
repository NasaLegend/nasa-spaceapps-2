#!/bin/bash

# Script para configurar el sistema de datos reales y IA

echo "🌤️  Configurando Weather Probability App con datos reales y IA..."

# Navegar al directorio backend
cd "$(dirname "$0")"

echo "📦 Instalando nuevas dependencias..."
pip install -r requirements.txt

echo "📁 Creando directorios necesarios..."
mkdir -p data_cache
mkdir -p models
mkdir -p logs

echo "🔧 Configurando variables de entorno..."
# Crear archivo .env si no existe
if [ ! -f .env ]; then
    cat > .env << EOL
# Configuración de la aplicación
DEBUG=True
USE_REAL_DATA=True

# APIs de datos meteorológicos
OPENWEATHER_API_KEY=your_api_key_here
NASA_POWER_ENABLED=True

# Configuración de ML
ML_ENABLED=True
AUTO_RETRAIN=True

# Logging
LOG_LEVEL=INFO
EOL
    echo "✅ Archivo .env creado"
else
    echo "ℹ️  Archivo .env ya existe"
fi

echo "🤖 Inicializando modelos de Machine Learning..."
python -c "
import asyncio
from app.data.real_weather_data import real_weather_service

async def init_models():
    print('Inicializando servicio de datos reales...')
    # El servicio se inicializa automáticamente
    print('✅ Servicio listo para usar datos reales de NASA POWER')

if __name__ == '__main__':
    asyncio.run(init_models())
"

echo "🔍 Verificando configuración..."
python -c "
import sys
try:
    import pandas as pd
    import numpy as np
    import sklearn
    import aiohttp
    import joblib
    print('✅ Todas las dependencias instaladas correctamente')
    
    from app.data.real_weather_data import real_weather_service
    print('✅ Servicio de datos reales inicializado')
    
    from app.services.weather_service import weather_service
    print('✅ Servicio meteorológico listo')
    
except ImportError as e:
    print(f'❌ Error importando dependencias: {e}')
    sys.exit(1)
"

echo ""
echo "🎉 ¡Configuración completada!"
echo ""
echo "📋 Funcionalidades disponibles:"
echo "   • Datos reales de NASA POWER API"
echo "   • Modelos de Machine Learning para predicciones"
echo "   • Cache inteligente de datos"
echo "   • Entrenamiento automático de modelos"
echo "   • Fallback a datos sintéticos si es necesario"
echo ""
echo "🚀 Para ejecutar el servidor:"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "📖 Documentación disponible en: http://localhost:8000/docs"
echo "🔍 Información del modelo en: http://localhost:8000/api/model/info"