import React, { useState } from "react";
import "./LoonaSection.css";

const LoonaSection = () => {
  const [selectedMember, setSelectedMember] = useState(null);
  const [showDiscography, setShowDiscography] = useState(false);

  const members = [
    {
      name: "HeeJin",
      koreanName: "희진",
      animal: "Rabbit",
      color: "#FF1A8C",
      birthDate: "2000.10.19",
      fact: "Primera integrante revelada de LOONA",
    },
    {
      name: "HyunJin",
      koreanName: "현진",
      animal: "Cat",
      color: "#FFD300",
      birthDate: "2000.11.15",
      fact: "Conocida por su versatilidad en el baile",
    },
    {
      name: "HaSeul",
      koreanName: "하슬",
      animal: "White Bird",
      color: "#00B04F",
      birthDate: "1997.08.18",
      fact: "Líder original del grupo",
    },
    {
      name: "YeoJin",
      koreanName: "여진",
      animal: "Frog",
      color: "#FF8500",
      birthDate: "2002.11.11",
      fact: "La integrante más joven",
    },
    {
      name: "ViVi",
      koreanName: "비비",
      animal: "Deer",
      color: "#FF69B4",
      birthDate: "1996.12.09",
      fact: "De origen chino-hongkonés",
    },
    {
      name: "Kim Lip",
      koreanName: "김립",
      animal: "Owl",
      color: "#ED0345",
      birthDate: "1999.02.10",
      fact: "Conocida por su poderosa voz",
    },
    {
      name: "JinSoul",
      koreanName: "진솔",
      animal: "Blue Betta",
      color: "#3366FF",
      birthDate: "1997.06.13",
      fact: "Rapera principal del grupo",
    },
    {
      name: "Choerry",
      koreanName: "최리",
      animal: "Bat",
      color: "#7F007F",
      birthDate: "2001.06.04",
      fact: "Representa la conexión entre los subunits",
    },
    {
      name: "Yves",
      koreanName: "이브",
      animal: "Swan",
      color: "#A7194B",
      birthDate: "1997.05.24",
      fact: "Líder de la línea francesa",
    },
    {
      name: "Chuu",
      koreanName: "츄",
      animal: "Penguin",
      color: "#FFB3D9",
      birthDate: "1999.10.20",
      fact: "Conocida por su personalidad adorable",
    },
    {
      name: "Go Won",
      koreanName: "고원",
      animal: "Butterfly",
      color: "#6CFFFF",
      birthDate: "2000.11.19",
      fact: "Visual del grupo",
    },
    {
      name: "Olivia Hye",
      koreanName: "올리비아 혜",
      animal: "Wolf",
      color: "#A8A8A8",
      birthDate: "2001.11.13",
      fact: "La última integrante revelada",
    },
  ];

  const albums = [
    {
      title: "++",
      year: "2018",
      type: "Mini Album",
      tracks: ["favOriTe", "Hi High", "Perfect Love", "Stylish"],
    },
    {
      title: "XX",
      year: "2019",
      type: "Mini Album",
      tracks: ["Butterfly", "Satellite", "Curious", "Colors"],
    },
    {
      title: "12:00",
      year: "2020",
      type: "Mini Album",
      tracks: ["So What", "Number 1", "Oh (Yes I Am)", "Star"],
    },
    {
      title: "&",
      year: "2021",
      type: "Mini Album",
      tracks: ["Paint The Town", "WOW", "Be Honest", "Dance On My Own"],
    },
    {
      title: "Flip That",
      year: "2022",
      type: "Summer Special",
      tracks: ["Flip That", "Need U", "POSE", "Playback"],
    },
  ];

  return (
    <div className="loona-section">
      <div className="loona-header">
        <h2>🌙 Sobre LOONA (이달의 소녀)</h2>
        <p>
          LOONA es un grupo de K-pop de 12 integrantes formado por BBC
          (Blockberry Creative). Conocidas por su concepto único del LOONAverse
          y su música innovadora.
        </p>
      </div>

      <div className="loona-content">
        <div className="info-tabs">
          <button
            className={`tab-btn ${!showDiscography ? "active" : ""}`}
            onClick={() => setShowDiscography(false)}
          >
            👭 Integrantes
          </button>
          <button
            className={`tab-btn ${showDiscography ? "active" : ""}`}
            onClick={() => setShowDiscography(true)}
          >
            🎵 Discografía
          </button>
        </div>

        {!showDiscography ? (
          <div className="members-section">
            <div className="members-grid">
              {members.map((member, index) => (
                <div
                  key={index}
                  className={`member-card ${
                    selectedMember === index ? "selected" : ""
                  }`}
                  onClick={() =>
                    setSelectedMember(selectedMember === index ? null : index)
                  }
                  style={{ "--member-color": member.color }}
                >
                  <div className="member-name">
                    <h3>{member.name}</h3>
                    <span className="korean-name">{member.koreanName}</span>
                  </div>
                  <div className="member-animal">
                    <span className="animal-label">Animal:</span>
                    <span className="animal-name">{member.animal}</span>
                  </div>
                  {selectedMember === index && (
                    <div className="member-details">
                      <p>
                        <strong>Fecha de nacimiento:</strong> {member.birthDate}
                      </p>
                      <p>
                        <strong>Dato curioso:</strong> {member.fact}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="discography-section">
            <div className="albums-grid">
              {albums.map((album, index) => (
                <div key={index} className="album-card">
                  <div className="album-header">
                    <h3>{album.title}</h3>
                    <span className="album-year">{album.year}</span>
                  </div>
                  <p className="album-type">{album.type}</p>
                  <div className="track-list">
                    <h4>Canciones destacadas:</h4>
                    <ul>
                      {album.tracks.map((track, trackIndex) => (
                        <li key={trackIndex}>{track}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="loona-facts">
          <h3>✨ Datos Interesantes</h3>
          <div className="facts-grid">
            <div className="fact-item">
              <span className="fact-icon">🌙</span>
              <div>
                <h4>LOONAverse</h4>
                <p>
                  Cada integrante tiene su propio universo musical conectado
                </p>
              </div>
            </div>
            <div className="fact-item">
              <span className="fact-icon">🎨</span>
              <div>
                <h4>Colores Únicos</h4>
                <p>Cada miembro tiene un color representativo específico</p>
              </div>
            </div>
            <div className="fact-item">
              <span className="fact-icon">🔄</span>
              <div>
                <h4>Sub-units</h4>
                <p>LOONA 1/3, LOONA/Odd Eye Circle, LOONA/yyxy</p>
              </div>
            </div>
            <div className="fact-item">
              <span className="fact-icon">🌍</span>
              <div>
                <h4>Reconocimiento Global</h4>
                <p>Fanbase internacional muy activa llamada "Orbit"</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoonaSection;
