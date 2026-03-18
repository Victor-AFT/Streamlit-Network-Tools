import streamlit as st

if not st.session_state.get("authenticated", False):
    st.warning("🔒 Debes iniciar sesión en la página principal.")
    st.stop()

import pandas as pd
import socket
from datetime import datetime
import os
import time

now = datetime.now()
time2 = now.strftime("%d-%m-%Y")


# Nombre dinámico basado en la fecha del día
HOY = datetime.now().strftime("%Y-%m-%d")
LOG_FILE = f"log_{HOY}.csv"


## FUNCIONES
def check_port(ip, port, timeout=2):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((ip, port))
            return result == 0   # True = abierto
    except Exception as e:
        return False

def clear_ip():
    st.session_state["ip"] = ""

def clear_lista_ips():
    st.session_state["lista_ips"] = ""

def write_log(ip, modelo, puerto, estado):
    """
    Crea automáticamente un log diario en CSV y añade una línea por comprobación.

    Parámetros:
        ip (str): IP comprobada
        modelo (str): Modelo asignado
        puerto (int/None): Puerto correspondiente al modelo
        estado (str): Resultado (OK, NOK, MODELO_DESCONOCIDO, etc.)
    """

    # Fecha del día para el nombre del archivo
    hoy = datetime.now().strftime("%Y-%m-%d")
    filename = f"log_{hoy}.csv"

    # Crear cabecera si no existe
    if not os.path.exists(filename):
        df_empty = pd.DataFrame(columns=["IP", "MODELO", "PUERTO", "ESTADO", "FECHA"])
        df_empty.to_csv(filename, index=False)

    # Crear registro
    registro = {
        "IP": ip,
        "MODELO": modelo,
        "PUERTO": puerto,
        "ESTADO": estado,
        "FECHA": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Guardar al CSV (append sin cabecera)
    df_row = pd.DataFrame([registro])
    df_row.to_csv(filename, index=False, mode="a", header=False)

    return filename  # por si lo quieres mostrar o descargar


# En Streamlit las páginas secundarias no necesitan tener st.set_page_config
# a no ser que quieras sobreescribir el título o icono de esta pestaña concreta.

# Inicializar LOG en session_state si no existe
if "log" not in st.session_state:
    st.session_state["log"] = []

st.write("En construccion web en desarrollo - Otros Equipos")

st.write("Prueba de Comunicación (Otros Equipos)")
tab1, tab2, tab3, tab4 = st.tabs(["Unitario", "Multiples", "Upload File", "Log Sesión"])

## MAPEO DE PUERTOS NUEVOS ###
puertos_pro = {
    "ROUTER_CISCO": 22,         # SSH
    "SERVIDOR_WINDOWS": 3389,   # RDP
    "SERVIDOR_LINUX": 22,       # SSH
    "BASE_DATOS_SQL": 1433,     # SQL Server
    "CAMARA_CCTV": 80,          # HTTP
    "PUNTO_ACCESO_WIFI": 443    # HTTPS
}
# Extraemos los nombres autom��ticamente del diccionario para el selectbox
listado_puertos = list(puertos_pro.keys())

with tab1:
    st.write("Comprobacion de protección")

    # ---- Inicializar session_state ----
    if "ip" not in st.session_state:
        st.session_state["ip"] = ""


    # --- Selectbox con modelos ---
    opcion = st.selectbox(
        "Selecciona el modelo",listado_puertos,key="modelo_unico_nueva"
    )
    puerto = puertos_pro[opcion]

    # ---- Input IP usando session_state ----
    ip = st.text_input("Introduce la IP:", key="ip_nueva")

    col1, col2 = st.columns(2)
    # ---- Botón Probar conexión ----
    with col1:
        if st.button("Probar conexión"):
            if not st.session_state["ip_nueva"]:
                st.error("Debes introducir una IP.")
            else:
                st.info(f"Probando conexión a {st.session_state['ip_nueva']}:{puerto} (modelo {opcion})")

                estado = "OK" if check_port(ip, puerto) else "NOK"
                if estado == "OK":
                    st.success(f"�?Existe comunicacion")
                else:
                    st.error(f"�?no existe comunicacion")

            registro = {
                "IP": st.session_state["ip_nueva"],
                "MODELO": opcion,
                "PUERTO": puerto,
                "ESTADO": estado,
                "FECHA": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            st.session_state["log"].append(registro)
            write_log(ip, opcion, puerto, estado)


        with col2:
            st.button("🧹 Borrar IP", key="btn_clear_ip_nueva", on_click=lambda: st.session_state.update(ip_nueva=""))

    with tab2:

        st.write("Comprobación múltiple de equipos")

        # --- Selectbox con modelos ---
        opcion = st.selectbox(
            "Selecciona el modelo",listado_puertos,key="modelo_multiple_nueva"
        )

        puerto = puertos_pro[opcion]

        if "lista_ips_nueva" not in st.session_state:
            st.session_state["lista_ips_nueva"] = ""

        # ---- Área para pegar listado de IPs ----
        lista_ips = st.text_area(
            "Pega aquí el listado de IPs (una por línea)",
            height=200,
            placeholder="192.168.1.10\n192.168.1.20\n192.168.1.30",
            key="lista_ips_nueva"
        )

        col1_t2, col2_t2 = st.columns(2)
        with col1_t2:
            btn_probar = st.button("Probar equipos", key="btn_probar_m_nueva")
        with col2_t2:
            st.button("🧹 Borrar IPs", key="btn_borrar_t2_nueva", on_click=lambda: st.session_state.update(lista_ips_nueva=""))

        # ---- Botón para ejecutar la prueba ----
        if btn_probar:

            if not lista_ips.strip():
                st.error("Debes introducir al menos una IP.")
            else:
                ips = [ip.strip() for ip in lista_ips.split("\n") if ip.strip()]
                resultados = []
                st.info(f"Probando {len(ips)} equipos en el puerto {puerto} ({opcion})...")

                for ip in ips:
                    try:
                        estado = "OK" if check_port(ip, puerto) else "NOK"
                    except Exception as e:
                        estado = f"ERROR: {e}"
                    # Guardar resultado
                    resultados.append({
                        "IP": ip,
                        "Modelo": opcion,
                        "Puerto": puerto,
                        "Estado": estado,
                        "FECHA": time2
                    })

                    registro = {
                        "IP": ip,
                        "MODELO": opcion,
                        "PUERTO": puerto,
                        "ESTADO": estado,
                        "FECHA": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }

                    st.session_state["log"].append(registro)
                    write_log(ip, opcion, puerto, estado)
                # ---- Convertir resultados a tabla ----
                df = pd.DataFrame(resultados)
                st.dataframe(df)

                # ---- Descargar resultados en Excel ----
                csv = df.to_csv(index=False)
                st.download_button(
                    "Descargar resultados (CSV)",
                    csv,
                    "resultados.csv",
                    "text/csv",
                    key="dl_btn_1"
                )

with tab3:

    st.write("📁 Comprobación Masiva desde Fichero")
    file = st.file_uploader("Sube un fichero CSV o TXT con columnas: IP;MODELO", key="uploader_nueva")
    with st.spinner("Cargando datos...", show_time=True):
        time.sleep(1)

        if file:

            # Detectar el tipo de fichero
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            elif file.name.endswith(".txt"):
                df = pd.read_csv(file, sep=";", names=["IP", "MODELO"])
            else:
                st.error("Formato no soportado. Usa CSV o TXT.")
                st.stop()

            # Validación
            if not {"IP", "MODELO"}.issubset(df.columns):
                st.error("El fichero debe contener columnas: IP, MODELO")
                st.stop()

            st.write("📄 Fichero cargado:")
            st.success("Done!")
            st.dataframe(df)
            # Procesar
            results = []
            for idx, row in df.iterrows():
                ip = row["IP"]
                modelo = row["MODELO"]

                # 1) Solo se puede comprobar si el modelo está en puertos
                if modelo in puertos_pro:
                    puerto = puertos_pro[modelo]

                    # Aquí haces tu comprobación real
                    estado = "OK" if check_port(ip, puerto) else "NOK"

                    # Fecha o timestamp
                    fecha = time2

                    # IMPORTANTE: SIEMPRE MISMA ESTRUCTURA
                    results.append([ip, modelo, puerto, estado, fecha])

                else:
                    # Modelo NO existe -> registrar error para que no falle el DataFrame
                    results.append([ip, modelo, None, "MODELO_DESCONOCIDO", time2])

                registro = {
                    "IP": ip,
                    "MODELO": modelo,
                    "PUERTO": puerto,
                    "ESTADO": estado,
                    "FECHA": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                write_log(ip, modelo, puerto, estado)
                st.session_state["log"].append(registro)


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
                file_name="resultado_comprobaciones.csv",
                mime="text/csv",
                key="dl_btn_2"
            )


with tab4:
    st.write("📘 Log de comprobaciones de la sesión")
    df_log = pd.DataFrame(st.session_state["log"])
    
    # Mostrar la tabla en la pestaña
    st.dataframe(df_log)
    
    if not df_log.empty:
        csv_log = df_log.to_csv(index=False).encode("utf-8")
        
        st.download_button(
            label="⬇️ Descargar log CSV",
            data=csv_log,
            file_name="log_comprobaciones.csv",
            mime="text/csv",
            key="dl_btn_3"
        )
    else:
        st.info("Aún no se ha realizado ninguna comprobación.")
