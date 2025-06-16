# src/utils/get_textos_menu.py

def get_textos_menu(lang="es"):
    textos_menu = {
        "es": {
            "perfil": "Mi perfil",
            "rol": "Rol",
            "cambiar_contrasena": "Cambiar contraseña",
            "cerrar_sesion": "Cerrar sesión"
        },
        "en": {
            "perfil": "My profile",
            "rol": "Role",
            "cambiar_contrasena": "Change password",
            "cerrar_sesion": "Log out"
        },
        "it": {
            "perfil": "Il mio profilo",
            "rol": "Ruolo",
            "cambiar_contrasena": "Cambia password",
            "cerrar_sesion": "Esci"
        }
    }
    return textos_menu.get(lang, textos_menu["es"])

def get_textos_login(lang="es"):
    textos_login = {
        "es": {
            "recuperar_titulo": "Recuperar contraseña",
            "recuperar_subtitulo": "Ingresá tu correo y te enviaremos un enlace.",
            "recuperar_asunto": "Recuperación de contraseña",
            "recuperar_mensaje": "Hacé clic en este enlace para restablecer tu contraseña: {link}",
            "enviar": "Enviar",
            "error_confirmacion": "Las contraseñas no coinciden o no cumplen requisitos.",
            "nueva_pass": "Nueva contraseña",
            "confirmar_pass": "Confirmar contraseña",
            "restablecer": "Restablecer",
            "token_invalido": "El enlace es inválido o ha expirado.",
            "restablecer_ok": "Contraseña actualizada exitosamente.",
            "saludo": "Hola",
            "recuperacion": "Recibimos una solicitud para restablecer tu contraseña.",
            "firma": "Si no fuiste vos, ignorá este mensaje. Si fuiste vos, continuá en"
        },
        "en": {
            "recuperar_titulo": "Recover password",
            "recuperar_subtitulo": "Enter your email and we will send you a link.",
            "recuperar_asunto": "Password recovery",
            "recuperar_mensaje": "Click this link to reset your password: {link}",
            "enviar": "Send",
            "error_confirmacion": "Passwords do not match or are invalid.",
            "nueva_pass": "New password",
            "confirmar_pass": "Confirm password",
            "restablecer": "Reset",
            "token_invalido": "The link is invalid or has expired.",
            "restablecer_ok": "Password successfully updated.",
            "saludo": "Hello",
            "recuperacion": "We received a request to reset your password.",
            "firma": "If it wasn't you, ignore this. If it was, continue on"
        },
        "it": {
            "recuperar_titulo": "Recupera password",
            "recuperar_subtitulo": "Inserisci la tua email e ti invieremo un link.",
            "recuperar_asunto": "Recupero password",
            "recuperar_mensaje": "Clicca su questo link per reimpostare la tua password: {link}",
            "enviar": "Invia",
            "error_confirmacion": "Le password non coincidono o non sono valide.",
            "nueva_pass": "Nuova password",
            "confirmar_pass": "Conferma password",
            "restablecer": "Reimposta",
            "token_invalido": "Il link non è valido o è scaduto.",
            "restablecer_ok": "Password aggiornata correttamente.",
            "saludo": "Ciao",
            "recuperacion": "Abbiamo ricevuto una richiesta per reimpostare la tua password.",
            "firma": "Se non sei stato tu, ignora questo messaggio. Altrimenti continua su"
        }
    }
    return textos_login.get(lang, textos_login["es"])
