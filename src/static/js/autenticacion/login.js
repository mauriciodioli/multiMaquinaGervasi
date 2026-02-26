const formLogin = document.getElementById("form-login");
const btnSubmit = document.getElementById("btn-submit");
const errorLogin = document.getElementById("error-login");

localStorage.removeItem("user_id");

// Mostrar intentos fallidos anteriores si existen
const intentos = localStorage.getItem("intentos_fallidos");
if (intentos) {
  errorLogin.textContent = `Intentos fallidos anteriores: ${intentos}`;
}

// ⏱️ Verificar si el usuario está bloqueado
function verificarBloqueo() {
  const bloqueoHasta = localStorage.getItem("bloqueo_hasta");
  const ahora = Date.now();

  if (bloqueoHasta && ahora < parseInt(bloqueoHasta)) {
    const segundosRestantes = Math.ceil((parseInt(bloqueoHasta) - ahora) / 1000);
    const lang = localStorage.getItem("lang") || "es";
    const t = I18N.dict.login[lang] || I18N.dict.login["es"];
    errorLogin.textContent = `${t.bloqueo} ${segundosRestantes} ${t.segundos}`;

    btnSubmit.disabled = true;

    setTimeout(() => {
      btnSubmit.disabled = false;
      errorLogin.textContent = "";
      localStorage.removeItem("bloqueo_hasta");
      localStorage.setItem("intentos_fallidos", "0");
    }, parseInt(bloqueoHasta) - ahora);

    return true;
  }

  return false;
}

// 🧠 Al cargar la página, verificamos bloqueo
if (verificarBloqueo()) {
  // ya está manejado
} else {
  // Si hay intentos previos, los mostramos
  const intentos = localStorage.getItem("intentos_fallidos");
  if (intentos) {
    errorLogin.textContent = `Intentos fallidos anteriores: ${intentos}`;
  }
}

formLogin.addEventListener("submit", async (e) => {
  e.preventDefault();

  if (verificarBloqueo()) return;

  const correo = document.getElementById("correo").value;
  const password = document.getElementById("password").value;
  const lang = document.getElementById("lang-select").value;

  try {
    const res = await fetch("/login_usuario/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ correo_electronico: correo, password, lang }),
    });

    const data = await res.json();

    if (data.success) {
      localStorage.removeItem("intentos_fallidos");
      localStorage.removeItem("bloqueo_hasta");
      localStorage.setItem("user_id", data.user_id);
      window.location.href = data.redireccion;
    } else {
      let intentos = parseInt(localStorage.getItem("intentos_fallidos") || "0") + 1;
      localStorage.setItem("intentos_fallidos", intentos);

      if (intentos >= 5) {
        const bloqueoPorMs = 60000; // 1 minuto
        const tiempoBloqueo = Date.now() + bloqueoPorMs;
        localStorage.setItem("bloqueo_hasta", tiempoBloqueo.toString());
        btnSubmit.disabled = true;
        const t = I18N.dict.login[lang] || I18N.dict.login["es"];
        errorLogin.textContent = `${t.demasiados_intentos || "Demasiados intentos. Espera 60 segundos."}`;

        setTimeout(() => {
          btnSubmit.disabled = false;
          errorLogin.textContent = "";
          localStorage.removeItem("bloqueo_hasta");
          localStorage.setItem("intentos_fallidos", "0");
        }, bloqueoPorMs);
      } else {
        const t = I18N.dict.login[lang] || I18N.dict.login["es"];
        errorLogin.textContent = `${data.error || t.error_login} (Intentos: ${intentos})`;
      }
    }
  } catch (error) {
    const lang = localStorage.getItem("lang") || "es";
    const t = I18N.dict.login[lang] || I18N.dict.login["es"];
    errorLogin.textContent = t.error_conexion || "Error de conexión. Intenta más tarde.";
  }
});

// Función para aplicar los textos según el idioma
function aplicarIdioma(lang) {
  const t = I18N.dict.login[lang] || I18N.dict.login['es'];
  document.getElementById("login-title").textContent = t.titulo;
  document.getElementById("correo").placeholder = t.correo;
  document.getElementById("password").placeholder = t.pass;
  btnSubmit.textContent = t.entrar;
  document.getElementById("link-olvidar").textContent = t.olvidar;
  document.getElementById("link-registrarse").textContent = t.registrar;
  document.getElementById("lang-select").value = lang;
}

document.addEventListener("DOMContentLoaded", () => {
  let lang = localStorage.getItem("lang") || (navigator.language || 'es').slice(0, 2);
  debugger;
  if (!I18N.dict.login[lang]) lang = 'es';
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

// Guardar país en cookie usando ipapi
fetch("https://ipapi.co/json/")
  .then(res => res.json())
  .then(data => {
    const pais = data.country || "AR"; // Código de país, ej: "AR", "IT", "ES"
    document.cookie = `pais=${encodeURIComponent(pais)}; path=/; max-age=${3600 * 24 * 7}`;
  })
  .catch(() => {
    document.cookie = `pais=AR; path=/; max-age=${3600 * 24 * 7}`; // Fallback por si falla
  });