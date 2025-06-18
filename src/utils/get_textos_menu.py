# src/utils/get_textos_menu.py
def get_textos_menu(lang="es"):
    textos = {
        "es": {
            # Menú
            "titulo_composicion": "Composición de los agregados",
            "agregar": "Agregar",
            "nombre": "Nombre",
            "descripcion": "Descripción",
            "entidad": "Entidad",
            "estado": "Estado",
            "acciones": "Acciones",
            "perfil": "Mi perfil",
            "rol": "Rol",
            "cambiar_contrasena": "Cambiar contraseña",
            "cerrar_sesion": "Cerrar sesión",
            "mostrar_ocultar": "Mostrar / Ocultar",
            "nombre_comercial": "Nombre comercial",
            "diametro": "Diámetro (mm)",
            
            
            # Pantalla  /pantalla_mallas/pantalla_mallas.html
            "titulo_mallas": "Mallas Registradas",

            
            
             # Pantalla /pantalla_tipo_mezcla/pantalla_tipo_mezcla.html
             "titulo_tipo_mezcla": "Tipos de Mezcla Registrados",

            
            
            
            # Pantalla /pantalla_componente_quimico/modals/modal_modificar_comp_quimico.html
             "guardar_cambios": "Guardar Cambios",

            # Pantalla /pantalla_componente_quimico/pantalla_componente_quimico.html
            "titulo_componentes_quimicos": "Componentes Químicos Registrados",
            "tipo_mezcla": "Tipo Mezcla",
            "modificar": "Modificar",
            "eliminar": "Eliminar",
            
            # Pantalla /pantalla_componente_quimico/modals/modal_tipo_mezla.html
            "seleccionar_tipo_mezcla": "Selecciona Tipo de Mezcla",


            
            
            # Pantalla /pantalla_agregados/agregado_detalle.html
           "volver_lista": "Volver a la lista",
            "pais": "País",
            "idioma": "Idioma",
            "mallas_asociadas": "Mallas asociadas",
            "componentes_quimicos": "Componentes químicos",
            "porcentaje": "Porcentaje (%)",
            "orden": "Orden",
            "malla": "malla",
            "componente": "componente",

            # Pantalla /pantalla_agregados/modals/modal_agregar_malla.html
            "al_agregado": "al Agregado",
            "seleccionar_malla": "Seleccionar malla:",
            "elegir_malla": "Seleccioná una malla",
            "cerrar": "Cerrar",
             # Pantalla /pantalla_agregados/agregado_detalle.html
            "seleccionar_componente": "Seleccionar componente:",
            "elegir_componente": "Seleccioná un componente",

            
            # Login / Recuperación
            "recuperar_link_texto": "[enlace en tu correo]",
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
            "firma": "Si no fuiste vos, ignorá este mensaje. Si fuiste vos, continuá en",
            "entrar": "Iniciar sesión",
            "criterios": {
                "min": "Mínimo 8 caracteres",
                "mayus": "Una letra mayúscula",
                "num": "Un número",
                "esp": "Un carácter especial (!@#$...)"
            }
        },
        "en": {
            "titulo_composicion": "Aggregate Composition",
            "agregar": "Add",
            "nombre": "Name",
            "descripcion": "Description",
            "entidad": "Entity",
            "estado": "Status",
            "acciones": "Actions",
            "perfil": "My profile",
            "rol": "Role",
            "cambiar_contrasena": "Change password",
            "cerrar_sesion": "Log out",
            "mostrar_ocultar": "Show / Hide",
            "nombre_comercial": "Trade name",
            "diametro": "Diameter (mm)",
            
            # Pantalla  /pantalla_mallas/pantalla_mallas.html
            "titulo_mallas": "Registered Sieves",

            
            
            
            
            # Pantalla /pantalla_tipo_mezcla/pantalla_tipo_mezcla.html
            "titulo_tipo_mezcla": "Registered Mixture Types",

            
            
            
              
            # Pantalla /pantalla_componente_quimico/pantalla_componente_quimico.html
           "titulo_componentes_quimicos": "Registered Chemical Components",
            "tipo_mezcla": "Mixture Type",
            "modificar": "Edit",
            "eliminar": "Delete",

            # Pantalla /pantalla_componente_quimico/modals/modal_modificar_comp_quimico.html
           "guardar_cambios": "Save Changes",
           
            # Pantalla /pantalla_componente_quimico/modals/modal_tipo_mezla.html
            "seleccionar_tipo_mezcla": "Select Mixture Type",
            
            
             # Pantalla /pantalla_agregados/agregado_detalle.html
            "volver_lista": "Back to the list",
            "pais": "Country",
            "idioma": "Language",
            "mallas_asociadas": "Associated sieves",
            "componentes_quimicos": "Chemical components",
            "porcentaje": "Percentage (%)",
            "orden": "Order",
            "malla": "sieve",
            "componente": "component",
            
            # Pantalla /pantalla_agregados/modals/modal_agregar_malla.html
            "al_agregado": "to the Aggregate",
            "seleccionar_malla": "Select sieve:",
            "elegir_malla": "Choose a sieve",
            "cerrar": "Close",
            
             # Pantalla /pantalla_agregados/modals/modal_agregar_comp_quimi.html
            "seleccionar_componente": "Select component:",
            "elegir_componente": "Choose a component",




            "recuperar_link_texto": "[link in your email]",
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
            "firma": "If it wasn't you, ignore this. If it was, continue on",
            "entrar": "Login",
            "criterios": {
                "min": "At least 8 characters",
                "mayus": "An uppercase letter",
                "num": "A number",
                "esp": "A special character (!@#$...)"
            }
        },
        "it": {
            "titulo_composicion": "Composizione degli aggregati",
            "agregar": "Aggiungi",
            "nombre": "Nome",
            "descripcion": "Descrizione",
            "entidad": "Entità",
            "estado": "Stato",
            "acciones": "Azioni",
            "perfil": "Il mio profilo",
            "rol": "Ruolo",
            "cambiar_contrasena": "Cambia password",
            "cerrar_sesion": "Esci",
            "mostrar_ocultar": "Mostra / Nascondi",
            "nombre_comercial": "Nome commerciale",
            "diametro": "Diametro (mm)",
            
            
            # Pantalla  /pantalla_mallas/pantalla_mallas.html
            "titulo_mallas": "Maglie Registrate",

            
            
            
            # Pantalla /pantalla_tipo_mezcla/pantalla_tipo_mezcla.html
            "titulo_tipo_mezcla": "Tipi di Miscela Registrati",

            
            
            
            
            
            # Pantalla /pantalla_componente_quimico/pantalla_componente_quimico.html
           "titulo_componentes_quimicos": "Componenti Chimici Registrati",
            "tipo_mezcla": "Tipo Miscela",
            "modificar": "Modificare",
            "eliminar": "Eliminare",

            # Pantalla /pantalla_componente_quimico/modals/modal_modificar_comp_quimico.html
            "guardar_cambios": "Salvare Modifiche",
            
            
            # Pantalla /pantalla_componente_quimico/modals/modal_tipo_mezla.html
            "seleccionar_tipo_mezcla": "Seleziona Tipo Miscela",

            # Pantalla /pantalla_agregados/agregado_detalle.html
           "volver_lista": "Torna alla lista",
            "pais": "Paese",
            "idioma": "Lingua",
            "mallas_asociadas": "Maglie associate",
            "componentes_quimicos": "Componenti chimici",
            "porcentaje": "Percentuale (%)",
            "orden": "Ordine",
            "malla": "maglia",
            "componente": "componente",

            # Pantalla /pantalla_agregados/modals/modal_agregar_malla.html
            "al_agregado": "all'Aggregato",
            "seleccionar_malla": "Seleziona maglia:",
            "elegir_malla": "Scegli una maglia",
            "cerrar": "Chiudi",


            # Pantalla /pantalla_agregados/modals/modal_agregar_comp_quimi.html
            "seleccionar_componente": "Seleziona componente:",
            "elegir_componente": "Scegli un componente",

            
            
            "recuperar_link_texto": "[link nella tua email]",
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
            "firma": "Se non sei stato tu, ignora questo messaggio. Altrimenti continua su",
            "entrar": "Accedi",
            "criterios": {
                "min": "Almeno 8 caratteri",
                "mayus": "Una lettera maiuscola",
                "num": "Un numero",
                "esp": "Un carattere speciale (!@#$...)"
            }
        }
    }

    return textos.get(lang, textos["es"])



