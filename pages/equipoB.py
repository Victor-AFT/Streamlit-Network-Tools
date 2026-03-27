__author__ = "Víctor Fuentes Toledo"
__version__ = "1.1"
__date__ = "18/03/2026"
__last_modified__ = "26/03/2026"

#-------------- LIBRERIAS ----------------------------

import streamlit as st
import pandas as pd
import socket
from datetime import datetime
import os
import time
from pandas import json_normalize


"""
#
# VERSION DESARROLLO
#
"""
#-------------- VARIABLES ----------------------------
day_hours=datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
day_log=datetime.now().strftime("%Y-%m-%d")
ruta_pages="pages/"
ruta_actual=""
LOG_FILE = f"{ruta_pages}logs/check_sesion/registros_{day_log}.csv"
tipo="equipoB"
file_json_equipos="equipos.json"
file_name_log_user=f"{ruta_pages}logs/comprobaciones.csv"
RUTA_PLANTILLAS=f"{ruta_pages}plantillas/PLANTILLA_CTRL.xlsx"
ruta_json_equipos=f"{ruta_pages}equipos/"+file_json_equipos

puerto_tab1=int()
puerto_tab2=int()
puerto_tab3=int()

#-------------- FUNCIONES ----------------------------

def check_port(ip, port, timeout=2):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((ip, port))
            return result == 0   # True = abierto
    except Exception as e:
        print('Error en la funcion check_port', e)


def write_log(ip,tipo, modelo, puerto, estado, fecha):

    filename = LOG_FILE

    # Crear cabecera si no existe
    if not os.path.exists(filename):
        df_empty = pd.DataFrame(columns=["IP", "MODELO", "PUERTO", "ESTADO", "FECHA"])
        df_empty.to_csv(filename, index=False)

    # Crear registro
    registro = {
        "IP": ip,
        "TIPO": tipo,
        "MODELO": modelo,
        "PUERTO": puerto,
        "ESTADO": estado,
        "FECHA": fecha
    }

    # Guardar al CSV (append sin cabecera)
    df_row = pd.DataFrame([registro])
    df_row.to_csv(filename, index=False, mode="a", header=False)

    return filename  # por si lo quieres mostrar o descargar

def clear_ip():
    st.session_state["ip"] = ""

def clear_lista_ips():
    st.session_state["lista_ips"] = ""


#-------------- WEB ----------------------------

if not st.session_state.get("authenticated", False):
    st.warning("Debes iniciar sesion en la pagina principal.")
    st.stop()

st.set_page_config(page_title="equipoB ⚡")


st.set_page_config(
    page_title="Comprobacion de equipos equipoB ⚡",
    page_icon="🔎",
    layout="wide"
)

# Inicializar LOG en session_state si no existe
if "log" not in st.session_state:
    st.session_state["log"] = []


st.header("Comprobacion de equipos equipoB ⚡")
st.write(f"Versión: {__version__}")

st.write("Elige la opcion que mas te interese: ")
tab1, tab2, tab3,tab4,tab5 = st.tabs(["🧩Individual", "📦 Varios","📁 Mediante Archivo", "📘 Leyenda"," 🧾logs"])


df_pro = pd.read_json(ruta_json_equipos)
protecciones = df_pro["equipoB"][0]
listado_equipos = []

for bloque in protecciones:
    listado_equipos.append(bloque)

