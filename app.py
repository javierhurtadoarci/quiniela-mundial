import streamlit as st
import pandas as pd
from supabase import create_client, Client
import pytz
from datetime import datetime

st.set_page_config(page_title="Quiniela Mundial 2026", page_icon="🏆", layout="wide")

# --- CONEXIÓN A SUPABASE ---
@st.cache_resource
def init_connection():
    return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])

supabase: Client = init_connection()

# --- CONFIGURACIÓN DE EQUIPOS Y GRUPOS ---
flag_ing = "\U0001F3F4\U000E0067\U000E0062\U000E0065\U000E006E\U000E0067\U000E007F"
flag_sct = "\U0001F3F4\U000E0067\U000E0062\U000E0073\U000E0063\U000E0074\U000E007F"

grupos_equipos = {
    "A": ["🇲🇽 México", "🇿🇦 Sudáfrica", "🇰🇷 Corea del Sur", "🇨🇿 Rep. Checa"],
    "B": ["🇨🇦 Canadá", "🇧🇦 Bosnia y Herz.", "🇶🇦 Catar", "🇨🇭 Suiza"],
    "C": ["🇧🇷 Brasil", "🇲🇦 Marruecos", "🇭🇹 Haití", f"{flag_sct} Escocia"],
    "D": ["🇺🇸 USA", "🇹🇷 Turquía", "🇵🇾 Paraguay", "🇦🇺 Australia"],
    "E": ["🇩🇪 Alemania", "🇨🇼 Curazao", "🇨🇮 Costa de Marfil", "🇪🇨 Ecuador"],
    "F": ["🇳🇱 Países Bajos", "🇯🇵 Japón", "🇸🇪 Suecia", "🇹🇳 Túnez"],
    "G": ["🇧🇪 Bélgica", "🇪🇬 Egipto", "🇮🇷 Irán", "🇳🇿 Nueva Zelanda"],
    "H": ["🇪🇸 España", "🇺🇾 Uruguay", "🇨🇻 Cabo Verde", "🇸🇦 Arabia Saudita"],
    "I": ["🇫🇷 Francia", "🇳🇴 Noruega", "🇸🇳 Senegal", "🇮🇶 Irak"],
    "J": ["🇦🇷 Argentina", "🇦🇹 Austria", "🇩🇿 Argelia", "🇯🇴 Jordania"],
    "K": ["🇵🇹 Portugal", "🇨🇴 Colombia", "🇺🇿 Uzbekistán", "🇨🇩 RD Congo"],
    "L": [f"{flag_ing} Inglaterra", "🇭🇷 Croacia", "🇬🇭 Ghana", "🇵🇦 Panamá"]
}

# Llaves oficiales de la FIFA para Dieciseisavos (M73 a M88)
llaves_32_oficial = {
    73: "2A vs 2B",
    74: "1E vs 3A/B/C/D/F",
    75: "1I vs 3C/D/F/G/H",
    76: "2G vs 2H",
    77: "1C vs 3A/B/F/G/H",
    78: "2I vs 2L",
    79: "1A vs 3C/E/F/H/I",
    80: "1L vs 3E/H/I/J/K",
    81: "1D vs 3B/E/G/I/J",
    82: "2D vs 2E",
    83: "1K vs 3D/E/I/J/L",
    84: "1J vs 2H",
    85: "1B vs 3E/G/H/I/K",
    86: "1F vs 2C",
    87: "1G vs 3A/B/D/E/F",
    88: "1H vs 2J"
}

lista_equipos = [equipo for grupo in grupos_equipos.values() for equipo in grupo] + ["Por definir", "Otro"]

