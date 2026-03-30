/**
 * DPIA I18N - Global Translation Dictionary for Dynamic Modals
 * Loaded BEFORE calculoPorRetenidos.js
 */
window.DPIA_I18N = {
  es: {
    validation_title: "⚠️ Errores de Validación Detectados",
    validation_subtitle: "No se puede continuar con el cálculo. Corrija los errores indicados:",
    tabla: "Tabla",
    retidos_suman: "Retidos suman",
    falta: "Falta",
    datos_incompletos: "Datos incompletos",
    tamiz_incorrecto: "Tamiz Incorrecto",
    valor_ingresado: "Valor ingresado",
    quiso_decir: "¿Quiso decir",
    mm: "mm?",
    tamices_duplicados: "Tamices Duplicados",
    valores_repetidos: "Valores repetidos encontrados",
    porcentajes_fuera_rango: "Porcentajes fuera de rango",
    rango_invalido: "Los porcentajes deben estar entre 0% y 100%",
    valor_negativo: "valor negativo",
    mayor_100: "mayor que 100%",
    fix_errors: "Corrija estos errores antes de continuar.",
    btn_entendido: "Entendido, voy a corregir",
    sugerencia_fundo: "💡 SUGERENCIA: Parece que falta la fila del \"Fundo\" (últimas partículas).",
    agregar_fila: "Agrege una fila con:",
    tamiz_label: "Tamiz",
    fundo_alt: "(o < {{mm}})",
    porcentaje_label: "Porcentaje"
  },
  en: {
    validation_title: "⚠️ Validation Errors Detected",
    validation_subtitle: "Cannot continue with calculation. Fix the errors indicated:",
    tabla: "Table",
    retidos_suman: "Retained sum",
    falta: "Missing",
    datos_incompletos: "Incomplete data",
    tamiz_incorrecto: "Incorrect Sieve",
    valor_ingresado: "Value entered",
    quiso_decir: "Did you mean",
    mm: "mm?",
    tamices_duplicados: "Duplicate Sieves",
    valores_repetidos: "Repeated values found",
    porcentajes_fuera_rango: "Percentages out of range",
    rango_invalido: "Percentages must be between 0% and 100%",
    valor_negativo: "negative value",
    mayor_100: "greater than 100%",
    fix_errors: "Fix these errors before proceeding.",
    btn_entendido: "Understood, I'll fix it",
    sugerencia_fundo: "💡 SUGGESTION: It looks like the \"Fundo\" row (bottom particles) is missing.",
    agregar_fila: "Add a row with:",
    tamiz_label: "Sieve",
    fundo_alt: "(or < {{mm}})",
    porcentaje_label: "Percentage"
  },
  it: {
    validation_title: "⚠️ Errori di Validazione Rilevati",
    validation_subtitle: "Non è possibile continuare con il calcolo. Correggere gli errori indicati:",
    tabla: "Tabella",
    retidos_suman: "Somma trattenuta",
    falta: "Manca",
    datos_incompletos: "Dati incompleti",
    tamiz_incorrecto: "Setaccio Scorretto",
    valor_ingresado: "Valore inserito",
    quiso_decir: "Volevi dire",
    mm: "mm?",
    tamices_duplicados: "Setacci Duplicati",
    valores_repetidos: "Valori ripetuti trovati",
    porcentajes_fuera_rango: "Percentuali fuori intervallo",
    rango_invalido: "Le percentuali devono essere tra 0% e 100%",
    valor_negativo: "valore negativo",
    mayor_100: "superiore al 100%",
    fix_errors: "Correggi questi errori prima di continuare.",
    btn_entendido: "Capito, lo correggerò",
    sugerencia_fundo: "💡 SUGGERIMENTO: Sembra che manchi la riga \"Fondo\" (ultime particelle).",
    agregar_fila: "Aggiungi una riga con:",
    tamiz_label: "Setaccio",
    fundo_alt: "(o < {{mm}})",
    porcentaje_label: "Percentuale"
  }
};

// Language resolution (read from localStorage, fallback to es)
const DPIA_LANG = localStorage.getItem("lang") || "es";
const DPIA_T = window.DPIA_I18N[DPIA_LANG] || window.DPIA_I18N["es"];

// Debug log (temporary)
console.log("[DPIA I18N] Lang:", DPIA_LANG, "Keys:", DPIA_T);
