// Utilidades para configuración de gráficos
export const chartUtils = {
  // Colores predefinidos para gráficos
  colors: {
    temperature: {
      primary: "rgba(255, 99, 132, 0.8)",
      background: "rgba(255, 99, 132, 0.1)",
      gradient: ["#ff6384", "#ff8fa3"],
    },
    precipitation: {
      primary: "rgba(54, 162, 235, 0.8)",
      background: "rgba(54, 162, 235, 0.1)",
      gradient: ["#36a2eb", "#4fc3f7"],
    },
    wind_speed: {
      primary: "rgba(75, 192, 192, 0.8)",
      background: "rgba(75, 192, 192, 0.1)",
      gradient: ["#4bc0c0", "#80cbc4"],
    },
    humidity: {
      primary: "rgba(153, 102, 255, 0.8)",
      background: "rgba(153, 102, 255, 0.1)",
      gradient: ["#9966ff", "#b39ddb"],
    },
  },

  // Configuraciones comunes para Chart.js
  getDefaultOptions: (title, unit) => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top",
        labels: {
          font: {
            size: 12,
          },
        },
      },
      title: {
        display: true,
        text: title,
        font: {
          size: 16,
          weight: "bold",
        },
        color: "#333",
      },
      tooltip: {
        backgroundColor: "rgba(0, 0, 0, 0.8)",
        titleColor: "white",
        bodyColor: "white",
        borderColor: "rgba(255, 255, 255, 0.2)",
        borderWidth: 1,
        callbacks: {
          label: function (context) {
            return `${context.dataset.label}: ${context.parsed.y.toFixed(
              2
            )} ${unit}`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: `${title} (${unit})`,
          font: {
            size: 12,
          },
        },
        grid: {
          color: "rgba(0, 0, 0, 0.1)",
        },
      },
      x: {
        title: {
          display: true,
          text: "Año",
          font: {
            size: 12,
          },
        },
        grid: {
          color: "rgba(0, 0, 0, 0.1)",
        },
      },
    },
    interaction: {
      intersect: false,
      mode: "index",
    },
  }),

  // Crear gradiente para gráficos
  createGradient: (ctx, colorConfig) => {
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, colorConfig.gradient[0]);
    gradient.addColorStop(1, colorConfig.gradient[1]);
    return gradient;
  },

  // Formatear datos para exportación a CSV
  formatDataForCSV: (data, headers) => {
    const csvHeaders = headers.join(",");
    const csvRows = data.map((row) =>
      headers
        .map((header) => {
          const value = row[header];
          // Escapar valores que contengan comas
          return typeof value === "string" && value.includes(",")
            ? `"${value}"`
            : value;
        })
        .join(",")
    );

    return [csvHeaders, ...csvRows].join("\n");
  },

  // Calcular estadísticas básicas
  calculateStats: (values) => {
    if (!values || values.length === 0) return null;

    const sortedValues = [...values].sort((a, b) => a - b);
    const sum = values.reduce((acc, val) => acc + val, 0);
    const mean = sum / values.length;

    // Mediana
    const median =
      sortedValues.length % 2 === 0
        ? (sortedValues[sortedValues.length / 2 - 1] +
            sortedValues[sortedValues.length / 2]) /
          2
        : sortedValues[Math.floor(sortedValues.length / 2)];

    // Desviación estándar
    const variance =
      values.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) /
      values.length;
    const std = Math.sqrt(variance);

    return {
      min: Math.min(...values),
      max: Math.max(...values),
      mean,
      median,
      std,
      count: values.length,
    };
  },

  // Detectar outliers usando IQR
  detectOutliers: (values) => {
    if (!values || values.length < 4) return [];

    const sortedValues = [...values].sort((a, b) => a - b);
    const q1Index = Math.floor(sortedValues.length * 0.25);
    const q3Index = Math.floor(sortedValues.length * 0.75);

    const q1 = sortedValues[q1Index];
    const q3 = sortedValues[q3Index];
    const iqr = q3 - q1;

    const lowerBound = q1 - 1.5 * iqr;
    const upperBound = q3 + 1.5 * iqr;

    return values
      .map((value, index) => ({
        index,
        value,
        isOutlier: value < lowerBound || value > upperBound,
      }))
      .filter((item) => item.isOutlier);
  },
};
