import streamlit as st
import pandas as pd
from supabase import create_client, Client
import pytz
from datetime import datetime, timedelta
import extra_streamlit_components as stx

st.set_page_config(page_title="Quiniela Mundial 2026", page_icon="🏆", layout="wide")

# --- CONEXIÓN A SUPABASE ---
@st.cache_resource
def init_connection():
    return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])

supabase: Client = init_connection()

# --- MANEJADOR DE COOKIES (NATIVO Y SIN CACHÉ PARA EVITAR ERRORES) ---
cookie_manager = stx.CookieManager(key="cookie_manager")

# --- CONFIGURACIÓN DE EQUIPOS Y GRUPOS ---
flag_ing = "\U0001F3F4\U000E0067\U000E0062\U000E0065\U000E006E\U000E0067\U000E007F"
flag_sct = "\U0001F3F4\U000E0067\U000E0062\U000E0073\U000E0063\U000E0074\U000E007F"

grupos_equipos = {
    "A": ["🇲🇽 México", "🇿🇦 Sudáfrica", "🇰🇷 Corea del Sur", "🇨🇿 Chequia"],
    "B": ["🇨🇦 Canadá", "🇧🇦 Bosnia y Herzegovina", "🇶🇦 Catar", "🇨🇭 Suiza"],
    "C": ["🇧🇷 Brasil", "🇲🇦 Marruecos", "🇭🇹 Haití", f"{flag_sct} Escocia"],
    "D": ["🇺🇸 EE.UU.", "🇹🇷 Turquía", "🇵🇾 Paraguay", "🇦🇺 Australia"],
    "E": ["🇩🇪 Alemania", "🇨🇼 Curazao", "🇨🇮 Costa de Marfil", "🇪🇨 Ecuador"],
    "F": ["🇳🇱 Países Bajos", "🇯🇵 Japón", "🇸🇪 Suecia", "🇹🇳 Túnez"],
    "G": ["🇧🇪 Bélgica", "🇪🇬 Egipto", "🇮🇷 Irán", "🇳🇿 Nueva Zelanda"],
    "H": ["🇪🇸 España", "🇺🇾 Uruguay", "🇨🇻 Cabo Verde", "🇸🇦 Arabia Saudita"],
    "I": ["🇫🇷 Francia", "🇳🇴 Noruega", "🇸🇳 Senegal", "🇮🇶 Irak"],
    "J": ["🇦🇷 Argentina", "🇦🇹 Austria", "🇩🇿 Argelia", "🇯🇴 Jordania"],
    "K": ["🇵🇹 Portugal", "🇨🇴 Colombia", "🇺🇿 Uzbekistán", "🇨🇩 RD Congo"],
    "L": [f"{flag_ing} Inglaterra", "🇭🇷 Croacia", "🇬🇭 Ghana", "🇵🇦 Panamá"]
}

llaves_32_oficial = {
    73: "2A vs 2B", 74: "1E vs Mejor 3° (A/B/C/D/F)", 75: "1I vs Mejor 3° (C/D/F/G/H)", 76: "2G vs 2H",
    77: "1C vs Mejor 3° (A/B/F/G/H)", 78: "2I vs 2L", 79: "1A vs Mejor 3° (C/E/F/H/I)", 80: "1L vs Mejor 3° (E/H/I/J/K)",
    81: "1D vs Mejor 3° (B/E/G/I/J)", 82: "2D vs 2E", 83: "1K vs Mejor 3° (D/E/I/J/L)", 84: "1J vs 2H",
    85: "1B vs Mejor 3° (E/G/H/I/K)", 86: "1F vs 2C", 87: "1G vs Mejor 3° (A/B/D/E/F)", 88: "1H vs 2J"
}

lista_equipos = [eq for grupo in grupos_equipos.values() for eq in grupo] + ["Por definir", "Otro"]

