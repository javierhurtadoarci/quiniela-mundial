import streamlit as st
import pandas as pd
from supabase import create_client, Client
import pytz
from datetime import datetime

st.set_page_config(page_title="Quiniela Mundial 2026 Fam Arciniega", page_icon="🏆", layout="wide")

# --- CONEXIÓN A SUPABASE ---
@st.cache_resource
def init_connection():
    return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])

supabase: Client = init_connection()

# --- GENERACIÓN DE LOS 104 PARTIDOS ---
matches = [
    # --- JORNADA 1 ---
    {"id": 1, "fase": "Grupo A", "default_a": "🇲🇽 México", "default_b": "🇿🇦 Sudáfrica", "fecha_base": "2026-06-11 13:00:00"},
    {"id": 2, "fase": "Grupo A", "default_a": "🇰🇷 Corea del Sur", "default_b": "🇨🇿 Rep. Checa", "fecha_base": "2026-06-11 20:00:00"},
    {"id": 3, "fase": "Grupo B", "default_a": "🇨🇦 Canadá", "default_b": "🇧🇦 Bosnia y Herz.", "fecha_base": "2026-06-12 13:00:00"},
    {"id": 4, "fase": "Grupo D", "default_a": "🇺🇸 USA", "default_b": "🇵🇾 Paraguay", "fecha_base": "2026-06-12 19:00:00"},
    {"id": 5, "fase": "Grupo B", "default_a": "🇶🇦 Catar", "default_b": "🇨🇭 Suiza", "fecha_base": "2026-06-13 13:00:00"},
    {"id": 6, "fase": "Grupo C", "default_a": "🇧🇷 Brasil", "default_b": "🇲🇦 Marruecos", "fecha_base": "2026-06-13 16:00:00"},
    {"id": 7, "fase": "Grupo C", "default_a": "🇭🇹 Haití", "default_b": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia", "fecha_base": "2026-06-13 19:00:00"},
    {"id": 8, "fase": "Grupo D", "default_a": "🇦🇺 Australia", "default_b": "🇹🇷 Turquía", "fecha_base": "2026-06-13 22:00:00"},
    {"id": 9, "fase": "Grupo E", "default_a": "🇩🇪 Alemania", "default_b": "🇨🇼 Curazao", "fecha_base": "2026-06-14 11:00:00"},
    {"id": 10, "fase": "Grupo F", "default_a": "🇳🇱 Países Bajos", "default_b": "🇯🇵 Japón", "fecha_base": "2026-06-14 14:00:00"},
    {"id": 11, "fase": "Grupo E", "default_a": "🇨🇮 Costa de Marfil", "default_b": "🇪🇨 Ecuador", "fecha_base": "2026-06-14 17:00:00"},
    {"id": 12, "fase": "Grupo F", "default_a": "🇸🇪 Suecia", "default_b": "🇹🇳 Túnez", "fecha_base": "2026-06-14 20:00:00"},
    {"id": 13, "fase": "Grupo H", "default_a": "🇪🇸 España", "default_b": "🇨🇻 Cabo Verde", "fecha_base": "2026-06-15 10:00:00"},
    {"id": 14, "fase": "Grupo G", "default_a": "🇧🇪 Bélgica", "default_b": "🇪🇬 Egipto", "fecha_base": "2026-06-15 13:00:00"},
    {"id": 15, "fase": "Grupo H", "default_a": "🇸🇦 Arabia Saudita", "default_b": "🇺🇾 Uruguay", "fecha_base": "2026-06-15 16:00:00"},
    {"id": 16, "fase": "Grupo G", "default_a": "🇮🇷 Irán", "default_b": "🇳🇿 Nueva Zelanda", "fecha_base": "2026-06-15 19:00:00"},
    {"id": 17, "fase": "Grupo I", "default_a": "🇫🇷 Francia", "default_b": "🇸🇳 Senegal", "fecha_base": "2026-06-16 13:00:00"},
    {"id": 18, "fase": "Grupo I", "default_a": "🇮🇶 Irak", "default_b": "🇳🇴 Noruega", "fecha_base": "2026-06-16 16:00:00"},
    {"id": 19, "fase": "Grupo J", "default_a": "🇦🇷 Argentina", "default_b": "🇩🇿 Argelia", "fecha_base": "2026-06-16 19:00:00"},
    {"id": 20, "fase": "Grupo J", "default_a": "🇦🇹 Austria", "default_b": "🇯🇴 Jordania", "fecha_base": "2026-06-16 22:00:00"},
    {"id": 21, "fase": "Grupo K", "default_a": "🇵🇹 Portugal", "default_b": "🇨🇩 RD Congo", "fecha_base": "2026-06-17 11:00:00"},
    {"id": 22, "fase": "Grupo L", "default_a": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra", "default_b": "🇭🇷 Croacia", "fecha_base": "2026-06-17 14:00:00"},
    {"id": 23, "fase": "Grupo L", "default_a": "🇬🇭 Ghana", "default_b": "🇵🇦 Panamá", "fecha_base": "2026-06-17 17:00:00"},
    {"id": 24, "fase": "Grupo K", "default_a": "🇺🇿 Uzbekistán", "default_b": "🇨🇴 Colombia", "fecha_base": "2026-06-17 20:00:00"},

    # --- JORNADA 2 ---
    {"id": 25, "fase": "Grupo A", "default_a": "🇨🇿 Rep. Checa", "default_b": "🇿🇦 Sudáfrica", "fecha_base": "2026-06-18 10:00:00"},
    {"id": 26, "fase": "Grupo B", "default_a": "🇨🇭 Suiza", "default_b": "🇧🇦 Bosnia y Herz.", "fecha_base": "2026-06-18 13:00:00"},
    {"id": 27, "fase": "Grupo B", "default_a": "🇨🇦 Canadá", "default_b": "🇶🇦 Catar", "fecha_base": "2026-06-18 16:00:00"},
    {"id": 28, "fase": "Grupo A", "default_a": "🇲🇽 México", "default_b": "🇰🇷 Corea del Sur", "fecha_base": "2026-06-18 19:00:00"},
    {"id": 29, "fase": "Grupo D", "default_a": "🇺🇸 USA", "default_b": "🇦🇺 Australia", "fecha_base": "2026-06-19 13:00:00"},
    {"id": 30, "fase": "Grupo C", "default_a": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia", "default_b": "🇲🇦 Marruecos", "fecha_base": "2026-06-19 16:00:00"},
    {"id": 31, "fase": "Grupo C", "default_a": "🇧🇷 Brasil", "default_b": "🇭🇹 Haití", "fecha_base": "2026-06-19 18:30:00"},
    {"id": 32, "fase": "Grupo D", "default_a": "🇹🇷 Turquía", "default_b": "🇵🇾 Paraguay", "fecha_base": "2026-06-19 21:00:00"},
    {"id": 33, "fase": "Grupo F", "default_a": "🇳🇱 Países Bajos", "default_b": "🇸🇪 Suecia", "fecha_base": "2026-06-20 11:00:00"},
    {"id": 34, "fase": "Grupo E", "default_a": "🇩🇪 Alemania", "default_b": "🇨🇮 Costa de Marfil", "fecha_base": "2026-06-20 14:00:00"},
    {"id": 35, "fase": "Grupo E", "default_a": "🇪🇨 Ecuador", "default_b": "🇨🇼 Curazao", "fecha_base": "2026-06-20 18:00:00"},
    {"id": 36, "fase": "Grupo F", "default_a": "🇹🇳 Túnez", "default_b": "🇯🇵 Japón", "fecha_base": "2026-06-20 22:00:00"},
    {"id": 37, "fase": "Grupo H", "default_a": "🇪🇸 España", "default_b": "🇸🇦 Arabia Saudita", "fecha_base": "2026-06-21 10:00:00"},
    {"id": 38, "fase": "Grupo G", "default_a": "🇧🇪 Bélgica", "default_b": "🇮🇷 Irán", "fecha_base": "2026-06-21 13:00:00"},
    {"id": 39, "fase": "Grupo H", "default_a": "🇺🇾 Uruguay", "default_b": "🇨🇻 Cabo Verde", "fecha_base": "2026-06-21 16:00:00"},
    {"id": 40, "fase": "Grupo G", "default_a": "🇳🇿 Nueva Zelanda", "default_b": "🇪🇬 Egipto", "fecha_base": "2026-06-21 19:00:00"},
    {"id": 41, "fase": "Grupo I", "default_a": "🇫🇷 Francia", "default_b": "🇮🇶 Irak", "fecha_base": "2026-06-22 13:00:00"},
    {"id": 42, "fase": "Grupo I", "default_a": "🇸🇳 Senegal", "default_b": "🇳🇴 Noruega", "fecha_base": "2026-06-22 16:00:00"},
    {"id": 43, "fase": "Grupo J", "default_a": "🇦🇷 Argentina", "default_b": "🇦🇹 Austria", "fecha_base": "2026-06-22 19:00:00"},
    {"id": 44, "fase": "Grupo J", "default_a": "🇩🇿 Argelia", "default_b": "🇯🇴 Jordania", "fecha_base": "2026-06-22 22:00:00"},
    {"id": 45, "fase": "Grupo K", "default_a": "🇵🇹 Portugal", "default_b": "🇺🇿 Uzbekistán", "fecha_base": "2026-06-23 11:00:00"},
    {"id": 46, "fase": "Grupo K", "default_a": "🇨🇴 Colombia", "default_b": "🇨🇩 RD Congo", "fecha_base": "2026-06-23 14:00:00"},
    {"id": 47, "fase": "Grupo L", "default_a": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra", "default_b": "🇬🇭 Ghana", "fecha_base": "2026-06-23 17:00:00"},
    {"id": 48, "fase": "Grupo L", "default_a": "🇭🇷 Croacia", "default_b": "🇵🇦 Panamá", "fecha_base": "2026-06-23 20:00:00"},

    # --- JORNADA 3 ---
    {"id": 49, "fase": "Grupo A", "default_a": "🇨🇿 Rep. Checa", "default_b": "🇲🇽 México", "fecha_base": "2026-06-24 13:00:00"},
    {"id": 50, "fase": "Grupo A", "default_a": "🇿🇦 Sudáfrica", "default_b": "🇰🇷 Corea del Sur", "fecha_base": "2026-06-24 13:00:00"},
    {"id": 51, "fase": "Grupo B", "default_a": "🇨🇦 Canadá", "default_b": "🇨🇭 Suiza", "fecha_base": "2026-06-24 17:00:00"},
    {"id": 52, "fase": "Grupo B", "default_a": "🇧🇦 Bosnia y Herz.", "default_b": "🇶🇦 Catar", "fecha_base": "2026-06-24 17:00:00"},
    {"id": 53, "fase": "Grupo C", "default_a": "🇧🇷 Brasil", "default_b": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia", "fecha_base": "2026-06-25 13:00:00"},
    {"id": 54, "fase": "Grupo C", "default_a": "🇲🇦 Marruecos", "default_b": "🇭🇹 Haití", "fecha_base": "2026-06-25 13:00:00"},
    {"id": 55, "fase": "Grupo D", "default_a": "🇺🇸 USA", "default_b": "🇹🇷 Turquía", "fecha_base": "2026-06-25 17:00:00"},
    {"id": 56, "fase": "Grupo D", "default_a": "🇵🇾 Paraguay", "default_b": "🇦🇺 Australia", "fecha_base": "2026-06-25 17:00:00"},
    {"id": 57, "fase": "Grupo E", "default_a": "🇩🇪 Alemania", "default_b": "🇪🇨 Ecuador", "fecha_base": "2026-06-26 13:00:00"},
    {"id": 58, "fase": "Grupo E", "default_a": "🇨🇼 Curazao", "default_b": "🇨🇮 Costa de Marfil", "fecha_base": "2026-06-26 13:00:00"},
    {"id": 59, "fase": "Grupo F", "default_a": "🇳🇱 Países Bajos", "default_b": "🇹🇳 Túnez", "fecha_base": "2026-06-26 17:00:00"},
    {"id": 60, "fase": "Grupo F", "default_a": "🇯🇵 Japón", "default_b": "🇸🇪 Suecia", "fecha_base": "2026-06-26 17:00:00"},
    {"id": 61, "fase": "Grupo G", "default_a": "🇧🇪 Bélgica", "default_b": "🇳🇿 Nueva Zelanda", "fecha_base": "2026-06-27 13:00:00"},
    {"id": 62, "fase": "Grupo G", "default_a": "🇪🇬 Egipto", "default_b": "🇮🇷 Irán", "fecha_base": "2026-06-27 13:00:00"},
    {"id": 63, "fase": "Grupo H", "default_a": "🇪🇸 España", "default_b": "🇺🇾 Uruguay", "fecha_base": "2026-06-27 17:00:00"},
    {"id": 64, "fase": "Grupo H", "default_a": "🇨🇻 Cabo Verde", "default_b": "🇸🇦 Arabia Saudita", "fecha_base": "2026-06-27 17:00:00"},
    {"id": 65, "fase": "Grupo I", "default_a": "🇫🇷 Francia", "default_b": "🇳🇴 Noruega", "fecha_base": "2026-06-28 13:00:00"},
    {"id": 66, "fase": "Grupo I", "default_a": "🇸🇳 Senegal", "default_b": "🇮🇶 Irak", "fecha_base": "2026-06-28 13:00:00"},
    {"id": 67, "fase": "Grupo J", "default_a": "🇦🇷 Argentina", "default_b": "🇯🇴 Jordania", "fecha_base": "2026-06-28 17:00:00"},
    {"id": 68, "fase": "Grupo J", "default_a": "🇩🇿 Argelia", "default_b": "🇦🇹 Austria", "fecha_base": "2026-06-28 17:00:00"},
    {"id": 69, "fase": "Grupo K", "default_a": "🇵🇹 Portugal", "default_b": "🇨🇴 Colombia", "fecha_base": "2026-06-29 13:00:00"},
    {"id": 70, "fase": "Grupo K", "default_a": "🇨🇩 RD Congo", "default_b": "🇺🇿 Uzbekistán", "fecha_base": "2026-06-29 13:00:00"},
    {"id": 71, "fase": "Grupo L", "default_a": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra", "default_b": "🇵🇦 Panamá", "fecha_base": "2026-06-29 17:00:00"},
    {"id": 72, "fase": "Grupo L", "default_a": "🇭🇷 Croacia", "default_b": "🇬🇭 Ghana", "fecha_base": "2026-06-29 17:00:00"}
]

# --- FASE ELIMINATORIA (Generación dinámica con el diagrama exacto) ---
fechas_16vos = ["2026-06-28", "2026-06-29", "2026-06-30", "2026-07-01", "2026-07-02", "2026-07-03"]
for i in range(73, 89):
    matches.append({
        "id": i, "fase": "Dieciseisavos (32)", 
        "default_a": "Clasificado de Grupo", "default_b": "Clasificado de Grupo", 
        "fecha_base": f"{fechas_16vos[(i - 73) % 6]} 18:00:00"
    })

dia_oct = 4
for i in range(89, 97):
    m_a, m_b = 73 + (i - 89) * 2, 74 + (i - 89) * 2
    matches.append({
        "id": i, "fase": "Octavos (16)", 
        "default_a": f"Ganador M{m_a}", "default_b": f"Ganador M{m_b}", 
        "fecha_base": f"2026-07-0{dia_oct} 18:00:00"
    })
    if i % 2 == 0: dia_oct += 1

dia_cua = 9
for i in range(97, 101):
    m_a, m_b = 89 + (i - 97) * 2, 90 + (i - 97) * 2
    matches.append({
        "id": i, "fase": "Cuartos (8)", 
        "default_a": f"Ganador M{m_a}", "default_b": f"Ganador M{m_b}", 
        "fecha_base": f"2026-07-{dia_cua:02d} 18:00:00"
    })
    if i % 2 == 0: dia_cua += 1

matches.append({"id": 101, "fase": "Semifinal 1", "default_a": "Ganador M97", "default_b": "Ganador M98", "fecha_base": "2026-07-14 18:00:00"})
matches.append({"id": 102, "fase": "Semifinal 2", "default_a": "Ganador M99", "default_b": "Ganador M100", "fecha_base": "2026-07-15 18:00:00"})
matches.append({"id": 103, "fase": "Tercer Lugar", "default_a": "Perdedor M101", "default_b": "Perdedor M102", "fecha_base": "2026-07-18 18:00:00"})
matches.append({"id": 104, "fase": "FINAL", "default_a": "Ganador M101", "default_b": "Ganador M102", "fecha_base": "2026-07-19 18:00:00"})

# Lista de equipos para Campeón Global
lista_equipos = ["🇲🇽 México", "🇺🇸 USA", "🇨🇦 Canadá", "🇦🇷 Argentina", "🇧🇷 Brasil", "🇫🇷 Francia", "🇪🇸 España", "🇩🇪 Alemania", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra", "🇵🇹 Portugal", "Otro"]

# --- FUNCIONES AUXILIARES ---
def convertir_hora(fecha_base_str, timezone_destino):
    # Toma la hora base como la hora oficial de América Central y la convierte a la zona del usuario
    dt_base = pytz.timezone('America/Mexico_City').localize(datetime.strptime(fecha_base_str, '%Y-%m-%d %H:%M:%S'))
    return dt_base.astimezone(pytz.timezone(timezone_destino)).strftime('%d %b %Y - %H:%M')

# --- SISTEMA DE AUTENTICACIÓN ---
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("⚽ Quiniela Mundial 2026")
    tab_login, tab_registro = st.tabs(["Ingresar", "Registrarse"])
    
    with tab_login:
        email_login = st.text_input("Correo Electrónico", key="login_email")
        pass_login = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Entrar"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email_login, "password": pass_login})
                st.session_state.user = res.user
                st.rerun()
            except:
                st.error("Credenciales incorrectas.")

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
    st.sidebar.success(f"Usuario: {user_email}")
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

    es_admin = user_email == "adam666.die@gmail.com" # <--- ¡ASEGÚRATE DE CAMBIAR ESTO A TU CORREO!
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
                        supabase.table('predictions').upsert({"email": user_email, "match_id": m_id, "prediction": seleccion}).execute()
                        st.toast(f"M{m_id} Guardado", icon="✅")
                st.divider()

    # --- PESTAÑA 2: CAMPEÓN ---
    with app_tabs[1]:
        st.header("👑 Predicción del Campeón")
        st.write("Acierta al campeón del mundo y gana 15 puntos extra al final del torneo.")
        
        try:
            mi_campeon_db = supabase.table('champion_predictions').select('prediction').eq('email', user_email).execute().data
            mi_campeon = mi_campeon_db[0]['prediction'] if mi_campeon_db else "No seleccionado"
        except:
            mi_campeon = "No seleccionado"

        if campeon_real:
            st.error(f"El torneo ha terminado. El campeón oficial es: **{campeon_real}**")
            st.info(f"Tu elección fue: {mi_campeon}")
        else:
            st.success(f"Tu selección actual: **{mi_campeon}**")
            nuevo_campeon = st.selectbox("Selecciona tu candidato:", lista_equipos)
            if st.button("Guardar Campeón"):
                supabase.table('champion_predictions').upsert({"email": user_email, "prediction": nuevo_campeon}).execute()
                st.toast("Campeón guardado", icon="✅")
                st.rerun()

    # --- PESTAÑA 3: RANKING ---
    with app_tabs[2]:
        st.header("📊 Tabla de Posiciones")
        if st.button("🔄 Actualizar Ranking"):
            usuarios = pd.DataFrame(supabase.table('users').select('*').execute().data)
            predicciones = pd.DataFrame(supabase.table('predictions').select('*').execute().data)
            resultados = pd.DataFrame(supabase.table('results').select('*').execute().data)
            campeones = pd.DataFrame(supabase.table('champion_predictions').select('*').execute().data)

            if not usuarios.empty and not predicciones.empty and not resultados.empty:
                df_cruce = pd.merge(predicciones, resultados[['match_id', 'real_result']], on='match_id', how='inner')
                df_cruce['puntos_partidos'] = df_cruce.apply(lambda row: 2 if row['prediction'] == row['real_result'] else 0, axis=1)
                puntos_por_user = df_cruce.groupby('email')['puntos_partidos'].sum().reset_index()

                if campeon_real and not campeones.empty:
                    campeones['puntos_campeon'] = campeones['prediction'].apply(lambda x: 15 if x == campeon_real else 0)
                    puntos_por_user = pd.merge(puntos_por_user, campeones[['email', 'puntos_campeon']], on='email', how='left').fillna(0)
                    puntos_por_user['Total'] = puntos_por_user['puntos_partidos'] + puntos_por_user['puntos_campeon']
                else:
                    puntos_por_user['Total'] = puntos_por_user['puntos_partidos']

                ranking_final = pd.merge(usuarios[['email', 'username']], puntos_por_user, on='email', how='left').fillna(0)
                ranking_final = ranking_final[['username', 'Total']].sort_values(by='Total', ascending=False).reset_index(drop=True)
                ranking_final['Total'] = ranking_final['Total'].astype(int)
                
                st.dataframe(ranking_final, use_container_width=True)
            else:
                st.write("Aún no hay puntos suficientes para calcular el ranking.")

    # --- PESTAÑA 4: ADMIN ---
    if es_admin:
        with app_tabs[3]:
            st.error("🚨 PANEL DE ADMINISTRADOR 🚨")
            
            st.subheader("1. Configurar Llaves y Resultados")
            partido_sel = st.selectbox("Selecciona un partido a editar:", [f"M{m['id']} - {m['fase']}" for m in matches])
            m_id_admin = int(partido_sel.split(" ")[0][1:])
            
            # Autocompletar con los datos guardados o los default generados dinámicamente
            default_a = next(m['default_a'] for m in matches if m['id'] == m_id_admin)
            default_b = next(m['default_b'] for m in matches if m['id'] == m_id_admin)
            
            col1, col2 = st.columns(2)
            with col1:
                eq_a_admin = st.text_input("Equipo A", value=oficiales.get(m_id_admin, {}).get('equipo_a') or default_a)
                marc_a = st.number_input("Goles Equipo A", min_value=0, step=1, value=oficiales.get(m_id_admin, {}).get('marcador_a', 0))
            with col2:
                eq_b_admin = st.text_input("Equipo B", value=oficiales.get(m_id_admin, {}).get('equipo_b') or default_b)
                marc_b = st.number_input("Goles Equipo B", min_value=0, step=1, value=oficiales.get(m_id_admin, {}).get('marcador_b', 0))
            
            resultado_admin = st.selectbox("¿Quién ganó la apuesta? (Para repartir puntos)", ["Pendiente", eq_a_admin, "Empate", eq_b_admin])
            
            if st.button("Guardar Partido"):
                data = {
                    "match_id": m_id_admin, "equipo_a": eq_a_admin, "equipo_b": eq_b_admin,
                    "marcador_a": marc_a, "marcador_b": marc_b,
                    "real_result": None if resultado_admin == "Pendiente" else resultado_admin
                }
                supabase.table('results').upsert(data).execute()
                st.success("Partido actualizado.")
            
            st.divider()
            st.subheader("2. Finalizar Torneo (Otorgar 15 pts)")
            camp_oficial = st.selectbox("Selecciona al Campeón Oficial:", ["Ninguno (Torneo Activo)"] + lista_equipos)
            if st.button("Establecer Campeón Global"):
                val = None if camp_oficial == "Ninguno (Torneo Activo)" else camp_oficial
                supabase.table('tournament_settings').upsert({"id": 1, "actual_champion": val}).execute()
                st.success("Configuración de campeón guardada.")
