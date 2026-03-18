// i18n.js — módulo único con namespaces: login., registrarse., verificar., sim.
const I18N = (() => {
  // --- Diccionario central ---
  const dict = {
    sim: {
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
        data_error: "❌ Błąd: niekompletne lub nieprawidłowe dane.",
        prop_titulo: "Proporcje mieszanki (%)",
        prop_cerrar: "Zamknij",
        prop_instruccion: "Wpisz % każdego agregatu. Suma musi wynosić 100%.",
        prop_total: "Razem:",
        prop_usar_valores: "Użyj wartości",
        retido_titulo: "Krzywa % Kumulacyjny zatrzymany",
        retido_tabla1_titulo: "Granulometria ważona dwa agregaty",
        retido_tabla1_col1: "#",
        retido_tabla1_col2: "%",
        retido_tabla2_titulo: "Zalecane zakresy granulometryczne",
        retido_tabla2_col1: "Sita",
        retido_tabla2_col2: "Blok",
        retido_tabla2_col3: "Paver",
        retido_tabla2_col4: "Lim. Inf.",
        retido_tabla2_col5: "Lim. Sup.",
        retido_tabla2_nota: "Wartości w % kumulacyjnie zatrzymane.",
        btn_cerrar: "Zamknij",
        btn_consumo: "Krzywa zużycia",
        ensayos_titulo: "Badania: Stosunek Agregat/Cement (A/C) vs Wytrzymałość (MPa)",
        ensayos_resistencia_label: "Docelowa wytrzymałość (MPa)",
        ensayos_masa_label: "Całkowita masa kruszyw na m³ (kg)",
        ensayos_tabla_label: "Punkty badań (A/C, MPa)",
        ensayos_tabla_col1: "A/C",
        ensayos_tabla_col2: "MPa",
        ensayos_btn_agregar: "+ Dodaj punkt",
        ensayos_resultado_titulo: "Wynik (dla docelowej MPa)",
        ensayos_btn_cancelar: "Anuluj",
        ensayos_btn_calcular: "Oblicz",
        consumo_trazo_label: "Wymagany stosunek (A/C):",
        consumo_cemento_label: "Cement:",
        consumo_por_label: "na",
        consumo_kg_agregados: "kg kruszyw",
        prop_error_suma_100: "Suma musi wynosić dokładnie 100%.",
        chart_label_ensayos: "Testy",
        chart_label_ajuste: "Dopasowanie y = a·ln(x) + b",
        chart_axis_x: "Stosunek A/C (kruszyw/cementu)",
        chart_axis_y: "Wytrzymałość (MPa)",
        btn_eliminar: "Usunąć",
        nuevo_producto: "Nowy Produkt",
        mezcla_eliminada: "🗑 Mieszanka \"{nombre}\" całkowicie usunięta.",
        error_sin_tablas: "Brak załadowanych tabel w localStorage."
      },
      resultado_simulador: {
        titulo: "Wynik symulacji",
        zona_gruesa: "Strefa gruba:",
        zona_media: "Strefa średnia:",
        zona_fina: "Strefa drobna:",
        recomendacion: "🔎 Rekomendacja:",
        btn_ocultar: "❌ Ukryj wynik"
      },
      simulador_dosificacion: {
        grafico_alt: "Krzywa wynikowa vs Fuller",
        error_proporciones: "⚠️ Proporcje muszą dodawać się do 100%",
        error_procesar: "❌ Błąd przetwarzania mieszanki"
      }
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
        data_error: "❌ Error: datos incompletos o mal formateados.",
        prop_titulo: "Proporciones de la mezcla (%)",
        prop_cerrar: "Cerrar",
        prop_instruccion: "Ingresá el % de cada agregado. La suma debe ser 100%.",
        prop_total: "Total:",
        prop_usar_valores: "Usar valores",
        retido_titulo: "Curva % Retido Acumulado",
        retido_tabla1_titulo: "Granulometría ponderada dos agregados",
        retido_tabla1_col1: "#",
        retido_tabla1_col2: "%",
        retido_tabla2_titulo: "Faixas granulométricas recomendadas",
        retido_tabla2_col1: "Peneira",
        retido_tabla2_col2: "Bloco",
        retido_tabla2_col3: "Paver",
        retido_tabla2_col4: "Lim. Inf.",
        retido_tabla2_col5: "Lim. Sup.",
        retido_tabla2_nota: "Valores en % de retido acumulado.",
        btn_cerrar: "Cerrar",
        btn_consumo: "Curva de consumo",
        ensayos_titulo: "Ensayos: Relación Agregado/Cemento (A/C) vs Resistencia (MPa)",
        ensayos_resistencia_label: "Resistencia objetivo (MPa)",
        ensayos_masa_label: "Masa total de agregados por m³ (kg)",
        ensayos_tabla_label: "Puntos de ensayo (A/C, MPa)",
        ensayos_tabla_col1: "A/C",
        ensayos_tabla_col2: "MPa",
        ensayos_btn_agregar: "+ Agregar punto",
        ensayos_resultado_titulo: "Resultado (para la MPa objetivo)",
        ensayos_btn_cancelar: "Cancelar",
        ensayos_btn_calcular: "Calcular",
        consumo_trazo_label: "Trazo requerido (A/C):",
        consumo_cemento_label: "Cemento:",
        consumo_por_label: "por",
        consumo_kg_agregados: "kg de agregados",
        prop_error_suma_100: "La suma debe ser exactamente 100%.",
        chart_label_ensayos: "Ensayos",
        chart_label_ajuste: "Ajuste y = a·ln(x) + b",
        chart_axis_x: "Relación A/C (agregado/cemento)",
        chart_axis_y: "Resistencia (MPa)",
        btn_eliminar: "Eliminar",
        nuevo_producto: "Nuevo Producto",
        mezcla_eliminada: "🗑 Mezcla \"{nombre}\" eliminada completamente.",
        error_sin_tablas: "No hay tablas cargadas en localStorage."
      },
      resultado_simulador: {
        titulo: "Resultado de simulación",
        zona_gruesa: "Zona gruesa:",
        zona_media: "Zona media:",
        zona_fina: "Zona fina:",
        recomendacion: "🔎 Recomendación:",
        btn_ocultar: "❌ Ocultar resultado"
      },
      simulador_dosificacion: {
        grafico_alt: "Curva resultante vs Fuller",
        error_proporciones: "⚠️ Las proporciones deben sumar 100%",
        error_procesar: "❌ Error al procesar la mezcla"
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
        data_error: "❌ Error: incomplete or malformed data.",
        prop_titulo: "Mix proportions (%)",
        prop_cerrar: "Close",
        prop_instruccion: "Enter the % of each aggregate. The sum must be 100%.",
        prop_total: "Total:",
        prop_usar_valores: "Use values",
        retido_titulo: "Cumulative % Retained Curve",
        retido_tabla1_titulo: "Weighted granulometry two aggregates",
        retido_tabla1_col1: "#",
        retido_tabla1_col2: "%",
        retido_tabla2_titulo: "Recommended granulometric ranges",
        retido_tabla2_col1: "Sieve",
        retido_tabla2_col2: "Block",
        retido_tabla2_col3: "Paver",
        retido_tabla2_col4: "Lower Limit",
        retido_tabla2_col5: "Upper Limit",
        retido_tabla2_nota: "Values in % cumulative retained.",
        btn_cerrar: "Close",
        btn_consumo: "Consumption curve",
        ensayos_titulo: "Tests: Aggregate/Cement Ratio (A/C) vs Strength (MPa)",
        ensayos_resistencia_label: "Target strength (MPa)",
        ensayos_masa_label: "Total mass of aggregates per m³ (kg)",
        ensayos_tabla_label: "Test points (A/C, MPa)",
        ensayos_tabla_col1: "A/C",
        ensayos_tabla_col2: "MPa",
        ensayos_btn_agregar: "+ Add point",
        ensayos_resultado_titulo: "Result (for target MPa)",
        ensayos_btn_cancelar: "Cancel",
        ensayos_btn_calcular: "Calculate",
        consumo_trazo_label: "Required ratio (A/C):",
        consumo_cemento_label: "Cement:",
        consumo_por_label: "per",
        consumo_kg_agregados: "kg of aggregates",
        prop_error_suma_100: "The sum must be exactly 100%.",
        chart_label_ensayos: "Tests",
        chart_label_ajuste: "Fit y = a·ln(x) + b",
        chart_axis_x: "A/C Ratio (aggregate/cement)",
        chart_axis_y: "Strength (MPa)",
        btn_eliminar: "Delete",
        nuevo_producto: "New Product",
        mezcla_eliminada: "🗑 Mix \"{nombre}\" deleted completely.",
        error_sin_tablas: "No loaded tables in localStorage."
      },
      resultado_simulador: {
        titulo: "Simulation Result",
        zona_gruesa: "Coarse Zone:",
        zona_media: "Medium Zone:",
        zona_fina: "Fine Zone:",
        recomendacion: "🔎 Recommendation:",
        btn_ocultar: "❌ Hide Result"
      },
      simulador_dosificacion: {
        grafico_alt: "Resulting curve vs Fuller",
        error_proporciones: "⚠️ Proportions must add up to 100%",
        error_procesar: "❌ Error processing the mix"
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
        data_error: "❌ Errore: dati incompleti o non validi.",
        prop_titulo: "Proporzioni della miscela (%)",
        prop_cerrar: "Chiudi",
        prop_instruccion: "Inserisci la % di ogni aggregato. La somma deve essere 100%.",
        prop_total: "Totale:",
        prop_usar_valores: "Usa valori",
        retido_titulo: "Curva % Trattenuto Cumulato",
        retido_tabla1_titulo: "Granulometria ponderata due aggregati",
        retido_tabla1_col1: "#",
        retido_tabla1_col2: "%",
        retido_tabla2_titulo: "Intervalli granulometrici consigliati",
        retido_tabla2_col1: "Setaccio",
        retido_tabla2_col2: "Blocco",
        retido_tabla2_col3: "Paver",
        retido_tabla2_col4: "Lim. Inf.",
        retido_tabla2_col5: "Lim. Sup.",
        retido_tabla2_nota: "Valori in % trattenuto cumulato.",
        btn_cerrar: "Chiudi",
        btn_consumo: "Curva di consumo",
        ensayos_titulo: "Test: Rapporto Aggregato/Cemento (A/C) vs Resistenza (MPa)",
        ensayos_resistencia_label: "Resistenza obiettivo (MPa)",
        ensayos_masa_label: "Massa totale aggregati per m³ (kg)",
        ensayos_tabla_label: "Punti di prova (A/C, MPa)",
        ensayos_tabla_col1: "A/C",
        ensayos_tabla_col2: "MPa",
        ensayos_btn_agregar: "+ Aggiungi punto",
        ensayos_resultado_titulo: "Risultato (per MPa obiettivo)",
        ensayos_btn_cancelar: "Annulla",
        ensayos_btn_calcular: "Calcola",
        consumo_trazo_label: "Rapporto richiesto (A/C):",
        consumo_cemento_label: "Cemento:",
        consumo_por_label: "per",
        consumo_kg_agregados: "kg di aggregati",
        prop_error_suma_100: "La somma deve essere esattamente 100%.",
        chart_label_ensayos: "Prove",
        chart_label_ajuste: "Adattamento y = a·ln(x) + b",
        chart_axis_x: "Rapporto A/C (aggregato/cemento)",
        chart_axis_y: "Resistenza (MPa)",
        btn_eliminar: "Elimina",
        nuevo_producto: "Nuovo Prodotto",
        mezcla_eliminada: "🗑 Miscela \"{nombre}\" eliminata completamente.",
        error_sin_tablas: "Nessuna tabella caricata in localStorage."
      },
      resultado_simulador: {
        titulo: "Risultato della simulazione",
        zona_gruesa: "Zona grossa:",
        zona_media: "Zona media:",
        zona_fina: "Zona fine:",
        recomendacion: "🔎 Raccomandazione:",
        btn_ocultar: "❌ Nascondi risultato"
      },
      simulador_dosificacion: {
        grafico_alt: "Curva risultante vs Fuller",
        error_proporcioni: "⚠️ Le proporzioni devono sommare al 100%",
        error_procesar: "❌ Errore nell'elaborazione della miscela"
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
        data_error: "❌ Erro: dados incompletos ou inválidos.",
        prop_titulo: "Proporções da mistura (%)",
        prop_cerrar: "Fechar",
        prop_instruccion: "Insira a % de cada agregado. A soma deve ser 100%.",
        prop_total: "Total:",
        prop_usar_valores: "Usar valores",
        retido_titulo: "Curva % Retido Acumulado",
        retido_tabla1_titulo: "Granulometria ponderada dois agregados",
        retido_tabla1_col1: "#",
        retido_tabla1_col2: "%",
        retido_tabla2_titulo: "Faixas granulométricas recomendadas",
        retido_tabla2_col1: "Peneira",
        retido_tabla2_col2: "Bloco",
        retido_tabla2_col3: "Paver",
        retido_tabla2_col4: "Lim. Inf.",
        retido_tabla2_col5: "Lim. Sup.",
        retido_tabla2_nota: "Valores em % retido acumulado.",
        btn_cerrar: "Fechar",
        btn_consumo: "Curva de consumo",
        ensayos_titulo: "Ensaios: Relação Agregado/Cimento (A/C) vs Resistência (MPa)",
        ensayos_resistencia_label: "Resistência alvo (MPa)",
        ensayos_masa_label: "Massa total de agregados por m³ (kg)",
        ensayos_tabla_label: "Pontos de ensaio (A/C, MPa)",
        ensayos_tabla_col1: "A/C",
        ensayos_tabla_col2: "MPa",
        ensayos_btn_agregar: "+ Adicionar ponto",
        ensayos_resultado_titulo: "Resultado (para a MPa alvo)",
        ensayos_btn_cancelar: "Cancelar",
        ensayos_btn_calcular: "Calcular",
        consumo_trazo_label: "Traço requerido (A/C):",
        consumo_cemento_label: "Cimento:",
        consumo_por_label: "por",
        consumo_kg_agregados: "kg de agregados",
        prop_error_suma_100: "A soma deve ser exatamente 100%.",
        chart_label_ensayos: "Ensaios",
        chart_label_ajuste: "Ajuste y = a·ln(x) + b",
        chart_axis_x: "Relação A/C (agregado/cimento)",
        chart_axis_y: "Resistência (MPa)",
        btn_eliminar: "Eliminar",
        nuevo_producto: "Novo Produto",
        mezcla_eliminada: "🗑 Mistura \"{nome}\" eliminada completamente.",
        error_sin_tablas: "Nenhuma tabela carregada no localStorage."
      },
      resultado_simulador: {
        titulo: "Resultado da simulação",
        zona_gruesa: "Zona grossa:",
        zona_media: "Zona média:",
        zona_fina: "Zona fina:",
        recomendacion: "🔎 Recomendação:",
        btn_ocultar: "❌ Occultar resultado"
      },
      simulador_dosificacion: {
        grafico_alt: "Curva resultante vs Fuller",
        error_proporciones: "⚠️ As proporções devem somar 100%",
        error_procesar: "❌ Erro ao processar a mistura"
      }
    },

    login: {
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
    },

    registrarse: {
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
    },

    // Namespace faltante en tu código original:
    verificar: {
      es: {
        titulo: "Verificá tu email",
        enviado: "Te enviamos un enlace de verificación.",
        reenviar: "Reenviar correo"
      },
      en: {
        titulo: "Verify your email",
        enviado: "We sent you a verification link.",
        reenviar: "Resend email"
      },
      it: {
        titulo: "Verifica la tua email",
        enviado: "Ti abbiamo inviato un link di verifica.",
        reenviar: "Invia di nuovo"
      },
      pt: {
        titulo: "Verifique seu e-mail",
        enviado: "Enviamos um link de verificação.",
        reenviar: "Reenviar e-mail"
      },
      pl: {
        titulo: "Zweryfikuj swój e-mail",
        enviado: "Wysłaliśmy link weryfikacyjny.",
        reenviar: "Wyślij ponownie"
      }
    }
  };

  const SUP_LANGS = new Set(["es", "en", "it", "pt", "pl"]);

  function getLang() {
    // Primero intenta leer de localStorage
    let v = localStorage.getItem("lang") || "";
    if (SUP_LANGS.has(v)) return v;
    
    // Si no está en localStorage, intenta desde las cookies
    const raw = document.cookie.split("; ").find(c => c.startsWith("lang="));
    v = raw ? decodeURIComponent(raw.split("=")[1] || "") : "";
    if (SUP_LANGS.has(v)) return v;
    
    // Default a español
    return "es";
  }

  // t("login.titulo") / t("registrarse.errores.correo") / t("sim.header") / t("verificar.titulo")
  function t(key) {
    const lang = getLang();
    const parts = key.split(".");
    const ns = parts.shift() || "login";  // default a login
    const path = parts;                   // resto de la ruta

    // Navega dict[ns][lang][...path]
    let node = dict?.[ns]?.[lang];
    for (const p of path) node = node?.[p];
    if (node !== undefined) return node;

    // Fallback a español
    node = dict?.[ns]?.["es"];
    for (const p of path) node = node?.[p];
    return node !== undefined ? node : `[${key}]`;
  }

  // Función auxiliar para traducir elementos con data-i18n
  function applyTranslations(container = document) {
    container.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      const text = t(key);
      
      if (el.tagName === 'BUTTON') {
        el.textContent = text;
        if (el.hasAttribute('aria-label')) {
          el.setAttribute('aria-label', text);
        }
        if (el.hasAttribute('title')) {
          el.setAttribute('title', text);
        }
      } else {
        el.textContent = text;
      }
    });
  }

  return { t, getLang, applyTranslations, dict };
})();
