document.getElementById("form-login").addEventListener("submit", function (e) {
  e.preventDefault();

  const correo = document.getElementById("correo").value;
  const password = document.getElementById("password").value;
  const errorDiv = document.getElementById("error-login");
  const lang = localStorage.getItem("lang") || "es";

  fetch("/login_usuario/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      correo_electronico: correo,
      password: password,
      lang: lang  // ✅ se envía al backend
    })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        window.location.href = data.redireccion;
      } else {
        errorDiv.textContent = data.error || "Credenciales incorrectas";
      }
    })
    .catch(() => {
      errorDiv.textContent = "Error de red o servidor";
    });
});






const mensajes = {
    es: {
      titulo: "Iniciar Sesión",
      correo: "Correo electrónico",
      pass: "Contraseña",
      entrar: "Entrar",
      olvidar: "¿Olvidaste tu contraseña?",
      registrar: "¿No tenés cuenta? Registrate",
      error_credenciales: "Correo o contraseña incorrectos",
      error_inactivo: "Tu cuenta no está activa. Verificá tu correo",
      error_servidor: "Error interno del servidor"
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
      error_servidor: "Internal server error"
    },
    it: {
      titulo: "Accedi",
      correo: "Email",
      pass: "Password",
      entrar: "Entra",
      olvidar: "Hai dimenticato la password?",
      registrar: "Non hai un account? Registrati",
      error_credenciales: "Invalid email or password",
      error_inactivo: "Your account is not active. Check your email",
      error_servidor: "Internal server error"
    }
  };

  function aplicarIdioma(lang) {
    const t = mensajes[lang] || mensajes['es'];
    document.getElementById("login-title").textContent = t.titulo;
    document.getElementById("correo").placeholder = t.correo;
    document.getElementById("password").placeholder = t.pass;
    document.getElementById("btn-submit").textContent = t.entrar;
    document.getElementById("link-olvidar").textContent = t.olvidar;
    document.getElementById("link-registrarse").textContent = t.registrar;

    document.getElementById("lang-select").value = lang;
  }

  document.addEventListener("DOMContentLoaded", () => {
    let lang = localStorage.getItem("lang") || (navigator.language || 'es').slice(0, 2);
    if (!mensajes[lang]) lang = 'es';
    aplicarIdioma(lang);

    document.getElementById("lang-select").addEventListener("change", function () {
      const selectedLang = this.value;
      localStorage.setItem("lang", selectedLang);
      aplicarIdioma(selectedLang);
    });




    const langSelect = document.getElementById("lang-select");
if (langSelect) {
  langSelect.addEventListener("change", function () {
    const selectedLang = this.value;
    localStorage.setItem("lang", selectedLang);
    aplicarIdioma(selectedLang);
  });
}

const linkRegistro = document.getElementById("link-registrarse");
if (linkRegistro) {
  linkRegistro.addEventListener("click", function () {
    const currentLang = langSelect?.value || 'es';
    localStorage.setItem("lang", currentLang);
  });
}

  });