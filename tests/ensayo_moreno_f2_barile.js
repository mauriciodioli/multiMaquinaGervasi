
(() => {
  "use strict";

  const tamices = [10, 8, 4, 2, 1, 0.5, 0.25, 0.125, 0.063];

  const materiales = [
    {
      nombre: "F2",
      valores: [10, 13, 726, 252, 14, 1.2, 1.1, 1, 1.5],
      fondo: 0.2
    },
    {
      nombre: "BARILE",
      valores: [11, 3.1, 12.7, 39, 264.6, 260.4, 201.5, 175.5, 46.5],
      fondo: 11.3
    }
  ];

  const contenedor = document.getElementById("mezclasContainer");

  if (!contenedor || typeof agregarMezcla !== "function") {
    console.error("Abrí la pantalla principal de Fuller.");
    return;
  }

  if (!confirm(
    "Se reemplazarán las tablas visibles por F2 y BARILE. ¿Continuar?"
  )) return;

  const escribir = (celda, valor) => {
    if (!celda || celda.tagName !== "TD") {
      throw Error("Celda editable no encontrada");
    }
    celda.textContent = String(valor);
    celda.dispatchEvent(new Event("input", { bubbles: true }));
  };

  try {
    contenedor.replaceChildren();
    const resumen = [];

    for (const material of materiales) {
      agregarMezcla();

      const bloque = contenedor.lastElementChild;
      const tbody = bloque.querySelector("table.tabla tbody");
      const nombre = bloque.querySelector(".nombreProducto");
      const muestra = bloque.querySelector(".pesoCampione");
      const fondo = tbody.querySelector('tr[data-fondo="true"]');

      if (!nombre || !muestra || !fondo) {
        throw Error("Estructura incorrecta para " + material.nombre);
      }

      let filas = [...tbody.rows].filter(f => f !== fondo);

      while (filas.length > tamices.length) filas.pop().remove();

      if (filas.length < tamices.length) {
        throw Error("Faltan filas de tamices para " + material.nombre);
      }

      const total = material.valores.reduce(
        (a, b) => a + b, material.fondo
      );

      nombre.value = material.nombre;
      muestra.value = String(Number(total.toFixed(3)));

      nombre.dispatchEvent(new Event("input", { bubbles: true }));
      muestra.dispatchEvent(new Event("input", { bubbles: true }));

      filas.forEach((fila, i) => {
        const td = fila.querySelectorAll(":scope > td");
        escribir(td[0], tamices[i]);
        escribir(td[1], material.valores[i]);
      });

      escribir(fondo.querySelectorAll(":scope > td")[1], material.fondo);

      if (typeof numerarFilasFuller === "function") {
        numerarFilasFuller(bloque);
      }

      resumen.push({
        material: material.nombre,
        masa_muestra_g: Number(total.toFixed(3)),
        fondo_g: material.fondo,
        fondo_pct: (100 * material.fondo / total).toFixed(4) + "%"
      });
    }

    window.__ensayoMorenoF2 = { tamices, materiales, resumen };

    console.table(resumen);
    console.log("PASS: F2 y BARILE cargados correctamente.");
    console.log("Ahora ejecutá Calculate All y Calculate Retained.");

  } catch (error) {
    console.error("ERROR:", error);
    console.warn("Recargá la página antes de repetir.");
  }
})();