with tab1:
    st.write("**Comprobación Individual**")
    # ---- Inicializar session_state ----
    if "ip" not in st.session_state:
        st.session_state["ip"] = ""

    # --- Selectbox con modelos ---
    proteccion_selecionada_tab1=st.selectbox("Selecciona el modelo",listado_equipos,key="modelo_unico",index=None)
    if proteccion_selecionada_tab1:
        st.success(f"Modelo: {proteccion_selecionada_tab1}")
        puerto_tab1 = df_pro["equipoB"][0][proteccion_selecionada_tab1]

    # ---- Input IP usando session_state ----
    ip = st.text_input("Introduce la IP:", key="ip_nueva")

    col1, col2 = st.columns(2)
    # ---- Botón Probar conexión ----
    with col1:
        if st.button("Probar conexión"):
            if not st.session_state["ip_nueva"]:
                st.error("❌ Debes introducir una IP.")
            else:
                st.info(f"Probando conexión a {st.session_state['ip']}:{puerto_tab1} (modelo {proteccion_selecionada_tab1})")

                estado_tab1 = "OK" if check_port(ip, puerto_tab1) else "NOK"
                if estado_tab1 == "OK":
                    st.success(f"✔ Existe comunicacion")
                else:
                    st.error(f"✘ no existe comunicacion")

            registro_automatico = {
                "IP": ip,
                "TIPO": "equipoB",
                "MODELO": proteccion_selecionada_tab1,
                "PUERTO": puerto_tab1,
                "ESTADO": estado_tab1,
                "FECHA": day_hours
            }

            st.session_state["log"].append(registro_automatico)
            write_log(ip,"equipoB", proteccion_selecionada_tab1, puerto_tab1, estado_tab1, day_hours)

        with col2:
            st.button("🧹 Borrar IP", key="btn_clear_ip_nueva", on_click=lambda: st.session_state.update(ip_nueva=""))

with tab2:

    st.write("**Comprobación múltiple de equipos**")

    # --- Selectbox con modelos ---
    opcion_modelo = st.selectbox("Selecciona el modelo",listado_equipos,key="modelo_multiple",index=None)
    if opcion_modelo:
        st.success(f"Modelo: {opcion_modelo}")
        puerto_tab2 = df_pro["equipoB"][0][opcion_modelo]

    if "lista_ips_nueva" not in st.session_state:
        st.session_state["lista_ips_nueva"] = ""

    # ---- Area para pegar listado de IPs ----
    lista_ips = st.text_area("Pega aqui el listado de IPs (una por linea)",height=200,placeholder="192.168.1.10\n192.168.1.20\n192.168.1.30",key="lista_ips_nueva")

    col1_t2, col2_t2 = st.columns(2)
    with col1_t2:
        btn_probar = st.button("Probar equipos", key="btn_probar_m_nueva")
    with col2_t2:
        st.button("Borrar IPs", key="btn_borrar_t2_nueva",
                  on_click=lambda: st.session_state.update(lista_ips_nueva=""))

    # ---- Botón para ejecutar la prueba ----
    if btn_probar:

        if not lista_ips.strip():
            st.error(" ❌ Debes introducir al menos una IP.")
        else:
            ips = [ip.strip() for ip in lista_ips.split("\n") if ip.strip()]
            resultados = []
            st.info(f"Probando {len(ips)} equipos en el puerto {puerto_tab2} ({opcion_modelo})...")

            for ip in ips:
                try:
                    estado = "OK" if check_port(ip, puerto_tab2) else "NOK"
                except Exception as e:
                    estado = f"ERROR: {e}"
                # Guardar resultado
                resultados.append({
                    "IP": ip,
                    "TIPO":"equipoB",
                    "Modelo": opcion_modelo,
                    "Puerto": puerto_tab2,
                    "Estado": estado,
                    "FECHA": day_hours
                })

                registro_automatico = {
                    "IP":ip,
                    "TIPO": "equipoB",
                    "MODELO": opcion_modelo,
                    "PUERTO": puerto_tab2,
                    "ESTADO": estado,
                    "FECHA": day_hours
                }

                st.session_state["log"].append(registro_automatico)
                write_log(ip,"equipoB", opcion_modelo, puerto_tab2, estado,day_hours)
            # ---- Convertir resultados a tabla ----
            df = pd.DataFrame(resultados)
            st.dataframe(df)

            # ---- Descargar resultados en Excel ----
            csv = df.to_csv(index=False)
            st.download_button(
                "Descargar resultados (CSV)",
                csv,
                "resultados.csv",
                "text/csv"
            )

