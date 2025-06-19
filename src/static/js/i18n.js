// i18n.js — sistema simple de internacionalización frontend

const I18N = (() => {
  const mensajes = {
    es: {
      verificar_titulo: "📬 ¡Revisá tu correo!",
      verificar_mensaje: "Te enviamos un enlace de confirmación a tu casilla de correo.",
      verificar_instruccion: "Hacelo clic y luego iniciá sesión.",
      verificar_link: "Iniciá sesión",
      verificar_reenviar_label: "¿No lo recibiste?",
      verificar_boton: "📨 Reenviar correo",
      verificar_exito: "Correo reenviado correctamente.",
      verificar_error: "No se pudo reenviar el correo."
    },
    en: {
      verificar_titulo: "📬 Check your email!",
      verificar_mensaje: "We sent you a confirmation link.",
      verificar_instruccion: "Click it and then log in.",
      verificar_link: "Log in",
      verificar_reenviar_label: "Didn't receive it?",
      verificar_boton: "📨 Resend email",
      verificar_exito: "Email resent successfully.",
      verificar_error: "Could not resend email."
    },
    it: {
      verificar_titulo: "📬 Controlla la tua email!",
      verificar_mensaje: "Ti abbiamo inviato un link di conferma.",
      verificar_instruccion: "Clicca sul link e poi accedi.",
      verificar_link: "Accedi",
      verificar_reenviar_label: "Non l'hai ricevuto?",
      verificar_boton: "📨 Invia di nuovo",
      verificar_exito: "Email inviata nuovamente.",
      verificar_error: "Impossibile inviare di nuovo l'email."
    },
    pt: {
      verificar_titulo: "📬 Verifique seu e-mail!",
      verificar_mensaje: "Enviamos um link de confirmação para o seu e-mail.",
      verificar_instruccion: "Clique no link e depois faça login.",
      verificar_link: "Faça login",
      verificar_reenviar_label: "Não recebeu?",
      verificar_boton: "📨 Reenviar e-mail",
      verificar_exito: "E-mail reenviado com sucesso.",
      verificar_error: "Não foi possível reenviar o e-mail."
    }
  };

  function getLang() {
    const cookieLang = document.cookie.split("; ").find(c => c.startsWith("lang="));
    return cookieLang ? cookieLang.split("=")[1] : "es";
  }

  function t(key) {
    const lang = getLang();
    return mensajes[lang]?.[key] || mensajes["es"]?.[key] || `[${key}]`;
  }

  return { t };
})();
