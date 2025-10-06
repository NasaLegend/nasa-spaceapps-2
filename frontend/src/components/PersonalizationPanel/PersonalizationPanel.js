import React, { useState } from "react";
import "./PersonalizationPanel.css";

const PersonalizationPanel = ({ onConfigChange, currentConfig }) => {
  const [config, setConfig] = useState({
    selectedConditions: currentConfig?.selectedConditions || [
      "very_hot",
      "very_cold",
    ],
    temperatureUnit: currentConfig?.temperatureUnit || "celsius",
    includeFuturePredictions: currentConfig?.includeFuturePredictions || true,
    futureDays: currentConfig?.futureDays || 14,
    customThresholds: currentConfig?.customThresholds || {},
    analysisMode: currentConfig?.analysisMode || "basic", // 'basic' o 'outdoor_event'
    visibleMetrics: currentConfig?.visibleMetrics || {
      temperature: true,
      precipitation: true,
      wind_speed: true,
      humidity: true,
      heat_index: true,
    },
  });

  const weatherConditions = [
    {
      id: "very_hot",
      name: "Muy Caliente",
      icon: "🔥",
      description: "Temperaturas extremadamente altas",
    },
    {
      id: "very_cold",
      name: "Muy Frío",
      icon: "🧊",
      description: "Temperaturas extremadamente bajas",
    },
    {
      id: "very_windy",
      name: "Muy Ventoso",
      icon: "💨",
      description: "Vientos fuertes",
    },
    {
      id: "very_wet",
      name: "Muy Húmedo",
      icon: "🌧️",
      description: "Alta precipitación",
    },
    {
      id: "very_uncomfortable",
      name: "Muy Incómodo",
      icon: "😰",
      description: "Condiciones de confort extremas",
    },
  ];

  const availableMetrics = [
    {
      id: "temperature",
      name: "Temperatura",
      icon: "🌡️",
      description:
        "Medida del calor o frío del aire. Fundamental para determinar el confort térmico y planificar actividades.",
      unit: "°C/°F",
    },
    {
      id: "precipitation",
      name: "Precipitación",
      icon: "🌧️",
      description:
        "Cantidad de lluvia, nieve o granizo que cae. Esencial para actividades al aire libre y agricultura.",
      unit: "mm",
    },
    {
      id: "wind_speed",
      name: "Velocidad del Viento",
      icon: "💨",
      description:
        "Velocidad del movimiento del aire. Afecta la sensación térmica y actividades como navegación o deportes.",
      unit: "km/h",
    },
    {
      id: "humidity",
      name: "Humedad Relativa",
      icon: "💧",
      description:
        "Porcentaje de humedad en el aire. Alta humedad aumenta la sensación de calor y puede causar incomodidad.",
      unit: "%",
    },
    {
      id: "heat_index",
      name: "Índice de Calor",
      icon: "🌡️🔥",
      description:
        "Temperatura percibida considerando humedad. Indica qué tan caliente se siente realmente el ambiente.",
      unit: "°C/°F",
    },
  ];

  const handleConditionToggle = (conditionId) => {
    const newConditions = config.selectedConditions.includes(conditionId)
      ? config.selectedConditions.filter((id) => id !== conditionId)
      : [...config.selectedConditions, conditionId];

    const newConfig = { ...config, selectedConditions: newConditions };
    setConfig(newConfig);
    onConfigChange(newConfig);
  };

  const handleMetricToggle = (metricId) => {
    const newVisibleMetrics = {
      ...config.visibleMetrics,
      [metricId]: !config.visibleMetrics[metricId],
    };

    const newConfig = { ...config, visibleMetrics: newVisibleMetrics };
    setConfig(newConfig);
    onConfigChange(newConfig);
  };

  const handleUnitChange = (unit) => {
    const newConfig = { ...config, temperatureUnit: unit };
    setConfig(newConfig);
    onConfigChange(newConfig);
  };

  const handleFuturePredictionToggle = () => {
    const newConfig = {
      ...config,
      includeFuturePredictions: !config.includeFuturePredictions,
    };
    setConfig(newConfig);
    onConfigChange(newConfig);
  };

  const handleFutureDaysChange = (days) => {
    const newConfig = {
      ...config,
      futureDays: Math.max(1, Math.min(60, days)),
    };
    setConfig(newConfig);
    onConfigChange(newConfig);
  };

  const handleCustomThresholdChange = (condition, value) => {
    const newThresholds = {
      ...config.customThresholds,
      [`${condition}_threshold`]: value ? parseFloat(value) : null,
    };
    const newConfig = { ...config, customThresholds: newThresholds };
    setConfig(newConfig);
    onConfigChange(newConfig);
  };

  const handleAnalysisModeChange = (mode) => {
    const newConfig = { ...config, analysisMode: mode };
    setConfig(newConfig);
    onConfigChange(newConfig);
  };

  return (
    <div className="personalization-panel">
      <div className="panel-header">
        <h3>🎯 Personalizar Análisis Meteorológico</h3>
        <p>
          Configure análisis, métricas visibles y exportaciones (JSON/CSV) para
          eventos al aire libre
        </p>
      </div>

      {/* Modo de Análisis */}
      <div className="config-section">
        <h4>📊 Tipo de Análisis</h4>
        <div className="analysis-mode-options">
          <button
            className={`mode-button ${
              config.analysisMode === "basic" ? "active" : ""
            }`}
            onClick={() => handleAnalysisModeChange("basic")}
          >
            🔍 Análisis Básico
          </button>
          {/* <button
            className={`mode-button ${
              config.analysisMode === "outdoor_event" ? "active" : ""
            }`}
            onClick={() => handleAnalysisModeChange("outdoor_event")}
          >
            🏕️ Evento al Aire Libre
          </button> */}
        </div>
      </div>

      {/* Selección de Condiciones */}
      <div className="config-section">
        <h4>⚡ Condiciones a Analizar</h4>
        <div className="conditions-grid">
          {weatherConditions.map((condition) => (
            <div
              key={condition.id}
              className={`condition-card ${
                config.selectedConditions.includes(condition.id)
                  ? "selected"
                  : ""
              }`}
              onClick={() => handleConditionToggle(condition.id)}
            >
              <div className="condition-icon">{condition.icon}</div>
              <div className="condition-info">
                <h5>{condition.name}</h5>
                <p>{condition.description}</p>
              </div>
              <div className="condition-toggle">
                {config.selectedConditions.includes(condition.id) ? "✅" : "⬜"}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Unidades de Temperatura */}
      <div className="config-section">
        <h4>🌡️ Unidad de Temperatura</h4>
        <div className="temperature-units">
          <button
            className={`unit-button ${
              config.temperatureUnit === "celsius" ? "active" : ""
            }`}
            onClick={() => handleUnitChange("celsius")}
          >
            °C Celsius
          </button>
          <button
            className={`unit-button ${
              config.temperatureUnit === "fahrenheit" ? "active" : ""
            }`}
            onClick={() => handleUnitChange("fahrenheit")}
          >
            °F Fahrenheit
          </button>
        </div>
      </div>

      {/* Predicciones Futuras */}
      <div className="config-section">
        <h4>🔮 Predicciones Futuras</h4>
        <div className="future-predictions-config">
          <label className="toggle-container">
            <input
              type="checkbox"
              checked={config.includeFuturePredictions}
              onChange={handleFuturePredictionToggle}
            />
            <span className="toggle-slider"></span>
            Incluir predicciones para los próximos días
          </label>

          {config.includeFuturePredictions && (
            <div className="days-selector">
              <label>Días a predecir (máximo 60):</label>
              <input
                type="range"
                min="1"
                max="60"
                value={config.futureDays}
                onChange={(e) =>
                  handleFutureDaysChange(parseInt(e.target.value))
                }
                className="days-slider"
              />
              <span className="days-value">{config.futureDays} días</span>
            </div>
          )}
        </div>
      </div>

      {/* Métricas Visibles */}
      <div className="config-section">
        <h4>📊 Métricas a Mostrar</h4>
        <p className="section-description">
          Seleccione qué variables meteorológicas desea visualizar en el
          dashboard
        </p>
        <div className="metrics-grid">
          {availableMetrics.map((metric) => (
            <div key={metric.id} className="metric-item">
              <label className="metric-label">
                <input
                  type="checkbox"
                  checked={config.visibleMetrics[metric.id]}
                  onChange={() => handleMetricToggle(metric.id)}
                  className="metric-checkbox"
                />
                <div className="metric-info">
                  <div className="metric-header">
                    <span className="metric-icon">{metric.icon}</span>
                    <span className="metric-name">{metric.name}</span>
                    <span className="metric-unit">{metric.unit}</span>
                  </div>
                  <p className="metric-description">{metric.description}</p>
                </div>
              </label>
            </div>
          ))}
        </div>
      </div>

      {/* Umbrales Personalizados */}
      <div className="config-section">
        <h4>⚙️ Umbrales Personalizados (Opcional)</h4>
        <p className="section-description">
          Defina sus propios valores para considerar condiciones como "extremas"
        </p>
        <div className="custom-thresholds">
          {config.selectedConditions.map((conditionId) => {
            const condition = weatherConditions.find(
              (c) => c.id === conditionId
            );
            if (!condition) return null;

            const getThresholdInfo = (id) => {
              switch (id) {
                case "very_hot":
                  return {
                    unit: "°C",
                    placeholder: "ej: 35",
                    label: "Temperatura máxima",
                  };
                case "very_cold":
                  return {
                    unit: "°C",
                    placeholder: "ej: 5",
                    label: "Temperatura mínima",
                  };
                case "very_windy":
                  return {
                    unit: "km/h",
                    placeholder: "ej: 25",
                    label: "Velocidad del viento",
                  };
                case "very_wet":
                  return {
                    unit: "mm",
                    placeholder: "ej: 10",
                    label: "Precipitación",
                  };
                case "very_uncomfortable":
                  return {
                    unit: "°C",
                    placeholder: "ej: 40",
                    label: "Índice de calor",
                  };
                default:
                  return { unit: "", placeholder: "", label: "" };
              }
            };

            const thresholdInfo = getThresholdInfo(conditionId);

            return (
              <div key={conditionId} className="threshold-input">
                <label>
                  {condition.icon} {thresholdInfo.label}:
                </label>
                <div className="input-with-unit">
                  <input
                    type="number"
                    placeholder={thresholdInfo.placeholder}
                    value={
                      config.customThresholds[`${conditionId}_threshold`] || ""
                    }
                    onChange={(e) =>
                      handleCustomThresholdChange(conditionId, e.target.value)
                    }
                    className="threshold-value"
                  />
                  <span className="unit-label">{thresholdInfo.unit}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Configuración de Exportación */}
      <div className="config-section">
        <h4>💾 Configuración de Exportación (JSON/CSV)</h4>
        <p className="section-description">
          Configure qué datos incluir en las exportaciones JSON y CSV
        </p>
        <div className="export-config">
          <div className="export-options-grid">
            {availableMetrics.map((metric) => (
              <label key={`export-${metric.id}`} className="export-option">
                <input
                  type="checkbox"
                  checked={config.visibleMetrics[metric.id]}
                  onChange={() => handleMetricToggle(metric.id)}
                  className="export-checkbox"
                />
                <span className="export-icon">{metric.icon}</span>
                <span className="export-name">{metric.name}</span>
              </label>
            ))}
          </div>

          <div className="export-settings">
            <label className="export-setting">
              <input
                type="checkbox"
                checked={config.includeFuturePredictions}
                onChange={handleFuturePredictionToggle}
              />
              <span>
                Incluir predicciones futuras ({config.futureDays} días)
              </span>
            </label>

            <label className="export-setting">
              <input
                type="checkbox"
                checked={config.analysisMode === "outdoor_event"}
                onChange={(e) => {
                  const newConfig = {
                    ...config,
                    analysisMode: e.target.checked ? "outdoor_event" : "basic",
                  };
                  setConfig(newConfig);
                  onConfigChange(newConfig);
                }}
              />
              <span>Incluir análisis de eventos al aire libre</span>
            </label>

            <div className="export-info">
              <h5>📋 Datos que se incluirán en la exportación:</h5>
              <ul>
                <li>
                  ✅ Datos históricos (
                  {config.analysisMode === "outdoor_event" ? "30" : "10"} años)
                </li>
                <li>✅ Condiciones actuales</li>
                {config.includeFuturePredictions && (
                  <li>✅ Predicciones futuras ({config.futureDays} días)</li>
                )}
                <li>
                  ✅ Métricas seleccionadas (
                  {Object.values(config.visibleMetrics).filter(Boolean).length}{" "}
                  de {availableMetrics.length})
                </li>
                <li>✅ Configuración personalizada (umbrales, unidades)</li>
                {config.analysisMode === "outdoor_event" && (
                  <li>✅ Análisis de eventos al aire libre</li>
                )}
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Resumen de Configuración */}
      <div className="config-summary">
        <h4>📋 Resumen de Configuración</h4>
        <div className="summary-items">
          <div className="summary-item">
            <strong>Condiciones:</strong> {config.selectedConditions.length}{" "}
            seleccionadas
          </div>
          <div className="summary-item">
            <strong>Temperatura:</strong>{" "}
            {config.temperatureUnit === "celsius"
              ? "Celsius (°C)"
              : "Fahrenheit (°F)"}
          </div>
          <div className="summary-item">
            <strong>Predicciones:</strong>{" "}
            {config.includeFuturePredictions
              ? `${config.futureDays} días`
              : "Desactivadas"}
          </div>
          <div className="summary-item">
            <strong>Métricas visibles:</strong>{" "}
            {Object.values(config.visibleMetrics).filter(Boolean).length} de{" "}
            {availableMetrics.length}
          </div>
          <div className="summary-item">
            <strong>Modo:</strong>{" "}
            {config.analysisMode === "basic"
              ? "Análisis Básico"
              : "Evento al Aire Libre"}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PersonalizationPanel;
