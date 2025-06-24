let mezclaSeleccionada = null;

function agregarAgredadosPreCardados(boton) {
    mezclaSeleccionada = boton.closest(".mezcla");
    fetch("/crud_agregados_mixFamiliari_lista_agregados_json/")  // 🔁 Este endpoint lo creamos abajo
        .then(res => res.json())
        .then(agregados => {
            const select = document.getElementById("selectAgregado");
            select.innerHTML = "";
            agregados.forEach(agg => {
                const option = document.createElement("option");
                option.value = agg.id;
                option.textContent = agg.nombre;
                select.appendChild(option);
            });
            document.getElementById("modalAgregados").style.display = "block";
        });
}

function cerrarModalAgregados() {
    document.getElementById("modalAgregados").style.display = "none";
}







function usarAgregadoSeleccionado() {
  const id = document.getElementById("selectAgregado").value;

  fetch(`/api/crud_agregados_mixFamiliari/obtener_curva_agregado/${id}`)
    .then(res => res.json())
    .then(tamices => {
      const nombre = tamices[0].nombre_agregado?.trim() || "Agregado";

      // 🔍 Seleccionar la mezcla ya existente (ej: con data-id="0")
      const mezclaSeleccionada = document.querySelector(".mezcla[data-id='0']");

      if (!mezclaSeleccionada) {
        console.error("❌ No se encontró la mezcla para sobrescribir.");
        return;
      }

      // 📝 Actualizar el nombre del producto
      const inputNombre = mezclaSeleccionada.querySelector(".nombreProducto");
      if (inputNombre) {
        inputNombre.value = nombre;
        inputNombre.dataset.original = nombre;
      }

      // 🧼 Limpiar y actualizar las filas de la tabla
      const tbody = mezclaSeleccionada.querySelector("table.tabla tbody");
      if (!tbody) {
        console.error("❌ No se encontró el tbody de la tabla.");
        return;
      }
      tbody.innerHTML = "";

      tamices.forEach(t => {
        const fila = document.createElement("tr");
        fila.innerHTML = `
          <td contenteditable="true">${t.tamiz}</td>
          <td contenteditable="true">${isNaN(t.porcentaje) ? "" : t.porcentaje}</td>
          <td><button class="btn btn-danger" onclick="this.closest('tr').remove()">Eliminar</button></td>
        `;
        tbody.appendChild(fila);
      });

      // (Opcional) Ocultar botón de agregar fila si querés, o dejalo visible
      const btnAgregar = mezclaSeleccionada.querySelector('button[onclick*="agregarFilaMultiple"]');
      if (btnAgregar) {
        btnAgregar.style.display = "none"; // o "inline-block" si querés que siga visible
      }

      cerrarModalAgregados();
    })
    .catch(err => {
      console.error("❌ Error al obtener curva del agregado:", err);
    });
}


