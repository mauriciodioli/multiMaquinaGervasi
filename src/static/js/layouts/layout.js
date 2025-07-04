


document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById("conexionSqlServer");
  const modal = document.getElementById("modal-sqlserver");

  console.log("Btn conexión SQL:", btn, "Modal SQL:", modal);
  if (!btn || !modal) return;  // si no existe, abortamos

  btn.addEventListener("click", e => {
    e.preventDefault();
    debugger;  // aquí debería parar si todo está bien enlazado

    // Rellenar campos
    document.getElementById("input-sql-ip").value       = localStorage.getItem("ipSqlServer") || "";
    document.getElementById("input-sql-port").value     = localStorage.getItem("portSqlServer") || "";
    document.getElementById("input-sql-user").value     = localStorage.getItem("userSqlServer") || "";
    document.getElementById("input-sql-password").value = localStorage.getItem("pasSqlServer")    || "";

    // Mostrar modal
    modal.style.display = "block";
  });

  // Ojo: recuerda enganchar también el cierre del modal aquí si aún no lo has hecho.
});

// Función para cerrar el modal
document.getElementById("modal-sql-close").addEventListener("click", () => {
    const modal = document.getElementById("modal-sqlserver");
    modal.style.display = "none";
});

function cerrarModalConfiguraSqlServer() {
  document.getElementById('modal-sqlserver').style.display = 'none';
}


// Cerrar el modal si se hace clic fuera de él
window.addEventListener("click", (e) => {
    const modal = document.getElementById("modal-sqlserver");
    if (e.target === modal) {
        modal.style.display = "none";
    }
});

