
// ---------- Config ----------
const MF_ENDPOINT = "/mixFamiliari_crud_materia_forma_listar_forma_json/";
const MF_STORAGE_KEY = "materia_forma_id";
const MF_COOKIE_NAME = "materia_forma_id";
const MF_COOKIE_MAX_AGE = 60 * 60 * 24 * 180; // 180 días

// ---------- Utils ----------
function setCookie(name, value, maxAgeSeconds, path = "/") {
  document.cookie = `${encodeURIComponent(name)}=${encodeURIComponent(value)}; max-age=${maxAgeSeconds}; path=${path}`;
}
function getCookie(name) {
  const cookies = document.cookie.split(";").map(c => c.trim());
  const target = cookies.find(c => c.startsWith(encodeURIComponent(name) + "="));
  if (!target) return null;
  return decodeURIComponent(target.split("=").slice(1).join("="));
}
function getStoredMateriaFormaId() {
  return localStorage.getItem(MF_STORAGE_KEY) || getCookie(MF_COOKIE_NAME) || null;
}
function storeMateriaFormaId(id) {
  localStorage.setItem(MF_STORAGE_KEY, id);

  setCookie(MF_COOKIE_NAME, id, MF_COOKIE_MAX_AGE);
}

// Dado que el esquema puede variar, priorizamos campos comunes
function itemLabel(it) {
  return it.nombre || it.name || it.descripcion || (`#${it.id}`);
}

// ---------- Modal helpers ----------
function getModalInstance() {
  const el = document.getElementById("modal-materia-forma");
  // Bootstrap 5: reusa instancia si existe
  let instance = bootstrap.Modal.getInstance(el);
  if (!instance) instance = new bootstrap.Modal(el, { backdrop: 'static' });
  return instance;
}

async function cargarOpcionesMateriaForma(preselectId = null) {
  const sel = document.getElementById("select-materia-forma");
  sel.innerHTML = `<option value="">Cargando...</option>`;

  try {
    const res = await fetch(MF_ENDPOINT, { headers: { "Accept": "application/json" } });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (!data.success) throw new Error("Respuesta success=false");

    const lista = data.tipos || [];
    if (!Array.isArray(lista) || lista.length === 0) {
      sel.innerHTML = `<option value="">(Sin opciones disponibles)</option>`;
      return;
    }

    // Construir opciones
    const opts = ['<option value="">Seleccioná una opción...</option>'];
    for (const it of lista) {
    const id = it.id ?? it.materia_forma_id ?? it.pk ?? "";
    const label = it.forma ?? it.descripcion ?? `#${id}`;  // <<-- usa 'forma' primero
    if (id === "") continue;
    const selected = (preselectId && String(preselectId) === String(id)) ? ' selected' : '';
    opts.push(`<option value="${id}"${selected}>${label}</option>`);
    }
    sel.innerHTML = opts.join("");


  } catch (err) {
    console.error("Error cargando MateriaForma:", err);
    sel.innerHTML = `<option value="">Error al cargar opciones</option>`;
  }
}




// ---------- Event delegation para abrir modal ----------
document.addEventListener("click", async function (e) {
  const btn = e.target?.closest(".btn-abrir-modal-materia-forma");
  if (!btn) return;
  
  // Si querés atar el componenteId al botón guardar, lo dejamos seteado:
  const componenteId = btn.dataset.id || null;
  document.getElementById("btn-guardar-tipo-mezcla").dataset.componenteId = componenteId;
  localStorage.setItem('componente_id', componenteId);
  const preselect = getStoredMateriaFormaId();
  await cargarOpcionesMateriaForma(preselect);
document.getElementById('modal-materia-forma').style.display = "block";  
});