# --- GENERACIÓN DE LOS 104 PARTIDOS ---
matches = [
    # JORNADA 1
    {"id": 1, "fase": "Grupo A", "default_a": grupos_equipos["A"][0], "default_b": grupos_equipos["A"][1], "fecha_base": "2026-06-11 13:00:00"},
    {"id": 2, "fase": "Grupo A", "default_a": grupos_equipos["A"][2], "default_b": grupos_equipos["A"][3], "fecha_base": "2026-06-11 20:00:00"},
    {"id": 3, "fase": "Grupo B", "default_a": grupos_equipos["B"][0], "default_b": grupos_equipos["B"][1], "fecha_base": "2026-06-12 13:00:00"},
    {"id": 4, "fase": "Grupo D", "default_a": grupos_equipos["D"][0], "default_b": grupos_equipos["D"][2], "fecha_base": "2026-06-12 19:00:00"},
    {"id": 5, "fase": "Grupo B", "default_a": grupos_equipos["B"][2], "default_b": grupos_equipos["B"][3], "fecha_base": "2026-06-13 13:00:00"},
    {"id": 6, "fase": "Grupo C", "default_a": grupos_equipos["C"][0], "default_b": grupos_equipos["C"][1], "fecha_base": "2026-06-13 16:00:00"},
    {"id": 7, "fase": "Grupo C", "default_a": grupos_equipos["C"][2], "default_b": grupos_equipos["C"][3], "fecha_base": "2026-06-13 19:00:00"},
    {"id": 8, "fase": "Grupo D", "default_a": grupos_equipos["D"][3], "default_b": grupos_equipos["D"][1], "fecha_base": "2026-06-13 22:00:00"},
    {"id": 9, "fase": "Grupo E", "default_a": grupos_equipos["E"][0], "default_b": grupos_equipos["E"][1], "fecha_base": "2026-06-14 11:00:00"},
    {"id": 10, "fase": "Grupo F", "default_a": grupos_equipos["F"][0], "default_b": grupos_equipos["F"][1], "fecha_base": "2026-06-14 14:00:00"},
    {"id": 11, "fase": "Grupo E", "default_a": grupos_equipos["E"][2], "default_b": grupos_equipos["E"][3], "fecha_base": "2026-06-14 17:00:00"},
    {"id": 12, "fase": "Grupo F", "default_a": grupos_equipos["F"][2], "default_b": grupos_equipos["F"][3], "fecha_base": "2026-06-14 20:00:00"},
    {"id": 13, "fase": "Grupo H", "default_a": grupos_equipos["H"][0], "default_b": grupos_equipos["H"][2], "fecha_base": "2026-06-15 10:00:00"},
    {"id": 14, "fase": "Grupo G", "default_a": grupos_equipos["G"][0], "default_b": grupos_equipos["G"][1], "fecha_base": "2026-06-15 13:00:00"},
    {"id": 15, "fase": "Grupo H", "default_a": grupos_equipos["H"][3], "default_b": grupos_equipos["H"][1], "fecha_base": "2026-06-15 16:00:00"},
    {"id": 16, "fase": "Grupo G", "default_a": grupos_equipos["G"][2], "default_b": grupos_equipos["G"][3], "fecha_base": "2026-06-15 19:00:00"},
    {"id": 17, "fase": "Grupo I", "default_a": grupos_equipos["I"][0], "default_b": grupos_equipos["I"][1], "fecha_base": "2026-06-16 13:00:00"},
    {"id": 18, "fase": "Grupo I", "default_a": grupos_equipos["I"][2], "default_b": grupos_equipos["I"][3], "fecha_base": "2026-06-16 16:00:00"},
    {"id": 19, "fase": "Grupo J", "default_a": grupos_equipos["J"][0], "default_b": grupos_equipos["J"][2], "fecha_base": "2026-06-16 19:00:00"},
    {"id": 20, "fase": "Grupo J", "default_a": grupos_equipos["J"][1], "default_b": grupos_equipos["J"][3], "fecha_base": "2026-06-16 22:00:00"},
    {"id": 21, "fase": "Grupo K", "default_a": grupos_equipos["K"][0], "default_b": grupos_equipos["K"][3], "fecha_base": "2026-06-17 11:00:00"},
    {"id": 22, "fase": "Grupo L", "default_a": grupos_equipos["L"][0], "default_b": grupos_equipos["L"][1], "fecha_base": "2026-06-17 14:00:00"},
    {"id": 23, "fase": "Grupo L", "default_a": grupos_equipos["L"][2], "default_b": grupos_equipos["L"][3], "fecha_base": "2026-06-17 17:00:00"},
    {"id": 24, "fase": "Grupo K", "default_a": grupos_equipos["K"][2], "default_b": grupos_equipos["K"][1], "fecha_base": "2026-06-17 20:00:00"},

    # JORNADA 2
    {"id": 25, "fase": "Grupo A", "default_a": grupos_equipos["A"][3], "default_b": grupos_equipos["A"][1], "fecha_base": "2026-06-18 10:00:00"},
    {"id": 26, "fase": "Grupo B", "default_a": grupos_equipos["B"][3], "default_b": grupos_equipos["B"][1], "fecha_base": "2026-06-18 13:00:00"},
    {"id": 27, "fase": "Grupo B", "default_a": grupos_equipos["B"][0], "default_b": grupos_equipos["B"][2], "fecha_base": "2026-06-18 16:00:00"},
    {"id": 28, "fase": "Grupo A", "default_a": grupos_equipos["A"][0], "default_b": grupos_equipos["A"][2], "fecha_base": "2026-06-18 19:00:00"},
    {"id": 29, "fase": "Grupo D", "default_a": grupos_equipos["D"][0], "default_b": grupos_equipos["D"][3], "fecha_base": "2026-06-19 13:00:00"},
    {"id": 30, "fase": "Grupo C", "default_a": grupos_equipos["C"][3], "default_b": grupos_equipos["C"][1], "fecha_base": "2026-06-19 16:00:00"},
    {"id": 31, "fase": "Grupo C", "default_a": grupos_equipos["C"][0], "default_b": grupos_equipos["C"][2], "fecha_base": "2026-06-19 18:30:00"},
    {"id": 32, "fase": "Grupo D", "default_a": grupos_equipos["D"][1], "default_b": grupos_equipos["D"][2], "fecha_base": "2026-06-19 21:00:00"},
    {"id": 33, "fase": "Grupo F", "default_a": grupos_equipos["F"][0], "default_b": grupos_equipos["F"][2], "fecha_base": "2026-06-20 11:00:00"},
    {"id": 34, "fase": "Grupo E", "default_a": grupos_equipos["E"][0], "default_b": grupos_equipos["E"][2], "fecha_base": "2026-06-20 14:00:00"},
    {"id": 35, "fase": "Grupo E", "default_a": grupos_equipos["E"][3], "default_b": grupos_equipos["E"][1], "fecha_base": "2026-06-20 18:00:00"},
    {"id": 36, "fase": "Grupo F", "default_a": grupos_equipos["F"][3], "default_b": grupos_equipos["F"][1], "fecha_base": "2026-06-20 22:00:00"},
    {"id": 37, "fase": "Grupo H", "default_a": grupos_equipos["H"][0], "default_b": grupos_equipos["H"][3], "fecha_base": "2026-06-21 10:00:00"},
    {"id": 38, "fase": "Grupo G", "default_a": grupos_equipos["G"][0], "default_b": grupos_equipos["G"][2], "fecha_base": "2026-06-21 13:00:00"},
    {"id": 39, "fase": "Grupo H", "default_a": grupos_equipos["H"][1], "default_b": grupos_equipos["H"][2], "fecha_base": "2026-06-21 16:00:00"},
    {"id": 40, "fase": "Grupo G", "default_a": grupos_equipos["G"][3], "default_b": grupos_equipos["G"][1], "fecha_base": "2026-06-21 19:00:00"},
    {"id": 41, "fase": "Grupo I", "default_a": grupos_equipos["I"][0], "default_b": grupos_equipos["I"][3], "fecha_base": "2026-06-22 13:00:00"},
    {"id": 42, "fase": "Grupo I", "default_a": grupos_equipos["I"][2], "default_b": grupos_equipos["I"][1], "fecha_base": "2026-06-22 16:00:00"},
    {"id": 43, "fase": "Grupo J", "default_a": grupos_equipos["J"][0], "default_b": grupos_equipos["J"][1], "fecha_base": "2026-06-22 19:00:00"},
    {"id": 44, "fase": "Grupo J", "default_a": grupos_equipos["J"][2], "default_b": grupos_equipos["J"][3], "fecha_base": "2026-06-22 22:00:00"},
    {"id": 45, "fase": "Grupo K", "default_a": grupos_equipos["K"][0], "default_b": grupos_equipos["K"][2], "fecha_base": "2026-06-23 11:00:00"},
    {"id": 46, "fase": "Grupo K", "default_a": grupos_equipos["K"][1], "default_b": grupos_equipos["K"][3], "fecha_base": "2026-06-23 14:00:00"},
    {"id": 47, "fase": "Grupo L", "default_a": grupos_equipos["L"][0], "default_b": grupos_equipos["L"][2], "fecha_base": "2026-06-23 17:00:00"},
    {"id": 48, "fase": "Grupo L", "default_a": grupos_equipos["L"][1], "default_b": grupos_equipos["L"][3], "fecha_base": "2026-06-23 20:00:00"},

    # JORNADA 3
    {"id": 49, "fase": "Grupo A", "default_a": grupos_equipos["A"][3], "default_b": grupos_equipos["A"][0], "fecha_base": "2026-06-24 13:00:00"},
    {"id": 50, "fase": "Grupo A", "default_a": grupos_equipos["A"][1], "default_b": grupos_equipos["A"][2], "fecha_base": "2026-06-24 13:00:00"},
    {"id": 51, "fase": "Grupo B", "default_a": grupos_equipos["B"][0], "default_b": grupos_equipos["B"][3], "fecha_base": "2026-06-24 17:00:00"},
    {"id": 52, "fase": "Grupo B", "default_a": grupos_equipos["B"][1], "default_b": grupos_equipos["B"][2], "fecha_base": "2026-06-24 17:00:00"},
    {"id": 53, "fase": "Grupo C", "default_a": grupos_equipos["C"][0], "default_b": grupos_equipos["C"][3], "fecha_base": "2026-06-25 13:00:00"},
    {"id": 54, "fase": "Grupo C", "default_a": grupos_equipos["C"][1], "default_b": grupos_equipos["C"][2], "fecha_base": "2026-06-25 13:00:00"},
    {"id": 55, "fase": "Grupo D", "default_a": grupos_equipos["D"][0], "default_b": grupos_equipos["D"][1], "fecha_base": "2026-06-25 17:00:00"},
    {"id": 56, "fase": "Grupo D", "default_a": grupos_equipos["D"][2], "default_b": grupos_equipos["D"][3], "fecha_base": "2026-06-25 17:00:00"},
    {"id": 57, "fase": "Grupo E", "default_a": grupos_equipos["E"][0], "default_b": grupos_equipos["E"][3], "fecha_base": "2026-06-26 13:00:00"},
    {"id": 58, "fase": "Grupo E", "default_a": grupos_equipos["E"][1], "default_b": grupos_equipos["E"][2], "fecha_base": "2026-06-26 13:00:00"},
    {"id": 59, "fase": "Grupo F", "default_a": grupos_equipos["F"][0], "default_b": grupos_equipos["F"][3], "fecha_base": "2026-06-26 17:00:00"},
    {"id": 60, "fase": "Grupo F", "default_a": grupos_equipos["F"][1], "default_b": grupos_equipos["F"][2], "fecha_base": "2026-06-26 17:00:00"},
    {"id": 61, "fase": "Grupo G", "default_a": grupos_equipos["G"][0], "default_b": grupos_equipos["G"][3], "fecha_base": "2026-06-27 13:00:00"},
    
    # Partido M62 Específico: Senegal vs Irak
    {"id": 62, "fase": "Grupo I", "default_a": grupos_equipos["I"][1], "default_b": grupos_equipos["I"][3], "fecha_base": "2026-06-27 13:00:00"},
    
    {"id": 63, "fase": "Grupo H", "default_a": grupos_equipos["H"][0], "default_b": grupos_equipos["H"][1], "fecha_base": "2026-06-27 17:00:00"},
    {"id": 64, "fase": "Grupo H", "default_a": grupos_equipos["H"][2], "default_b": grupos_equipos["H"][3], "fecha_base": "2026-06-27 17:00:00"},
    {"id": 65, "fase": "Grupo I", "default_a": grupos_equipos["I"][0], "default_b": grupos_equipos["I"][2], "fecha_base": "2026-06-28 13:00:00"},
    {"id": 66, "fase": "Grupo G", "default_a": grupos_equipos["G"][1], "default_b": grupos_equipos["G"][2], "fecha_base": "2026-06-28 13:00:00"},
    {"id": 67, "fase": "Grupo J", "default_a": grupos_equipos["J"][0], "default_b": grupos_equipos["J"][3], "fecha_base": "2026-06-28 17:00:00"},
    {"id": 68, "fase": "Grupo J", "default_a": grupos_equipos["J"][2], "default_b": grupos_equipos["J"][1], "fecha_base": "2026-06-28 17:00:00"},
    {"id": 69, "fase": "Grupo K", "default_a": grupos_equipos["K"][0], "default_b": grupos_equipos["K"][1], "fecha_base": "2026-06-29 13:00:00"},
    {"id": 70, "fase": "Grupo K", "default_a": grupos_equipos["K"][3], "default_b": grupos_equipos["K"][2], "fecha_base": "2026-06-29 13:00:00"},
    {"id": 71, "fase": "Grupo L", "default_a": grupos_equipos["L"][0], "default_b": grupos_equipos["L"][3], "fecha_base": "2026-06-29 17:00:00"},
    {"id": 72, "fase": "Grupo L", "default_a": grupos_equipos["L"][1], "default_b": grupos_equipos["L"][2], "fecha_base": "2026-06-29 17:00:00"}
]

