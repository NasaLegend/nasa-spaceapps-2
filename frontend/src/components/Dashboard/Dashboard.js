import React, { useState } from "react";
import LocationPicker from "../LocationPicker/LocationPicker";
import WeatherChart from "../WeatherChart/WeatherChart";
// import ProbabilityDisplay from "../ProbabilityDisplay/ProbabilityDisplay"; // Disponible si se necesita
import DataExport from "../DataExport/DataExport";
// import SettingsPanel from "../SettingsPanel/SettingsPanel"; // Desactivado - ahora solo se usa PersonalizationPanel
import PersonalizationPanel from "../PersonalizationPanel/PersonalizationPanel";
import WeatherMetricsDisplay from "../WeatherMetricsDisplay/WeatherMetricsDisplay";
import "./Dashboard.css";

const Dashboard = ({
  loading,
  error,
  weatherData,
  // availableConditions, // No se usa actualmente - disponible si se necesita ProbabilityDisplay
  userPreferences,
  onWeatherQuery,
  onExportData,
  onClearError,
  onUpdatePreferences,
}) => {
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [yearsRange, setYearsRange] = useState(30);
  // const [showSettings, setShowSettings] = useState(false); // Desactivado - solo se usa PersonalizationPanel
  const [showPersonalization, setShowPersonalization] = useState(false);
  const [showMetricsView, setShowMetricsView] = useState(true); // Nueva vista por defecto

  // Estado para configuración personalizada
  const [personalizationConfig, setPersonalizationConfig] = useState({
    selectedConditions: [
      "very_hot",
      "very_cold",
      "very_windy",
      "very_wet",
      "very_uncomfortable",
    ],
    temperatureUnit: "celsius",
    includeFuturePredictions: true,
    futureDays: 14,
    customThresholds: {},
    analysisMode: "basic",
    visibleMetrics: {
      temperature: true,
      precipitation: true,
      wind_speed: true,
      humidity: true,
      heat_index: true,
    },
  });

  const handleLocationSelect = (location) => {
    console.log("Dashboard received location:", location);
    setSelectedLocation(location);
  };

  const handleAnalyze = () => {
    console.log(
      "Analyze clicked - Location:",
      selectedLocation,
      "Config:",
      personalizationConfig
    );
    if (!selectedLocation) {
      alert("Por favor selecciona una ubicación y fecha");
      return;
    }

    // Crear query data con personalización
    const queryData = {
      latitude: selectedLocation.latitude,
      longitude: selectedLocation.longitude,
      // date_of_year se omite para usar la fecha actual automáticamente
      selected_conditions: personalizationConfig.selectedConditions,
      temperature_unit: personalizationConfig.temperatureUnit,
      include_future_predictions:
        personalizationConfig.includeFuturePredictions,
      future_days: personalizationConfig.futureDays,
      custom_thresholds:
        Object.keys(personalizationConfig.customThresholds).length > 0
          ? personalizationConfig.customThresholds
          : null,
      years_range: yearsRange,
    };

    onWeatherQuery(queryData);
  };

  const getCurrentQueryData = () => {
    if (!selectedLocation) return null;

    const enabledVariables = [];
    if (userPreferences.showTemperature) enabledVariables.push("temperature");
    if (userPreferences.showPrecipitation)
      enabledVariables.push("precipitation");
    if (userPreferences.showWindSpeed) enabledVariables.push("wind_speed");
    if (userPreferences.showHumidity) enabledVariables.push("humidity");

    return {
      latitude: selectedLocation.latitude,
      longitude: selectedLocation.longitude,
      // date_of_year se omite para usar la fecha actual automáticamente
      variables:
        enabledVariables.length > 0 ? enabledVariables : ["temperature"],
      years_range: yearsRange,
    };
  };

  // Ya no necesitamos validar la fecha porque el backend usa la fecha actual automáticamente
  const isFormValid = selectedLocation;

  return (
    <div
      className={`dashboard ${userPreferences.compactView ? "compact" : ""}`}
    >
      {error && (
        <div className="error">
          <p>{error}</p>
          <button onClick={onClearError} className="btn btn-secondary">
            ✕ Cerrar
          </button>
        </div>
      )}

      <div className="dashboard-header">
        <div className="dashboard-title">
          <h1>🌤️ Panel de Control Meteorológico</h1>
          <p>
            Análisis personalizado de probabilidades climáticas para eventos al
            aire libre
          </p>
        </div>
        <div className="header-buttons">
          <button
            onClick={() => setShowMetricsView(!showMetricsView)}
            className={`btn ${
              showMetricsView ? "btn-primary" : "btn-secondary"
            } metrics-btn`}
            title="Cambiar entre vista de métricas y gráficos"
          >
            {showMetricsView ? "📊 Métricas" : "📈 Gráficos"}
          </button>
          <button
            onClick={() => setShowPersonalization(!showPersonalization)}
            className={`btn ${
              showPersonalization ? "btn-primary" : "btn-secondary"
            } personalization-btn`}
            title="Configuración personalizada para eventos al aire libre"
          >
            🎯{" "}
            {showPersonalization
              ? "Ocultar"
              : "Personalizar Análisis Meteorológico"}
          </button>
          {/* Botón de configuración desactivado - ahora se usa solo Personalizar Análisis
          <button
            onClick={() => setShowSettings(true)}
            className="btn btn-secondary settings-btn"
            title="Configuración avanzada"
          >
            ⚙️ Configuración
          </button>
          */}
        </div>
      </div>

      {/* Panel de Personalización */}
      {showPersonalization && (
        <PersonalizationPanel
          onConfigChange={setPersonalizationConfig}
          currentConfig={personalizationConfig}
        />
      )}

      <div className="dashboard-grid">
        {/* Panel de configuración */}
        <div className="config-panel">
          <div className="card">
            <h2>📍 Configuración de Consulta</h2>

            <div className="form-group">
              <label>Ubicación:</label>
              <LocationPicker
                onLocationSelect={handleLocationSelect}
                selectedLocation={selectedLocation}
              />
            </div>

            {/* Campo de fecha eliminado - ahora se usa la fecha actual automáticamente */}

            <div className="form-group">
              <label htmlFor="years-range">Años de datos históricos:</label>
              <select
                id="years-range"
                value={yearsRange}
                onChange={(e) => setYearsRange(parseInt(e.target.value))}
              >
                <option value={10}>⏰ 10 años</option>
                <option value={20}>📅 20 años</option>
                <option value={30}>📆 30 años</option>
                <option value={50}>🗓️ 50 años</option>
              </select>
            </div>

            {/* Resumen de variables seleccionadas */}
            <div className="selected-variables">
              <h4>Variables Activas:</h4>
              <div className="variable-tags">
                {userPreferences.showTemperature && (
                  <span className="tag">🌡️ Temperatura</span>
                )}
                {userPreferences.showPrecipitation && (
                  <span className="tag">🌧️ Precipitación</span>
                )}
                {userPreferences.showWindSpeed && (
                  <span className="tag">💨 Viento</span>
                )}
                {userPreferences.showHumidity && (
                  <span className="tag">💧 Humedad</span>
                )}
                {userPreferences.showHeatIndex && (
                  <span className="tag">🔥 Índice de Calor</span>
                )}
              </div>
            </div>

            <button
              onClick={handleAnalyze}
              disabled={loading || !isFormValid}
              className="btn analyze-btn"
            >
              {loading ? (
                <>🔄 Analizando datos meteorológicos...</>
              ) : (
                <>📊 Analizar Probabilidades</>
              )}
            </button>
          </div>

          {weatherData && (
            <DataExport
              queryData={getCurrentQueryData()}
              onExportData={onExportData}
              userPreferences={{
                // Convertir configuración de personalización a formato de userPreferences
                showTemperature:
                  personalizationConfig.visibleMetrics?.temperature !== false,
                showPrecipitation:
                  personalizationConfig.visibleMetrics?.precipitation !== false,
                showWindSpeed:
                  personalizationConfig.visibleMetrics?.wind_speed !== false,
                showHumidity:
                  personalizationConfig.visibleMetrics?.humidity !== false,
                showHeatIndex:
                  personalizationConfig.visibleMetrics?.heat_index !== false,
                chartType: "line",
                compactView: false,
                showStatistics: true,
                showProbabilityBars: true,
                temperatureUnit: personalizationConfig.temperatureUnit,
                includeFuturePredictions:
                  personalizationConfig.includeFuturePredictions,
                futureDays: personalizationConfig.futureDays,
                analysisMode: personalizationConfig.analysisMode,
                customThresholds: personalizationConfig.customThresholds,
                selectedConditions: personalizationConfig.selectedConditions,
              }}
            />
          )}
        </div>

        {/* Panel de resultados */}
        <div className="results-panel">
          {loading && (
            <div className="loading">
              <div className="loading-animation">
                <div className="loading-dots">
                  <div></div>
                  <div></div>
                  <div></div>
                </div>
                <p>🔄 Obteniendo datos históricos de NASA...</p>
                <small>
                  Esto puede tomar hasta 60 segundos la primera vez por
                  ubicación
                </small>
                <small>Procesando {yearsRange} años de datos históricos</small>
              </div>
            </div>
          )}

          {weatherData && !loading && (
            <>
              {showMetricsView ? (
                <WeatherMetricsDisplay
                  weatherData={weatherData}
                  personalizationConfig={personalizationConfig}
                  futurePredictions={weatherData.future_predictions || []}
                />
              ) : (
                <WeatherChart
                  historicalData={weatherData.historical_data}
                  statistics={weatherData.statistics}
                  userPreferences={userPreferences}
                  currentLocation={selectedLocation}
                  currentDate={new Date().toISOString().substr(5, 5)} // Usar fecha actual MM-DD
                  onYearsRangeChange={onWeatherQuery}
                  currentPersonalizationConfig={personalizationConfig}
                />
              )}
            </>
          )}

          {!weatherData && !loading && (
            <div className="card no-data">
              <div className="welcome-content">
                <h2>🌟 Bienvenido al Análisis Meteorológico</h2>
                <p>
                  Selecciona una ubicación y fecha para comenzar el análisis de
                  probabilidades climáticas basado en datos históricos de la
                  NASA.
                </p>
                <div className="cta-section">
                  <button
                    onClick={() => setShowPersonalization(true)}
                    className="btn btn-secondary"
                  >
                    🎯 Personalizar Análisis Meteorológico
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Panel de configuración desactivado - ahora solo se usa Personalizar Análisis Meteorológico
      <SettingsPanel
        preferences={userPreferences}
        onUpdatePreferences={onUpdatePreferences}
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
      />
      */}
    </div>
  );
};

export default Dashboard;
