#!/usr/bin/env python3
"""
Script de configuración para Weather Probability App con datos reales y IA
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def run_command(command):
    """Ejecuta un comando y muestra el resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {command}")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
        else:
            print(f"❌ Error ejecutando: {command}")
            if result.stderr:
                print(f"   {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Excepción ejecutando {command}: {e}")
        return False

def create_directories():
    """Crea los directorios necesarios"""
    directories = ['data_cache', 'models', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Directorio creado: {directory}")

def create_env_file():
    """Crea el archivo .env si no existe"""
    env_content = """# Configuración de la aplicación
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
"""
    
    if not Path('.env').exists():
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Archivo .env creado")
    else:
        print("ℹ️  Archivo .env ya existe")

async def test_real_data_service():
    """Prueba el servicio de datos reales"""
    try:
        from app.data.real_weather_data import real_weather_service
        print("✅ Servicio de datos reales inicializado")
        
        # Probar con una ubicación de ejemplo
        test_data = await real_weather_service.get_historical_data(
            latitude=40.7128,  # Nueva York
            longitude=-74.0060,
            date_of_year="06-15",  # 15 de junio
            years=5  # Solo 5 años para prueba rápida
        )
        
        if test_data:
            print(f"✅ Datos de prueba obtenidos: {len(test_data)} puntos")
            
            # Entrenar modelos con datos de prueba
            if len(test_data) >= 3:
                real_weather_service.train_prediction_models(test_data, 40.7128, -74.0060)
                print("✅ Modelos de prueba entrenados")
        else:
            print("⚠️  No se pudieron obtener datos de prueba (normal en primera ejecución)")
            
    except Exception as e:
        print(f"⚠️  Error en prueba de datos reales: {e}")
        print("   Esto es normal si es la primera ejecución o no hay conexión a internet")

def verify_installation():
    """Verifica que todas las dependencias estén instaladas"""
    dependencies = [
        'pandas', 'numpy', 'sklearn', 'aiohttp', 'joblib',
        'fastapi', 'uvicorn', 'pydantic'
    ]
    
    missing = []
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            missing.append(dep)
            print(f"❌ {dep} no encontrado")
    
    if missing:
        print(f"\n⚠️  Dependencias faltantes: {', '.join(missing)}")
        print("Ejecuta: pip install -r requirements.txt")
        return False
    
    return True

async def main():
    """Función principal de configuración"""
    print("🌤️  Configurando Weather Probability App con datos reales y IA...\n")
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        return
    
    print(f"✅ Python {sys.version}")
    
    # Instalar dependencias
    print("\n📦 Instalando dependencias...")
    if not run_command("pip install -r requirements.txt"):
        print("❌ Error instalando dependencias")
        return
    
    # Crear directorios
    print("\n📁 Creando directorios...")
    create_directories()
    
    # Crear archivo .env
    print("\n🔧 Configurando variables de entorno...")
    create_env_file()
    
    # Verificar instalación
    print("\n🔍 Verificando instalación...")
    if not verify_installation():
        return
    
    # Probar servicio de datos reales
    print("\n🤖 Probando servicio de datos reales...")
    await test_real_data_service()
    
    # Información final
    print("\n🎉 ¡Configuración completada!")
    print("\n📋 Funcionalidades disponibles:")
    print("   • Datos reales de NASA POWER API")
    print("   • Modelos de Machine Learning para predicciones")
    print("   • Cache inteligente de datos")
    print("   • Entrenamiento automático de modelos")
    print("   • Fallback a datos sintéticos si es necesario")
    print("\n🚀 Para ejecutar el servidor:")
    print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("\n📖 Documentación: http://localhost:8000/docs")
    print("🔍 Info del modelo: http://localhost:8000/api/model/info")

if __name__ == "__main__":
    asyncio.run(main())