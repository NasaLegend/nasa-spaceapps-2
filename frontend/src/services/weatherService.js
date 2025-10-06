import api from "./api";

export const weatherService = {
  // Obtener probabilidades climáticas con personalización completa
  async getWeatherProbabilities(query) {
    try {
      const response = await api.post("/api/weather/probability", query);
      return response.data;
    } catch (error) {
      // Manejo más específico de errores
      if (error.code === "ECONNABORTED") {
        throw new Error(
          "La consulta está tardando más de lo esperado. Por favor, espere un momento y vuelva a intentar."
        );
      }
      if (error.response?.status === 504) {
        throw new Error(
          "El servidor está procesando los datos. Por favor, espere un momento y vuelva a intentar."
        );
      }
      if (error.response?.status >= 500) {
        throw new Error(
          "Error interno del servidor. Los datos se están procesando, intente nuevamente en unos segundos."
        );
      }
      throw new Error(
        error.response?.data?.detail ||
          "Error al obtener probabilidades climáticas"
      );
    }
  },

  // Análisis personalizado para eventos al aire libre
  async getCustomWeatherAnalysis(analysisConfig) {
    try {
      const response = await api.post(
        "/api/weather/custom-analysis",
        analysisConfig
      );
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.detail ||
          "Error al obtener análisis personalizado"
      );
    }
  },

  // Versión GET para consultas simples con personalización
  async getWeatherProbabilitiesGet(params) {
    try {
      const response = await api.get("/api/weather/probability", { params });
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.detail ||
          "Error al obtener probabilidades climáticas"
      );
    }
  },

  // Exportar datos
  async exportWeatherData(query, format = "json") {
    try {
      const response = await api.post(
        `/api/weather/export?format=${format}`,
        query
      );
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.detail || "Error al exportar datos"
      );
    }
  },

  // Obtener condiciones disponibles
  async getAvailableConditions() {
    try {
      const response = await api.get("/api/weather/conditions");
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.detail ||
          "Error al obtener condiciones disponibles"
      );
    }
  },

  // Buscar ubicaciones
  async searchLocations(query, limit = 10) {
    try {
      const response = await api.get("/api/locations/search", {
        params: { query, limit },
      });
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.detail || "Error al buscar ubicaciones"
      );
    }
  },

  // Obtener ubicaciones populares
  async getPopularLocations() {
    try {
      const response = await api.get("/api/locations/popular");
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.detail || "Error al obtener ubicaciones populares"
      );
    }
  },

  // Obtener información por coordenadas
  async getLocationByCoordinates(latitude, longitude) {
    try {
      const response = await api.get("/api/locations/coordinates", {
        params: { latitude, longitude },
      });
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.detail ||
          "Error al obtener información de ubicación"
      );
    }
  },
};