# --- MATRIZ OFICIAL ---
raw_schedule = f"""
1|2026-06-11 13:00|🇲🇽 México|🇿🇦 Sudáfrica|Grupo A
2|2026-06-11 20:00|🇰🇷 Corea del Sur|🇨🇿 Chequia|Grupo A
3|2026-06-12 13:00|🇨🇦 Canadá|🇧🇦 Bosnia y Herzegovina|Grupo B
4|2026-06-12 19:00|🇺🇸 EE.UU.|🇵🇾 Paraguay|Grupo D
5|2026-06-13 13:00|🇶🇦 Catar|🇨🇭 Suiza|Grupo B
6|2026-06-13 16:00|🇧🇷 Brasil|🇲🇦 Marruecos|Grupo C
7|2026-06-13 19:00|🇭🇹 Haití|{flag_sct} Escocia|Grupo C
8|2026-06-13 22:00|🇦🇺 Australia|🇹🇷 Turquía|Grupo D
9|2026-06-14 11:00|🇩🇪 Alemania|🇨🇼 Curazao|Grupo E
10|2026-06-14 14:00|🇳🇱 Países Bajos|🇯🇵 Japón|Grupo F
11|2026-06-14 17:00|🇨🇮 Costa de Marfil|🇪🇨 Ecuador|Grupo E
12|2026-06-14 20:00|🇸🇪 Suecia|🇹🇳 Túnez|Grupo F
13|2026-06-15 10:00|🇪🇸 España|🇨🇻 Cabo Verde|Grupo H
14|2026-06-15 13:00|🇧🇪 Bélgica|🇪🇬 Egipto|Grupo G
15|2026-06-15 16:00|🇸🇦 Arabia Saudita|🇺🇾 Uruguay|Grupo H
16|2026-06-15 19:00|🇮🇷 Irán|🇳🇿 Nueva Zelanda|Grupo G
17|2026-06-16 13:00|🇫🇷 Francia|🇸🇳 Senegal|Grupo I
18|2026-06-16 16:00|🇮🇶 Irak|🇳🇴 Noruega|Grupo I
19|2026-06-16 19:00|🇦🇷 Argentina|🇩🇿 Argelia|Grupo J
20|2026-06-16 22:00|🇦🇹 Austria|🇯🇴 Jordania|Grupo J
21|2026-06-17 11:00|🇵🇹 Portugal|🇨🇩 RD Congo|Grupo K
22|2026-06-17 14:00|{flag_ing} Inglaterra|🇭🇷 Croacia|Grupo L
23|2026-06-17 17:00|🇬🇭 Ghana|🇵🇦 Panamá|Grupo L
24|2026-06-17 20:00|🇺🇿 Uzbekistán|🇨🇴 Colombia|Grupo K
25|2026-06-18 10:00|🇨🇿 Chequia|🇿🇦 Sudáfrica|Grupo A
26|2026-06-18 13:00|🇨🇭 Suiza|🇧🇦 Bosnia y Herzegovina|Grupo B
27|2026-06-18 16:00|🇨🇦 Canadá|🇶🇦 Catar|Grupo B
28|2026-06-18 19:00|🇲🇽 México|🇰🇷 Corea del Sur|Grupo A
29|2026-06-19 13:00|🇺🇸 EE.UU.|🇦🇺 Australia|Grupo D
30|2026-06-19 16:00|{flag_sct} Escocia|🇲🇦 Marruecos|Grupo C
31|2026-06-19 18:30|🇧🇷 Brasil|🇭🇹 Haití|Grupo C
32|2026-06-19 21:00|🇹🇷 Turquía|🇵🇾 Paraguay|Grupo D
33|2026-06-20 11:00|🇳🇱 Países Bajos|🇸🇪 Suecia|Grupo F
34|2026-06-20 14:00|🇩🇪 Alemania|🇨🇮 Costa de Marfil|Grupo E
35|2026-06-20 18:00|🇪🇨 Ecuador|🇨🇼 Curazao|Grupo E
36|2026-06-20 22:00|🇹🇳 Túnez|🇯🇵 Japón|Grupo F
37|2026-06-21 16:00|🇺🇾 Uruguay|🇨🇻 Cabo Verde|Grupo H
38|2026-06-21 10:00|🇪🇸 España|🇸🇦 Arabia Saudita|Grupo H
39|2026-06-21 13:00|🇧🇪 Bélgica|🇮🇷 Irán|Grupo G
40|2026-06-21 19:00|🇳🇿 Nueva Zelanda|🇪🇬 Egipto|Grupo G
41|2026-06-22 11:00|🇦🇷 Argentina|🇦🇹 Austria|Grupo J
42|2026-06-22 15:00|🇫🇷 Francia|🇮🇶 Irak|Grupo I
43|2026-06-22 18:00|🇳🇴 Noruega|🇸🇳 Senegal|Grupo I
44|2026-06-22 21:00|🇯🇴 Jordania|🇩🇿 Argelia|Grupo J
45|2026-06-23 11:00|🇵🇹 Portugal|🇺🇿 Uzbekistán|Grupo K
46|2026-06-23 14:00|{flag_ing} Inglaterra|🇬🇭 Ghana|Grupo L
47|2026-06-23 17:00|🇵🇦 Panamá|🇭🇷 Croacia|Grupo L
48|2026-06-23 20:00|🇨🇴 Colombia|🇨🇩 RD Congo|Grupo K
49|2026-06-24 16:00|{flag_sct} Escocia|🇧🇷 Brasil|Grupo C
50|2026-06-24 16:00|🇲🇦 Marruecos|🇭🇹 Haití|Grupo C
51|2026-06-24 13:00|🇨🇭 Suiza|🇨🇦 Canadá|Grupo B
52|2026-06-24 13:00|🇧🇦 Bosnia y Herzegovina|🇶🇦 Catar|Grupo B
53|2026-06-24 19:00|🇨🇿 Chequia|🇲🇽 México|Grupo A
54|2026-06-24 19:00|🇿🇦 Sudáfrica|🇰🇷 Corea del Sur|Grupo A
55|2026-06-25 13:00|🇨🇼 Curazao|🇨🇮 Costa de Marfil|Grupo E
56|2026-06-25 14:00|🇪🇨 Ecuador|🇩🇪 Alemania|Grupo E
57|2026-06-25 17:00|🇯🇵 Japón|🇸🇪 Suecia|Grupo F
58|2026-06-25 17:00|🇹🇳 Túnez|🇳🇱 Países Bajos|Grupo F
59|2026-06-25 20:00|🇹🇷 Turquía|🇺🇸 EE.UU.|Grupo D
60|2026-06-25 20:00|🇵🇾 Paraguay|🇦🇺 Australia|Grupo D
61|2026-06-26 13:00|🇳🇴 Noruega|🇫🇷 Francia|Grupo I
62|2026-06-26 13:00|🇸🇳 Senegal|🇮🇶 Irak|Grupo I
63|2026-06-26 21:00|🇪🇬 Egipto|🇮🇷 Irán|Grupo G
64|2026-06-26 21:00|🇳🇿 Nueva Zelanda|🇧🇪 Bélgica|Grupo G
65|2026-06-26 18:00|🇨🇻 Cabo Verde|🇸🇦 Arabia Saudita|Grupo H
66|2026-06-26 18:00|🇺🇾 Uruguay|🇪🇸 España|Grupo H
67|2026-06-27 15:00|🇵🇦 Panamá|{flag_ing} Inglaterra|Grupo L
68|2026-06-27 15:00|🇭🇷 Croacia|🇬🇭 Ghana|Grupo L
69|2026-06-27 20:00|🇩🇿 Argelia|🇦🇹 Austria|Grupo J
70|2026-06-27 20:00|🇯🇴 Jordania|🇦🇷 Argentina|Grupo J
71|2026-06-27 17:30|🇨🇴 Colombia|🇵🇹 Portugal|Grupo K
72|2026-06-27 17:30|🇨🇩 RD Congo|🇺🇿 Uzbekistán|Grupo K
73|2026-06-28 13:00|2A|2B|Dieciseisavos (32)
74|2026-06-29 11:00|1C|2F|Dieciseisavos (32)
75|2026-06-29 15:00|1E|Mejor 3° (A/B/C/D/F)|Dieciseisavos (32)
76|2026-06-29 19:00|1F|2C|Dieciseisavos (32)
77|2026-06-30 11:00|2E|2I|Dieciseisavos (32)
78|2026-06-30 15:00|1I|Mejor 3° (C/D/F/G/H)|Dieciseisavos (32)
79|2026-06-30 19:00|1A|Mejor 3° (C/E/F/H/I)|Dieciseisavos (32)
80|2026-07-01 10:00|1L|Mejor 3° (E/H/I/J/K)|Dieciseisavos (32)
81|2026-07-01 18:00|1G|Mejor 3° (A/E/H/I/J)|Dieciseisavos (32)
82|2026-07-01 18:00|1D|Mejor 3° (B/E/F/I/J)|Dieciseisavos (32)
83|2026-07-02 13:00|1H|2J|Dieciseisavos (32)
84|2026-07-02 17:00|2K|2L|Dieciseisavos (32)
85|2026-07-02 21:00|1B|Mejor 3° (E/F/G/I/J)|Dieciseisavos (32)
86|2026-07-03 12:00|2D|2G|Dieciseisavos (32)
87|2026-07-03 19:00|1J|2H|Dieciseisavos (32)
88|2026-07-03 19:00|1K|Mejor 3° (D/E/I/J/L)|Dieciseisavos (32)
89|2026-07-04 15:00|Ganador M73|Ganador M75|Octavos (16)
90|2026-07-04 15:00|Ganador M74|Ganador M77|Octavos (16)
91|2026-07-05 14:00|Ganador M76|Ganador M78|Octavos (16)
92|2026-07-05 18:00|Ganador M79|Ganador M80|Octavos (16)
93|2026-07-06 13:00|Ganador M83|Ganador M84|Octavos (16)
94|2026-07-06 18:00|Ganador M81|Ganador M82|Octavos (16)
95|2026-07-07 10:00|Ganador M86|Ganador M88|Octavos (16)
96|2026-07-07 14:00|Ganador M85|Ganador M87|Octavos (16)
97|2026-07-09 14:00|Ganador M89|Ganador M90|Cuartos (8)
98|2026-07-10 13:00|Ganador M93|Ganador M94|Cuartos (8)
99|2026-07-11 15:00|Ganador M91|Ganador M92|Cuartos (8)
100|2026-07-11 19:00|Ganador M95|Ganador M96|Cuartos (8)
101|2026-07-14 13:00|Ganador M97|Ganador M98|Semifinal
102|2026-07-15 13:00|Ganador M99|Ganador M100|Semifinal
103|2026-07-18 15:00|Perdedor M101|Perdedor M102|Tercer Lugar
104|2026-07-19 13:00|Ganador M101|Ganador M102|Final
"""

