/**
 * modal-i18n.js
 * Helper para internacionalizar modales dinámicamente
 * Lee el idioma de localStorage.lang
 */

// Función para traducir un modal específico
function translateModal(modalSelector) {
  const modal = document.querySelector(modalSelector);
  if (!modal) return;
  
  I18N.applyTranslations(modal);
}

// Función para traducir todos los modales abiertos
function translateAllModals() {
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
  setTimeout(() => translateModal(modalSelector), 50);
}

// Listener para cambios de idioma (si tienes un selector de idioma)
document.addEventListener('languageChanged', () => {
  translateAllModals();
});

// También traducir cuando se cambia localStorage.lang
window.addEventListener('storage', (event) => {
  if (event.key === 'lang') {
    translateAllModals();
  }
});

// Aplicar traducciones a elementos con data-i18n al cargar la página
document.addEventListener('DOMContentLoaded', () => {
  I18N.applyTranslations();
});
