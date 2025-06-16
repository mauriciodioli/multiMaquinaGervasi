# src/utils/textos.py

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