matches = []
for line in raw_schedule.strip().split('\n'):
    parts = line.split('|')
    matches.append({"id": int(parts[0]), "fecha_base": parts[1] + ":00", "default_a": parts[2], "default_b": parts[3], "fase": parts[4]})

# --- MOTOR DE CÁLCULO DE GRUPOS ---
def calcular_posiciones_grupos(resultados_oficiales):
    tablas = {g: {eq: {'PJ': 0, 'G': 0, 'E': 0, 'P': 0, 'GF': 0, 'GC': 0, 'DIF': 0, 'PTS': 0} for eq in grupos_equipos[g]} for g in grupos_equipos}
    for m in matches:
        m_id = m['id']
        fase = m['fase']
        if "Grupo" in fase:
            g = fase.split(" ")[1]
            if m_id in resultados_oficiales:
                res = resultados_oficiales[m_id]
                ganador = res.get('real_result')
                if ganador and ganador != "Pendiente":
                    eq_a = res['equipo_a']
                    eq_b = res['equipo_b']
                    marc_a = int(res.get('marcador_a', 0))
                    marc_b = int(res.get('marcador_b', 0))

                    if eq_a in tablas[g]:
                        tablas[g][eq_a]['PJ'] += 1
                        tablas[g][eq_a]['GF'] += marc_a; tablas[g][eq_a]['GC'] += marc_b
                        tablas[g][eq_a]['DIF'] += (marc_a - marc_b)
                        if ganador == eq_a:
                            tablas[g][eq_a]['G'] += 1; tablas[g][eq_a]['PTS'] += 3
                        elif ganador == "Empate":
                            tablas[g][eq_a]['E'] += 1; tablas[g][eq_a]['PTS'] += 1
                        else: tablas[g][eq_a]['P'] += 1

                    if eq_b in tablas[g]:
                        tablas[g][eq_b]['PJ'] += 1
                        tablas[g][eq_b]['GF'] += marc_b; tablas[g][eq_b]['GC'] += marc_a
                        tablas[g][eq_b]['DIF'] += (marc_b - marc_a)
                        if ganador == eq_b:
                            tablas[g][eq_b]['G'] += 1; tablas[g][eq_b]['PTS'] += 3
                        elif ganador == "Empate":
                            tablas[g][eq_b]['E'] += 1; tablas[g][eq_b]['PTS'] += 1
                        else: tablas[g][eq_b]['P'] += 1

    for g in tablas:
        tablas[g] = dict(sorted(tablas[g].items(), key=lambda item: (item[1]['PTS'], item[1]['DIF'], item[1]['GF']), reverse=True))
    return tablas

