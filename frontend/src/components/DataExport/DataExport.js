import React, { useState } from "react";
import "./DataExport.css";

const DataExport = ({ queryData, onExportData, userPreferences = {} }) => {
  const [exportFormat, setExportFormat] = useState("json");
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async () => {
    if (!queryData) {
      alert("No hay datos para exportar");
      return;
    }

    setIsExporting(true);
    try {
      // Incluir información sobre las preferencias del usuario en la exportación
      const exportData = {
        ...queryData,
        userPreferences: {
          selectedVariables: {
            temperature: userPreferences.showTemperature !== false,
            precipitation: userPreferences.showPrecipitation !== false,
            windSpeed: userPreferences.showWindSpeed !== false,
            humidity: userPreferences.showHumidity !== false,
            heatIndex: userPreferences.showHeatIndex !== false,
          },
          chartType: userPreferences.chartType || "line",
          compactView: userPreferences.compactView || false,
          showStatistics: userPreferences.showStatistics !== false,
          showProbabilityBars: userPreferences.showProbabilityBars !== false,
        },
        exportTimestamp: new Date().toISOString(),
      };

      const success = await onExportData(exportData, exportFormat);
      if (success) {
        // El éxito se maneja en el componente padre
      }
    } catch (error) {
      console.error("Error exporting data:", error);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div
      className={`card export-card ${
        userPreferences.compactView ? "compact" : ""
      }`}
    >
      <h2>📥 Exportar Datos</h2>

      <div className="export-options">
        <div className="form-group">
          <label htmlFor="export-format">Formato de exportación:</label>
          <select
            id="export-format"
            value={exportFormat}
            onChange={(e) => setExportFormat(e.target.value)}
            disabled={isExporting}
          >
            <option value="json">📄 JSON</option>
            <option value="csv">📊 CSV</option>
          </select>
        </div>

        <div className="export-info">
          <h4>📦 Contenido del archivo:</h4>
          <ul>
            <li>📊 Datos históricos meteorológicos</li>
            <li>🎯 Probabilidades calculadas</li>
            <li>📍 Información de ubicación</li>
            <li>⚙️ Configuración personalizada</li>
            {userPreferences.showStatistics !== false && (
              <li>📈 Estadísticas resumidas</li>
            )}
            <li>⏰ Marca de tiempo de exportación</li>
          </ul>

          {!userPreferences.compactView && (
            <div className="preferences-summary">
              <h4>🎛️ Variables incluidas:</h4>
              <div className="variable-tags">
                {userPreferences.showTemperature !== false && (
                  <span className="tag active">🌡️ Temperatura</span>
                )}
                {userPreferences.showPrecipitation !== false && (
                  <span className="tag active">🌧️ Precipitación</span>
                )}
                {userPreferences.showWindSpeed !== false && (
                  <span className="tag active">💨 Viento</span>
                )}
                {userPreferences.showHumidity !== false && (
                  <span className="tag active">💧 Humedad</span>
                )}
                {userPreferences.showHeatIndex !== false && (
                  <span className="tag active">🔥 Índice de Calor</span>
                )}
              </div>
            </div>
          )}
        </div>

        <button
          onClick={handleExport}
          disabled={isExporting || !queryData}
          className="btn export-btn"
        >
          {isExporting ? (
            <>
              <span className="spinner"></span>
              Exportando...
            </>
          ) : (
            <>📥 Exportar {exportFormat.toUpperCase()}</>
          )}
        </button>
      </div>

      {!userPreferences.compactView && (
        <div className="export-note">
          <small>
            💡 <strong>Nota:</strong> Los archivos exportados incluyen tanto los
            datos de la consulta como la configuración personalizada utilizada
            para generar los resultados.
          </small>
        </div>
      )}
    </div>
  );
};

export default DataExport;
