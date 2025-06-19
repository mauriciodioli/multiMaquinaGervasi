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


  const mensajes_login = {
    es: {
      titulo: "Iniciar Sesión",
      correo: "Correo electrónico",
      pass: "Contraseña",
      entrar: "Entrar",
      olvidar: "¿Olvidaste tu contraseña?",
      registrar: "¿No tenés cuenta? Registrate",
      error_credenciales: "Correo o contraseña incorrectos",
      error_inactivo: "Tu cuenta no está activa. Verificá tu correo",
      error_servidor: "Error interno del servidor",
      intentos_previos: "Intentos fallidos anteriores",
      demasiados_intentos: "Demasiados intentos.",
      espera: "Espera",
      segundos: "segundos.",
      error_conexion: "Error de conexión. Intenta más tarde.",
      bloqueo: "Demasiados intentos. Espera"
    },
    en: {
      titulo: "Sign In",
      correo: "Email",
      pass: "Password",
      entrar: "Log In",
      olvidar: "Forgot your password?",
      registrar: "Don't have an account? Register",
      error_credenciales: "Invalid email or password",
      error_inactivo: "Your account is not active. Check your email",
      error_servidor: "Internal server error",
      intentos_previos: "Previous failed attempts",
      demasiados_intentos: "Too many attempts.",
      espera: "Wait",
      segundos: "seconds.",
      error_conexion: "Connection error. Try again later.",
      bloqueo: "Too many attempts. Wait"
    },
    it: {
      titulo: "Accedi",
      correo: "Email",
      pass: "Password",
      entrar: "Entra",
      olvidar: "Hai dimenticato la password?",
      registrar: "Non hai un account? Registrati",
      error_credenciales: "Email o password non validi",
      error_inactivo: "Il tuo account non è attivo. Controlla la tua email",
      error_servidor: "Errore interno del server",
      intentos_previos: "Tentativi falliti precedenti",
      demasiados_intentos: "Troppi tentativi.",
      espera: "Aspetta",
      segundos: "secondi.",
      error_conexion: "Errore di connessione. Riprova più tardi.",
      bloqueo: "Troppi tentativi. Aspetta"
    },
    pt: {
      titulo: "Entrar",
      correo: "E-mail",
      pass: "Senha",
      entrar: "Acessar",
      olvidar: "Esqueceu sua senha?",
      registrar: "Não tem uma conta? Cadastre-se",
      error_credenciales: "E-mail ou senha incorretos",
      error_inactivo: "Sua conta não está ativa. Verifique seu e-mail",
      error_servidor: "Erro interno do servidor",
      intentos_previos: "Tentativas anteriores falhadas",
      demasiados_intentos: "Muitas tentativas.",
      espera: "Aguarde",
      segundos: "segundos.",
      error_conexion: "Erro de conexão. Tente novamente mais tarde.",
      bloqueo: "Muitas tentativas. Aguarde"
    }
  };






const mensajes_registrarse = {
    es: {
      titulo: "Crear una cuenta nueva",
      correo: "Correo electrónico",
      pass: "Contraseña",
      repetir: "Repetir contraseña",
      captcha: "No soy un robot",
      registrarse: "Registrarse",
      volver: "Volver al login",
      errores: {
        correo: "El correo electrónico no es válido.",
        longitud: "La contraseña debe tener al menos 8 caracteres.",
        mayus: "Debe contener al menos una letra mayúscula.",
        numero: "Debe contener al menos un número.",
        especial: "Debe tener un carácter especial.",
        coinciden: "Las contraseñas no coinciden.",
        captcha: "Debes verificar el captcha."
      },
      requisitos: {
        longitud: "Mínimo 8 caracteres",
        mayus: "Al menos una letra mayúscula",
        numero: "Al menos un número",
        especial: "Al menos un carácter especial (!@#$...)"
      }
    },
    en: {
      titulo: "Create a new account",
      correo: "Email",
      pass: "Password",
      repetir: "Repeat password",
      captcha: "I'm not a robot",
      registrarse: "Register",
      volver: "Back to login",
      errores: {
        correo: "Invalid email address.",
        longitud: "Password must be at least 8 characters.",
        mayus: "Must include at least one uppercase letter.",
        numero: "Must include at least one number.",
        especial: "Must include a special character.",
        coinciden: "Passwords do not match.",
        captcha: "You must check the captcha."
      },
      requisitos: {
        longitud: "Minimum 8 characters",
        mayus: "At least one uppercase letter",
        numero: "At least one number",
        especial: "At least one special character (!@#$...)"
      }
    },
    it: {
      titulo: "Crea un nuovo account",
      correo: "Email",
      pass: "Password",
      repetir: "Ripeti password",
      captcha: "Non sono un robot",
      registrarse: "Registrati",
      volver: "Torna al login",
      errores: {
        correo: "Email non valida.",
        longitud: "La password deve contenere almeno 8 caratteri.",
        mayus: "Deve contenere almeno una lettera maiuscola.",
        numero: "Deve contenere almeno un numero.",
        especial: "Deve contenere un carattere speciale.",
        coinciden: "Le password non coincidono.",
        captcha: "Devi confermare il captcha."
      },
      requisitos: {
        longitud: "Minimo 8 caratteri",
        mayus: "Almeno una lettera maiuscola",
        numero: "Almeno un numero",
        especial: "Almeno un carattere speciale (!@#$...)"
      }
    },
    pt: {
      titulo: "Criar uma nova conta",
      correo: "E-mail",
      pass: "Senha",
      repetir: "Repetir senha",
      captcha: "Não sou um robô",
      registrarse: "Registrar-se",
      volver: "Voltar para o login",
      errores: {
        correo: "Endereço de e-mail inválido.",
        longitud: "A senha deve ter pelo menos 8 caracteres.",
        mayus: "Deve conter pelo menos uma letra maiúscula.",
        numero: "Deve conter pelo menos um número.",
        especial: "Deve conter um caractere especial.",
        coinciden: "As senhas não coincidem.",
        captcha: "Você deve verificar o captcha."
      },
      requisitos: {
        longitud: "Mínimo de 8 caracteres",
        mayus: "Pelo menos uma letra maiúscula",
        numero: "Pelo menos um número",
        especial: "Pelo menos um caractere especial (!@#$...)"
      }
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

  return {
  t,
  mensajes_login, // 👈 lo exponés
  mensajes_registrarse, // 👈 lo exponés
  getLang
};
})();