# --- TRADUCTOR DE LLAVES ---
def resolver_llave(etiqueta, tablas_posiciones, oficiales):
    etiqueta = str(etiqueta).strip()
    if len(etiqueta) == 2 and etiqueta[0] in ["1", "2"] and etiqueta[1] in grupos_equipos.keys():
        pos = int(etiqueta[0]) - 1
        grupo = etiqueta[1]
        equipos_ordenados = list(tablas_posiciones[grupo].keys())
        partidos_jugados = sum(tablas_posiciones[grupo][eq]['PJ'] for eq in equipos_ordenados)
        if partidos_jugados == 12: return equipos_ordenados[pos]
    if etiqueta.startswith("Ganador M"):
        m_id = int(etiqueta.replace("Ganador M", ""))
        res = oficiales.get(m_id, {}).get("real_result")
        if res and res not in ["Pendiente", "Empate"]: return res
    if etiqueta.startswith("Perdedor M"):
        m_id = int(etiqueta.replace("Perdedor M", ""))
        res = oficiales.get(m_id, {}).get("real_result")
        eq_a = oficiales.get(m_id, {}).get("equipo_a")
        eq_b = oficiales.get(m_id, {}).get("equipo_b")
        if res and res not in ["Pendiente", "Empate"] and eq_a and eq_b:
            return eq_b if res == eq_a else eq_a
    return etiqueta

def convertir_hora(fecha_base_str, timezone_destino):
    dt_base = pytz.timezone('America/Mexico_City').localize(datetime.strptime(fecha_base_str, '%Y-%m-%d %H:%M:%S'))
    return dt_base.astimezone(pytz.timezone(timezone_destino)).strftime('%d %b %Y - %H:%M')

# --- SISTEMA DE AUTENTICACIÓN ---
if 'user' not in st.session_state: st.session_state.user = None

# --- RECUPERAR SESIÓN DESDE LAS COOKIES ---
if st.session_state.user is None:
    auth_cookie = cookie_manager.get(cookie="sb_auth_token")
    if auth_cookie and type(auth_cookie) == str and '|' in auth_cookie:
        try:
            acc_tok, ref_tok = auth_cookie.split('|')
            res = supabase.auth.set_session(acc_tok, ref_tok)
            st.session_state.user = res.user
            st.rerun()
        except:
            pass 

if st.session_state.user is None:
    st.title("⚽ Quiniela Mundial 2026")
    tab_login, tab_registro = st.tabs(["Ingresar", "Registrarse"])
    
    with tab_login:
        with st.form("form_login"):
            st.text_input("Correo Electrónico", key="login_email_input")
            st.text_input("Contraseña", type="password", key="login_pass_input")
            if st.form_submit_button("Entrar"):
                email_actual = st.session_state.login_email_input
                pass_actual = st.session_state.login_pass_input
                if email_actual and pass_actual:
                    try:
                        res = supabase.auth.sign_in_with_password({"email": email_actual, "password": pass_actual})
                        st.session_state.user = res.user
                        exp_date = datetime.now() + timedelta(days=30)
                        cookie_manager.set("sb_auth_token", f"{res.session.access_token}|{res.session.refresh_token}", expires_at=exp_date)
                        st.rerun()
                    except Exception as e:
                        if "Invalid login credentials" in str(e): st.error("Credenciales incorrectas.")
                        else: st.error(f"Error de conexión: {e}")
                else: st.warning("Llena ambos campos.")

    with tab_registro:
        email_reg = st.text_input("Correo", key="reg_email")
        pass_reg = st.text_input("Contraseña (Mínimo 6)", type="password", key="reg_pass")
        username = st.text_input("Nombre para el Ranking")
        if st.button("Registrarse"):
            try:
                supabase.auth.sign_up({"email": email_reg, "password": pass_reg})
                supabase.table('users').insert({"username": username, "email": email_reg}).execute()
                st.success("¡Registrado! Ahora inicia sesión.")
            except Exception as e: st.error(f"Error: {e}")

