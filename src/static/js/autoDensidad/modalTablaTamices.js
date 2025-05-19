 function tablTamizes() {
     
    document.getElementById('modal-tablaTamices').style.display = "block";   
  }
  function cerrarModalTamices() {
    document.getElementById('modal-tablaTamices').style.display = 'none';
  }


function copiarFilaTamiz(event, valor) {
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