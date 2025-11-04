// ===== i18n básico para el simulador =====
const SIM_I18N = {
  es: {
    sum100_alert: "⚠️ Las proporciones deben sumar 100%",
    bad_response: "Respuesta no válida del servidor",
    process_error: "❌ Error al procesar la mezcla",
    chart_alt: "Curva resultante vs Fuller",
    header: "Resultado de simulación",
    zone_coarse: "Zona gruesa",
    zone_medium: "Zona media",
    zone_fine: "Zona fina",
    recommendation: "🔎 Recomendación",
    hide_btn: "❌ Ocultar resultado",
    data_error: "❌ Error: datos incompletos o mal formateados."
  },
  en: {
    sum100_alert: "⚠️ Percentages must sum to 100%",
    bad_response: "Invalid server response",
    process_error: "❌ Error processing mix",
    chart_alt: "Resulting curve vs Fuller",
    header: "Simulation result",
    zone_coarse: "Coarse zone",
    zone_medium: "Medium zone",
    zone_fine: "Fine zone",
    recommendation: "🔎 Recommendation",
    hide_btn: "❌ Hide result",
    data_error: "❌ Error: incomplete or malformed data."
  },
  it: {
    sum100_alert: "⚠️ Le percentuali devono sommare 100%",
    bad_response: "Risposta non valida dal server",
    process_error: "❌ Errore nell'elaborare la miscela",
    chart_alt: "Curva risultante vs Fuller",
    header: "Risultato della simulazione",
    zone_coarse: "Zona grossolana",
    zone_medium: "Zona media",
    zone_fine: "Zona fine",
    recommendation: "🔎 Raccomandazione",
    hide_btn: "❌ Nascondi risultato",
    data_error: "❌ Errore: dati incompleti o non validi."
  },
  pt: {
    sum100_alert: "⚠️ As proporções devem somar 100%",
    bad_response: "Resposta inválida do servidor",
    process_error: "❌ Erro ao processar a mistura",
    chart_alt: "Curva resultante vs Fuller",
    header: "Resultado da simulação",
    zone_coarse: "Zona grossa",
    zone_medium: "Zona média",
    zone_fine: "Zona fina",
    recommendation: "🔎 Recomendação",
    hide_btn: "❌ Ocultar resultado",
    data_error: "❌ Erro: dados incompletos ou inválidos."
  },
  pl: {
    sum100_alert: "⚠️ Udziały muszą sumować się do 100%",
    bad_response: "Nieprawidłowa odpowiedź serwera",
    process_error: "❌ Błąd podczas przetwarzania mieszanki",
    chart_alt: "Krzywa wynikowa vs Fuller",
    header: "Wynik symulacji",
    zone_coarse: "Strefa gruba",
    zone_medium: "Strefa średnia",
    zone_fine: "Strefa drobna",
    recommendation: "🔎 Rekomendacja",
    hide_btn: "❌ Ukryj wynik",
    data_error: "❌ Błąd: niekompletne lub nieprawidłowe dane."
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
      bloqueo: "Demasiados intentos. Espera",
      guardar_analisis_granulometrico: "Guardar análisis granulométrico"
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
      bloqueo: "Too many attempts. Wait",
      guardar_analisis_granulometrico: "Save granulometric analysis"
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
      bloqueo: "Troppi tentativi. Aspetta",
      guardar_analisis_granulometrico: "Salva analisi granulometrica"
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
      bloqueo: "Muitas tentativas. Aguarde",
      guardar_analisis_granulometrico: "Salvar análise granulométrica"
    },
    pl: {
    titulo: "Zaloguj się",
    correo: "E-mail",
    pass: "Hasło",
    entrar: "Zaloguj się",
    olvidar: "Zapomniałeś hasła?",
    registrar: "Nie masz konta? Zarejestruj się",
    error_credenciales: "Nieprawidłowy e-mail lub hasło",
    error_inactivo: "Twoje konto nie jest aktywne. Sprawdź swój e-mail",
    error_servidor: "Wewnętrzny błąd serwera",
    intentos_previos: "Poprzednie nieudane próby",
    demasiados_intentos: "Za dużo prób.",
    espera: "Poczekaj",
    segundos: "sekund.",
    error_conexion: "Błąd połączenia. Spróbuj ponownie później.",
    bloqueo: "Za dużo prób. Poczekaj",
    guardar_analisis_granulometrico: "Zapisz analizę granulometryczną"
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
    },
    pl: {
    titulo: "Utwórz nowe konto",
    correo: "E-mail",
    pass: "Hasło",
    repetir: "Powtórz hasło",
    captcha: "Nie jestem robotem",
    registrarse: "Zarejestruj się",
    volver: "Powrót do logowania",
    errores: {
      correo: "Nieprawidłowy adres e-mail.",
      longitud: "Hasło musi mieć co najmniej 8 znaków.",
      mayus: "Musi zawierać co najmniej jedną wielką literę.",
      numero: "Musi zawierać co najmniej jedną cyfrę.",
      especial: "Musi zawierać znak specjalny.",
      coinciden: "Hasła nie są zgodne.",
      captcha: "Musisz zaznaczyć captcha."
    },
    requisitos: {
      longitud: "Minimum 8 znaków",
      mayus: "Co najmniej jedna wielka litera",
      numero: "Co najmniej jedna cyfra",
      especial: "Co najmniej jeden znak specjalny (!@#$...)"
    }
  }
};

  function getLang() {
    const cookieLang = document.cookie.split("; ").find(c => c.startsWith("lang="));
    return cookieLang ? cookieLang.split("=")[1] : "es";
  }

  function t(key) {
    const lang = getLang();
    debugger;
    // Soporte para claves tipo "verificar.titulo"
    if (key.startsWith("verificar.")) {
      const subkey = "verificar_" + key.split(".")[1];
      return mensajes_verifica_email[lang]?.[subkey] || mensajes_verifica_email["es"]?.[subkey] || `[${key}]`;
    }
    if (key.startsWith("login.")) {
      const subkey = key.split(".")[1];
      return mensajes_login[lang]?.[subkey] || mensajes_login["es"]?.[subkey] || `[${key}]`;
    }
    if (key.startsWith("registrarse.")) {
      const subkey = key.split(".")[1];
      return mensajes_registrarse[lang]?.[subkey] || mensajes_registrarse["es"]?.[subkey] || `[${key}]`;
    }
    // Por defecto busca en mensajes_login
    return mensajes_login[lang]?.[key] || mensajes_login["es"]?.[key] || `[${key}]`;
  }
  return {
  t,
  mensajes_verifica_email,
  mensajes_login, // 👈 lo exponés
  mensajes_registrarse, // 👈 lo exponés
  getLang
};
})();
