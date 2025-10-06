import React, { useState, useEffect } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { Line, Bar } from "react-chartjs-2";
import "./WeatherChart.css";

// Registrar componentes de Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const WeatherChart = ({
  historicalData,
  statistics,
  userPreferences = {},
  currentLocation,
  currentDate,
  onYearsRangeChange,
  currentPersonalizationConfig,
}) => {
  const [activeChart, setActiveChart] = useState("temperature");
  const [chartType, setChartType] = useState(
    userPreferences.chartType || "line"
  );
  const [selectedYears, setSelectedYears] = useState(30); // Por defecto 30 años
  const [forceUpdate, setForceUpdate] = useState(0);

  // Sincronizar selectedYears con los datos realmente mostrados
  useEffect(() => {
    if (historicalData && historicalData.length > 0) {
      // Si los datos recibidos no coinciden con selectedYears, actualizarlo
      // para que la UI esté sincronizada con los datos reales
      console.log(
        "📊 Data received:",
        historicalData.length,
        "records. Current selectedYears:",
        selectedYears
      );
      setForceUpdate((prev) => prev + 1);
    }
  }, [historicalData, selectedYears]);

  // Handler para cambios específicos de años (evita useEffect problemático)
  const handleYearsChange = (newYears) => {
    console.log("🔄 WeatherChart: User changed years to", newYears);
    setSelectedYears(newYears);

    if (currentLocation && onYearsRangeChange && currentPersonalizationConfig) {
      const queryData = {
        latitude: currentLocation.latitude,
        longitude: currentLocation.longitude,
        // date_of_year se omite para usar la fecha actual automáticamente
        selected_conditions: currentPersonalizationConfig.selectedConditions,
        temperature_unit: currentPersonalizationConfig.temperatureUnit,
        include_future_predictions:
          currentPersonalizationConfig.includeFuturePredictions,
        future_days: currentPersonalizationConfig.futureDays,
        custom_thresholds:
          Object.keys(currentPersonalizationConfig.customThresholds || {})
            .length > 0
            ? currentPersonalizationConfig.customThresholds
            : null,
        years_range: newYears,
      };

      onYearsRangeChange(queryData);
    }

    // setForceUpdate se maneja en useEffect cuando llegan los datos
  };

  if (!historicalData || historicalData.length === 0) {
    return (
      <div className="weather-chart-container">
        <div className="chart-header">
          <h2>📊 Análisis Histórico de Datos Meteorológicos</h2>
          <p className="chart-subtitle">Datos científicos de NASA POWER</p>
        </div>
        <div className="no-data-message">
          <div className="no-data-icon">📈</div>
          <h3>Sin Datos Históricos</h3>
          <p>No hay información histórica disponible para mostrar gráficos.</p>
        </div>
      </div>
    );
  }

  // Preparar datos para los gráficos - Los datos ya vienen filtrados del backend
  console.log(
    "📊 WeatherChart render - historicalData:",
    historicalData.length,
    "records, selectedYears:",
    selectedYears
  );

  const years = historicalData.map((item) => new Date(item.date).getFullYear());
  const temperatures = historicalData.map((item) => item.temperature);
  const precipitations = historicalData.map((item) => item.precipitation);
  const windSpeeds = historicalData.map((item) => item.wind_speed);
  const humidities = historicalData.map((item) => item.humidity);

  console.log(
    "📊 Chart data prepared - years range:",
    Math.min(...years),
    "to",
    Math.max(...years)
  );

  const chartTypes = [
    {
      value: "line",
      label: "📈 Línea",
      icon: "📈",
      description: "Tendencias suaves",
    },
    {
      value: "bar",
      label: "📊 Barras",
      icon: "📊",
      description: "Comparación directa",
    },
    {
      value: "area",
      label: "📉 Área",
      icon: "📉",
      description: "Volumen de datos",
    },
  ];

  const yearOptions = [
    {
      value: 10,
      label: "📅 10 años",
      icon: "📅",
      description: "Década reciente",
    },
    {
      value: 20,
      label: "📅 20 años",
      icon: "📅",
      description: "Dos décadas",
    },
    {
      value: 30,
      label: "📅 30 años",
      icon: "📅",
      description: "Tres décadas",
    },
    {
      value: 50,
      label: "📅 50 años",
      icon: "📅",
      description: "Medio siglo",
    },
  ];

  const chartConfigs = {
    temperature: {
      title: "🌡️ Temperatura Histórica",
      subtitle: "Análisis térmico anual",
      data: temperatures,
      color: "#ef4444",
      gradient: "linear-gradient(135deg, #ef4444, #dc2626)",
      backgroundColor: "rgba(239, 68, 68, 0.1)",
      unit: "°C",
      enabled: userPreferences.showTemperature !== false,
      icon: "🌡️",
      trend:
        temperatures.length > 1
          ? temperatures[temperatures.length - 1] > temperatures[0]
            ? "up"
            : "down"
          : "stable",
    },
    precipitation: {
      title: "🌧️ Precipitación Histórica",
      subtitle: "Patrones de lluvia",
      data: precipitations,
      color: "#3b82f6",
      gradient: "linear-gradient(135deg, #3b82f6, #2563eb)",
      backgroundColor: "rgba(59, 130, 246, 0.1)",
      unit: "mm",
      enabled: userPreferences.showPrecipitation !== false,
      icon: "🌧️",
      trend:
        precipitations.length > 1
          ? precipitations[precipitations.length - 1] > precipitations[0]
            ? "up"
            : "down"
          : "stable",
    },
    wind_speed: {
      title: "💨 Velocidad del Viento",
      subtitle: "Intensidad del viento",
      data: windSpeeds,
      color: "#06b6d4",
      gradient: "linear-gradient(135deg, #06b6d4, #0891b2)",
      backgroundColor: "rgba(6, 182, 212, 0.1)",
      unit: "km/h",
      enabled: userPreferences.showWindSpeed !== false,
      icon: "💨",
      trend:
        windSpeeds.length > 1
          ? windSpeeds[windSpeeds.length - 1] > windSpeeds[0]
            ? "up"
            : "down"
          : "stable",
    },
    humidity: {
      title: "💧 Humedad Relativa",
      subtitle: "Niveles de humedad",
      data: humidities,
      color: "#8b5cf6",
      gradient: "linear-gradient(135deg, #8b5cf6, #7c3aed)",
      backgroundColor: "rgba(139, 92, 246, 0.1)",
      unit: "%",
      enabled: userPreferences.showHumidity !== false,
      icon: "💧",
      trend:
        humidities.length > 1
          ? humidities[humidities.length - 1] > humidities[0]
            ? "up"
            : "down"
          : "stable",
    },
  };

  // Filtrar opciones según las preferencias del usuario
  const availableCharts = Object.entries(chartConfigs).filter(
    ([key, config]) => config.enabled
  );

  // Si el gráfico activo no está habilitado, cambiar al primer disponible
  const currentConfig = chartConfigs[activeChart];
  if (!currentConfig?.enabled && availableCharts.length > 0) {
    setActiveChart(availableCharts[0][0]);
    return null; // Re-render con el nuevo activeChart
  }

  if (availableCharts.length === 0) {
    return (
      <div className="weather-chart-container">
        <div className="chart-header">
          <h2>📊 Análisis Histórico de Datos Meteorológicos</h2>
          <p className="chart-subtitle">Configure las variables a mostrar</p>
        </div>
        <div className="no-variables-selected">
          <div className="no-data-icon">⚙️</div>
          <h3>Variables No Seleccionadas</h3>
          <p>
            Vaya a Configuración para activar las variables meteorológicas que
            desea visualizar
          </p>
        </div>
      </div>
    );
  }

  // Calcular estadísticas básicas
  const calculateStats = (data) => {
    const sorted = [...data].sort((a, b) => a - b);
    const sum = data.reduce((a, b) => a + b, 0);
    return {
      mean: sum / data.length,
      median: sorted[Math.floor(sorted.length / 2)],
      min: Math.min(...data),
      max: Math.max(...data),
      std: Math.sqrt(
        data.reduce((sq, n) => sq + Math.pow(n - sum / data.length, 2), 0) /
          data.length
      ),
    };
  };

  const currentStats = calculateStats(currentConfig.data);

  const chartData = {
    labels: years,
    datasets: [
      {
        label: currentConfig.title,
        data: currentConfig.data,
        borderColor: currentConfig.color,
        backgroundColor:
          chartType === "area"
            ? currentConfig.backgroundColor
            : chartType === "bar"
            ? currentConfig.color
            : "rgba(0, 0, 0, 0)",
        borderWidth: chartType === "bar" ? 0 : 3,
        fill: chartType === "area",
        tension: chartType === "line" || chartType === "area" ? 0.4 : 0,
        pointRadius: chartType === "bar" ? 0 : 5,
        pointHoverRadius: chartType === "bar" ? 0 : 8,
        pointBackgroundColor: currentConfig.color,
        pointBorderColor: "#ffffff",
        pointBorderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      intersect: false,
      mode: "index",
    },
    plugins: {
      legend: {
        position: "top",
        display: true,
        labels: {
          color: "#374151",
          usePointStyle: true,
          font: {
            size: 14,
            weight: "600",
          },
          padding: 20,
        },
      },
      title: {
        display: false,
      },
      tooltip: {
        backgroundColor: "rgba(0, 0, 0, 0.9)",
        titleColor: "white",
        bodyColor: "white",
        cornerRadius: 10,
        displayColors: true,
        callbacks: {
          title: function (context) {
            return `Año ${context[0].label}`;
          },
          label: function (context) {
            return `${context.dataset.label}: ${context.parsed.y.toFixed(1)} ${
              currentConfig.unit
            }`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: `${currentConfig.unit}`,
          color: "#6b7280",
          font: {
            size: 12,
            weight: "600",
          },
        },
        ticks: {
          color: "#6b7280",
          font: {
            size: 11,
          },
          callback: function (value) {
            return `${value.toFixed(1)} ${currentConfig.unit}`;
          },
        },
        grid: {
          color: "rgba(0, 0, 0, 0.05)",
          drawBorder: false,
        },
      },
      x: {
        title: {
          display: true,
          text: "Año",
          color: "#6b7280",
          font: {
            size: 12,
            weight: "600",
          },
        },
        ticks: {
          color: "#6b7280",
          font: {
            size: 11,
          },
        },
        grid: {
          color: "rgba(0, 0, 0, 0.05)",
          drawBorder: false,
        },
      },
    },
  };

  const ChartComponent = chartType === "bar" ? Bar : Line;

  const getTrendIcon = (trend) => {
    switch (trend) {
      case "up":
        return "📈";
      case "down":
        return "📉";
      default:
        return "➡️";
    }
  };

  return (
    <div className="weather-chart-container">
      <div className="chart-header">
        <div className="header-content">
          <h2>📊 Análisis Histórico de Datos Meteorológicos</h2>
          <p className="chart-subtitle">
            Mostrando últimos {selectedYears} años • {historicalData.length}{" "}
            años de datos disponibles • NASA POWER
          </p>
        </div>
        <div className="chart-trend">
          <span className="trend-icon">
            {getTrendIcon(currentConfig.trend)}
          </span>
          <span className="trend-text">
            Tendencia{" "}
            {currentConfig.trend === "up"
              ? "Ascendente"
              : currentConfig.trend === "down"
              ? "Descendente"
              : "Estable"}
          </span>
        </div>
      </div>

      <div className="chart-controls">
        <div className="variable-selector">
          <label>Variable Meteorológica:</label>
          <div className="variable-buttons">
            {availableCharts.map(([key, config]) => (
              <button
                key={key}
                className={`variable-btn ${
                  activeChart === key ? "active" : ""
                }`}
                onClick={() => setActiveChart(key)}
                style={{
                  background:
                    activeChart === key
                      ? config.gradient
                      : "rgba(255, 255, 255, 0.8)",
                  color: activeChart === key ? "white" : "#374151",
                }}
              >
                <span className="variable-icon">{config.icon}</span>
                <div className="variable-info">
                  <span className="variable-name">
                    {config.title.replace(/🌡️|🌧️|💨|💧/, "").trim()}
                  </span>
                  <span className="variable-subtitle">{config.subtitle}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="chart-type-selector">
          <label>Tipo de Visualización:</label>
          <div className="chart-type-buttons">
            {chartTypes.map((type) => (
              <button
                key={type.value}
                className={`chart-type-btn ${
                  chartType === type.value ? "active" : ""
                }`}
                onClick={() => setChartType(type.value)}
                title={type.description}
              >
                <span className="chart-icon">{type.icon}</span>
                <span className="chart-label">
                  {type.label.replace(/�|📊|�📉/, "").trim()}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="chart-main-content">
        <div className="chart-wrapper">
          <div className="chart-title-bar">
            <h3>{currentConfig.title}</h3>
            <div className="stat-content">
              <span className="stat-label">Último valor:</span>
              <span className="stat-value">
                {currentConfig.data[currentConfig.data.length - 1]?.toFixed(1)}{" "}
                {currentConfig.unit}
              </span>
            </div>
          </div>
          <div className="chart-canvas">
            <ChartComponent
              key={`chart-${selectedYears}-${forceUpdate}-${activeChart}-${chartType}-${historicalData.length}`}
              data={chartData}
              options={chartOptions}
            />
          </div>
        </div>

        <div className="statistics-panel">
          <h3>📊 Estadísticas Descriptivas</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">📊</div>
              <div className="stat-content">
                <span className="stat-label">Promedio</span>
                <span className="stat-value">
                  {currentStats.mean.toFixed(1)} {currentConfig.unit}
                </span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">🎯</div>
              <div className="stat-content">
                <span className="stat-label">Mediana</span>
                <span className="stat-value">
                  {currentStats.median.toFixed(1)} {currentConfig.unit}
                </span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">⬇️</div>
              <div className="stat-content">
                <span className="stat-label">Mínimo</span>
                <span className="stat-value">
                  {currentStats.min.toFixed(1)} {currentConfig.unit}
                </span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">⬆️</div>
              <div className="stat-content">
                <span className="stat-label">Máximo</span>
                <span className="stat-value">
                  {currentStats.max.toFixed(1)} {currentConfig.unit}
                </span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">📏</div>
              <div className="stat-content">
                <span className="stat-label">Desv. Estándar</span>
                <span className="stat-value">
                  {currentStats.std.toFixed(1)} {currentConfig.unit}
                </span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">📈</div>
              <div className="stat-content">
                <span className="stat-label">Rango</span>
                <span className="stat-value">
                  {(currentStats.max - currentStats.min).toFixed(1)}{" "}
                  {currentConfig.unit}
                </span>
              </div>
            </div>
          </div>

          <div className="insights-section">
            <h4>💡 Insights Climáticos</h4>
            <div className="insights-list">
              <div className="insight-item">
                <span className="insight-icon">🎯</span>
                <span>
                  Variabilidad:{" "}
                  {currentStats.std > currentStats.mean * 0.3
                    ? "Alta"
                    : currentStats.std > currentStats.mean * 0.15
                    ? "Media"
                    : "Baja"}
                </span>
              </div>
              <div className="insight-item">
                <span className="insight-icon">📊</span>
                <span>
                  Años analizados: {historicalData.length} años de datos NASA
                </span>
              </div>
              <div className="insight-item">
                <span className="insight-icon">🔍</span>
                <span>
                  Confiabilidad: Datos satelitales validados científicamente
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WeatherChart;
