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
            "mix_familiari": " 📊 Familia Mezla",          
            "tipos_mezcla": "🔀 Tipos de Mezcla",
            "materia_forma": "🧩 Materia Forma",
            "mallas": "🕸️ Mallas",
            "informes": "📋 Informes",
            "descargar_tabla_excel": "⬇️ Descargar tabla Excel",
            "macchine": "🛠️ Máquinas",
            "ver_macchine": "🔍 Ver Máquinas",            
            "crud_macchine": "📝 CRUD Máquinas",
            "conexion_sqlserver": "🔌 Conexión SQL Server",
            
            "Pannelli":"⚡ Paneles Solares",
            "Pannelli_Solari": "🔍 Ver Paneles",
            "crud_panelli": "📝 CRUD Paneles",
            "conexion_panelli": "🔌 Conexión IP dirección",
            
            
            
            
            
            # Pantalla /pantalla_usuarios/perfil_usuario.html
            "perfil_titulo": "Mi perfil",
            "perfil_correo": "Correo electrónico",
            "perfil_rol": "Rol general",
            "perfil_pais": "País",
            "perfil_idioma": "Idioma preferido",
            "perfil_estado": "Cuenta activa",
            "perfil_entidades": "Entidades asociadas",
            "perfil_rol_entidad": "Rol en la entidad",
            "perfil_sin_entidades": "No hay entidades asociadas.",
            "perfil_analisis": "Últimos análisis granulométricos",
            "perfil_sin_analisis": "No hay análisis registrados.",

           
            
            # Menú
            "titulo_composicion": "Composición de los agregados",
            "agregar": "Agregar",
            "nombre": "Nombre",
            "descripcion": "Descripción",
            "forma": "Forma",
            "origen": "Origen",
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
            "porcentaje": "Porcentaje (%)",
            
            
            
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
            "calcular_retenidos": "Calcular retenidos",
            "seleccionar_curva_target": "Seleccionar curva objetivo",
            "configurar_agregado": "Configurar agregado",
            "limpiar_tablas": "Limpiar Tablas",
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
            "mix_familiari": " 📊 Family Mix",         
            "componentes_quimicos": "⚗️ Chemical Components",
            "tipos_mezcla": "🔀 Mix Types",
            "materia_forma": "🧩 Matter Form",
            "mallas": "🕸️ Sieves",
            "informes": "📋 Reports",
            "descargar_tabla_excel": "⬇️ Download Excel Table",
            "macchine": "🛠️ Machines",           
            "ver_macchine": "🔍 View Machines",           
            "crud_macchine": "📝 CRUD Machines",
            "conexion_sqlserver": "🔌 SQL Server Connection",

            "Pannelli": "⚡ Solar Panels",
            "Pannelli_Solari": "🔍 View Panels",
            "crud_panelli": "📝 CRUD Panels",
            "conexion_panelli": "🔌 IP Address Connection",
            
            # Pantalla /pantalla_usuarios/perfil_usuario.html
            "perfil_titulo": "My profile",
            "perfil_correo": "Email address",
            "perfil_rol": "Global role",
            "perfil_pais": "Country",
            "perfil_idioma": "Preferred language",
            "perfil_estado": "Account status",
            "perfil_entidades": "Associated entities",
            "perfil_rol_entidad": "Role in entity",
            "perfil_sin_entidades": "No associated entities.",
            "perfil_analisis": "Latest granulometric analyses",
            "perfil_sin_analisis": "No analyses recorded.",

            
            
            
            
            "titulo_composicion": "Aggregate Composition",
            "agregar": "Add",
            "nombre": "Name",
            "descripcion": "Description",
            "forma": "Form",
            "origen": "Origin",
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
            "porcentaje": "Percentage (%)",
            
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
            "calcular_retenidos": "Calculate Retained",
            "seleccionar_curva_target": "Select Target Curve",
            "configurar_agregado": "Configure Aggregate",
            "limpiar_tablas": "Clear Tables",
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
        "pt": {
                    "home": "🏠 Início",
                    "administracion": "⚙️ Administração",
                    "usuarios": "👥 Usuários",
                    "entidades": "🏢 Entidades",
                    "fuller": "📊 Fuller",
                    "test_fuller_multiple": "📐 Teste Fuller Múltiplo",
                    "simulador_dosificacion": "🧮 Simulador de Dosagem",
                    "agregados": "🧱 Agregados",
                    "mix_familiari": " 📊 Mistura Familiar", 
                    "componentes_quimicos": "⚛️ Componentes Químicos",
                    "tipos_mezcla": "🔀 Tipos de Mistura",
                    "materia_forma": "🧩 Forma da Matéria",
                    "mallas": "🕸️ Peneiras",
                    "informes": "📋 Relatórios",
                    "descargar_tabla_excel": "⬇️ Baixar tabela Excel",
                    "macchine": "🛠️ Máquinas",
                    "ver_macchine": "🔍 Ver Máquinas",                    
                    "crud_macchine": "📝 CRUD Máquinas",
                    "conexion_sqlserver": "🔌 Conexão SQL Server",
                    
                    "Pannelli": "⚡ Painéis Solares",
                    "Pannelli_Solari": "🔍 Ver Painéis",
                    "crud_panelli": "📝 CRUD Painéis",
                    # Pantalla /pantalla_usuarios/perfil_usuario.html
                    "perfil_titulo": "Meu perfil",
                    "perfil_correo": "E-mail",
                    "perfil_rol": "Função global",
                    "perfil_pais": "País",
                    "perfil_idioma": "Idioma preferido",
                    "perfil_estado": "Estado da conta",
                    "perfil_entidades": "Entidades associadas",
                    "perfil_rol_entidad": "Função na entidade",
                    "perfil_sin_entidades": "Nenhuma entidade associada.",
                    "perfil_analisis": "Últimas análises granulométricas",
                    "perfil_sin_analisis": "Nenhuma análise registrada.",


                    "titulo_composicion": "Composição dos agregados",
                    "agregar": "Adicionar",
                    "nombre": "Nome",
                    "descripcion": "Descrição",
                    "forma": "Forma",
                    "origen": "Origem",
                    "entidad": "Entidade",
                    "estado": "Estado",
                    "acciones": "Ações",
                    "perfil": "Meu perfil",
                    "rol": "Função",
                    "cambiar_contrasena": "Alterar senha",
                    "cerrar_sesion": "Encerrar sessão",
                    "mostrar_ocultar": "Mostrar / Ocultar",
                    "nombre_comercial": "Nome comercial",
                    "diametro": "Diâmetro (mm)",
                    "porcentaje": "Percentual (%)",
                    
                     # Pantalla /pantalla_agregados/modals/modal_agregar_agregado.html

                    "agregar_agregado": "Adicionar Agregado",
                    "seleccionar_estado": "Selecione um estado",
                    "activo": "Ativo",
                    "inactivo": "Inativo",

                    "titulo_mallas": "Peneiras Registradas",
                    "titulo_tipo_mezcla": "Tipos de Mistura Registrados",
                    "guardar_cambios": "Salvar Alterações",
                    "titulo_componentes_quimicos": "Componentes Químicos Registrados",
                    "tipo_mezcla": "Tipo de Mistura",
                    "modificar": "Modificar",
                    "eliminar": "Excluir",
                    "seleccionar_tipo_mezcla": "Selecione o Tipo de Mistura",
                    "volver_lista": "Voltar à lista",
                    "pais": "País",
                    "idioma": "Idioma",
                    "mallas_asociadas": "Peneiras associadas",
                    "porcentaje": "Percentual (%)",
                    "orden": "Ordem",
                    "malla": "peneira",
                    "componente": "componente",
                    "al_agregado": "ao Agregado",
                    "seleccionar_malla": "Selecionar peneira:",
                    "elegir_malla": "Escolha uma peneira",
                    "cerrar": "Fechar",
                    "seleccionar_componente": "Selecionar componente:",
                    "elegir_componente": "Escolha um componente",
                    "simulador_titulo": "🔧 Simulador manual de mistura (modo planta)",
                    "simular_mezcla": "Simular mistura",
                    "resultado_simulador": "Resultado da simulação",

                    "exportar_analisis": "Exportar análise",
                    "descargar_csv": "Você pode baixar a análise atual como CSV.",
                    "exportar_csv": "Exportar CSV",
                    "titulo_densidad_fuller_multiple": "Cálculo de misturas múltiplas – Curva de Fuller",
                    "agregar_aggregato": "Adicionar agregado",
                    "equivalencias_crivelli": "Equivalências de peneiras",
                    "calcular_todas": "Calcular todas",
                    "calcular_retenidos": "Calcular retidos",
                    "seleccionar_curva_target": "Selecionar curva alvo",
                    "configurar_agregado": "Configurar agregado",
                    "limpiar_tablas": "Limpar Tabelas",
                    "titulo_curva_optima": "Curva Ótima Corrigida vs. Fuller e Média",
                    "guardar_seleccion": "Salvar seleção",
                    "configuracion_parametros": "Configuração de Parâmetros",
                    "seleccionar_norma": "Selecione país / norma de referência:",
                    "norma_argentina": "Argentina (Norma IRAM – Concreto)",
                    "norma_italiana": "Itália (UNI – Granulometria)",
                    "norma_personalizada": "Personalizado",
                    "dmax": "dmax (mm):",
                    "exponente_n": "Expoente n:",
                    "guardar": "Salvar",
                    "tabla_parametros_tamices": "Tabela de Parâmetros de Peneiras",
                    "tamiz_comercial": "Peneira comercial",

                    "recuperar_link_texto": "[link no seu e‑mail]",
                    "recuperar_titulo": "Recuperar senha",
                    "recuperar_subtitulo": "Digite seu e-mail e enviaremos um link.",
                    "recuperar_asunto": "Recuperação de senha",
                    "recuperar_mensaje": "Clique neste link para redefinir sua senha: {link}",
                    "enviar": "Enviar",
                    "error_confirmacion": "As senhas não coincidem ou são inválidas.",
                    "nueva_pass": "Nova senha",
                    "confirmar_pass": "Confirmar senha",
                    "restablecer": "Redefinir",
                    "token_invalido": "O link é inválido ou expirou.",
                    "restablecer_ok": "Senha atualizada com sucesso.",
                    "saludo": "Olá",
                    "recuperacion": "Recebemos uma solicitação para redefinir sua senha.",
                    "firma": "Se não foi você, ignore. Se foi, continue em",
                    "entrar": "Entrar",
                    "criterios": {
                        "min": "Mínimo 8 caracteres",
                        "mayus": "Uma letra maiúscula",
                        "num": "Um número",
                        "esp": "Um caractere especial (!@#$...)"
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
            "mix_familiari": " 📊 Mix Familiari", 
            "componentes_quimicos": "⚗️ Componente Chimico",
            "tipos_mezcla": "🔀 Tipi Miscela",
            "materia_forma": "🧩 Materia Forma",
            "mallas": "🕸️ Maglie",
            "informes": "📋 Report",
            "descargar_tabla_excel": "⬇️ Scarica tabella Excel",
            "macchine": "🛠️ Macchine",           
            "ver_macchine": "🔍 Vedi Macchine",            
            "crud_macchine": "📝 CRUD Macchine",
            "conexion_sqlserver": "🔌 Connessione SQL Server",
            
            "Pannelli": "⚡ Pannelli Solari",
            "Pannelli_Solari": "🔍 Vedi Pannelli",
            "crud_panelli": "📝 CRUD Pannelli",
            "conexion_panelli": "🔌 Connessione Indirizzo IP",

            # Pantalla /pantalla_usuarios/perfil_usuario.html
            "perfil_titulo": "Il mio profilo",
            "perfil_correo": "Indirizzo e-mail",
            "perfil_rol": "Ruolo globale",
            "perfil_pais": "Paese",
            "perfil_idioma": "Lingua preferita",
            "perfil_estado": "Stato dell'account",
            "perfil_entidades": "Entità associate",
            "perfil_rol_entidad": "Ruolo nell'entità",
            "perfil_sin_entidades": "Nessuna entità associata.",
            "perfil_analisis": "Ultime analisi granulometriche",
            "perfil_sin_analisis": "Nessuna analisi registrata.",

            
            
            
            "titulo_composicion": "Composizione degli aggregati",
            "agregar": "Aggiungi",
            "nombre": "Nome",
            "descripcion": "Descrizione",
            "forma": "Forma",
            "origen": "Origine",
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
            "porcentaje": "Percentuale (%)",
            
            
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
            "calcular_retenidos": "Calcola trattenuti",
            "seleccionar_curva_target": "Seleziona la curva target",
            "configurar_agregado": "Configura Aggregato",
            "limpiar_tablas": "Pulisci Tabelle",
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
            "error": "Error interno del servidor.",  # es
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
            "error": "Internal server error." ,      # en
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
            "error": "Errore interno del server.",   # it
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
        },
        "pt": {
            "recuperar_link_texto": "[link no seu e-mail]",
            "recuperar_titulo": "Recuperar senha",
            "recuperar_subtitulo": "Digite seu e-mail e enviaremos um link.",
            "recuperar_asunto": "Recuperação de senha",
            "recuperar_mensaje": "Clique neste link para redefinir sua senha: {link}",
            "enviar": "Enviar",
            "error": "Erro interno do servidor.",    # pt
            "error_confirmacion": "As senhas não coincidem ou não atendem aos requisitos.",
            "nueva_pass": "Nova senha",
            "confirmar_pass": "Confirmar senha",
            "restablecer": "Redefinir",
            "token_invalido": "O link é inválido ou expirou.",
            "restablecer_ok": "Senha atualizada com sucesso.",
            "saludo": "Olá",
            "recuperacion": "Recebemos uma solicitação para redefinir sua senha.",
            "firma": "Se não foi você, ignore esta mensagem. Se foi, continue em",
            "entrar": "Entrar",
            "criterios": {
                "min": "Mínimo de 8 caracteres",
                "mayus": "Uma letra maiúscula",
                "num": "Um número",
                "esp": "Um caractere especial (!@#$...)"
            }
        }

    }
    return textos_login.get(lang, textos_login["es"])



