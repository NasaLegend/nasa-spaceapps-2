import React, { useState } from "react";
import "./SettingsPanel.css";

const SettingsPanel = ({
  preferences,
  onUpdatePreferences,
  isOpen,
  onClose,
}) => {
  const [tempPreferences, setTempPreferences] = useState(preferences);

  const handleChange = (key, value) => {
    setTempPreferences((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = () => {
    onUpdatePreferences(tempPreferences);
    onClose();
  };

  const handleReset = () => {
    const defaultPreferences = {
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
    };
    setTempPreferences(defaultPreferences);
  };

  if (!isOpen) return null;

  return (
    <div className="settings-overlay">
      <div className="settings-panel">
        <div className="settings-header">
          <h2>⚙️ Configuración Personalizada</h2>
          <button onClick={onClose} className="close-btn">
            ✕
          </button>
        </div>

        <div className="settings-content">
          <div className="settings-section">
            <h3>📊 Variables Meteorológicas</h3>
            <div className="settings-group">
              {[
                { key: "showTemperature", label: "🌡️ Temperatura", icon: "🌡️" },
                {
                  key: "showPrecipitation",
                  label: "🌧️ Precipitación",
                  icon: "🌧️",
                },
                {
                  key: "showWindSpeed",
                  label: "💨 Velocidad del Viento",
                  icon: "💨",
                },
                { key: "showHumidity", label: "💧 Humedad", icon: "💧" },
                {
                  key: "showHeatIndex",
                  label: "🔥 Índice de Calor",
                  icon: "🔥",
                },
              ].map(({ key, label, icon }) => (
                <label key={key} className="setting-item">
                  <div className="setting-label">
                    <span className="setting-icon">{icon}</span>
                    <span>{label}</span>
                  </div>
                  <div className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={tempPreferences[key]}
                      onChange={(e) => handleChange(key, e.target.checked)}
                    />
                    <span className="toggle-slider"></span>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div className="settings-section">
            <h3>📈 Configuración de Gráficos</h3>
            <div className="settings-group">
              <label className="setting-item">
                <span className="setting-label">Tipo de Gráfico</span>
                <select
                  value={tempPreferences.chartType}
                  onChange={(e) => handleChange("chartType", e.target.value)}
                  className="setting-select"
                >
                  <option value="line">📈 Líneas</option>
                  <option value="bar">📊 Barras</option>
                  <option value="area">📉 Área</option>
                </select>
              </label>
            </div>
          </div>

          <div className="settings-section">
            <h3>🎨 Configuración de Vista</h3>
            <div className="settings-group">
              {[
                {
                  key: "showStatistics",
                  label: "📈 Mostrar Estadísticas",
                  icon: "📈",
                },
                {
                  key: "showProbabilityBars",
                  label: "📊 Barras de Probabilidad",
                  icon: "📊",
                },
                { key: "compactView", label: "📱 Vista Compacta", icon: "📱" },
                { key: "autoRefresh", label: "🔄 Auto-actualizar", icon: "🔄" },
              ].map(({ key, label, icon }) => (
                <label key={key} className="setting-item">
                  <div className="setting-label">
                    <span className="setting-icon">{icon}</span>
                    <span>{label}</span>
                  </div>
                  <div className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={tempPreferences[key]}
                      onChange={(e) => handleChange(key, e.target.checked)}
                    />
                    <span className="toggle-slider"></span>
                  </div>
                </label>
              ))}
            </div>
          </div>
        </div>

        <div className="settings-footer">
          <button onClick={handleReset} className="btn btn-secondary">
            🔄 Restablecer
          </button>
          <div className="footer-actions">
            <button onClick={onClose} className="btn btn-secondary">
              ✕ Cancelar
            </button>
            <button onClick={handleSave} className="btn btn-success">
              ✓ Guardar Cambios
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;