with tab3:

    st.write("📁 **Comprobación Masiva desde Fichero**")

    # Cargar archivo de plantilla desde tu proyecto
    with open(RUTA_PLANTILLAS, "rb") as file:
        plantilla_bytes = file.read()

    st.download_button(
        label="📥 Descargar plantilla equipoB",
        data=plantilla_bytes,
        file_name="plantilla_equipoB.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.write("📌**Importante: Mirar la pestaña leyenda para saber los modelos de equipoB.**")
    file = st.file_uploader("Sube la plantilla con los datos")
    if file:

        if file.name.endswith(".xlsx"):
            df = pd.read_excel(file)
        else:
            st.error("Error de formato, solo se puede subir XLSX")
            st.stop()

        # Validación
        if not {"IP", "MODELO"}.issubset(df.columns):
            st.error(" ❌ El fichero debe contener columnas: IP, MODELO")
            st.stop()

        st.write("📄 Fichero cargado:")
        st.success("Done!")
        with st.expander("Ver carga de datos"):
            st.dataframe(df)

        # Procesar
        results = []

        # ---- lectura del fichero ----
        with st.spinner("Obteniendo resultado...", show_time=True):
            time.sleep(1)
            for idx, row in df.iterrows():
                ip_tab3 = row["IP"]
                modelo_tab3 = row["MODELO"]
                # 1) Solo se puede comprobar si el modelo está en puertos
                if df_pro["equipoB"][0][modelo_tab3]:
                    puerto_tab3 = df_pro["equipoB"][0][modelo_tab3]
                    estado_tab3 = "OK" if check_port(ip_tab3, puerto_tab3) else "NOK"

                    # IMPORTANTE: SIEMPRE MISMA ESTRUCTURA
                    results.append([ip_tab3, modelo_tab3, puerto_tab3, estado_tab3, day_hours])

                else:
                    # Modelo NO existe -> registrar error para que no falle el DataFrame
                    results.append([ip, modelo_tab3, None, "MODELO_DESCONOCIDO", day_hours])

                registro_automatico = {
                    "IP": ip,
                    "TIPO": "equipoB",
                    "MODELO": modelo_tab3,
                    "PUERTO": puerto_tab3,
                    "ESTADO": estado_tab3,
                    "FECHA": day_hours
                }
                write_log(ip,"equipoB", modelo_tab3, puerto_tab3, estado,day_hours)
                st.session_state["log"].append(registro_automatico)

        with st.expander("Ver Resultado"):
            st.subheader("📊 Resultados")
            df_result = pd.DataFrame(
                results,
                columns=["IP", "MODELO", "PUERTO", "ESTADO", "FECHA"]
            )
            st.dataframe(df_result)

        # Descargar
        csv = df_result.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Descargar resultados CSV",
            data=csv,
            file_name="resultado_comprobaciones_equipoB.csv",
            mime="text/csv"
        )


with tab4:
    st.write("**Modelo de equipoB**⬇️")
    df_prosd = pd.read_json(ruta_json_equipos)
    prodfs = json_normalize(df_prosd['equipoB'])
    st.dataframe(prodfs.T)

with tab5:
    st.header("⚙️ Configuración")
    st.write("Aquí podrás añadir opciones de configuración, logs, parámetros avanzados, etc.")
    st.write("📘 Log de check equipoB")
    df_log = pd.DataFrame(st.session_state["log"])

    csv_log = df_log.to_csv(index=False).encode("utf-8")
    with st.expander("📘Ver Log"):
        st.dataframe(df_log)

    st.download_button(
        label="⬇️ Descargar log CSV",
        data=csv_log,
        file_name="log_comprobaciones_equipoB.csv",
        mime="text/csv"
    )
