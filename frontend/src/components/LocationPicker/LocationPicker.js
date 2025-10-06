import React, { useState, useEffect } from "react";
import { weatherService } from "../../services/weatherService";
import "./LocationPicker.css";

const LocationPicker = ({ onLocationSelect, selectedLocation }) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [popularLocations, setPopularLocations] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);

  // Cargar ubicaciones populares al iniciar
  useEffect(() => {
    const loadPopularLocations = async () => {
      try {
        const response = await weatherService.getPopularLocations();
        setPopularLocations(response.locations || []);
      } catch (error) {
        console.error("Error loading popular locations:", error);
      }
    };

    loadPopularLocations();
  }, []);

  // Búsqueda de ubicaciones con debounce
  useEffect(() => {
    const timeoutId = setTimeout(async () => {
      if (searchQuery.trim().length > 2) {
        setIsSearching(true);
        try {
          const response = await weatherService.searchLocations(searchQuery);
          setSearchResults(response.locations || []);
          setShowResults(true);
        } catch (error) {
          console.error("Error searching locations:", error);
          setSearchResults([]);
        } finally {
          setIsSearching(false);
        }
      } else {
        setSearchResults([]);
        setShowResults(false);
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  const handleLocationClick = (location) => {
    console.log("Location selected:", location);
    onLocationSelect(location);
    setSearchQuery(
      location.name || `${location.latitude}, ${location.longitude}`
    );
    setShowResults(false);
    setSearchResults([]); // Limpiar resultados
  };

  const handleManualCoordinates = () => {
    const lat = prompt("Ingresa la latitud:");
    const lng = prompt("Ingresa la longitud:");

    if (lat && lng) {
      const latitude = parseFloat(lat);
      const longitude = parseFloat(lng);

      if (
        !isNaN(latitude) &&
        !isNaN(longitude) &&
        latitude >= -90 &&
        latitude <= 90 &&
        longitude >= -180 &&
        longitude <= 180
      ) {
        const manualLocation = {
          latitude,
          longitude,
          name: `Coordenadas (${latitude}, ${longitude})`,
        };

        handleLocationClick(manualLocation);
      } else {
        alert(
          "Coordenadas inválidas. Latitud debe estar entre -90 y 90, longitud entre -180 y 180."
        );
      }
    }
  };

  return (
    <div className="location-picker">
      <div className="search-container">
        <input
          type="text"
          placeholder="Buscar ubicación..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="location-search"
        />

        <button
          type="button"
          onClick={handleManualCoordinates}
          className="btn btn-secondary manual-coords-btn"
          title="Ingresar coordenadas manualmente"
        >
          📍
        </button>
      </div>

      {selectedLocation && (
        <div className="selected-location">
          <h4>Ubicación seleccionada:</h4>
          <p>
            {selectedLocation.name}
            <span className="coordinates">
              ({selectedLocation.latitude.toFixed(4)},{" "}
              {selectedLocation.longitude.toFixed(4)})
            </span>
          </p>
        </div>
      )}

      {isSearching && (
        <div className="search-loading">Buscando ubicaciones...</div>
      )}

      {showResults && searchResults.length > 0 && (
        <div className="search-results">
          <h4>Resultados de búsqueda:</h4>
          <ul className="location-list">
            {searchResults.map((location, index) => (
              <li
                key={index}
                onClick={() => handleLocationClick(location)}
                className="location-item"
              >
                <div className="location-name">{location.name}</div>
                <div className="location-details">
                  {location.country && (
                    <span className="country">{location.country}</span>
                  )}
                  <span className="coordinates">
                    {location.latitude.toFixed(4)},{" "}
                    {location.longitude.toFixed(4)}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {!showResults && popularLocations.length > 0 && (
        <div className="popular-locations">
          <h4>Ubicaciones populares:</h4>
          <ul className="location-list">
            {popularLocations.map((location, index) => (
              <li
                key={index}
                onClick={() => handleLocationClick(location)}
                className="location-item"
              >
                <div className="location-name">{location.name}</div>
                <div className="location-details">
                  {location.country && (
                    <span className="country">{location.country}</span>
                  )}
                  <span className="coordinates">
                    {location.latitude.toFixed(4)},{" "}
                    {location.longitude.toFixed(4)}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default LocationPicker;
