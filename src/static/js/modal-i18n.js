/**
 * modal-i18n.js
 * Helper para internacionalizar modales dinámicamente
 * Lee el idioma de localStorage.lang
 */

// Verificar primero si I18N está disponible globalmente
const i18nReady = () => typeof I18N !== 'undefined' && I18N && typeof I18N.t === 'function';

// Función para traducir un modal específico
function translateModal(modalSelector) {
  if (!i18nReady()) return;
  const modal = document.querySelector(modalSelector);
  if (!modal) return;
  I18N.applyTranslations(modal);
}

// Función para traducir todos los modales abiertos
function translateAllModals() {
  if (!i18nReady()) return;
  document.querySelectorAll('[role="dialog"]').forEach(modal => {
    I18N.applyTranslations(modal);
  });
}

// Función para abrir un modal y aplicar traducciones
function openModalWithTranslations(modalSelector, openFunction) {
  // Ejecutar la función que abre el modal (si existe)
  if (typeof openFunction === 'function') {
    openFunction();
  } else {
    // Si no hay función, simplemente mostrar el modal
    const modal = document.querySelector(modalSelector);
    if (modal) {
      modal.style.display = 'block';
    }
  }
  
  // Aplicar traducciones al modal
  if (i18nReady()) {
    setTimeout(() => translateModal(modalSelector), 50);
  }
}

// Listener para cambios de idioma (si tienes un selector de idioma)
document.addEventListener('languageChanged', () => {
  if (i18nReady()) {
    translateAllModals();
  }
});

// También traducir cuando se cambia localStorage.lang
window.addEventListener('storage', (event) => {
  if (event.key === 'lang' && i18nReady()) {
    translateAllModals();
  }
});

// Aplicar traducciones a elementos con data-i18n al cargar la página
document.addEventListener('DOMContentLoaded', () => {
  if (i18nReady()) {
    I18N.applyTranslations();
  }
});