# --- FASE ELIMINATORIA (Con Llaves Oficiales FIFA) ---
fechas_16vos = ["2026-06-28", "2026-06-29", "2026-06-30", "2026-07-01", "2026-07-02", "2026-07-03"]
for i in range(73, 89):
    cruce_oficial = llaves_32_oficial[i].split(" vs ")
    matches.append({
        "id": i, "fase": "Dieciseisavos (32)", 
        "default_a": cruce_oficial[0], "default_b": cruce_oficial[1], 
        "fecha_base": f"{fechas_16vos[(i - 73) % 6]} 18:00:00"
    })

dia_oct = 4
for i in range(89, 97):
    m_a, m_b = 73 + (i - 89) * 2, 74 + (i - 89) * 2
    matches.append({"id": i, "fase": "Octavos (16)", "default_a": f"Ganador M{m_a}", "default_b": f"Ganador M{m_b}", "fecha_base": f"2026-07-0{dia_oct} 18:00:00"})
    if i % 2 == 0: dia_oct += 1

dia_cua = 9
for i in range(97, 101):
    m_a, m_b = 89 + (i - 97) * 2, 90 + (i - 97) * 2
    matches.append({"id": i, "fase": "Cuartos (8)", "default_a": f"Ganador M{m_a}", "default_b": f"Ganador M{m_b}", "fecha_base": f"2026-07-{dia_cua:02d} 18:00:00"})
    if i % 2 == 0: dia_cua += 1

