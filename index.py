__author__ = "Víctor Fuentes Toledo"
__version__ = "1.1"
__date__ = "18/03/2026"
__last_modified__ = "26/03/2026"

import streamlit as st
import subprocess
from datetime import datetime
import os
import time

#Librerias de log
import logging.handlers

ruta_pages="pages/"
day_log=datetime.now().strftime("%Y-%m-%d")
ruta_log_system=f"{ruta_pages}logs/system"
os.makedirs(ruta_log_system, exist_ok=True)
file_log_system=os.path.join(ruta_log_system,f"log_system_{day_log}.log")
if not os.path.exists(file_log_system):
        with open(file_log_system, "w", encoding="utf-8") as f:
            f.write("")
logging.getLogger().disabled = False
log_handler = logging.handlers.WatchedFileHandler(file_log_system)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter.converter = time.gmtime  # if you want UTC time
log_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)


#Proceso de conexion con SSL
subprocess.run([
    "streamlit", "run", "index.py",
    "--server.sslCertFile=pages/ssl/mi_cert.pem",
    "--server.sslKeyFile=pages/ssl/mi_cert.key",
    "--server.port=45850"
])

st.set_page_config(page_title="Acceso al portal OyM", page_icon="🔒", layout="centered")
st.write(f"Versión: {__version__}")
logging.info(f"Origin IP : {st.context.ip_address} to Destiny IP :{st.context.headers.get("Host")}")

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
        if usuario == "admin" and password == "admin":
            st.session_state["authenticated"] = True
            st.success("Acceso concedido.")
            logging.info(f"Sesion iniciada con el usuario: {usuario}")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

else:
    st.title("Bienvenido al Portal de Comprobación")
    st.success("Has iniciado sesión correctamente.")
    st.write("👈 Usa el menú lateral para navegar entre las distintas check de equipos.")
    st.divider()

    if st.button("🚪 Cerrar Sesión"):
        st.session_state["authenticated"] = False
        st.rerun()
