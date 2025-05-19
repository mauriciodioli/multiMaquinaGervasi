document.getElementById("conexionSqlServer").addEventListener("click", (e) => {
    e.preventDefault();
    debugger;
    // Llenar los inputs con los valores de localStorage
    document.getElementById("input-sql-ip").value = localStorage.getItem("ipSqlServer") || "";
    document.getElementById("input-sql-port").value = localStorage.getItem("portSqlServer") || "";
    document.getElementById("input-sql-user").value = localStorage.getItem("userSqlServer") || "";
    document.getElementById("input-sql-password").value = localStorage.getItem("pasSqlServer") || "";

    // Mostrar el modal
    const modal = document.getElementById("modal-sqlserver");
    modal.style.display = "block";
});

// Función para cerrar el modal
document.getElementById("modal-close").addEventListener("click", () => {
    const modal = document.getElementById("modal-sqlserver");
    modal.style.display = "none";
});

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
    


























