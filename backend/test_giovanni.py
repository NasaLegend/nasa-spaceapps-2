#!/usr/bin/env python3
"""
Script de prueba para la integración con Giovanni NASA Data
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio padre al path para importar los módulos
sys.path.append(str(Path(__file__).parent))

from app.data.giovanni_nasa_data import giovanni_weather_service

async def test_giovanni_integration():
    """
    Prueba la integración con Giovanni NASA Data
    """
    print("🌍 Probando integración con Giovanni NASA Data...")
    print("=" * 60)
    
    # Ubicaciones de prueba
    test_locations = [
        {
            "name": "Nueva York",
            "lat": 40.7128,
            "lon": -74.0060
        },
        {
            "name": "Madrid",
            "lat": 40.4168,
            "lon": -3.7038
        },
        {
            "name": "Ciudad de México",
            "lat": 19.4326,
            "lon": -99.1332
        }
    ]
    
    for location in test_locations:
        print(f"\n📍 Probando: {location['name']} ({location['lat']}, {location['lon']})")
        print("-" * 40)
        
        try:
            # Obtener datos históricos para el 15 de junio
            historical_data = await giovanni_weather_service.get_historical_data(
                latitude=location['lat'],
                longitude=location['lon'],
                date_of_year="06-15",  # 15 de junio
                years=5  # Solo 5 años para prueba rápida
            )
            
            if historical_data:
                print(f"✅ Datos obtenidos: {len(historical_data)} registros")
                
                # Mostrar algunos datos de ejemplo
                if len(historical_data) > 0:
                    sample = historical_data[0]
                    print(f"📊 Ejemplo de datos:")
                    print(f"   Fecha: {sample['date']}")
                    print(f"   Temperatura: {sample.get('temperature', 'N/A')}°C")
                    print(f"   Precipitación: {sample.get('precipitation', 'N/A')}mm")
                    print(f"   Viento: {sample.get('wind_speed', 'N/A')}m/s")
                    print(f"   Humedad: {sample.get('humidity', 'N/A')}%")
                
                # Entrenar modelos si hay suficientes datos
                if len(historical_data) >= 3:
                    print("🤖 Entrenando modelos...")
                    giovanni_weather_service.train_prediction_models(
                        historical_data, 
                        location['lat'], 
                        location['lon']
                    )
                    
                    # Calcular probabilidades
                    probabilities = giovanni_weather_service.predict_probabilities(
                        location['lat'],
                        location['lon'],
                        "06-15",
                        historical_data
                    )
                    
                    print("📈 Probabilidades calculadas:")
                    for condition, data in probabilities.items():
                        print(f"   {condition}: {data['probability']:.2%} (umbral: {data['threshold']:.1f} {data['unit']})")
                
            else:
                print("⚠️  No se obtuvieron datos")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Prueba de Giovanni completada")

async def test_giovanni_api_direct():
    """
    Prueba directa de la API Giovanni
    """
    print("\n🔗 Probando acceso directo a Giovanni API...")
    
    try:
        # Probar con una variable específica
        giovanni_data = await giovanni_weather_service.fetch_giovanni_data(
            variable="M2T1NXSLV_5_12_4_T2M",  # Temperatura
            latitude=40.7128,  # Nueva York
            longitude=-74.0060,
            start_date="2023-06-01",
            end_date="2023-06-30"
        )
        
        if giovanni_data and giovanni_data['data']:
            print(f"✅ API directa funcional: {len(giovanni_data['data'])} puntos")
            print(f"📊 Variable: {giovanni_data['variable']}")
            print(f"🔬 Fuente: {giovanni_data['source']}")
        else:
            print("⚠️  Sin datos de API directa")
            
    except Exception as e:
        print(f"❌ Error en API directa: {e}")

async def test_url_construction():
    """
    Prueba la construcción de URLs para Giovanni
    """
    print("\n🔧 Probando construcción de URLs...")
    
    # Probar diferentes endpoints
    endpoints = ["proxy-timeseries", "timeseries"]
    
    for endpoint in endpoints:
        url = giovanni_weather_service.build_giovanni_url(
            variable="M2T1NXSLV_5_12_4_T2M",
            location=(40.7128, -74.0060),
            time_range=("2023-06-01", "2023-06-30"),
            endpoint=endpoint
        )
        print(f"📎 {endpoint}: {url}")

async def main():
    """
    Función principal de pruebas
    """
    print("🌤️  Giovanni NASA Data Integration Test")
    print("🚀 Iniciando pruebas...\n")
    
    # Verificar dependencias
    try:
        import aiohttp
        import numpy as np
        import pandas as pd
        print("✅ Dependencias verificadas")
    except ImportError as e:
        print(f"❌ Dependencia faltante: {e}")
        return
    
    # Crear directorios si no existen
    giovanni_weather_service.data_cache_dir.mkdir(exist_ok=True)
    giovanni_weather_service.models_dir.mkdir(exist_ok=True)
    print("✅ Directorios verificados")
    
    # Ejecutar pruebas
    await test_url_construction()
    await test_giovanni_api_direct()
    await test_giovanni_integration()
    
    print(f"\n📁 Cache directory: {giovanni_weather_service.data_cache_dir}")
    print(f"🤖 Models directory: {giovanni_weather_service.models_dir}")
    print("\n🎉 ¡Todas las pruebas completadas!")

if __name__ == "__main__":
    asyncio.run(main())