def get_textos_login(lang="es"):
    textos_login = {
        "es": {
            "recuperar_link_texto": "[enlace en tu correo]",
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
            "firma": "Si no fuiste vos, ignorá este mensaje. Si fuiste vos, continuá en",
            "entrar": "Iniciar sesión",
            "criterios": {
                "min": "Mínimo 8 caracteres",
                "mayus": "Una letra mayúscula",
                "num": "Un número",
                "esp": "Un carácter especial (!@#$...)"
            }
        },
        "en": {
            "recuperar_link_texto": "[link in your email]",
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
            "firma": "If it wasn't you, ignore this. If it was, continue on",
            "entrar": "Login",
            "criterios": {
                "min": "At least 8 characters",
                "mayus": "An uppercase letter",
                "num": "A number",
                "esp": "A special character (!@#$...)"
            }
        },
        "it": {
            "recuperar_link_texto": "[link nella tua email]",
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
            "firma": "Se non sei stato tu, ignora questo messaggio. Altrimenti continua su",
            "entrar": "Accedi",
            "criterios": {
                "min": "Almeno 8 caratteri",
                "mayus": "Una lettera maiuscola",
                "num": "Un numero",
                "esp": "Un carattere speciale (!@#$...)"
            }
        }
    }
    return textos_login.get(lang, textos_login["es"])

