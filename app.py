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
    "A": ["🇲🇽 México", "🇿🇦 Sudáfrica", "🇰🇷 Corea del Sur", "🇨🇿 Chequia"],
    "B": ["🇨🇦 Canadá", "🇧🇦 Bosnia y Herz.", "🇶🇦 Catar", "🇨🇭 Suiza"],
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

lista_equipos = [eq for grupo in grupos_equipos.values() for eq in grupo] + ["Por definir", "Otro"]

# --- MATRIZ OFICIAL DE LOS 104 PARTIDOS (Mapeada exacta al PDF de FIFA) ---
raw_schedule = f"""
1|2026-06-11 13:00|🇲🇽 México|🇿🇦 Sudáfrica|Grupo A
2|2026-06-11 20:00|🇰🇷 Corea del Sur|🇨🇿 Chequia|Grupo A
3|2026-06-12 13:00|🇨🇦 Canadá|🇧🇦 Bosnia y Herz.|Grupo B
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
26|2026-06-18 13:00|🇨🇭 Suiza|🇧🇦 Bosnia y Herz.|Grupo B
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
52|2026-06-24 13:00|🇧🇦 Bosnia y Herz.|🇶🇦 Catar|Grupo B
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
    matches.append({
        "id": int(parts[0]),
        "fecha_base": parts[1] + ":00",
        "default_a": parts[2],
        "default_b": parts[3],
        "fase": parts[4]
    })

# --- FUNCIONES AUXILIARES PARA EL ADMIN ---
def convertir_hora(fecha_base_str, timezone_destino):
    dt_base = pytz.timezone('America/Mexico_City').localize(datetime.strptime(fecha_base_str, '%Y-%m-%d %H:%M:%S'))
    return dt_base.astimezone(pytz.timezone(timezone_destino)).strftime('%d %b %Y - %H:%M')

def get_candidates(label):
    label_clean = label.strip()
    if label_clean.startswith("1") or label_clean.startswith("2"):
        grupo = label_clean[1]
        return grupos_equipos.get(grupo, []) + ["Por definir", "Otro"]
    elif "Mejor 3°" in label_clean:
        grupos_str = label_clean.split("(")[1].split(")")[0]
        cands = []
        for g in grupos_str.split("/"):
            cands.extend(grupos_equipos.get(g, []))
        return cands + ["Por definir", "Otro"]
    return [label_clean] + lista_equipos

def get_winner_loser_candidates(label, oficiales):
    if label.startswith("Ganador M"):
        m_id = int(label.replace("Ganador M", ""))
        res = oficiales.get(m_id, {}).get("real_result")
        if res and res not in ["Pendiente", "Empate"]:
            return [res] + lista_equipos
    elif label.startswith("Perdedor M"):
        m_id = int(label.replace("Perdedor M", ""))
        res = oficiales.get(m_id, {}).get("real_result")
        eq_a = oficiales.get(m_id, {}).get("equipo_a")
        eq_b = oficiales.get(m_id, {}).get("equipo_b")
        if res and res not in ["Pendiente", "Empate"] and eq_a and eq_b:
            loser = eq_b if res == eq_a else eq_a
            return [loser] + lista_equipos
    return [label] + lista_equipos


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
            st.error("⛔ La selección de campeón se cerró al finalizar el Partido M4.")
            st.info(f"Tu elección guardada es: **{mi_campeon}**")
        else:
            st.write("Acierta al campeón del mundo y gana 15 puntos extra al final del torneo.")
            st.success(f"Tu selección actual: **{mi_campeon}**")
            
            nuevo_campeon = st.selectbox("Selecciona tu candidato:", lista_equipos)
            if st.button("Guardar Campeón"):
                st.session_state.confirm_champion = nuevo_campeon

            if 'confirm_champion' in st.session_state:
                st.warning(f"⚠️ ¿Estás seguro de elegir a **{st.session_state.confirm_champion}**? Una vez que el Partido M4 inicie y se registre su resultado, no podrás cambiar tu decisión.")
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

            # Restricciones estrictas según la fase
            if m_id_admin <= 72:
                cand_a, cand_b = [default_a], [default_b]
            elif 73 <= m_id_admin <= 88:
                cand_a = get_candidates(default_a)
                cand_b = get_candidates(default_b)
            else:
                cand_a = get_winner_loser_candidates(default_a, oficiales)
                cand_b = get_winner_loser_candidates(default_b, oficiales)

            info_guardada = oficiales.get(m_id_admin, {})
            current_a = info_guardada.get('equipo_a') or cand_a[0]
            current_b = info_guardada.get('equipo_b') or cand_b[0]
            val_marc_a = info_guardada.get('marcador_a', 0)
            val_marc_b = info_guardada.get('marcador_b', 0)
            res_guardado = info_guardada.get('real_result', "Pendiente")

            if current_a not in cand_a: cand_a = [current_a] + cand_a
            if current_b not in cand_b: cand_b = [current_b] + cand_b

            col1, col2 = st.columns(2)
            with col1:
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