# --- APLICACIÓN PRINCIPAL ---
else:
    user_email = st.session_state.user.email
    try:
        usuarios_db = supabase.table('users').select('email', 'username').execute().data
        email_to_user = {u['email']: u['username'] for u in usuarios_db} if usuarios_db else {}
        display_name = email_to_user.get(user_email, user_email)
    except:
        display_name = user_email
        email_to_user = {}
        
    st.sidebar.success(f"👤 Hola, {display_name}")
    if st.sidebar.button("Cerrar Sesión"):
        supabase.auth.sign_out()
        st.session_state.user = None
        cookie_manager.delete("sb_auth_token") 
        st.rerun()

    user_tz = st.sidebar.selectbox("🌍 Tu Zona Horaria", pytz.all_timezones, index=pytz.all_timezones.index('America/Mexico_City'))

    try:
        res_db = supabase.table('results').select('*').execute().data
        oficiales = {r['match_id']: r for r in res_db}
        
        torneo_db = supabase.table('tournament_settings').select('*').eq('id', 1).execute().data
        campeon_real = torneo_db[0].get('actual_champion') if torneo_db else None
        subcampeon_real = torneo_db[0].get('actual_subcampeon') if torneo_db else None
        tercero_real = torneo_db[0].get('actual_tercero') if torneo_db else None
        
        todas_preds_db = supabase.table('predictions').select('*').execute().data
        preds_comunidad = {}
        for p in todas_preds_db:
            preds_comunidad.setdefault(p['match_id'], []).append(p)
    except:
        oficiales = {}
        preds_comunidad = {}
        campeon_real = subcampeon_real = tercero_real = None

    tablas_posiciones = calcular_posiciones_grupos(oficiales)
    
    es_admin = user_email == "adam666.die@gmail.com"
    tabs = ["📝 Pronósticos", "🏆 Grupos", "👑 Podio Final", "📊 Ranking"]
    if es_admin: tabs.append("⚙️ Panel Admin")

    app_tabs = st.tabs(tabs)

    cdmx_tz = pytz.timezone('America/Mexico_City')
    ahora_cdmx = datetime.now(cdmx_tz)
    hoy_fecha_cdmx = ahora_cdmx.date()

    # --- PESTAÑA 1: PRONÓSTICOS ---
    with app_tabs[0]:
        st.header("Tus Pronósticos")
        
        fase_seleccionada = st.selectbox("📌 Filtrar Partidos por:", 
            ["Todos los partidos (M1 - M104)", "Jornada 1 (M1 - M24)", "Jornada 2 (M25 - M48)", "Jornada 3 (M49 - M72)", 
             "Dieciseisavos (M73 - M88)", "Octavos (M89 - M96)", "Cuartos (M97 - M100)", "Semifinales y Final (M101 - M104)"])
        
        matches_filtrados = []
        if "Todos los partidos" in fase_seleccionada: matches_filtrados = matches
        elif "Jornada 1" in fase_seleccionada: matches_filtrados = [m for m in matches if m['id'] <= 24]
        elif "Jornada 2" in fase_seleccionada: matches_filtrados = [m for m in matches if 25 <= m['id'] <= 48]
        elif "Jornada 3" in fase_seleccionada: matches_filtrados = [m for m in matches if 49 <= m['id'] <= 72]
        elif "Dieciseisavos" in fase_seleccionada: matches_filtrados = [m for m in matches if 73 <= m['id'] <= 88]
        elif "Octavos" in fase_seleccionada: matches_filtrados = [m for m in matches if 89 <= m['id'] <= 96]
        elif "Cuartos" in fase_seleccionada: matches_filtrados = [m for m in matches if 97 <= m['id'] <= 100]
        elif "Semifinales" in fase_seleccionada: matches_filtrados = [m for m in matches if m['id'] >= 101]

        mis_preds_exactas = {p['match_id']: p['prediction'] for lst in preds_comunidad.values() for p in lst if p['email'] == user_email} if preds_comunidad else {}

        for match in matches_filtrados:
            m_id = match['id']
            eq_a = oficiales.get(m_id, {}).get('equipo_a') or resolver_llave(match['default_a'], tablas_posiciones, oficiales)
            eq_b = oficiales.get(m_id, {}).get('equipo_b') or resolver_llave(match['default_b'], tablas_posiciones, oficiales)
            resultado_oficial = oficiales.get(m_id, {}).get('real_result')
            
            match_dt = cdmx_tz.localize(datetime.strptime(match['fecha_base'], '%Y-%m-%d %H:%M:%S'))
            partido_bloqueado = hoy_fecha_cdmx >= match_dt.date()
            
            with st.container():
                st.markdown(f"**M{m_id} | {match['fase']} | 🕒 {convertir_hora(match['fecha_base'], user_tz)}**")
                opciones = [eq_a, "Empate", eq_b]
                voto_crudo = mis_preds_exactas.get(m_id)
                idx = opciones.index(voto_crudo) if voto_crudo in opciones else None

                if resultado_oficial:
                    st.info(f"🔒 FINALIZADO: {eq_a} [{oficiales[m_id]['marcador_a']}] vs [{oficiales[m_id]['marcador_b']}] {eq_b} | Res: **{resultado_oficial}**")
                    st.write(f"Tu pronóstico: {voto_crudo if voto_crudo else 'Ninguno'}")
                elif partido_bloqueado:
                    st.warning("⏳ Partido bloqueado (Día del evento alcanzado).")
                    st.radio(f"Gana M{m_id}", opciones, index=idx, key=f"p_{m_id}", horizontal=True, disabled=True, label_visibility="collapsed")
                    st.write(f"Tu pronóstico guardado: **{voto_crudo if voto_crudo else 'Ninguno'}**")
                else:
                    st.markdown(f"### {eq_a} vs {eq_b}")
                    seleccion = st.radio(f"Gana M{m_id}", opciones, index=idx, key=f"p_{m_id}", horizontal=True, label_visibility="collapsed")
                    if st.button("Guardar Pronóstico", key=f"b_{m_id}"):
                        data_pronostico = {"email": user_email, "match_id": m_id, "prediction": seleccion}
                        supabase.table('predictions').upsert(data_pronostico, on_conflict="email,match_id").execute()
                        st.toast(f"M{m_id} Guardado", icon="✅")
                        st.rerun()
                
                if partido_bloqueado or resultado_oficial:
                    apuestas_partido = preds_comunidad.get(m_id, [])
                    total_apuestas = len(apuestas_partido)
                    if total_apuestas > 0:
                        votos_a = sum(1 for p in apuestas_partido if p['prediction'] == eq_a)
                        votos_e = sum(1 for p in apuestas_partido if p['prediction'] == "Empate")
                        votos_b = sum(1 for p in apuestas_partido if p['prediction'] == eq_b)
                        
                        st.caption(f"📊 **Estadísticas de la Comunidad:** ({total_apuestas} votos)")
                        st.progress(votos_a / total_apuestas if total_apuestas else 0, text=f"{eq_a} ({int(votos_a/total_apuestas*100)}%)")
                        st.progress(votos_e / total_apuestas if total_apuestas else 0, text=f"Empate ({int(votos_e/total_apuestas*100)}%)")
                        st.progress(votos_b / total_apuestas if total_apuestas else 0, text=f"{eq_b} ({int(votos_b/total_apuestas*100)}%)")
                        
                        if resultado_oficial and resultado_oficial != "Pendiente":
                            ganadores = [email_to_user.get(p['email'], 'Usuario') for p in apuestas_partido if p['prediction'] == resultado_oficial]
                            if ganadores: st.success(f"🎯 Acertaron: {', '.join(ganadores)}")
                            else: st.error("Nadie acertó a este partido.")
                st.divider()

    # --- PESTAÑA 2: GRUPOS ---
    with app_tabs[1]:
        st.header("🏆 Posiciones Fase de Grupos")
        cols = st.columns(3)
        idx_col = 0
        for g, tabla in tablas_posiciones.items():
            with cols[idx_col % 3]:
                st.subheader(f"Grupo {g}")
                df_grupo = pd.DataFrame.from_dict(tabla, orient='index')
                st.dataframe(df_grupo)
            idx_col += 1

    # --- PESTAÑA 3: PODIO FINAL ---
    with app_tabs[2]:
        st.header("👑 Podio del Mundial")
        m4_cerrado = oficiales.get(4, {}).get('real_result') is not None
        
        try:
            mi_podio_db = supabase.table('champion_predictions').select('*').eq('email', user_email).execute().data
            if mi_podio_db:
                mi_campeon = mi_podio_db[0].get('prediction') or "No seleccionado"
                mi_subcampeon = mi_podio_db[0].get('subcampeon') or "No seleccionado"
                mi_tercero = mi_podio_db[0].get('tercero') or "No seleccionado"
            else: mi_campeon = mi_subcampeon = mi_tercero = "No seleccionado"
        except: mi_campeon = mi_subcampeon = mi_tercero = "No seleccionado"

        if campeon_real:
            st.error(f"🏆 Torneo Terminado. Campeón: **{campeon_real}** | Subcampeón: **{subcampeon_real}** | 3ro: **{tercero_real}**")
            st.info(f"Tus elecciones -> 🥇: {mi_campeon} | 🥈: {mi_subcampeon} | 🥉: {mi_tercero}")
        elif m4_cerrado:
            st.error("⛔ La selección se cerró al finalizar el Partido 4.")
            st.info(f"Tus elecciones -> 🥇: {mi_campeon} | 🥈: {mi_subcampeon} | 🥉: {mi_tercero}")
        else:
            c1, c2, c3 = st.columns(3)
            with c1: nuevo_campeon = st.selectbox("🥇 Elegir Campeón:", lista_equipos)
            with c2: nuevo_sub = st.selectbox("🥈 Elegir Subcampeón:", lista_equipos)
            with c3: nuevo_ter = st.selectbox("🥉 Elegir Tercer Lugar:", lista_equipos)
            
            if st.button("Guardar Podio Completo"):
                st.session_state.confirm_podio = {"camp": nuevo_campeon, "sub": nuevo_sub, "ter": nuevo_ter}

            if 'confirm_podio' in st.session_state:
                st.warning("⚠️ ¿Seguro que quieres guardar este podio? Al cerrar el M4 ya no podrás cambiarlo.")
                btn1, btn2 = st.columns(2)
                if btn1.button("✅ Confirmar Podio"):
                    datos_podio = {"email": user_email, "prediction": st.session_state.confirm_podio["camp"], "subcampeon": st.session_state.confirm_podio["sub"], "tercero": st.session_state.confirm_podio["ter"]}
                    supabase.table('champion_predictions').upsert(datos_podio).execute()
                    del st.session_state.confirm_podio
                    st.success("¡Podio guardado exitosamente!")
                    st.rerun()
                if btn2.button("❌ Cancelar"):
                    del st.session_state.confirm_podio
                    st.rerun()

    # --- PESTAÑA 4: RANKING ---
    with app_tabs[3]:
        st.header("📊 Tabla de Posiciones")
        st.caption("Criterios de desempate: 1. Acierto de Campeón | 2. Más puntos en Fase de Grupos")
        if st.button("🔄 Actualizar Ranking", type="primary"):
            if not email_to_user: st.info("No hay usuarios registrados.")
            else:
                usuarios = pd.DataFrame(list(email_to_user.items()), columns=['email', 'username'])
                usuarios['Total'] = 0 
                usuarios['pts_grupos'] = 0
                usuarios['acerto_campeon'] = 0

                preds_data = [p for l in preds_comunidad.values() for p in l]
                res_data = supabase.table('results').select('*').execute().data
                
                if preds_data and res_data:
                    df_p = pd.DataFrame(preds_data)
                    df_r = pd.DataFrame(res_data).dropna(subset=['real_result'])
                    if not df_r.empty:
                        cruce = pd.merge(df_p, df_r[['match_id', 'real_result']], on='match_id', how='inner')
                        cruce['puntos'] = cruce.apply(lambda x: 2 if x['prediction'] == x['real_result'] else 0, axis=1)
                        cruce['es_grupo'] = cruce['match_id'] <= 72
                        
                        pts_totales = cruce.groupby('email')['puntos'].sum().reset_index()
                        pts_grupos = cruce[cruce['es_grupo']].groupby('email')['puntos'].sum().reset_index().rename(columns={'puntos': 'pts_grupos_calc'})
                        
                        usuarios = pd.merge(usuarios, pts_totales, on='email', how='left').fillna(0)
                        usuarios['Total'] += usuarios['puntos']
                        usuarios = pd.merge(usuarios, pts_grupos, on='email', how='left').fillna(0)
                        usuarios['pts_grupos'] = usuarios['pts_grupos_calc']

                if campeon_real:
                    camps_data = supabase.table('champion_predictions').select('*').execute().data
                    if camps_data:
                        df_c = pd.DataFrame(camps_data)
                        df_c['pts_camp'] = df_c['prediction'].apply(lambda x: 15 if x == campeon_real else 0)
                        df_c['pts_sub'] = df_c['subcampeon'].apply(lambda x: 8 if str(x) == str(subcampeon_real) else 0)
                        df_c['pts_ter'] = df_c['tercero'].apply(lambda x: 5 if str(x) == str(tercero_real) else 0)
                        df_c['acerto_campeon'] = df_c['prediction'].apply(lambda x: 1 if x == campeon_real else 0)
                        
                        df_c['pts_podio'] = df_c['pts_camp'] + df_c['pts_sub'] + df_c['pts_ter']
                        usuarios = pd.merge(usuarios, df_c[['email', 'pts_podio', 'acerto_campeon']], on='email', how='left').fillna(0)
                        usuarios['Total'] += usuarios['pts_podio']
                        usuarios['acerto_campeon'] = usuarios['acerto_campeon_y'] if 'acerto_campeon_y' in usuarios.columns else 0

                ranking_final = usuarios[['username', 'Total', 'acerto_campeon', 'pts_grupos']].sort_values(
                    by=['Total', 'acerto_campeon', 'pts_grupos'], ascending=[False, False, False]
                ).reset_index(drop=True)
                
                ranking_final['Total'] = ranking_final['Total'].astype(int)
                
                def add_medals(row):
                    if row.name == 0: return f"🥇 {row['username']}"
                    elif row.name == 1: return f"🥈 {row['username']}"
                    elif row.name == 2: return f"🥉 {row['username']}"
                    return row['username']
                
                if not ranking_final.empty:
                    ranking_final['username'] = ranking_final.apply(add_medals, axis=1)
                    ranking_final.index += 1
                st.dataframe(ranking_final[['username', 'Total']], use_container_width=True)

    # --- PESTAÑA 5: ADMIN ---
    if es_admin:
        with app_tabs[4]:
            st.error("🚨 PANEL DE ADMINISTRADOR 🚨")
            
            st.subheader("1. Configurar Llaves y Resultados")
            partido_sel = st.selectbox("Selecciona un partido a editar:", [f"M{m['id']} - {m['fase']}" for m in matches])
            m_id_admin = int(partido_sel.split(" ")[0][1:])
            
            default_a = next(m['default_a'] for m in matches if m['id'] == m_id_admin)
            default_b = next(m['default_b'] for m in matches if m['id'] == m_id_admin)

            sugerencia_a = resolver_llave(default_a, tablas_posiciones, oficiales)
            sugerencia_b = resolver_llave(default_b, tablas_posiciones, oficiales)

            info_guardada = oficiales.get(m_id_admin, {})
            current_a = info_guardada.get('equipo_a') or sugerencia_a
            current_b = info_guardada.get('equipo_b') or sugerencia_b
            val_marc_a = info_guardada.get('marcador_a', 0)
            val_marc_b = info_guardada.get('marcador_b', 0)
            res_guardado = info_guardada.get('real_result', "Pendiente")

            cand_a = list(dict.fromkeys([current_a] + lista_equipos))
            cand_b = list(dict.fromkeys([current_b] + lista_equipos))

            col1, col2 = st.columns(2)
            with col1:
                eq_a_admin = st.selectbox("Equipo A", options=cand_a, index=0, key=f"sel_a_{m_id_admin}")
                marc_a = st.number_input("Goles Equipo A", min_value=0, step=1, value=val_marc_a, key=f"marc_a_{m_id_admin}")
            with col2:
                eq_b_admin = st.selectbox("Equipo B", options=cand_b, index=0, key=f"sel_b_{m_id_admin}")
                marc_b = st.number_input("Goles Equipo B", min_value=0, step=1, value=val_marc_b, key=f"marc_b_{m_id_admin}")
            
            res_opciones = ["Pendiente", eq_a_admin, "Empate", eq_b_admin]
            if res_guardado not in res_opciones: res_guardado = "Pendiente"
            
            resultado_admin = st.selectbox("¿Quién ganó la apuesta?", res_opciones, index=res_opciones.index(res_guardado), key=f"res_{m_id_admin}")
            
            if st.button("Guardar Partido"):
                data = {"match_id": m_id_admin, "equipo_a": eq_a_admin, "equipo_b": eq_b_admin, "marcador_a": marc_a, "marcador_b": marc_b, "real_result": None if resultado_admin == "Pendiente" else resultado_admin}
                supabase.table('results').upsert(data).execute()
                st.success("Partido actualizado.")
                st.rerun()
            
            st.divider()
            
            # --- Tabla Clasificatoria de Terceros ---
            st.subheader("📋 Tabla de Mejores Terceros (Top 8 Avanzan a 16vos)")
            terceros = []
            for g, tabla in tablas_posiciones.items():
                equipos = list(tabla.keys())
                if len(equipos) >= 3:
                    eq = equipos[2]
                    stats = tabla[eq]
                    if stats['PJ'] > 0:
                        terceros.append({"Grupo": g, "Equipo": eq, "PTS": stats['PTS'], "DIF": stats['DIF'], "GF": stats['GF']})
            
            if terceros:
                df_terceros = pd.DataFrame(terceros)
                df_terceros = df_terceros.sort_values(by=['PTS', 'DIF', 'GF'], ascending=[False, False, False]).reset_index(drop=True)
                df_terceros.index += 1
                def highlight_top8(s): return ['background-color: #2E8B57' if s.name <= 8 else '' for v in s]
                st.dataframe(df_terceros.style.apply(highlight_top8, axis=1), use_container_width=True)
            else: st.info("Falta que se jueguen partidos para calcular a los terceros.")
            
            st.divider()
            st.subheader("2. Finalizar Torneo (Repartir Puntos Globales)")
            c_camp, c_sub, c_ter = st.columns(3)
            with c_camp: camp_oficial = st.selectbox("🥇 Campeón Oficial:", ["Ninguno (Torneo Activo)"] + lista_equipos)
            with c_sub: sub_oficial = st.selectbox("🥈 Subcampeón Oficial:", ["Ninguno (Torneo Activo)"] + lista_equipos)
            with c_ter: ter_oficial = st.selectbox("🥉 Tercer Lugar Oficial:", ["Ninguno (Torneo Activo)"] + lista_equipos)
                
            if st.button("Establecer Podio Global"):
                data_torneo = {"id": 1, "actual_champion": None if camp_oficial == "Ninguno (Torneo Activo)" else camp_oficial, "actual_subcampeon": None if sub_oficial == "Ninguno (Torneo Activo)" else sub_oficial, "actual_tercero": None if ter_oficial == "Ninguno (Torneo Activo)" else ter_oficial}
                supabase.table('tournament_settings').upsert(data_torneo).execute()
                st.success("Configuración de Podio Oficial guardada.")
                st.rerun()