matches.append({"id": 101, "fase": "Semifinal 1", "default_a": "Ganador M97", "default_b": "Ganador M98", "fecha_base": "2026-07-14 18:00:00"})
matches.append({"id": 102, "fase": "Semifinal 2", "default_a": "Ganador M99", "default_b": "Ganador M100", "fecha_base": "2026-07-15 18:00:00"})
matches.append({"id": 103, "fase": "Tercer Lugar", "default_a": "Perdedor M101", "default_b": "Perdedor M102", "fecha_base": "2026-07-18 18:00:00"})
matches.append({"id": 104, "fase": "FINAL", "default_a": "Ganador M101", "default_b": "Ganador M102", "fecha_base": "2026-07-19 18:00:00"})


# --- FUNCIONES AUXILIARES ---
def convertir_hora(fecha_base_str, timezone_destino):
    dt_base = pytz.timezone('America/Mexico_City').localize(datetime.strptime(fecha_base_str, '%Y-%m-%d %H:%M:%S'))
    return dt_base.astimezone(pytz.timezone(timezone_destino)).strftime('%d %b %Y - %H:%M')


# --- SISTEMA DE AUTENTICACIÓN ---
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("⚽ Quiniela Mundial 2026")
    tab_login, tab_registro = st.tabs(["Ingresar", "Registrarse"])
    
    with tab_login:
        with st.form("form_login"):
            st.text_input("Correo Electrónico", key="login_email_input")
            st.text_input("Contraseña", type="password", key="login_pass_input")
            submit_btn = st.form_submit_button("Entrar")
            
            if submit_btn:
                email_actual = st.session_state.login_email_input
                pass_actual = st.session_state.login_pass_input
                
                if email_actual and pass_actual:
                    try:
                        res = supabase.auth.sign_in_with_password({
                            "email": email_actual, 
                            "password": pass_actual
                        })
                        st.session_state.user = res.user
                        st.rerun()
                    except Exception as e:
                        if "Invalid login credentials" in str(e):
                            st.error("Credenciales incorrectas. Revisa tu correo o contraseña.")
                        else:
                            st.error(f"Hubo un error de conexión: {e}")
                else:
                    st.warning("Por favor, llena ambos campos antes de entrar.")

    with tab_registro:
        email_reg = st.text_input("Correo", key="reg_email")
        pass_reg = st.text_input("Contraseña (Mínimo 6)", type="password", key="reg_pass")
        username = st.text_input("Nombre para el Ranking")
        if st.button("Registrarse"):
            try:
                supabase.auth.sign_up({"email": email_reg, "password": pass_reg})
                supabase.table('users').insert({"username": username, "email": email_reg}).execute()
                st.success("¡Registrado! Ahora inicia sesión.")
            except Exception as e:
                st.error(f"Error: {e}")

