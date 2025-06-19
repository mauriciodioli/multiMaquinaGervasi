//workspaces/multiMaquinaGervasi/src/static/js/autenticacion/registrarse.js


function aplicarIdioma(lang) {
  const t = mensajes[lang] || mensajes["es"];
  document.getElementById("registro-title").textContent = t.titulo;
  document.getElementById("correo").placeholder = t.correo;
  document.getElementById("password").placeholder = t.pass;
  document.getElementById("repetir").placeholder = t.repetir;
  document.getElementById("captcha-text").textContent = t.captcha;
  document.getElementById("btn-registrarse").textContent = t.registrarse;
  document.getElementById("volver-login").textContent = t.volver;
}

function togglePassword(id) {
  const input = document.getElementById(id);
  input.type = input.type === "password" ? "text" : "password";
}

function validarFormulario() {
  const lang = localStorage.getItem("lang") || "es";
  const t = mensajes[lang];

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
  const t = mensajes[lang];

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
         const lang = localStorage.getItem("lang") || "es";
         document.cookie = `lang=${lang}; path=/`;
         window.location.href = "/verifica_email/";
      } else {
        errorDiv.textContent = data.error || "Error desconocido.";
      }
    })
    .catch(() => {
      errorDiv.textContent = "Error de red o servidor.";
    });
});

});







const mensajes = {
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