def obtener_textos_confirmacion(lang):
    textos = {
        "es": {
            "asunto": "Confirma tu cuenta",
            "saludo": "Hola 👋",
            "registro": "Gracias por registrarte en Gervasi.",
            "confirma": "Confirmá tu cuenta haciendo clic en el siguiente enlace:",
            "accion": "Una vez confirmada, podés iniciar sesión en"
        },
        "en": {
            "asunto": "Confirm your account",
            "saludo": "Hi 👋",
            "registro": "Thanks for signing up with Gervasi.",
            "confirma": "Please confirm your account by clicking the link below:",
            "accion": "Once confirmed, you can log in at"
        },
        "it": {
            "asunto": "Conferma il tuo account",
            "saludo": "Ciao 👋",
            "registro": "Grazie per esserti registrato su Gervasi.",
            "confirma": "Conferma il tuo account cliccando sul seguente link:",
            "accion": "Una volta confermato, puoi accedere da"
        },
        "pt": {
            "asunto": "Confirme sua conta",
            "saludo": "Olá 👋",
            "registro": "Obrigado por se registrar na Gervasi.",
            "confirma": "Confirme sua conta clicando no link abaixo:",
            "accion": "Uma vez confirmada, você pode fazer login em"
        }
    }
    return textos.get(lang, textos["es"])