# --- APLICACIÓN PRINCIPAL ---
else:
    user_email = st.session_state.user.email
    
    try:
        user_record = supabase.table('users').select('username').eq('email', user_email).execute().data
        display_name = user_record[0]['username'] if user_record else user_email
    except:
        display_name = user_email
        
    st.sidebar.success(f"👤 Hola, {display_name}")
    if st.sidebar.button("Cerrar Sesión"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    user_tz = st.sidebar.selectbox("🌍 Tu Zona Horaria", pytz.all_timezones, index=pytz.all_timezones.index('America/Mexico_City'))

    # Cargar datos globales
    try:
        res_db = supabase.table('results').select('*').execute().data
        oficiales = {r['match_id']: r for r in res_db}
        torneo_db = supabase.table('tournament_settings').select('*').eq('id', 1).execute().data
        campeon_real = torneo_db[0]['actual_champion'] if torneo_db else None
    except:
        oficiales = {}
        campeon_real = None

    es_admin = user_email == "adam666.die@gmail.com" # <--- RECUERDA PONER AQUÍ TU CORREO DE ADMIN
    tabs = ["📝 Pronósticos", "👑 Campeón (15 pts)", "📊 Ranking"]
    if es_admin:
        tabs.append("⚙️ Panel Admin")

    app_tabs = st.tabs(tabs)

    # --- PESTAÑA 1: PRONÓSTICOS ---
    with app_tabs[0]:
        st.header("Tus Pronósticos")
        try:
            mis_preds = {row['match_id']: row['prediction'] for row in supabase.table('predictions').select('*').eq('email', user_email).execute().data}
        except:
            mis_preds = {}

        for match in matches:
            m_id = match['id']
            eq_a = oficiales.get(m_id, {}).get('equipo_a') or match['default_a']
            eq_b = oficiales.get(m_id, {}).get('equipo_b') or match['default_b']
            resultado_oficial = oficiales.get(m_id, {}).get('real_result')
            
            with st.container():
                st.markdown(f"**M{m_id} | {match['fase']} | 🕒 {convertir_hora(match['fecha_base'], user_tz)}**")
                
                if resultado_oficial:
                    st.info(f"🔒 PARTIDO FINALIZADO: {eq_a} [{oficiales[m_id]['marcador_a']}] vs [{oficiales[m_id]['marcador_b']}] {eq_b} | Resultado: **{resultado_oficial}**")
                    st.write(f"Tu pronóstico fue: {mis_preds.get(m_id, 'Ninguno')}")
                else:
                    st.markdown(f"### {eq_a} vs {eq_b}")
                    opciones = [eq_a, "Empate", eq_b]
                    idx = opciones.index(mis_preds[m_id]) if mis_preds.get(m_id) in opciones else None
                    
                    seleccion = st.radio(f"Gana M{m_id}", opciones, index=idx, key=f"p_{m_id}", horizontal=True, label_visibility="collapsed")
                    if st.button("Guardar Pronóstico", key=f"b_{m_id}"):
                        data_pronostico = {"email": user_email, "match_id": m_id, "prediction": seleccion}
                        supabase.table('predictions').upsert(data_pronostico, on_conflict="email,match_id").execute()
                        st.toast(f"M{m_id} Guardado", icon="✅")
                        st.rerun()
                st.divider()

    # --- PESTAÑA 2: CAMPEÓN ---
    with app_tabs[1]:
        st.header("👑 Predicción del Campeón")
        
        # Bloqueo estricto si el Partido 4 ya fue calificado por el admin
        m4_cerrado = oficiales.get(4, {}).get('real_result') is not None
        
        try:
            mi_campeon_db = supabase.table('champion_predictions').select('prediction').eq('email', user_email).execute().data
            mi_campeon = mi_campeon_db[0]['prediction'] if mi_campeon_db else "No seleccionado"
        except:
            mi_campeon = "No seleccionado"

        if campeon_real:
            st.error(f"El torneo ha terminado. El campeón oficial es: **{campeon_real}**")
            st.info(f"Tu elección fue: {mi_campeon}")
        elif m4_cerrado:
            st.error("⛔ La selección de campeón se cerró al finalizar el Partido 4.")
            st.info(f"Tu elección guardada es: **{mi_campeon}**")
        else:
            st.write("Acierta al campeón del mundo y gana 15 puntos extra al final del torneo.")
            st.success(f"Tu selección actual: **{mi_campeon}**")
            
            nuevo_campeon = st.selectbox("Selecciona tu candidato:", lista_equipos)
            if st.button("Guardar Campeón"):
                st.session_state.confirm_champion = nuevo_campeon

            if 'confirm_champion' in st.session_state:
                st.warning(f"⚠️ ¿Estás seguro de elegir a **{st.session_state.confirm_champion}**? Una vez que se asigne resultado al Partido 4, no podrás cambiar tu decisión.")
                c1, c2 = st.columns(2)
                if c1.button("✅ Aceptar y Guardar"):
                    supabase.table('champion_predictions').upsert({"email": user_email, "prediction": st.session_state.confirm_champion}).execute()
                    del st.session_state.confirm_champion
                    st.success("¡Campeón guardado correctamente!")
                    st.rerun()
                if c2.button("❌ Cancelar"):
                    del st.session_state.confirm_champion
                    st.rerun()

    # --- PESTAÑA 3: RANKING ---
    with app_tabs[2]:
        st.header("📊 Tabla de Posiciones")
        if st.button("🔄 Actualizar Ranking", type="primary"):
            usuarios_data = supabase.table('users').select('email', 'username').execute().data
            
            if not usuarios_data:
                st.info("Aún no hay usuarios registrados.")
            else:
                usuarios = pd.DataFrame(usuarios_data)
                usuarios['Total'] = 0 
                
                preds_data = supabase.table('predictions').select('*').execute().data
                res_data = supabase.table('results').select('*').execute().data
                
                if preds_data and res_data:
                    df_p = pd.DataFrame(preds_data)
                    df_r = pd.DataFrame(res_data)
                    df_r = df_r.dropna(subset=['real_result']) 
                    
                    if not df_r.empty:
                        cruce = pd.merge(df_p, df_r[['match_id', 'real_result']], on='match_id', how='inner')
                        cruce['puntos'] = cruce.apply(lambda x: 2 if x['prediction'] == x['real_result'] else 0, axis=1)
                        pts_partidos = cruce.groupby('email')['puntos'].sum().reset_index()
                        
                        usuarios = pd.merge(usuarios, pts_partidos, on='email', how='left').fillna(0)
                        usuarios['Total'] += usuarios['puntos']
                        usuarios = usuarios.drop(columns=['puntos'])

                if campeon_real:
                    camps_data = supabase.table('champion_predictions').select('*').execute().data
                    if camps_data:
                        df_c = pd.DataFrame(camps_data)
                        df_c['pts_camp'] = df_c['prediction'].apply(lambda x: 15 if x == campeon_real else 0)
                        
                        usuarios = pd.merge(usuarios, df_c[['email', 'pts_camp']], on='email', how='left').fillna(0)
                        usuarios['Total'] += usuarios['pts_camp']
                        usuarios = usuarios.drop(columns=['pts_camp'])

                ranking_final = usuarios[['username', 'Total']].sort_values(by='Total', ascending=False).reset_index(drop=True)
                ranking_final['Total'] = ranking_final['Total'].astype(int)
                
                # Asignación de Medallas al Top 3
                def add_medals(row):
                    if row.name == 0: return f"🥇 {row['username']}"
                    elif row.name == 1: return f"🥈 {row['username']}"
                    elif row.name == 2: return f"🥉 {row['username']}"
                    else: return row['username']
                
                if not ranking_final.empty:
                    ranking_final['username'] = ranking_final.apply(add_medals, axis=1)
                    ranking_final.index += 1
                
                st.dataframe(ranking_final, use_container_width=True)

    # --- PESTAÑA 4: ADMIN ---
    if es_admin:
        with app_tabs[3]:
            st.error("🚨 PANEL DE ADMINISTRADOR 🚨")
            
            st.subheader("1. Configurar Llaves y Resultados")
            partido_sel = st.selectbox("Selecciona un partido a editar:", [f"M{m['id']} - {m['fase']}" for m in matches])
            m_id_admin = int(partido_sel.split(" ")[0][1:])
            
            default_a = next(m['default_a'] for m in matches if m['id'] == m_id_admin)
            default_b = next(m['default_b'] for m in matches if m['id'] == m_id_admin)

            if m_id_admin <= 72:
                cand_a, cand_b = [default_a], [default_b]
            else:
                cand_a = [default_a] + lista_equipos if default_a not in lista_equipos else lista_equipos
                cand_b = [default_b] + lista_equipos if default_b not in lista_equipos else lista_equipos

            # Si el partido no tiene datos guardados, info_guardada estará vacía y tomará los defaults (0 y Pendiente)
            info_guardada = oficiales.get(m_id_admin, {})
            current_a = info_guardada.get('equipo_a') or cand_a[0]
            current_b = info_guardada.get('equipo_b') or cand_b[0]
            
            # Aquí garantizamos el "Reset visual" al cambiar de partido
            val_marc_a = info_guardada.get('marcador_a', 0)
            val_marc_b = info_guardada.get('marcador_b', 0)
            res_guardado = info_guardada.get('real_result', "Pendiente")

            if current_a not in cand_a: cand_a = [current_a] + cand_a
            if current_b not in cand_b: cand_b = [current_b] + cand_b

            col1, col2 = st.columns(2)
            with col1:
                # El key dinámico fuerza a que el componente se redibuje limpio cada vez que cambias el partido en el selectbox
                eq_a_admin = st.selectbox("Equipo A", options=cand_a, index=cand_a.index(current_a), key=f"sel_a_{m_id_admin}")
                marc_a = st.number_input("Goles Equipo A", min_value=0, step=1, value=val_marc_a, key=f"marc_a_{m_id_admin}")
            with col2:
                eq_b_admin = st.selectbox("Equipo B", options=cand_b, index=cand_b.index(current_b), key=f"sel_b_{m_id_admin}")
                marc_b = st.number_input("Goles Equipo B", min_value=0, step=1, value=val_marc_b, key=f"marc_b_{m_id_admin}")
            
            res_opciones = ["Pendiente", eq_a_admin, "Empate", eq_b_admin]
            if res_guardado not in res_opciones: res_guardado = "Pendiente"
            
            resultado_admin = st.selectbox("¿Quién ganó la apuesta?", res_opciones, index=res_opciones.index(res_guardado), key=f"res_{m_id_admin}")
            
            if st.button("Guardar Partido"):
                data = {
                    "match_id": m_id_admin, "equipo_a": eq_a_admin, "equipo_b": eq_b_admin,
                    "marcador_a": marc_a, "marcador_b": marc_b,
                    "real_result": None if resultado_admin == "Pendiente" else resultado_admin
                }
                supabase.table('results').upsert(data).execute()
                st.success("Partido actualizado.")
                st.rerun()
            
            st.divider()
            st.subheader("2. Finalizar Torneo (Otorgar 15 pts)")
            camp_oficial = st.selectbox("Selecciona al Campeón Oficial:", ["Ninguno (Torneo Activo)"] + lista_equipos)
            if st.button("Establecer Campeón Global"):
                val = None if camp_oficial == "Ninguno (Torneo Activo)" else camp_oficial
                supabase.table('tournament_settings').upsert({"id": 1, "actual_champion": val}).execute()
                st.success("Configuración de campeón guardada.")
                st.rerun()
