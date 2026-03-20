import streamlit as st
import pandas as pd
import socket
from datetime import datetime
import os
import time
from pandas import json_normalize

# Nombre dinámico basado en la fecha del día
HOY = datetime.now().strftime("%Y-%m-%d")
LOG_FILE = f"pages/logs/log_{HOY}.csv"
JSON_EQUIPOS="pages/equipos/equipos.json"

if not st.session_state.get("authenticated", False):
    st.warning("Debes iniciar sesion en la pagina principal.")
    st.stop()

st.set_page_config(page_title="EQUIPOB")

## VARIABLES GLOBALES

puerto_multiples=""
puerto=""
registros = []
list_fabricante_U=[]
list_fabricante_M=[]
results_pross = []
puerto_all = int()
RUTA_PLANTILLAS="pages/plantillas/PLANTILLA_EQUIPOB.xlsx"

## FUNCIONES
def check_port(ip, port, timeout=2):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((ip, port))
            return result == 0   # True = abierto
    except Exception as e:
        return False


def write_log(ip,fabricante, modelo, puerto, estado):


    # Fecha del día para el nombre del archivo
    hoy = datetime.now().strftime("%Y-%m-%d")
    filename = f"pages/logs/log_control_{hoy}.csv"

    # Crear cabecera si no existe
    if not os.path.exists(filename):
        df_empty = pd.DataFrame(columns=["IP", "MODELO", "PUERTO", "ESTADO", "FECHA"])
        df_empty.to_csv(filename, index=False)

    # Crear registro
    registro = {
        "IP": ip,
        "FABRICANTE ":fabricante,
        "MODELO": modelo,
        "PUERTO": puerto,
        "ESTADO": estado,
        "FECHA": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Guardar al CSV (append sin cabecera)
    df_row = pd.DataFrame([registro])
    df_row.to_csv(filename, index=False, mode="a", header=False)

    return filename  # por si lo quieres mostrar o descargar

def clear_ip():
    st.session_state["ip"] = ""

def clear_lista_ips():
    st.session_state["lista_ips"] = ""

st.set_page_config(
    page_title="Comprobacion de equipos B",
    page_icon="🔎",
    layout="wide"
)

# Inicializar LOG en session_state si no existe
if "log" not in st.session_state:
    st.session_state["log"] = []


st.header("Comprobacion de equipos B 🖥️")

st.write("Elige la opcion que mas te interese: ")
tab1, tab2, tab3,tab4,tab5 = st.tabs(["🧩Individual", "📦 Varios","📁 Mediante Archivo", "📘 Leyenda"," 🧾logs"])

df_ctrl = pd.read_json(JSON_EQUIPOS)


with tab1:
    st.write("**Comprobación Individual**")
    for fab, mol in df_ctrl["equipoB"][0].items():
        list_fabricante_U.append(fab)

    sel_fabricante_u = st.selectbox("Selecciona fabricante:",list_fabricante_U,key="modelo_uno_f",index=None)
    if sel_fabricante_u:
        sel_modelo_uno = st.selectbox("Selecciona modelo:", df_ctrl["equipoB"][0][sel_fabricante_u].keys()
                                      ,key="modelo_uno",index=None)
        st.success(f"Fabricante: {sel_fabricante_u} → Modelo: {sel_fabricante_u}")

    if sel_fabricante_u and sel_modelo_uno:
        puerto = df_ctrl["equipoB"][0][sel_fabricante_u][sel_modelo_uno]

    # ---- Inicializar session_state ----
    if "ip" not in st.session_state:
        st.session_state["ip"] = ""

    if sel_fabricante_u and sel_modelo_uno:
        puerto = df_ctrl["equipoB"][0][str(sel_fabricante_u)][str(sel_modelo_uno)]

    # ---- Input IP usando session_state ----
    ip = st.text_input("Introduce la IP:", key="ip_nueva")

    col1, col2 = st.columns(2)
    # ---- Botón Probar conexión ----
    with col1:
        if st.button("Probar conexión"):
            if not st.session_state["ip_nueva"]:
                st.error("Debes introducir una IP.")
            else:
                st.info(f"Probando conexión a {st.session_state['ip']}:{puerto} (modelo {sel_modelo_uno})")

                estado = "OK" if check_port(ip, puerto) else "NOK"
                if estado == "OK":
                    st.success(f"✔ Existe comunicacion")
                else:
                    st.error(f"✘ no existe comunicacion")

            registro_automatico = {
                "IP": ip,
                "FABRICANTE":sel_fabricante_u,
                "MODELO": sel_modelo_uno,
                "PUERTO": puerto,
                "ESTADO": estado,
                "FECHA": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            st.session_state["log"].append(registro_automatico)
            write_log(ip, sel_fabricante_u,sel_modelo_uno, puerto, estado)

        with col2:
            st.button("🧹 Borrar IP", key="btn_clear_ip_nueva", on_click=lambda: st.session_state.update(ip_nueva=""))

with tab2:

    st.write("**Comprobación múltiple de equipos**")

    for fab, mol in df_ctrl["control"][0].items():
        list_fabricante_M.append(fab)

    sel_fabricante_m = st.selectbox("Selecciona fabricante:", list_fabricante_M,key="modelo_multiple_m",index=None)

    if sel_fabricante_m:
        sel_modelo_m = st.selectbox("Selecciona modelo:", df_ctrl["control"][0][sel_fabricante_m].keys(),key="modelo_multiple",index=None)
        st.success(f"Fabricante: {sel_fabricante_m}")


    if sel_fabricante_u and sel_modelo_m:
        st.success(f"Fabricante: {sel_fabricante_m} → Modelo: {sel_fabricante_m}")
        puerto_multiples = df_ctrl["control"][0][sel_fabricante_m][sel_modelo_m]
    if "lista_ips_nueva" not in st.session_state:
        st.session_state["lista_ips_nueva"] = ""

    # ---- Area para pegar listado de IPs ----
    lista_ips = st.text_area(
        "Pega aqui el listado de IPs (una por linea)",
        height=200,
        placeholder="192.168.1.10\n192.168.1.20\n192.168.1.30",
        key="lista_ips_nueva"
    )

    col1_t2, col2_t2 = st.columns(2)
    with col1_t2:
        btn_probar = st.button("Probar equipos", key="btn_probar_m_nueva")
    with col2_t2:
        st.button("Borrar IPs", key="btn_borrar_t2_nueva",
                  on_click=lambda: st.session_state.update(lista_ips_nueva=""))

    # ---- Botón para ejecutar la prueba ----
    if btn_probar:

        if not lista_ips.strip():
            st.error("Debes introducir al menos una IP.")
        else:
            ips = [ip.strip() for ip in lista_ips.split("\n") if ip.strip()]
            resultados = []
            st.info(f"Probando {len(ips)} equipos en el puerto {puerto_multiples} ({sel_modelo_m})...")

            for ip in ips:
                try:
                    estado = "OK" if check_port(ip, puerto) else "NOK"
                except Exception as e:
                    estado = f"ERROR: {e}"
                # Guardar resultado
                resultados.append({
                    "IP": ip,
                    "FABRICANTE":sel_fabricante_m,
                    "Modelo": sel_modelo_m,
                    "Puerto": puerto_multiples,
                    "Estado": estado,
                    "FECHA": HOY
                })

                registro_automatico = {
                    "IP":ip,
                    "FABRICANTE":sel_fabricante_m,
                    "MODELO": sel_modelo_m,
                    "PUERTO": puerto_multiples,
                    "ESTADO": estado,
                    "FECHA": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                st.session_state["log"].append(registro_automatico)
                write_log(ip,sel_fabricante_m, sel_modelo_m, puerto_multiples, estado)
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
        label="📥 Descargar plantilla control",
        data=plantilla_bytes,
        file_name="plantilla_control.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.write("📌 **Importante: Mirar la pestaña leyenda para saber el fabricante y modelo.**")

    file = st.file_uploader("Sube la plantilla con los datos")
    if file:
        # Detectar el tipo de fichero
        if file.name.endswith(".xlsx"):
            df = pd.read_excel(file)
        else:
            st.error("❌ Error de formato, solo se puede subir XLSX")
            st.stop()

        # Validación
        if not {"IP","FABRICANTE", "MODELO"}.issubset(df.columns):
            st.error("❌ El fichero debe contener columnas: IP, FABRICANTE, MODELO")
            st.stop()

        st.write("📄 Fichero cargado:")
        st.success("Done!")
        with st.expander("Ver carga de datos"):
            st.dataframe(df)

        # Procesar

        # ---- lectura del fichero ----
        with st.spinner("Obteniendo resultado...", show_time=True):
            time.sleep(1)
            for idx, row in df.iterrows():
                ip = row["IP"]
                fabricante= row["FABRICANTE"]
                modelo = row["MODELO"]
                # 1) Solo se puede comprobar si el modelo está en puertos
                if df_ctrl["control"][0][fabricante][modelo]:
                    puerto_all =df_ctrl["control"][0][fabricante][modelo]
                    # Aquí haces tu comprobación real
                    estado = "OK" if check_port(ip, puerto) else "NOK"

                    # IMPORTANTE: SIEMPRE MISMA ESTRUCTURA
                    results_pross.append([ip,fabricante, modelo, puerto, estado, HOY])

                else:
                    # Modelo NO existe -> registrar error para que no falle el DataFrame
                    results_pross.append([ip,fabricante, modelo, None, "MODELO_DESCONOCIDO", HOY])

                registro_automatico = {
                    "IP": ip,
                    "FABRICANTE": fabricante,
                    "MODELO": modelo,
                    "PUERTO": puerto,
                    "ESTADO": estado,
                    "FECHA": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                write_log(ip,fabricante, modelo, puerto, estado)
                st.session_state["log"].append(registro_automatico)

        with st.expander("Ver Resultado"):
            st.subheader("📊 Resultados")
            df_result = pd.DataFrame(
                results_pross,
                columns=["IP","FABRICANTE", "MODELO", "PUERTO", "ESTADO", "FECHA"]
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
    st.write("**Fabricantes de equipo B**➡️")
    st.write("**Modelo de equipo B**⬇️")
    df_ctrl = pd.read_json(JSON_EQUIPOS)
    st.dataframe(df_ctrl["equipoB"][0])

with tab5:
    st.header("⚙️ Configuración")
    st.write("Aquí podrás añadir opciones de configuración, logs, parámetros avanzados, etc.")
    st.write("📘 Log de comprobaciones equipo B")
    df_log = pd.DataFrame(st.session_state["log"])

    #st.dataframe(df_log)
    csv_log = df_log.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Descargar log CSV",
        data=csv_log,
        file_name="log_comprobaciones_equipoB.csv",
        mime="text/csv"
    )
