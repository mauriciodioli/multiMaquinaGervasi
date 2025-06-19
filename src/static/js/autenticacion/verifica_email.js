document.addEventListener("DOMContentLoaded", () => {
  const t = I18N.t;

  document.title = t("verificar.titulo");
  document.getElementById("verifica-titulo").textContent = t("verificar.titulo");
  document.getElementById("verifica-texto").textContent = t("verificar.mensaje");
  document.getElementById("verifica-link").innerHTML =
    `📩 ${t("verificar.instruccion")} <a href="/" id="link-login">${t("verificar.link")}</a>.`;
  document.getElementById("reenviar-label").textContent = t("verificar.reenviar_label");
  document.getElementById("btn-reenviar").textContent = t("verificar.boton");

  document.getElementById("btn-reenviar").addEventListener("click", () => {
    const correo = localStorage.getItem("registro_email");
    if (!correo) return;

    fetch("/reenviar_confirmacion/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ correo_electronico: correo })
    })
      .then(res => res.json())
      .then(data => {
        document.getElementById("mensaje-reenvio").textContent =
          data.success ? t("verificar.exito") : (data.error || t("verificar.error"));
      });
  });
});