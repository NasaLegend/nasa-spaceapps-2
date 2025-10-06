import React, { useState, useEffect } from "react";
import Dashboard from "./components/Dashboard/Dashboard";
// import LoonaSection from './components/LoonaSection/LoonaSection';
import { weatherService } from "./services/weatherService";
import "./App.css";

function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [weatherData, setWeatherData] = useState(null);
  const [availableConditions, setAvailableConditions] = useState(null);
  const [theme, setTheme] = useState("light");
  const [userPreferences, setUserPreferences] = useState({
    showTemperature: true,
    showPrecipitation: true,
    showWindSpeed: true,
    showHumidity: true,
    showHeatIndex: true,
    chartType: "line",
    showStatistics: true,
    showProbabilityBars: true,
    compactView: false,
    autoRefresh: false,
  });

  // Cargar condiciones disponibles al iniciar
  useEffect(() => {
    const loadConditions = async () => {
      try {
        const conditions = await weatherService.getAvailableConditions();
        setAvailableConditions(conditions);
      } catch (err) {
        console.error("Error loading conditions:", err);
      }
    };

    loadConditions();

    // Cargar preferencias del localStorage
    const savedPreferences = localStorage.getItem("weatherAppPreferences");
    if (savedPreferences) {
      setUserPreferences(JSON.parse(savedPreferences));
    }

    const savedTheme = localStorage.getItem("weatherAppTheme");
    if (savedTheme) {
      setTheme(savedTheme);
      document.documentElement.setAttribute("data-theme", savedTheme);
    }
  }, []);

  // Guardar preferencias cuando cambien
  useEffect(() => {
    localStorage.setItem(
      "weatherAppPreferences",
      JSON.stringify(userPreferences)
    );
  }, [userPreferences]);

  // Guardar tema cuando cambie
  useEffect(() => {
    localStorage.setItem("weatherAppTheme", theme);
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  const handleWeatherQuery = async (queryData) => {
    setLoading(true);
    setError(null);

    try {
      console.log("🔄 Starting weather query...", queryData);
      const result = await weatherService.getWeatherProbabilities(queryData);
      console.log("✅ Weather query completed successfully");
      setWeatherData(result);
    } catch (err) {
      console.error("❌ Weather query failed:", err.message);

      // Mostrar error más informativo dependiendo del tipo
      let errorMessage = err.message;
      if (
        err.message.includes("timeout") ||
        err.message.includes("ECONNABORTED")
      ) {
        errorMessage =
          "⏰ La consulta está tardando más de lo esperado. Esto es normal para la primera consulta por ubicación. Por favor espere un momento más.";
      } else if (err.message.includes("504") || err.message.includes("502")) {
        errorMessage =
          "🔄 El servidor está procesando los datos históricos. Por favor, espere un momento y vuelva a intentar.";
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleExportData = async (queryData, format) => {
    try {
      const exportData = await weatherService.exportWeatherData(
        queryData,
        format
      );

      // Crear y descargar archivo
      const blob = new Blob([JSON.stringify(exportData.data, null, 2)], {
        type: format === "csv" ? "text/csv" : "application/json",
      });

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `weather-data-${
        new Date().toISOString().split("T")[0]
      }.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      return true;
    } catch (err) {
      setError(err.message);
      return false;
    }
  };

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  const updatePreferences = (newPreferences) => {
    setUserPreferences((prev) => ({ ...prev, ...newPreferences }));
  };

  return (
    <div className="App app-container">
      <header className="header">
        <div className="container">
          <h1>🌤️ coNimbus </h1>
          <p>
            Predicciones meteorológicas inteligentes con datos reales de NASA
            POWER y Machine Learning
          </p>

          <div
            className="header-controls"
            style={{
              marginTop: "1rem",
              display: "flex",
              justifyContent: "center",
              gap: "1rem",
            }}
          >
            <button
              onClick={toggleTheme}
              className="btn btn-secondary"
              style={{ padding: "8px 16px", fontSize: "0.9rem" }}
            >
              {theme === "light" ? "🌙" : "☀️"}{" "}
              {theme === "light" ? "Modo Oscuro" : "Modo Claro"}
            </button>
          </div>
        </div>
      </header>

      <main className="container">
        <Dashboard
          loading={loading}
          error={error}
          weatherData={weatherData}
          availableConditions={availableConditions}
          userPreferences={userPreferences}
          onWeatherQuery={handleWeatherQuery}
          onExportData={handleExportData}
          onClearError={() => setError(null)}
          onUpdatePreferences={updatePreferences}
        />

        {/* <LoonaSection /> */}
      </main>
    </div>
  );
}

export default App;
