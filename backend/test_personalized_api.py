#!/usr/bin/env python3
"""
Prueba de las nuevas funcionalidades personalizables de la API
"""

import requests
import json
from datetime import date, timedelta

def test_personalized_api():
    """Prueba las nuevas funcionalidades personalizables"""
    print("🎯 Probando API personalizable para eventos al aire libre")
    print("=" * 70)
    
    # Datos base para Madrid
    base_url = "http://localhost:8000"
    
    # Test 1: API básica con personalización
    print("\n📍 Test 1: Análisis personalizado básico")
    test_data = {
        "latitude": 40.4168,
        "longitude": -3.7038,
        "date_of_year": "06-15",
        "selected_conditions": ["very_hot", "very_wet"],  # Solo calor y lluvia
        "temperature_unit": "celsius",
        "include_future_predictions": True,
        "future_days": 7
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/weather/probability",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API personalizada funcionando!")
            print(f"🌡️  Unidad de temperatura: {data.get('temperature_unit', 'Unknown')}")
            print(f"📊 Condiciones analizadas: {len(data.get('probabilities', []))}")
            print(f"🔮 Predicciones futuras: {len(data.get('future_predictions', []))}")
            
            # Mostrar probabilidades personalizadas
            print("\n🎯 Probabilidades personalizadas:")
            for prob in data.get('probabilities', []):
                print(f"   - {prob['condition']}: {prob['probability']*100:.1f}% (umbral: {prob['threshold']:.1f}{prob['unit']})")
                
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en prueba básica: {e}")
    
    # Test 2: Análisis con Fahrenheit
    print("\n🌡️  Test 2: Análisis con unidades Fahrenheit")
    test_data_f = {
        "latitude": 40.4168,
        "longitude": -3.7038,
        "date_of_year": "07-20",  # Verano
        "selected_conditions": ["very_hot", "very_cold"],
        "temperature_unit": "fahrenheit",
        "include_future_predictions": False
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/weather/probability",
            json=test_data_f,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Conversión a Fahrenheit funcionando!")
            for prob in data.get('probabilities', []):
                print(f"   - {prob['condition']}: {prob['threshold']:.1f}{prob['unit']}")
        else:
            print(f"❌ Error en Fahrenheit: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en test Fahrenheit: {e}")
    
    # Test 3: Análisis personalizado completo para evento al aire libre
    print("\n🏕️  Test 3: Análisis completo para camping")
    test_camping = {
        "latitude": 40.4168,
        "longitude": -3.7038,
        "date_of_year": "08-15",
        "selected_conditions": ["very_hot", "very_wet", "very_windy"],
        "temperature_unit": "celsius",
        "custom_thresholds": {
            "very_hot_threshold": 32.0,    # Muy caliente si > 32°C
            "very_wet_threshold": 5.0,     # Muy húmedo si > 5mm
            "very_windy_threshold": 20.0   # Muy ventoso si > 20 km/h
        },
        "include_future_predictions": True,
        "future_days": 14
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/weather/custom-analysis",
            json=test_camping,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Análisis personalizado para camping!")
            
            # Mostrar análisis personalizado
            analysis = data.get('user_preferences', {}).get('analysis_summary', {})
            if analysis:
                print(f"🎯 Idoneidad general: {analysis.get('outdoor_activity_suitability', {}).get('overall_suitability', 'N/A')}")
                print(f"📊 Puntuación: {analysis.get('outdoor_activity_suitability', {}).get('score', 0)}/100")
                
                # Mejores días
                best_days = analysis.get('best_days_ahead', [])
                if best_days:
                    print(f"\n📅 Mejores días próximos:")
                    for day in best_days[:3]:
                        print(f"   - {day['date']}: {day['suitability']} (score: {day['score']:.1f})")
                
                # Recomendaciones
                recommendations = analysis.get('recommendations', [])
                if recommendations:
                    print(f"\n💡 Recomendaciones:")
                    for rec in recommendations[:3]:
                        print(f"   - {rec}")
        else:
            print(f"❌ Error en análisis personalizado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en test camping: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Pruebas de personalización completadas!")

if __name__ == "__main__":
    test_personalized_api()