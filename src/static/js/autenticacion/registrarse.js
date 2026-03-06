function aplicarIdioma(lang) {
  const msgs = I18N.dict?.registrarse?.[lang] || I18N.dict?.registrarse?.["es"];
  if (!msgs) return;
  document.getElementById("registro-title").textContent = msgs.titulo;
  document.getElementById("correo").placeholder = msgs.correo;
  document.getElementById("password").placeholder = msgs.pass;
  document.getElementById("repetir").placeholder = msgs.repetir;
  document.getElementById("captcha-text").textContent = msgs.captcha;
  document.getElementById("btn-registrarse").textContent = msgs.registrarse;
  document.getElementById("volver-login").textContent = msgs.volver;
}

function togglePassword(id) {
  const input = document.getElementById(id);
  input.type = input.type === "password" ? "text" : "password";
}

function validarFormulario() {
  const lang = localStorage.getItem("lang") || "es";
  const t = I18N.dict?.registrarse?.[lang] || I18N.dict?.registrarse?.["es"];
  const correo = document.getElementById("correo");
  const pass = document.getElementById("password");
  const repetir = document.getElementById("repetir");
  const captcha = document.getElementById("captcha-check").checked;
  const btn = document.getElementById("btn-registrarse");

  const val = pass.value;
  const length = val.length >= 8;
  const mayus = /[A-Z]/.test(val);
  const num = /[0-9]/.test(val);
  const especial = /[!@#$%^&*(),.?":{}|<>]/.test(val);
  const passValida = length && mayus && num && especial;
  const coinciden = val === repetir.value;

  document.getElementById("req-length").textContent = `${length ? "🟢" : "🔴"} ${t.requisitos.longitud}`;
  document.getElementById("req-mayus").textContent = `${mayus ? "🟢" : "🔴"} ${t.requisitos.mayus}`;
  document.getElementById("req-num").textContent = `${num ? "🟢" : "🔴"} ${t.requisitos.numero}`;
  document.getElementById("req-especial").textContent = `${especial ? "🟢" : "🔴"} ${t.requisitos.especial}`;

  correo.classList.toggle("is-invalid", !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo.value));
  pass.classList.toggle("is-invalid", val.length > 0 && !passValida);
  repetir.classList.toggle("is-invalid", repetir.value.length > 0 && !coinciden);

  btn.disabled = !(correo.value && passValida && coinciden && captcha);
}

const requisitos = document.getElementById("requisitos-pass");
document.getElementById("password").addEventListener("input", e => {
  requisitos.style.display = e.target.value.length > 0 ? "block" : "none";
});

document.addEventListener("DOMContentLoaded", () => {
  const lang = localStorage.getItem("lang") || "es";
  aplicarIdioma(lang);
  validarFormulario(); // aseguro que arranca desactivado

  // Eventos para inputs
  document.querySelectorAll("#correo, #password, #repetir, #captcha-check").forEach(el =>
    el.addEventListener("input", validarFormulario)
  );

  document.getElementById("form-registro").addEventListener("submit", function (e) {
    e.preventDefault();
    const lang = localStorage.getItem("lang") || "es";
    const t = I18N.dict?.registrarse?.[lang] || I18N.dict?.registrarse?.["es"];

    const correo = document.getElementById("correo").value.trim();
    const password = document.getElementById("password").value;
    const repetir = document.getElementById("repetir").value;
    const captcha = document.getElementById("captcha-check").checked;
    const errorDiv = document.getElementById("error-registro");

    const errores = [];

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)) errores.push(t.errores.correo);
    if (password.length < 8) errores.push(t.errores.longitud);
    if (!/[A-Z]/.test(password)) errores.push(t.errores.mayus);
    if (!/[0-9]/.test(password)) errores.push(t.errores.numero);
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) errores.push(t.errores.especial);
    if (password !== repetir) errores.push(t.errores.coinciden);
    if (!captcha) errores.push(t.errores.captcha);

    if (errores.length > 0) {
          errorDiv.innerHTML = errores.map(e => `<div>⚠️ ${e}</div>`).join("");
      return;
    }

    fetch("/api/registrar_usuario/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ correo_electronico: correo, password , lang : lang})
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
           localStorage.setItem("registro_email", correo); // ⬅ necesario para reenviar
           document.cookie = `lang=${lang}; path=/`;
           window.location.href = "/verifica_email/";
        } else {
          errorDiv.textContent = data.error || I18N.t('login.error_servidor') || "Error desconocido.";
        }
      })
      .catch(() => {
        errorDiv.textContent = I18N.t('login.error_conexion') || "Error de red o servidor.";
      });
  });

  // Manejo de cambio de idioma (si tienes un selector)
  const langSelect = document.getElementById("lang-select");
  if (langSelect) {
    langSelect.value = lang;
    langSelect.addEventListener("change", function () {
      const selectedLang = this.value;
      localStorage.setItem("lang", selectedLang);
      document.cookie = `lang=${selectedLang}; path=/`;
      aplicarIdioma(selectedLang);
      validarFormulario();
    });
  }
});