// Guardar selección → actualizar backend y la fila
document.getElementById("btn-guardar-materia-forma").addEventListener("click", async function () {
  const sel = document.getElementById("select-materia-forma");
  const materiaFormaId = sel.value; // ← CORRECTO: era sel.seleccion
  const componenteId   = localStorage.getItem('componente_id');
  
  if (!materiaFormaId) {
    alert("Seleccioná una Materia Forma antes de guardar.");
    return;
  }
  if (!componenteId) {
    alert("Falta el componenteId en el botón guardar.");
    return;
  }

  // Persistir en cookie + localStorage
  storeMateriaFormaId(materiaFormaId);

  try {
    // Actualiza en el backend y refresca la fila
    await actualizarFilaComponente({ componenteId, materiaFormaId });

    // (Opcional) avisar a otros módulos
    document.dispatchEvent(new CustomEvent("materiaForma:changed", { detail: { componenteId, materiaFormaId }}));

    // Cerrar modal correctamente (Bootstrap 5)
  document.getElementById('modal-materia-forma').style.display = "none"; 
  } catch (err) {
    console.error("Error actualizando componente:", err);
    alert("No se pudo actualizar. Reintentá.");
  }
});




















// --- Actualiza backend y la fila de la tabla ---
async function actualizarFilaComponente({ componenteId, materiaFormaId }) {
  const row = document.querySelector(`tr[data-fila-id="${componenteId}"]`);
  if (!row) throw new Error(`No encontré la fila con data-fila-id="${componenteId}"`);

  // Tomamos los datos actuales desde el botón "Modificar" para NO pisarlos con nulls
  const btnModificar = row.querySelector('.btn-abrir-modal-modificar-componente');

  const payload = {
    nombre: btnModificar?.dataset.nombre ?? row.cells[1]?.textContent.trim(),
    pais: btnModificar?.dataset.pais ?? row.cells[2]?.textContent.trim(),
    descripcion: btnModificar?.dataset.descripcion ?? row.cells[3]?.textContent.trim(),
    tipo_mezcla_id: btnModificar?.dataset.tipo_mezcla_id ?? null,
    tipo_mezcla_nome: btnModificar?.dataset.tipo_mezcla_nome ?? row.cells[4]?.textContent.trim(),
    materia_forma_id: materiaFormaId,
  };

  const url = `/mixFamiliari_crud_componente_quimico_pantalla_modificar_agrega_materia_forma/${componenteId}`;

  const res = await fetch(url, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
      // Si usás CSRF, descomenta y poné tu token:
      // "X-CSRFToken": document.querySelector('meta[name="csrf-token"]')?.content || ""
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  if (!data.success) throw new Error(data.error || "Respuesta success=false");

  const cq = data.componente_quimico || {};
  
  
  // --- Refrescamos la fila ---
  // [0]=ID, [1]=Nombre, [2]=País, [3]=Descripción, [4]=Tipo Mezcla, [5]=Materia Forma
  if (cq.nombre) row.cells[1].textContent = cq.nombre;
  if (cq.pais) row.cells[2].textContent = cq.pais;
  if (typeof cq.descripcion !== "undefined") row.cells[3].textContent = cq.descripcion || "";

 const tipoMix = cq.tipo_mezcla_nome || row.cells[4].textContent.trim();
    row.cells[4].textContent = tipoMix;  // <- Tipo mezcla va en col 4

    const mfForma = cq.materia_forma_forma || "";
    row.cells[5].innerHTML = mfForma     // <- Materia forma va en col 5
    ? `<span class="badge bg-info text-dark ms-1">${mfForma}</span>`
    : "-";


  // --- Sincronizamos datasets para que los modales futuros lean lo correcto ---
  if (btnModificar) {
    if (cq.nombre) btnModificar.dataset.nombre = cq.nombre;
    if (typeof cq.descripcion !== "undefined") btnModificar.dataset.descripcion = cq.descripcion || "";
    if (cq.tipo_mezcla_id) btnModificar.dataset.tipo_mezcla_id = cq.tipo_mezcla_id;
    if (cq.tipo_mezcla_nome) btnModificar.dataset.tipo_mezcla_nome = cq.tipo_mezcla_nome;
    if (cq.materia_forma_forma) btnModificar.dataset.materia_forma_forma = cq.materia_forma_forma;
  }
  const btnMF = row.querySelector('.btn-abrir-modal-materia-forma');
  if (btnMF) btnMF.dataset.materia_forma_id = materiaFormaId;

  return data;
}