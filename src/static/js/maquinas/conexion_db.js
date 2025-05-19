document.addEventListener("DOMContentLoaded", () => {
    const idConexion = 1;  // Reemplazalo si necesitás otro ID

    fetch(`/conexion_db/${idConexion}`)
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                console.warn("❌ No se encontró la conexión:", data.error);
                return;
            }

            console.log("✅ Conexión obtenida:", data);

            // Guardar solo si NO existe ya en localStorage
            if (!localStorage.getItem("ipSqlServer")) {
                localStorage.setItem("ipSqlServer", data.ipSqlServer);
            }

            if (!localStorage.getItem("portSqlServer")) {
                localStorage.setItem("portSqlServer", data.portSqlServer);
            }

            if (!localStorage.getItem("userSqlServer")) {
                localStorage.setItem("userSqlServer", data.userSqlServer);
            }

            if (!localStorage.getItem("pasSqlServer")) {
                localStorage.setItem("pasSqlServer", data.pasSqlServer);
            }

            if (!localStorage.getItem("database")) {
                localStorage.setItem("database", data.database);
            }

            if (!localStorage.getItem("driver")) {
                localStorage.setItem("driver", data.driver || "SQL Server");
            }

            if (!localStorage.getItem("encrypt")) {
                localStorage.setItem("encrypt", data.encrypt || "no");
            }

            if (!localStorage.getItem("trustServerCertificate")) {
                localStorage.setItem("trustServerCertificate", data.trustServerCertificate || "yes");
            }

            console.log("📦 Datos cargados solo si no existían en localStorage");
        })
        .catch(err => {
            console.error("💥 Error al obtener la conexión:", err);
        });
});
