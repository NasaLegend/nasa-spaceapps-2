#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento del sistema de datos reales y IA
"""

import asyncio
import json
import sys
from datetime import datetime
import requests

async def test_nasa_power_integration():
    """Prueba la integración con NASA POWER API"""
    print("🧪 Probando integración con datos reales de NASA POWER...\n")
    
    try:
        from app.data.real_weather_data import real_weather_service
        
        # Coordenadas de prueba (Nueva York)
        test_location = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "name": "Nueva York, NY"
        }
        
        print(f"📍 Ubicación de prueba: {test_location['name']}")
        print(f"   Coordenadas: {test_location['latitude']}, {test_location['longitude']}")
        
        # Obtener datos históricos
        print("\n🌍 Obteniendo datos históricos de NASA POWER...")
        historical_data = await real_weather_service.get_historical_data(
            latitude=test_location['latitude'],
            longitude=test_location['longitude'],
            date_of_year="07-04",  # 4 de julio
            years=10  # Solo 10 años para prueba rápida
        )
        
        if historical_data:
            print(f"✅ Datos obtenidos: {len(historical_data)} registros históricos")
            
            # Mostrar muestra de datos
            if len(historical_data) > 0:
                sample = historical_data[0]
                print(f"\n📊 Muestra de datos (primer registro):")
                print(f"   Fecha: {sample.get('date', 'N/A')}")
                print(f"   Temperatura: {sample.get('temperature', 'N/A')}°C")
                print(f"   Precipitación: {sample.get('precipitation', 'N/A')}mm")
                print(f"   Viento: {sample.get('wind_speed', 'N/A')}km/h")
                print(f"   Humedad: {sample.get('humidity', 'N/A')}%")
            
            # Entrenar modelos
            print("\n🤖 Entrenando modelos de Machine Learning...")
            real_weather_service.train_prediction_models(
                historical_data, 
                test_location['latitude'], 
                test_location['longitude']
            )
            
            # Calcular probabilidades
            print("\n📈 Calculando probabilidades con IA...")
            probabilities = real_weather_service.predict_probabilities(
                test_location['latitude'],
                test_location['longitude'],
                "07-04",
                historical_data
            )
            
            print("✅ Probabilidades calculadas:")
            for condition, data in probabilities.items():
                prob_percent = data['probability'] * 100
                threshold = data['threshold']
                unit = data['unit']
                print(f"   {condition}: {prob_percent:.1f}% (umbral: {threshold:.1f} {unit})")
            
            return True
            
        else:
            print("⚠️  No se pudieron obtener datos (puede ser normal en primera ejecución)")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de datos reales: {e}")
        return False

async def test_api_endpoint():
    """Prueba el endpoint de la API"""
    print("\n🔗 Probando endpoint de la API...")
    
    try:
        # Datos de prueba
        test_query = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "date_of_year": "07-04",
            "variables": ["temperature", "precipitation", "wind_speed", "humidity"],
            "years_range": 10
        }
        
        # Hacer request a la API
        response = requests.post(
            "http://localhost:8000/api/weather/probabilities",
            json=test_query,
            timeout=60  # Timeout mayor para obtener datos reales
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API funcionando correctamente")
            
            location = data.get('location', {})
            probabilities = data.get('probabilities', [])
            
            print(f"📍 Ubicación procesada: {location.get('latitude')}, {location.get('longitude')}")
            print(f"🔬 Fuente de datos: {location.get('data_source', 'No especificada')}")
            print(f"📊 Puntos de datos: {location.get('data_points', 'N/A')}")
            
            if probabilities:
                print("\n📈 Probabilidades retornadas:")
                for prob in probabilities:
                    condition = prob.get('condition')
                    probability = prob.get('probability', 0) * 100
                    threshold = prob.get('threshold_value')
                    unit = prob.get('unit')
                    print(f"   {condition}: {probability:.1f}% (umbral: {threshold:.1f} {unit})")
            
            return True
        else:
            print(f"❌ Error en API: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar a la API. ¿Está el servidor ejecutándose?")
        return False
    except Exception as e:
        print(f"❌ Error probando API: {e}")
        return False

async def test_model_info():
    """Prueba el endpoint de información de modelos"""
    print("\n🤖 Probando información de modelos...")
    
    try:
        response = requests.get("http://localhost:8000/api/model/info")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint de modelos funcionando")
            
            models = data.get('models', {})
            print("\n🧠 Estado de modelos ML:")
            for model_name, status in models.items():
                trained = "✅ Entrenado" if status.get('trained') else "❌ No entrenado"
                model_type = status.get('type', 'N/A')
                print(f"   {model_name}: {trained} ({model_type})")
            
            print(f"\n📚 Fuentes de datos disponibles:")
            sources = data.get('data_sources', {})
            for source, desc in sources.items():
                print(f"   {source}: {desc}")
            
            return True
        else:
            print(f"❌ Error obteniendo info de modelos: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando info de modelos: {e}")
        return False

async def main():
    """Función principal de pruebas"""
    print("🌤️ Sistema de Pruebas - Weather Probability App con IA\n")
    print("=" * 60)
    
    # Prueba 1: Integración NASA POWER
    test1_ok = await test_nasa_power_integration()
    
    print("\n" + "=" * 60)
    
    # Prueba 2: API endpoint
    test2_ok = await test_api_endpoint()
    
    print("\n" + "=" * 60)
    
    # Prueba 3: Info de modelos
    test3_ok = await test_model_info()
    
    print("\n" + "=" * 60)
    
    # Resumen
    print("\n📋 RESUMEN DE PRUEBAS:")
    print(f"   🌍 Datos reales NASA POWER: {'✅ PASSED' if test1_ok else '❌ FAILED'}")
    print(f"   🔗 API Endpoint: {'✅ PASSED' if test2_ok else '❌ FAILED'}")
    print(f"   🤖 Info de modelos: {'✅ PASSED' if test3_ok else '❌ FAILED'}")
    
    if all([test1_ok, test2_ok, test3_ok]):
        print("\n🎉 ¡Todas las pruebas pasaron! El sistema está funcionando correctamente.")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisar configuración y conexión.")
    
    print("\n📖 Para usar la aplicación:")
    print("   • Frontend: http://localhost:3000")
    print("   • API Docs: http://localhost:8000/docs")
    print("   • Model Info: http://localhost:8000/api/model/info")

if __name__ == "__main__":
    asyncio.run(main())