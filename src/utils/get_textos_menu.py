# src/utils/get_textos_menu.py
def get_textos_menu(lang="es"):
    textos = {
        "es": {
            
             # Pantalla /layouts/layout.html 
            "home": "🏠 Inicio",
            "administracion": "⚙️ Administración",
            "usuarios": "👥 Usuarios",
            "entidades": "🏢 Entidades",
            "fuller": "📊 Fuller",
            "test_fuller_multiple": "🔬 Test Fuller Múltiple",
            "simulador_dosificacion": "🧮 Simulador Dosificación",
            "agregados": "🧱 Agregados",
            "componentes_quimicos": "⚗️ Componentes químicos",
            "tipos_mezcla": "🔀 Tipos de Mezcla",
            "mallas": "🕸️ Mallas",
            "informes": "📋 Informes",
            "descargar_tabla_excel": "⬇️ Descargar tabla Excel",
            "macchine": "🛠️ Máquinas",
            "ver_macchine": "🔍 Ver Máquinas",
            "crud_macchine": "📝 CRUD Máquinas",
            "conexion_sqlserver": "🔌 Conexión SQL Server",

            
            
            
            
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
            
            
            
            # Pantalla /pantalla_agregados/modals/modal_agregar_agregado.html
            "agregar_agregado": "Agregar Agregado",
            "seleccionar_estado": "Selecciona un estado",
            "activo": "Activo",
            "inactivo": "Inactivo",
            
            
            
            
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
            "componentes_quimicos": "⚗️Componentes químicos",
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

            # Pantalla /autoDensidad/simuladorDosificacion.html
            "simulador_titulo": "🔧 Simulador de miscelación manual (modo planta)",
            "simular_mezcla": "Simular la mezcla",
            "resultado_simulador": "Resultado de la simulación",

            # Pantalla /autoDensidad/densidadFullerMultiple.html
            "exportar_analisis": "Exportar análisis",
            "descargar_csv": "Podés descargar el análisis actual como CSV.",
            "exportar_csv": "Exportar CSV",
            "titulo_densidad_fuller_multiple": "Cálculo de mezclas múltiples - Curva de Fuller",  # español
            "agregar_aggregato": "Agregar agregado",
            "equivalencias_crivelli": "Equivalencias de tamices",
            "calcular_todas": "Calcular todas",
            "seleccionar_curva_target": "Seleccionar curva objetivo",
            "configurar_agregado": "Configurar agregado",
            "titulo_curva_optima": "Curva Óptima Corregida vs. Fuller y Promedio",
            "guardar_seleccion": "Guardar selección",
            "configuracion_parametros": "Configuración de Parámetros",
            "seleccionar_norma": "Seleccioná el país / norma de referencia:",
            "norma_argentina": "Argentina (Norma IRAM - Hormigón)",
            "norma_italiana": "Italia (UNI - Granulometría)",
            "norma_personalizada": "Personalizado",
            "dmax": "dmax (mm):",
            "exponente_n": "Exponente n:",
            "guardar": "Guardar",
            "tabla_parametros_tamices": "Tabla de Parámetros Tamices",
            "tamiz_comercial": "Tamiz comercial",

            


            
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
            # Pantalla /layouts/layout.html 
            "home": "🏠 Home",
            "administracion": "⚙️ Admin",
            "usuarios": "👥 Users",
            "entidades": "🏢 Entities",
            "fuller": "📊 Fuller",
            "test_fuller_multiple": "🧪 Fuller Multiple Test",
            "simulador_dosificacion": "🧮 Mixing Simulator",
            "agregados": "🧱 Aggregates",
            "componentes_quimicos": "⚗️ Chemical Components",
            "tipos_mezcla": "🔀 Mix Types",
            "mallas": "🕸️ Sieves",
            "informes": "📋 Reports",
            "descargar_tabla_excel": "⬇️ Download Excel Table",
            "macchine": "🛠️ Machines",
            "ver_macchine": "🔍 View Machines",
            "crud_macchine": "📝 CRUD Machines",
            "conexion_sqlserver": "🔌 SQL Server Connection",

            
            
            
            
            
            
            
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
            
             # Pantalla /pantalla_agregados/modals/modal_agregar_agregado.html
            "agregar_agregado": "Add Aggregate",
            "seleccionar_estado": "Select a state",
            "activo": "Active",
            "inactivo": "Inactive",

            
            
            
            
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

            # Pantalla /autoDensidad/simuladorDosificacion.html
            "simulador_titulo": "🔧 Manual Mixing Simulator (plant mode)",
            "simular_mezcla": "Simulate Mixing",
            "resultado_simulador": "Simulation Result",

            # Pantalla /autoDensidad/densidadFullerMultiple.html
            "exportar_analisis": "Export Analysis",
            "descargar_csv": "You can download the current analysis as CSV.",
            "exportar_csv": "Export CSV",
            "titulo_densidad_fuller_multiple": "Calculation of multiple mixes - Fuller curve",  # inglés
            "agregar_aggregato": "Add Aggregate",
            "equivalencias_crivelli": "Sieve Equivalences",
            "calcular_todas": "Calculate All",
            "seleccionar_curva_target": "Select Target Curve",
            "configurar_agregado": "Configure Aggregate",
            "titulo_curva_optima": "Optimal Corrected Curve vs. Fuller and Average",
            "guardar_seleccion": "Save selection",
            "configuracion_parametros": "Parameter Configuration",
            "seleccionar_norma": "Select country / reference standard:",
            "norma_argentina": "Argentina (IRAM Standard - Concrete)",
            "norma_italiana": "Italy (UNI - Granulometry)",
            "norma_personalizada": "Custom",
            "dmax": "dmax (mm):",
            "exponente_n": "Exponent n:",
            "guardar": "Save",
            "tabla_parametros_tamices": "Sieve Parameter Table",
            "tamiz_comercial": "Commercial Sieve",



            
            
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
            # Pantalla /layouts/layout.html 
            "home": "🏠 Home",
            "administracion": "⚙️ Amministrazione",
            "usuarios": "👥 Utenti",
            "entidades": "🏢 Entità",
            "fuller": "📊 Fuller",
            "test_fuller_multiple": "🧪 Test Fuller Multiplo",
            "simulador_dosificacion": "🧮 Simulatore Dosaggio",
            "agregados": "🧱 Aggregati",
            "componentes_quimicos": "⚗️ Componente Chimico",
            "tipos_mezcla": "🔀 Tipi Miscela",
            "mallas": "🕸️ Maglie",
            "informes": "📋 Report",
            "descargar_tabla_excel": "⬇️ Scarica tabella Excel",
            "macchine": "🛠️ Macchine",
            "ver_macchine": "🔍 Vedi Macchine",
            "crud_macchine": "📝 CRUD Macchine",
            "conexion_sqlserver": "🔌 Connessione SQL Server",

            
            
            
            
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
            
            
             # Pantalla /pantalla_agregados/modals/modal_agregar_agregado.html
            "agregar_agregado": "Aggiungi Aggregato",
            "seleccionar_estado": "Seleziona uno stato",
            "activo": "Attivo",
            "inactivo": "Inattivo",

            
            
            
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

             # Pantalla /autoDensidad/simuladorDosificacion.html
            "simulador_titulo": "🔧 Simulatore di miscelazione manuale (modalità impianto)",
            "simular_mezcla": "Simula Miscelazione",
            "resultado_simulador": "Risultato della simulazione",
            
            
            
            # Pantalla /autoDensidad/densidadFullerMultiple.html
            "exportar_analisis": "Esporta analisi",
            "descargar_csv": "Puoi scaricare l'analisi attuale in formato CSV.",
            "exportar_csv": "Esporta CSV",
            "titulo_densidad_fuller_multiple": "Calcolo di miscele multiple - Curva di Fuller",  # italiano
            "agregar_aggregato": "Aggiungi Aggregato",
            "equivalencias_crivelli": "Equivalenze dei crivelli",
            "calcular_todas": "Calcola tutte",
            "seleccionar_curva_target": "Seleziona la curva target",
            "configurar_agregado": "Configura Aggregato",
            "titulo_curva_optima": "Curva Ottimale Corretta vs. Fuller e Media",
            "guardar_seleccion": "Salva selezione",
            "configuracion_parametros": "Configurazione Parametri",
            "seleccionar_norma": "Seleziona paese / norma di riferimento:",
            "norma_argentina": "Argentina (Norma IRAM - Calcestruzzo)",
            "norma_italiana": "Italia (UNI - Granulometria)",
            "norma_personalizada": "Personalizzato",
            "dmax": "dmax (mm):",
            "exponente_n": "Esponente n:",
            "guardar": "Salva",
            "tabla_parametros_tamices": "Tabella dei Parametri dei Crivelli",
            "tamiz_comercial": "Crivello commerciale",



            
            
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

