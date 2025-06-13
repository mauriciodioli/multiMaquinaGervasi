const mensajes = {
  es: {
    titulo: "📬 ¡Revisá tu correo!",
    mensaje: "Te enviamos un enlace de confirmación a tu casilla de correo.",
    instruccion: "Hacelo clic y luego iniciá sesión.",
    reenviar: "📨 Reenviar correo",
    reenviado: "Correo reenviado correctamente.",
    error: "No se pudo reenviar el correo."
  },
  en: {
    titulo: "📬 Check your email!",
    mensaje: "We sent you a confirmation link.",
    instruccion: "Click it and then log in.",
    reenviar: "📨 Resend email",
    reenviado: "Email resent successfully.",
    error: "Could not resend email."
  },
  it: {
    titulo: "📬 Controlla la tua email!",
    mensaje: "Ti abbiamo inviato un link di conferma.",
    instruccion: "Clicca sul link e poi accedi.",
    reenviar: "📨 Invia di nuovo",
    reenviado: "Email inviata nuovamente.",
    error: "Impossibile inviare di nuovo l'email."
  }
};

document.addEventListener("DOMContentLoaded", () => {
  const lang = localStorage.getItem("lang") || "es";
  const t = mensajes[lang] || mensajes["es"];

  document.querySelector("h2").textContent = t.titulo;
  document.querySelectorAll("p")[0].textContent = t.mensaje;
  document.querySelectorAll("p")[1].innerHTML = `👉 ${t.instruccion}`;
  document.getElementById("btn-reenviar").textContent = t.reenviar;

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
          data.success ? t.reenviado : (data.error || t.error);
      });
  });
});
