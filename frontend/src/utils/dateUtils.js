// Utilidades para manejo de fechas
export const dateUtils = {
  // Formatear fecha en formato MM-DD
  formatDateOfYear: (date) => {
    if (!date) return "";
    const d = new Date(date);
    const month = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${month}-${day}`;
  },

  // Validar formato MM-DD
  validateDateOfYear: (dateString) => {
    if (!dateString) return false;
    const regex = /^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$/;
    if (!regex.test(dateString)) return false;

    const [month, day] = dateString.split("-").map(Number);

    // Validaciones básicas
    if (month < 1 || month > 12) return false;
    if (day < 1 || day > 31) return false;

    // Validar días por mes (simplificado)
    const daysInMonth = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    if (day > daysInMonth[month - 1]) return false;

    return true;
  },

  // Obtener fecha actual en formato MM-DD
  getCurrentDateOfYear: () => {
    return dateUtils.formatDateOfYear(new Date());
  },

  // Convertir MM-DD a nombre de mes y día
  formatDisplayDate: (dateString) => {
    if (!dateUtils.validateDateOfYear(dateString)) return dateString;

    const [month, day] = dateString.split("-").map(Number);
    const monthNames = [
      "Enero",
      "Febrero",
      "Marzo",
      "Abril",
      "Mayo",
      "Junio",
      "Julio",
      "Agosto",
      "Septiembre",
      "Octubre",
      "Noviembre",
      "Diciembre",
    ];

    return `${day} de ${monthNames[month - 1]}`;
  },

  // Obtener el día del año (1-366)
  getDayOfYear: (dateString) => {
    if (!dateUtils.validateDateOfYear(dateString)) return null;

    const [month, day] = dateString.split("-").map(Number);
    const currentYear = new Date().getFullYear();
    const date = new Date(currentYear, month - 1, day);
    const start = new Date(currentYear, 0, 0);
    const diff = date - start;
    return Math.floor(diff / (1000 * 60 * 60 * 24));
  },
};
