import streamlit as st

st.set_page_config(page_title="Acceso al portal", page_icon="🔒", layout="centered")

# Ocultar el panel lateral si no estamos autenticados para que no se puedan saltar el login
if not st.session_state.get("authenticated", False):
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 Iniciar Sesión")
    st.write("Por favor, introduce las credenciales para acceder a las herramientas.")
    
    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Entrar")
        
    if submit:
        # Credenciales de ejemplo (se pueden cambiar luego)
        if usuario == "admin" and password == "1234":
            st.session_state["authenticated"] = True
            st.success("Acceso concedido.")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
            
else:
    st.title("Bienvenido al Portal de Comprobación")
    st.success("Has iniciado sesión correctamente.")
    st.write("👈 Usa el menú lateral para navegar entre las distintas comprobaciones de equipos.")
    
    st.divider()
    
    if st.button("🚪 Cerrar Sesión"):
        st.session_state["authenticated"] = False
        st.rerun()