def get_textos_confirmacion(lang):
    base = {
        "titulo": "Cuenta confirmada",
        "mensaje": "Tu cuenta ha sido activada con éxito.",
        "boton": "Ir al inicio",
        "redireccion": "Serás redirigido en"
    }
    textos = {
        "es": base,
        "en": {
            **base,
            "titulo": "Account confirmed",
            "mensaje": "Your account has been successfully activated.",
            "boton": "Go to homepage",
            "redireccion": "You will be redirected in"
        },
        "it": {
            **base,
            "titulo": "Account confermato",
            "mensaje": "Il tuo account è stato attivato con successo.",
            "boton": "Vai alla home",
            "redireccion": "Verrai reindirizzato tra"
        },
        "pt": {
            **base,
            "titulo": "Conta confirmada",
            "mensaje": "Sua conta foi ativada com sucesso.",
            "boton": "Ir para a página inicial",
            "redireccion": "Você será redirecionado em"
        }
    }
    return textos.get(lang, base)

def get_textos_menu_confirmacion_entidad(lang):
    textos = {
        "es": {
            "titulo": "Seleccionar Entidad",
            "selecciona": "Selecciona tu entidad",
            "entidad": "Entidad",
            "confirmar": "Confirmar"
        },
        "en": {
            "titulo": "Select Entity",
            "selecciona": "Select your entity",
            "entidad": "Entity",
            "confirmar": "Confirm"
        },
        "it": {
            "titulo": "Seleziona Entità",
            "selecciona": "Seleziona la tua entità",
            "entidad": "Entità",
            "confirmar": "Conferma"
        },
        "pt": {
            "titulo": "Selecionar Entidade",
            "selecciona": "Selecione sua entidade",
            "entidad": "Entidade",
            "confirmar": "Confirmar"
        }
    }
    return textos.get(lang, textos["es"])