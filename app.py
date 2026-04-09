import streamlit as st
import pandas as pd
from supabase import create_client, Client
import pytz
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Quiniela Mundial 2026", page_icon="🏆", layout="wide")

# --- CONEXIÓN A SUPABASE ---
@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase: Client = init_connection()

# --- DATOS DE LOS PARTIDOS (Plantilla) ---
# Todas las fechas deben estar en UTC para poder convertirlas a la hora local del usuario
matches = [
    # FASE DE GRUPOS
    {"id": 1, "fase": "Grupo A", "equipo_a": "🇲🇽 México", "equipo_b": "Por definir (A2)", "ciudad": "Ciudad de México", "fecha_utc": "2026-06-11 17:00:00"},
    {"id": 2, "fase": "Grupo B", "equipo_a": "🇨🇦 Canadá", "equipo_b": "Por definir (B2)", "ciudad": "Toronto", "fecha_utc": "2026-06-12 19:00:00"},
    {"id": 3, "fase": "Grupo D", "equipo_a": "🇺🇸 USA", "equipo_b": "Por definir (D2)", "ciudad": "Los Ángeles", "fecha_utc": "2026-06-12 21:00:00"},
    # PLAYOFFS (Ejemplos)
    {"id": 100, "fase": "Cuartos de Final", "equipo_a": "Ganador 89", "equipo_b": "Ganador 90", "ciudad": "Boston", "fecha_utc": "2026-07-09 18:00:00"},
    {"id": 104, "fase": "FINAL", "equipo_a": "Ganador Semi 1", "equipo_b": "Ganador Semi 2", "ciudad": "Nueva York / Nueva Jersey", "fecha_utc": "2026-07-19 19:00:00"}
    # NOTA: Debes agregar los demás partidos siguiendo esta estructura
]

# --- FUNCIONES AUXILIARES ---
def convertir_hora(fecha_utc_str, timezone_destino):
    utc_dt = datetime.strptime(fecha_utc_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)
    local_dt = utc_dt.astimezone(pytz.timezone(timezone_destino))
    return local_dt.strftime('%d %b %Y - %H:%M')

# --- SISTEMA DE AUTENTICACIÓN ---
if 'user' not in st.session_state:
    st.session_state.user = None

# Pantalla de Login / Registro
if st.session_state.user is None:
    st.title("⚽ Bienvenido a la Quiniela 2026")
    
    tab_login, tab_registro, tab_recuperar = st.tabs(["Ingresar", "Registrarse", "Olvidé mi contraseña"])
    
    with tab_login:
        st.subheader("Inicia Sesión")
        email_login = st.text_input("Correo Electrónico", key="login_email")
        pass_login = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Entrar"):
            try:
                auth_response = supabase.auth.sign_in_with_password({"email": email_login, "password": pass_login})
                st.session_state.user = auth_response.user
                st.rerun()
            except Exception as e:
                st.error("Credenciales incorrectas. Intenta de nuevo.")

    with tab_registro:
        st.subheader("Crea tu cuenta")
        email_reg = st.text_input("Correo Electrónico", key="reg_email")
        pass_reg = st.text_input("Contraseña (Mínimo 6 caracteres)", type="password", key="reg_pass")
        username = st.text_input("Nombre para mostrar en el Ranking")
        if st.button("Registrarse"):
            try:
                # 1. Crear usuario en Auth
                res = supabase.auth.sign_up({"email": email_reg, "password": pass_reg})
                # 2. Guardar el nombre de usuario en la base de datos (requiere crear tabla profiles)
                supabase.table('users').insert({"username": username, "email": email_reg}).execute()
                st.success("¡Registro exitoso! Revisa tu correo (si habilitaste confirmación) o inicia sesión.")
            except Exception as e:
                st.error(f"Error al registrar: {e}")

    with tab_recuperar:
        st.subheader("Recuperar Contraseña")
        email_rec = st.text_input("Correo Electrónico", key="rec_email")
        if st.button("Enviar enlace de recuperación"):
            try:
                supabase.auth.reset_password_email(email_rec)
                st.success("Si el correo existe, te hemos enviado un enlace para restablecer tu contraseña.")
            except Exception as e:
                st.error("Hubo un error al intentar enviar el correo.")

