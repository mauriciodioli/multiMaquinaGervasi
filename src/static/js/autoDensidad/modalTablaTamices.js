 function tablTamizes() {
     
    document.getElementById('modal-tablaTamices').style.display = "block";   
  }
  function cerrarModalTamices() {
    document.getElementById('modal-tablaTamices').style.display = 'none';
  }


function copiarFilaTamiz(event, valor) {
    // Un clic mantiene el comportamiento original: copiar al portapapeles.

    // Copiar al portapapeles
    navigator.clipboard.writeText(valor);

    // Quitar selección previa
    const filas = document.querySelectorAll("#modal-tablaTamices tbody tr");
    filas.forEach(fila => fila.classList.remove("fila-seleccionada"));

    // Agregar clase a la fila actual
    event.currentTarget.classList.add("fila-seleccionada");

    // Mostrar mensaje flotante al lado del mouse
    const mensaje = document.getElementById('mensaje-copiado');
    mensaje.innerText = `✔️ Valor seleccionado: ${valor}`;
    mensaje.style.top = (event.clientY + 10) + 'px';
    mensaje.style.left = (event.clientX + 10) + 'px';
    mensaje.style.display = 'block';

    // Ocultar el mensaje después de 1.5 segundos
    setTimeout(() => {
      mensaje.style.display = 'none';
    }, 1500);
  }

  function cerrarModalTamices() {
    document.getElementById('modal-tablaTamices').style.display = 'none';
  }
    function cerrarModalParametros() {
    document.getElementById('modal-configuracion').style.display = 'none';
  }
// Doble clic: insertar en la última celda de diámetro seleccionada.
// Si no existe una celda válida, conservar el comportamiento de portapapeles.
function insertarTamizDobleClic(event, valor) {
    const celda = window.ultimaCeldaTamizFuller;
    const valida = celda && celda.isConnected && celda.isContentEditable &&
        celda.matches('table.tabla tbody tr td:first-child') &&
        !celda.closest('tr')?.dataset.fondo;
    if (valida) {
        celda.textContent = valor;
        celda.dispatchEvent(new Event('input', {bubbles:true}));
        celda.dispatchEvent(new Event('blur', {bubbles:true}));
        celda.style.backgroundColor = '';
    } else if (navigator.clipboard?.writeText) {
        navigator.clipboard.writeText(valor).catch(() => {});
    }
}
