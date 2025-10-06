#!/usr/bin/env python3
"""
Script de prueba para verificar que la API funciona correctamente
"""

import requests
import json

def test_api():
    print("🔧 Testing API endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"✅ Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test weather endpoint
    try:
        # Datos de prueba para Madrid
        test_data = {
            "latitude": 40.4168,
            "longitude": -3.7038,
            "date_of_year": "06-15"
        }
        
        print(f"\n🌍 Testing weather endpoint with data: {test_data}")
        response = requests.post(
            "http://localhost:8000/api/weather/probabilities",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Weather API working!")
            print(f"📊 Data source: {data.get('data_source', 'Unknown')}")
            print(f"🎯 Accuracy: {data.get('prediction_accuracy', 0)*100:.1f}%")
            print(f"📈 Probabilities:")
            for prob in data.get('probabilities', []):
                print(f"   - {prob['condition']}: {prob['probability']*100:.1f}%")
        else:
            print(f"❌ Weather API failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Weather API test failed: {e}")

if __name__ == "__main__":
    test_api()