# --- APLICACIÓN PRINCIPAL (Usuario Logueado) ---
else:
    user_email = st.session_state.user.email
    st.sidebar.success(f"Logueado como: {user_email}")
    if st.sidebar.button("Cerrar Sesión"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    # Selector de Zona Horaria global para el usuario
    tz_options = pytz.all_timezones
    # Por defecto busca la zona de CDMX
    default_tz = tz_options.index('America/Mexico_City') if 'America/Mexico_City' in tz_options else 0
    st.sidebar.markdown("---")
    user_tz = st.sidebar.selectbox("🌍 Tu Zona Horaria", tz_options, index=default_tz)

    # --- PESTAÑAS PRINCIPALES ---
    tabs = ["📝 Pronósticos", "📊 Ranking"]
    
    # PANEL DE ADMIN: Solo visible si el correo es el del administrador
    # IMPORTANTE: Registra este correo de forma normal en la app, no pongas la contraseña en el código
    es_admin = user_email == "adam666.die@gmail.com" # CAMBIA ESTO A TU CORREO REAL DE ADMIN
    if es_admin:
        tabs.append("⚙️ Panel de Resultados (Admin)")

    app_tabs = st.tabs(tabs)

    # PESTAÑA 1: PRONÓSTICOS
    with app_tabs[0]:
        st.header("Tus Pronósticos")
        
        # Cargar pronósticos actuales del usuario
        try:
            preds_res = supabase.table('predictions').select('*').eq('email', user_email).execute()
            user_preds = {row['match_id']: row['prediction'] for row in preds_res.data}
        except:
            user_preds = {}

        for match in matches:
            m_id = match['id']
            hora_local = convertir_hora(match['fecha_utc'], user_tz)
            
            with st.container():
                st.markdown(f"**{match['fase']} | 🏟️ {match['ciudad']} | 🕒 {hora_local}**")
                st.markdown(f"### {match['equipo_a']} vs {match['equipo_b']}")
                
                opciones = [match['equipo_a'], "Empate", match['equipo_b']]
                idx_actual = opciones.index(user_preds.get(m_id)) if user_preds.get(m_id) in opciones else None
                
                seleccion = st.radio(
                    f"Pronóstico partido {m_id}", 
                    opciones, 
                    index=idx_actual, 
                    key=f"pred_{m_id}", 
                    horizontal=True,
                    label_visibility="collapsed"
                )
                
                if st.button(f"Guardar Pronóstico", key=f"btn_{m_id}"):
                    data = {"email": user_email, "match_id": m_id, "prediction": seleccion}
                    supabase.table('predictions').upsert(data).execute()
                    st.toast(f"Pronóstico guardado", icon="✅")
                st.divider()

    # PESTAÑA 2: RANKING (Simplificado para evitar errores de JOIN complejos desde el cliente)
    with app_tabs[1]:
        st.header("🏆 Tabla de Posiciones")
        st.info("El sistema calculará 2 puntos por cada acierto exacto.")
        # Aquí puedes mantener tu consulta SQL usando st.connection como lo teníamos antes 
        # si se te facilita más el cálculo de puntos en SQL nativo.

    # PESTAÑA 3: ADMIN (Solo visible para el administrador)
    if es_admin:
        with app_tabs[2]:
            st.error("🚨 PANEL DE ADMINISTRADOR 🚨")
            st.write("Selecciona los resultados oficiales de los partidos para actualizar los puntos.")
            
            for match in matches:
                m_id = match['id']
                st.write(f"**{match['fase']}:** {match['equipo_a']} vs {match['equipo_b']}")
                resultado_real = st.selectbox(
                    "Resultado final",
                    ["Pendiente", match['equipo_a'], "Empate", match['equipo_b']],
                    key=f"res_{m_id}"
                )
                if st.button("Guardar Resultado Oficial", key=f"btn_res_{m_id}"):
                    if resultado_real != "Pendiente":
                        data = {"match_id": m_id, "real_result": resultado_real}
                        supabase.table('results').upsert(data).execute()
                        st.success(f"Resultado guardado: {resultado_real}")