// Función para confirmar la configuración
document.getElementById("confirmar-sql").addEventListener("click", () => {
    const ip = document.getElementById("input-sql-ip").value.trim();
    const port = document.getElementById("input-sql-port").value.trim();
    const user = document.getElementById("input-sql-user").value.trim();
    const pas = document.getElementById("input-sql-password").value.trim();

    if (!ip || !port) {
        alert("Compilare entrambi i campi: IP e Porta.");
        return;
    }

    // Guardar los valores en localStorage
    localStorage.setItem("ipSqlServer", ip);
    localStorage.setItem("portSqlServer", port);
    localStorage.setItem("userSqlServer", user);
    localStorage.setItem("pasSqlServer", pas);

    alert(`✅ IP e porta salvati: ${ip}:${port}`);

    // Datos a enviar al servidor
    const data = {
        user_id: 1,  // Este es solo un ejemplo, ajusta según tu lógica
        driver: "SQL Server",  // Ajusta según los campos que necesites
        ipSqlServer: ip,
        portSqlServer: port,
        userSqlServer: user,
        pasSqlServer: pas,
        encrypt: "yes",  // Ajusta si es necesario
        trustServerCertificate: "yes",  // Ajusta si es necesario
        sector: "multiMaquinaDB",  // Ajusta si es necesario
        fecha: new Date().toISOString(),  // Usa la fecha actual
        estado: "Activo"  // Ajusta según sea necesario
    };

    // Enviar los datos con fetch (AJAX)
    fetch("/conexion_db/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)  // Convierte los datos a formato JSON
    })
    .then(response => response.json())
    .then(data => {
        if (data) {
            alert("Conexión guardada exitosamente.");
        }
    })
    .catch(error => {
        console.error("Error al guardar la conexión:", error);
        alert("Hubo un error al guardar la conexión.");
    });

    // Ocultar el modal
    const modal = document.getElementById("modal-sqlserver");
    modal.style.display = "none";
});






























    function showToast(mensaje) {
        const toast = document.createElement("div");
        toast.className = "toast align-items-center text-bg-success border-0 position-fixed bottom-0 end-0 m-4 show";
        toast.role = "alert";
        toast.style.zIndex = "1055";
        toast.innerHTML = `
          <div class="d-flex">
            <div class="toast-body">
              ${mensaje}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
          </div>
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }
    
    
    



    
      
      document.getElementById("descargar_tabla_excel").addEventListener("click", (e) => {
          e.preventDefault();
        const tabla = document.querySelector(".tabla-container table");
        if (!tabla) return alert("Non ci sono dati da esportare.");
    
        const wb = XLSX.utils.book_new();
        const ws = XLSX.utils.table_to_sheet(tabla);
        XLSX.utils.book_append_sheet(wb, ws, "Datos");
    
        XLSX.writeFile(wb, "datos_maquina.xlsx");
    });
    









    















document.addEventListener('DOMContentLoaded', () => {
  // — Elementos del DOM —
  const btnMenu    = document.getElementById('btn-menu-toggle');
  const navMain    = document.querySelector('.navigation-main');
  const modalMenu  = document.getElementById('modal-menu');
  const modalList  = document.getElementById('modal-menu-list');
  const modalClose = document.getElementById('modal-menu-close');
  if (!btnMenu || !navMain || !modalMenu || !modalList || !modalClose) return;

  // — Map de handlers: para cada id de <a>, su función —
  const handlers = {
    // Ejemplo: conexión SQL Server
    conexionSqlServer(link) {
      // Rellenas campos…
      document.getElementById("input-sql-ip").value       = localStorage.getItem("ipSqlServer")   || "";
      document.getElementById("input-sql-port").value     = localStorage.getItem("portSqlServer") || "";
      document.getElementById("input-sql-user").value     = localStorage.getItem("userSqlServer") || "";
      document.getElementById("input-sql-password").value = localStorage.getItem("pasSqlServer")  || "";
      // Y abres tu modal específico
      document.getElementById('modal-sqlserver').style.display = 'block';
    },

    // Otro ejemplo: descargar Excel
    descargar_tabla_excel(link) {
      // Llama a tu función de exportar o dispara el click real
      exportarTablaAExcel();
    },

    // Puedes añadir aquí más handlers:
    // miOtroId(link) { … }
  };

  // — Funciones puras de clonación/recursividad —
  function cloneLink(aElem) {
    return aElem.cloneNode(true);
  }
  function buildMenu(ulElem) {
    const newUl = document.createElement('ul');
    Array.from(ulElem.children).forEach(liOrig => {
      if (liOrig.tagName !== 'LI') return;
      const aOrig = liOrig.querySelector(':scope > a');
      if (!aOrig) return;
      const liNew = document.createElement('li');
      liNew.appendChild(cloneLink(aOrig));
      const subUl = liOrig.querySelector(':scope > ul.sub-menu');
      if (subUl) {
        liNew.classList.add('has-sub');
        liNew.appendChild(buildMenu(subUl));
      }
      newUl.appendChild(liNew);
    });
    return newUl;
  }

  // — Abrir/Cerrar menú principal —
  btnMenu.addEventListener('click', e => {
    e.preventDefault();
    modalList.innerHTML = '';
    const rootUl = navMain.tagName === 'UL' ? navMain : navMain.querySelector('ul');
    if (!rootUl) return;
    modalList.appendChild(buildMenu(rootUl));
    modalMenu.style.display = 'block';
  });
  modalClose.addEventListener('click', () => modalMenu.style.display = 'none');
  modalMenu.addEventListener('click', e => {
    if (e.target === modalMenu) modalMenu.style.display = 'none';
  });

  // — Delegación: un sólo listener para TODO el menú clonado —
  modalList.addEventListener('click', e => {
    const link = e.target.closest('a');
    if (!link) return;

    // 1) Toggle submenus
    if (link.nextElementSibling && link.parentElement.classList.contains('has-sub')) {
      e.preventDefault();
      link.parentElement.classList.toggle('open');
      return;
    }

    // 2) Handler específico si existe en el map
    if (handlers[link.id]) {
      e.preventDefault();
      handlers[link.id](link);
      return;
    }

    // 3) Default: cierra menú y navega
    modalMenu.style.display = 'none';
    // si es # o javascript:void(0) no hace nada
    if (!/^#|javascript:/.test(link.getAttribute('href'))) {
      window.location.href = link.href;
    }
  });
});














    








document.addEventListener('DOMContentLoaded', function() {
  const btnMenu = document.getElementById('btn-menu-toggle');
  const navMain = document.querySelector('.navigation-main');

  // 1) Toggle menú principal
  btnMenu.addEventListener('click', function(e) {
    e.preventDefault();
    e.stopPropagation();
    navMain.classList.toggle('open');
  });

  // 2) Busca dinámicamente todos los <li> que tengan un <ul class="sub-menu">
  const submenuParents = Array.from(
    navMain.querySelectorAll('ul.sub-menu')
  ).map(ul => ul.parentElement);

  console.log('🔧 Padres de sub-menú detectados:', submenuParents);

  // 3) Para cada uno, enganchamos el click en su <a> principal
  submenuParents.forEach(li => {
    const trigger = li.querySelector('a');
    console.log('  📌 Añadiendo listener a:', trigger.textContent.trim());
    trigger.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      li.classList.toggle('open');
      console.log(
        `   ➤ ${trigger.textContent.trim()} ahora`,
        li.classList.contains('open') ? 'abierto' : 'cerrado'
      );
    });
  });
});










