import React from "react";
import "./ProbabilityDisplay.css";

const ProbabilityDisplay = ({
  probabilities,
  location,
  dateOfYear,
  availableConditions,
  userPreferences = {},
}) => {
  if (!probabilities) {
    return (
      <div className="probability-display-container">
        <h2>📊 Análisis de Probabilidades Climáticas</h2>
        <p>No hay datos disponibles</p>
      </div>
    );
  }

  const formatProbability = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const getConditionInfo = (condition) => {
    const conditionMap = {
      very_hot: {
        name: "�️ Muy Caliente",
        description:
          "Temperaturas extremadamente altas que pueden ser peligrosas para actividades al aire libre",
        details:
          "Temperatura superior al 90% de los datos históricos. Recomendamos evitar actividades intensas durante las horas más calurosas.",
        color: "#ef4444",
        icon: "🔥",
        riskLevel: "Peligro por calor extremo",
      },
      very_cold: {
        name: "❄️ Muy Frío",
        description:
          "Temperaturas extremadamente bajas que requieren preparación especial",
        details:
          "Temperatura inferior al 10% de los datos históricos. Necesario ropa de abrigo y precauciones adicionales.",
        color: "#3b82f6",
        icon: "🧊",
        riskLevel: "Riesgo de hipotermia",
      },
      very_windy: {
        name: "💨 Muy Ventoso",
        description:
          "Vientos fuertes que pueden afectar actividades al aire libre",
        details:
          "Velocidad del viento superior al 85% de los datos históricos. Puede dificultar actividades como camping o deportes.",
        color: "#06b6d4",
        icon: "🌪️",
        riskLevel: "Condiciones ventosas peligrosas",
      },
      very_wet: {
        name: "🌧️ Muy Húmedo",
        description:
          "Precipitación intensa que puede cancelar planes al aire libre",
        details:
          "Precipitación superior al 80% de los datos históricos. Alto riesgo de lluvia fuerte o tormentas.",
        color: "#8b5cf6",
        icon: "⛈️",
        riskLevel: "Riesgo de tormentas intensas",
      },
      very_uncomfortable: {
        name: "🥵 Muy Incómodo",
        description:
          "Combinación de temperatura y humedad que puede causar malestar",
        details:
          "Índice de calor superior al 85% de los datos históricos. La sensación térmica puede ser agobiante.",
        color: "#f59e0b",
        icon: "😰",
        riskLevel: "Condiciones de malestar térmico",
      },
    };

    return (
      conditionMap[condition] || {
        name: condition,
        description: "Condición climática",
        details: "Información no disponible",
        color: "#6b7280",
        icon: "🌤️",
        riskLevel: "Nivel de riesgo desconocido",
      }
    );
  };

  const getSeverityColor = (probability) => {
    if (probability >= 0.7) return "#ef4444"; // Rojo - Alto riesgo
    if (probability >= 0.4) return "#f59e0b"; // Amarillo - Riesgo moderado
    return "#10b981"; // Verde - Bajo riesgo
  };

  const getSeverityText = (probability) => {
    if (probability >= 0.7) return "ALTO RIESGO";
    if (probability >= 0.4) return "RIESGO MODERADO";
    return "BAJO RIESGO";
  };

  const getSeverityIcon = (probability) => {
    if (probability >= 0.7) return "🚨";
    if (probability >= 0.4) return "⚠️";
    return "✅";
  };

  // Convertir array de probabilidades a objeto con las condiciones
  const probabilityData = {};
  if (Array.isArray(probabilities)) {
    probabilities.forEach((prob) => {
      probabilityData[prob.condition] = {
        probability: prob.probability,
        threshold: prob.threshold_value,
        unit: prob.unit,
      };
    });
  } else {
    // Si ya es un objeto, usarlo directamente
    Object.assign(probabilityData, probabilities);
  }

  return (
    <div className="probability-display-container">
      <h2>📊 Análisis de Probabilidades Climáticas</h2>
      <p className="subtitle">
        Predicciones inteligentes basadas en datos reales de NASA POWER y
        modelos de Machine Learning
      </p>

      <div className="location-info">
        <p>
          <strong>📍 Ubicación:</strong>{" "}
          {location?.name ||
            `${location?.latitude || "N/A"}, ${location?.longitude || "N/A"}`}
        </p>
        <p>
          <strong>📅 Fecha objetivo:</strong> {dateOfYear}
        </p>
        {location?.data_source && (
          <p>
            <strong>🔬 Fuente de datos:</strong>{" "}
            {location.data_source === "real_nasa_power"
              ? "🌍 NASA POWER (Datos reales + IA)"
              : location.data_source === "mock"
              ? "🧪 Datos sintéticos"
              : location.data_source}
          </p>
        )}
        {location?.data_points && (
          <p>
            <strong>📊 Análisis:</strong> {location.data_points} registros
            históricos de {location.years_analyzed || 30} años procesados con
            Machine Learning
          </p>
        )}
      </div>

      {Object.keys(probabilityData).length === 0 ? (
        <div className="no-data-message">
          <p>
            📈 Haz clic en "Analizar Probabilidades" para obtener información
            detallada
          </p>
        </div>
      ) : (
        <div className="probabilities-container">
          <div className="explanation-box">
            <h3>🎯 ¿Qué significan estas probabilidades?</h3>
            <p>
              Estas probabilidades te ayudan a planificar actividades al aire
              libre como vacaciones, senderismo, pesca o eventos. Cada condición
              representa la likelihood de experimentar condiciones adversas en
              la fecha y ubicación seleccionadas, basándose en 30 años de datos
              históricos.
            </p>
          </div>

          <div className="conditions-grid">
            {Object.entries(probabilityData).map(([condition, data]) => {
              const conditionInfo = getConditionInfo(condition);
              const probability =
                typeof data === "number" ? data : data.probability;
              const threshold = data.threshold;
              const unit = data.unit;

              return (
                <div key={condition} className="condition-card">
                  <div className="condition-header">
                    <div className="condition-title">
                      <span className="condition-icon">
                        {conditionInfo.icon}
                      </span>
                      <h3>{conditionInfo.name}</h3>
                    </div>
                    <div
                      className="severity-badge"
                      style={{ backgroundColor: getSeverityColor(probability) }}
                    >
                      {getSeverityIcon(probability)}{" "}
                      {getSeverityText(probability)}
                    </div>
                  </div>

                  <div className="probability-display">
                    <div
                      className="probability-percentage"
                      style={{ color: conditionInfo.color }}
                    >
                      {formatProbability(probability)}
                    </div>
                    <div className="probability-label">de probabilidad</div>
                  </div>

                  {userPreferences.showProbabilityBars !== false && (
                    <div className="probability-bar">
                      <div
                        className="probability-fill"
                        style={{
                          width: `${probability * 100}%`,
                          backgroundColor: conditionInfo.color,
                        }}
                      />
                    </div>
                  )}

                  <div className="condition-description">
                    <p>
                      <strong>Descripción:</strong> {conditionInfo.description}
                    </p>
                    <p>
                      <strong>Detalles:</strong> {conditionInfo.details}
                    </p>
                    {threshold && unit && (
                      <p>
                        <strong>Umbral:</strong> {threshold.toFixed(1)} {unit}
                      </p>
                    )}
                    <p>
                      <strong>Implicación:</strong> {conditionInfo.riskLevel}
                    </p>
                  </div>

                  <div className="recommendation">
                    {probability >= 0.7 && (
                      <p className="rec high-risk">
                        🚨 <strong>Recomendación:</strong> Considerar
                        reprogramar la actividad o tomar precauciones extremas.
                      </p>
                    )}
                    {probability >= 0.4 && probability < 0.7 && (
                      <p className="rec medium-risk">
                        ⚠️ <strong>Recomendación:</strong> Prepararse
                        adecuadamente y monitorear las condiciones.
                      </p>
                    )}
                    {probability < 0.4 && (
                      <p className="rec low-risk">
                        ✅ <strong>Recomendación:</strong> Condiciones
                        favorables para actividades al aire libre.
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          <div className="methodology-note">
            <h4>📚 Metodología con Inteligencia Artificial</h4>
            <p>
              <strong>🌍 Datos Reales:</strong> Utilizamos la API NASA POWER que
              proporciona hasta 40 años de datos meteorológicos globales
              derivados de observaciones satelitales y reanálisis atmosféricos.
            </p>
            <p>
              <strong>🤖 Machine Learning:</strong> Los modelos de Random Forest
              y Gradient Boosting se entrenan automáticamente con los datos
              históricos para cada ubicación, mejorando la precisión de las
              predicciones.
            </p>
            <p>
              <strong>📊 Análisis Estadístico:</strong> Las probabilidades se
              calculan usando percentiles adaptativos que consideran la
              variabilidad climática local y tendencias temporales.
            </p>
            <p>
              <strong>🔄 Actualización Continua:</strong> Los modelos se
              reentrenan automáticamente cuando se obtienen nuevos datos,
              asegurando predicciones actualizadas.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProbabilityDisplay;
