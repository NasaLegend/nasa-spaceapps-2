#!/usr/bin/env python3
"""
Script de prueba para NASA POWER API (fuente principal)
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio padre al path para importar los módulos
sys.path.append(str(Path(__file__).parent))

from app.data.real_weather_data import real_weather_service

async def test_nasa_power():
    """
    Prueba rápida de NASA POWER API
    """
    print("🚀 NASA POWER API Test")
    print("=" * 50)
    
    # Ubicación de prueba: Madrid
    lat, lon = 40.4168, -3.7038
    date_of_year = "06-15"  # 15 de junio
    
    print(f"📍 Ubicación: Madrid ({lat}, {lon})")
    print(f"📅 Fecha: {date_of_year}")
    print("-" * 50)
    
    try:
        # Obtener datos históricos
        print("🔍 Obteniendo datos históricos...")
        historical_data = await real_weather_service.get_historical_data(
            latitude=lat,
            longitude=lon,
            date_of_year=date_of_year,
            years=5  # Solo 5 años para prueba rápida
        )
        
        if historical_data:
            print(f"✅ Datos obtenidos: {len(historical_data)} registros")
            
            # Mostrar muestra de datos
            if len(historical_data) > 0:
                sample = historical_data[-1]  # Último año
                print(f"\n📊 Datos del último año:")
                print(f"   Fecha: {sample['date']}")
                print(f"   Temperatura: {sample.get('temperature', 'N/A')}°C")
                print(f"   Precipitación: {sample.get('precipitation', 'N/A')}mm")
                print(f"   Viento: {sample.get('wind_speed', 'N/A')}m/s")
                print(f"   Humedad: {sample.get('humidity', 'N/A')}%")
            
            # Entrenar modelos si hay suficientes datos
            if len(historical_data) >= 3:
                print("\n🤖 Entrenando modelos...")
                real_weather_service.train_prediction_models(
                    historical_data, lat, lon
                )
                
                # Calcular probabilidades
                print("📈 Calculando probabilidades...")
                probabilities = real_weather_service.predict_probabilities(
                    lat, lon, date_of_year, historical_data
                )
                
                print("\n🎯 Probabilidades para condiciones extremas:")
                for condition, data in probabilities.items():
                    print(f"   {condition.replace('_', ' ').title()}: {data['probability']:.1%}")
                    print(f"      └─ Umbral: {data['threshold']:.1f} {data['unit']}")
                
                print(f"\n✅ Test completado exitosamente!")
                print(f"📁 Cache: {real_weather_service.data_cache_dir}")
                print(f"🤖 Modelos: {real_weather_service.models_dir}")
        else:
            print("❌ No se obtuvieron datos")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def test_api_endpoint():
    """
    Prueba el endpoint directo
    """
    print("\n🌐 Probando endpoint directo...")
    
    try:
        import aiohttp
        
        url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        params = {
            "parameters": "T2M,PRECTOTCORR,WS10M,RH2M",
            "community": "RE",
            "longitude": -3.7038,
            "latitude": 40.4168,
            "start": "20230615",
            "end": "20230615",
            "format": "JSON"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Endpoint directo funcional")
                    print(f"📊 Parámetros disponibles: {list(data.get('properties', {}).get('parameter', {}).keys())}")
                else:
                    print(f"⚠️  Status: {response.status}")
                    
    except Exception as e:
        print(f"❌ Error en endpoint directo: {e}")

async def main():
    """
    Función principal
    """
    print("🌤️  NASA POWER Integration Test")
    print("🎯 Prueba de funcionalidad principal\n")
    
    await test_api_endpoint()
    await test_nasa_power()

if __name__ == "__main__":
    asyncio.run(main())