import React, { useState } from "react";
import "./WeatherMetricsDisplay.css";

const WeatherMetricsDisplay = ({
  weatherData,
  personalizationConfig,
  futurePredictions = [],
}) => {
  const [showGlossary, setShowGlossary] = useState(false);
  // Iconos profesionales mejorados para diferentes condiciones
  const getWeatherIcon = (metricType, value, thresholds) => {
    switch (metricType) {
      case "temperature":
        if (value >= 35) return "🔥"; // Extremo calor
        if (value >= 30) return "☀️"; // Muy caliente
        if (value >= 25) return "🌤️"; // Caliente
        if (value >= 20) return "⛅"; // Templado
        if (value >= 15) return "🌥️"; // Fresco
        if (value >= 5) return "❄️"; // Frío
        return "🧊"; // Muy frío

      case "precipitation":
        if (value >= 20) return "⛈️"; // Tormenta intensa
        if (value >= 10) return "�️"; // Lluvia fuerte
        if (value >= 5) return "🌦️"; // Lluvia moderada
        if (value >= 1) return "�️"; // Lluvia ligera
        return "☀️"; // Sin lluvia

      case "wind_speed":
        if (value >= 50) return "🌪️"; // Tornado/Huracán
        if (value >= 30) return "�️💨"; // Viento muy fuerte
        if (value >= 20) return "💨"; // Viento fuerte
        if (value >= 10) return "🍃"; // Brisa
        return "🌀"; // Calma

      case "humidity":
        if (value >= 80) return "�"; // Muy húmedo
        if (value >= 60) return "💧"; // Húmedo
        if (value >= 40) return "�"; // Confortable
        if (value >= 20) return "�"; // Seco
        return "🏜️"; // Muy seco

      case "heat_index":
        if (value >= 40) return "�️🔥"; // Peligroso
        if (value >= 35) return "�"; // Extremo
        if (value >= 30) return "🌡️"; // Caliente
        if (value >= 25) return "�"; // Confortable
        if (value >= 20) return "🙂"; // Fresco
        return "❄️"; // Frío

      default:
        return "📊";
    }
  };

  // Determinar etiqueta basada en umbrales personalizados
  const getConditionLabel = (metricType, value, customThresholds, unit) => {
    const thresholds = customThresholds || {};

    switch (metricType) {
      case "temperature":
        const hotThreshold = thresholds.very_hot_threshold || 35;
        const coldThreshold = thresholds.very_cold_threshold || 5;

        if (value >= hotThreshold)
          return { label: "Muy Caliente", color: "#ef4444", intensity: "high" };
        if (value >= hotThreshold - 5)
          return { label: "Caliente", color: "#f97316", intensity: "medium" };
        if (value <= coldThreshold)
          return { label: "Muy Frío", color: "#3b82f6", intensity: "high" };
        if (value <= coldThreshold + 5)
          return { label: "Frío", color: "#6366f1", intensity: "medium" };
        return { label: "Templado", color: "#10b981", intensity: "low" };

      case "precipitation":
        const wetThreshold = thresholds.very_wet_threshold || 10;

        if (value >= wetThreshold)
          return { label: "Muy Húmedo", color: "#3b82f6", intensity: "high" };
        if (value >= wetThreshold / 2)
          return { label: "Húmedo", color: "#6366f1", intensity: "medium" };
        if (value > 0)
          return { label: "Ligera Lluvia", color: "#8b5cf6", intensity: "low" };
        return { label: "Seco", color: "#10b981", intensity: "low" };

      case "wind_speed":
        const windyThreshold = thresholds.very_windy_threshold || 25;

        if (value >= windyThreshold)
          return { label: "Muy Ventoso", color: "#ef4444", intensity: "high" };
        if (value >= windyThreshold / 2)
          return { label: "Ventoso", color: "#f97316", intensity: "medium" };
        if (value > 5)
          return { label: "Brisa", color: "#10b981", intensity: "low" };
        return { label: "Calma", color: "#6b7280", intensity: "low" };

      case "humidity":
        if (value >= 80)
          return { label: "Muy Húmedo", color: "#3b82f6", intensity: "high" };
        if (value >= 60)
          return { label: "Húmedo", color: "#6366f1", intensity: "medium" };
        if (value >= 40)
          return { label: "Cómodo", color: "#10b981", intensity: "low" };
        return { label: "Seco", color: "#f59e0b", intensity: "medium" };

      case "heat_index":
        const uncomfortableThreshold =
          thresholds.very_uncomfortable_threshold || 40;

        if (value >= uncomfortableThreshold)
          return { label: "Muy Incómodo", color: "#ef4444", intensity: "high" };
        if (value >= uncomfortableThreshold - 5)
          return { label: "Incómodo", color: "#f97316", intensity: "medium" };
        return { label: "Cómodo", color: "#10b981", intensity: "low" };

      default:
        return { label: "Normal", color: "#6b7280", intensity: "low" };
    }
  };

  // Formatear valor según unidad
  const formatValue = (value, metricType, unit) => {
    if (metricType === "temperature" || metricType === "heat_index") {
      return `${Math.round(value)}°${unit === "fahrenheit" ? "F" : "C"}`;
    }
    if (metricType === "precipitation") {
      return `${value.toFixed(1)}mm`;
    }
    if (metricType === "wind_speed") {
      return `${Math.round(value)}km/h`;
    }
    if (metricType === "humidity") {
      return `${Math.round(value)}%`;
    }
    return value.toString();
  };

  // Obtener predicciones para los próximos días configurados
  const getNextDays = () => {
    const today = new Date();
    const days = [];
    const futureDays = personalizationConfig.futureDays || 3; // Usar configuración del usuario

    for (let i = 1; i <= futureDays; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);

      // Buscar predicción para esta fecha en futurePredictions
      const prediction = futurePredictions.find((pred) => {
        const predDate = new Date(pred.date);
        return predDate.toDateString() === date.toDateString();
      });

      days.push({
        date: date,
        day: date.getDate(),
        month: date.toLocaleDateString("es-ES", { month: "long" }),
        prediction: prediction,
      });
    }

    return days;
  };

  const nextDays = getNextDays();

  // Métricas disponibles con iconos mejorados
  const allMetrics = [
    {
      type: "temperature",
      name: "Temperatura",
      icon: "🌡️",
      current: weatherData?.current_conditions?.temperature || 20,
      unit: personalizationConfig.temperatureUnit || "celsius",
    },
    {
      type: "precipitation",
      name: "Precipitación",
      icon: "🌧️",
      current: weatherData?.current_conditions?.precipitation || 0,
      unit: "mm",
    },
    {
      type: "wind_speed",
      name: "Velocidad del Viento",
      icon: "💨",
      current: weatherData?.current_conditions?.wind_speed || 10,
      unit: "km/h",
    },
    {
      type: "humidity",
      name: "Humedad Relativa",
      icon: "💧",
      current: weatherData?.current_conditions?.humidity || 50,
      unit: "%",
    },
    {
      type: "heat_index",
      name: "Índice de Calor",
      icon: "🌡️🔥",
      current: weatherData?.current_conditions?.heat_index || 22,
      unit: personalizationConfig.temperatureUnit || "celsius",
    },
  ];

  // Filtrar métricas basándose en la configuración del usuario
  const metricsToShow = allMetrics.filter(
    (metric) => personalizationConfig.visibleMetrics?.[metric.type] !== false
  );

  // Información detallada para tooltips/glosario
  const metricDescriptions = {
    temperature: {
      title: "Temperatura del Aire",
      description:
        "Medida del calor o frío del ambiente. Es fundamental para determinar el confort térmico y planificar actividades al aire libre.",
      ranges: {
        extreme_hot: "> 35°C - Calor extremo, evitar exposición prolongada",
        hot: "30-35°C - Muy caliente, buscar sombra e hidratación",
        warm: "25-30°C - Caliente, ideal para actividades acuáticas",
        comfortable:
          "20-25°C - Temperatura confortable para la mayoría de actividades",
        cool: "15-20°C - Fresco, ideal para deportes y senderismo",
        cold: "5-15°C - Frío, necesaria ropa de abrigo",
        extreme_cold: "< 5°C - Muy frío, protección especial requerida",
      },
    },
    precipitation: {
      title: "Precipitación",
      description:
        "Cantidad de agua que cae del cielo en forma de lluvia, nieve o granizo. Crítica para actividades al aire libre y agricultura.",
      ranges: {
        none: "0 mm - Sin precipitación, condiciones secas",
        light: "0.1-2.5 mm - Lluvia ligera, puede continuar actividades",
        moderate: "2.6-10 mm - Lluvia moderada, considerar refugio",
        heavy: "10.1-50 mm - Lluvia fuerte, suspender actividades exteriores",
        extreme: "> 50 mm - Lluvia torrencial, condiciones peligrosas",
      },
    },
    wind_speed: {
      title: "Velocidad del Viento",
      description:
        "Velocidad del movimiento del aire. Afecta la sensación térmica, la navegación, deportes y puede ser peligroso en intensidades altas.",
      ranges: {
        calm: "0-5 km/h - Calma, humo asciende verticalmente",
        light: "6-11 km/h - Brisa ligera, se siente en la cara",
        gentle: "12-19 km/h - Brisa suave, mueve hojas pequeñas",
        moderate: "20-28 km/h - Brisa moderada, polvo y papel suelto",
        fresh: "29-38 km/h - Brisa fresca, se mueven ramas pequeñas",
        strong: "39-61 km/h - Viento fuerte, dificulta caminar",
        gale: "> 62 km/h - Vendaval, condiciones peligrosas",
      },
    },
    humidity: {
      title: "Humedad Relativa",
      description:
        "Porcentaje de humedad en el aire respecto al máximo que puede contener. Alta humedad aumenta la sensación de calor.",
      ranges: {
        very_low: "< 20% - Muy seco, irritación nasal y ocular",
        low: "20-40% - Seco, confortable en invierno",
        comfortable: "40-60% - Ideal para confort humano",
        high: "60-80% - Húmedo, aumenta sensación de calor",
        very_high: "> 80% - Muy húmedo, incomodidad y condensación",
      },
    },
    heat_index: {
      title: "Índice de Calor (Sensación Térmica)",
      description:
        "Temperatura que percibe el cuerpo considerando humedad. Más preciso que la temperatura para evaluar confort y riesgo de calor.",
      ranges: {
        comfortable: "< 27°C - Confortable para la mayoría",
        caution: "27-32°C - Precaución, posible fatiga con exposición",
        extreme_caution: "32-40°C - Extrema precaución, riesgo de calambres",
        danger: "40-54°C - Peligro, alto riesgo de agotamiento por calor",
        extreme_danger: "> 54°C - Peligro extremo, insolación inminente",
      },
    },
  };

  return (
    <div className="weather-metrics-display">
      <div className="metrics-header">
        <div className="header-content">
          <h2>📊 Métricas Meteorológicas Personalizadas</h2>
          <button
            className="glossary-button"
            onClick={() => setShowGlossary(true)}
            title="Ver glosario de métricas"
          >
            📖 Glosario
          </button>
        </div>
        <div className="location-info">
          <span>📍 {weatherData?.location || "Ubicación"}</span>
          <span>
            📅{" "}
            {new Date().toLocaleDateString("es-ES", {
              weekday: "long",
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </span>
        </div>
      </div>

      <div className="metrics-grid">
        {metricsToShow.map((metric) => {
          const condition = getConditionLabel(
            metric.type,
            metric.current,
            personalizationConfig.customThresholds,
            metric.unit
          );

          return (
            <div
              key={metric.type}
              className={`metric-card ${condition.intensity}`}
            >
              <div className="metric-header">
                <div className="metric-icon">{metric.icon}</div>
                <div className="metric-info">
                  <div className="metric-name">
                    {metric.name}
                    <div className="metric-tooltip">
                      <span className="tooltip-icon">ℹ️</span>
                      <div className="tooltip-content">
                        <h4>{metricDescriptions[metric.type]?.title}</h4>
                        <p>{metricDescriptions[metric.type]?.description}</p>
                        <div className="ranges">
                          <strong>Rangos típicos:</strong>
                          <ul>
                            {Object.entries(
                              metricDescriptions[metric.type]?.ranges || {}
                            ).map(([key, range]) => (
                              <li key={key}>{range}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div
                  className="metric-label"
                  style={{ backgroundColor: condition.color }}
                >
                  {condition.label}
                </div>
              </div>

              <div className="metric-current">
                <span className="current-value">
                  {formatValue(metric.current, metric.type, metric.unit)}
                </span>
              </div>

              <div className="metric-forecast">
                <div className="forecast-header">
                  Próximos {personalizationConfig.futureDays || 3} días
                </div>
                <div className="forecast-days">
                  {nextDays.map((day, index) => {
                    // Intentar obtener predicción real del backend
                    let futureValue =
                      metric.current + (Math.random() - 0.5) * 10; // Valor por defecto simulado

                    if (day.prediction) {
                      // Si hay predicción real del backend, usarla
                      switch (metric.type) {
                        case "temperature":
                          futureValue =
                            day.prediction.temperature || futureValue;
                          break;
                        case "precipitation":
                          futureValue =
                            day.prediction.precipitation || futureValue;
                          break;
                        case "wind_speed":
                          futureValue =
                            day.prediction.wind_speed || futureValue;
                          break;
                        case "humidity":
                          futureValue = day.prediction.humidity || futureValue;
                          break;
                        case "heat_index":
                          futureValue =
                            day.prediction.heat_index || futureValue;
                          break;
                        default:
                          // Mantener valor simulado si no hay datos específicos
                          break;
                      }
                    }

                    const futureCondition = getConditionLabel(
                      metric.type,
                      futureValue,
                      personalizationConfig.customThresholds,
                      metric.unit
                    );

                    return (
                      <div key={index} className="forecast-day">
                        <div className="day-header">
                          <div className="day-date">
                            {day.day} de{" "}
                            {day.month.charAt(0).toUpperCase() +
                              day.month.slice(1)}
                          </div>
                          <div className="day-icon">
                            {getWeatherIcon(
                              metric.type,
                              futureValue,
                              personalizationConfig.customThresholds
                            )}
                          </div>
                        </div>
                        <div
                          className="day-value"
                          style={{ color: futureCondition.color }}
                          title={`${futureCondition.label} - ${
                            futureCondition.description || ""
                          }`}
                        >
                          {formatValue(futureValue, metric.type, metric.unit)}
                        </div>
                        <div className="day-condition-label">
                          {futureCondition.label}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Resumen de alertas basado en umbrales personalizados */}
      <div className="alerts-section">
        <h3>Notificaciones</h3>
        <div className="alerts-grid">
          {metricsToShow
            .map((metric) => {
              const condition = getConditionLabel(
                metric.type,
                metric.current,
                personalizationConfig.customThresholds,
                metric.unit
              );

              if (condition.intensity === "high") {
                return (
                  <div key={metric.type} className="alert-card high">
                    <div className="alert-icon">{metric.icon}</div>
                    <div className="alert-content">
                      <strong>{condition.label}</strong>
                      <span>
                        {metric.name}:{" "}
                        {formatValue(metric.current, metric.type, metric.unit)}
                      </span>
                    </div>
                  </div>
                );
              }
              return null;
            })
            .filter(Boolean)}

          {metricsToShow.every(
            (metric) =>
              getConditionLabel(
                metric.type,
                metric.current,
                personalizationConfig.customThresholds,
                metric.unit
              ).intensity !== "high"
          ) && (
            <div className="alert-card safe">
              <div className="alert-icon">✅</div>
              <div className="alert-content">
                <strong>Condiciones Favorables</strong>
                <span>Todas las métricas están dentro de rangos cómodos</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Modal del Glosario */}
      {showGlossary && (
        <div className="glossary-modal">
          <div className="glossary-content">
            <div className="glossary-header">
              <h3>📖 Glosario de Métricas Meteorológicas</h3>
              <button
                className="close-button"
                onClick={() => setShowGlossary(false)}
              >
                ✕
              </button>
            </div>
            <div className="glossary-body">
              {Object.entries(metricDescriptions).map(([key, info]) => (
                <div key={key} className="glossary-item">
                  <h4>{info.title}</h4>
                  <p>{info.description}</p>
                  <div className="ranges-info">
                    <strong>Rangos de interpretación:</strong>
                    <ul>
                      {Object.entries(info.ranges).map(([rangeKey, range]) => (
                        <li key={rangeKey}>{range}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WeatherMetricsDisplay;
