"""Gestor de descargas SSH mejorado.

Este script ofrece funcionalidad para conectar por SSH a dispositivos (originalmente Ruggedcom)
para obtener información de producto, guardar en archivos, y generar inventario a partir del contenido descargado.

Mejoras aplicadas:
- Nombres genéricos de proveedor (ProveedorX).
- Comentarios y docstrings en funciones.
- Manejo de errores más claro.
- Un solo formatear_tiempo.
- Rutas construidas con os.path.join.
- Validaciones de entrada y estado de descarga.
"""

import os
import re
import math
import time
import queue
import socket
import glob
import logging
import paramiko
import subprocess
import threading
import pandas as pd
import streamlit as st
import warnings
from datetime import datetime
from time import sleep
from typing import List, Dict, Optional
from paramiko.ssh_exception import NoValidConnectionsError
from cryptography.utils import CryptographyDeprecationWarning

# Suprimir warning de Cryptography obsoleta (no es ideal en producción)
warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

# Configuración global
HOY = datetime.now().strftime("%Y-%m-%d")
file_name_log = f"Get_Product_ProveedorX_Log_{HOY}.log"
ruta_file_logs = os.path.join("logs", file_name_log)
ruta_files = "files"

# Ajustar algoritmos de clave (fallback para conexiones legacy)
from paramiko import transport
transport.Transport._preferred_kex = (
    'ecdh-sha2-nistp256',
    'ecdh-sha2-nistp384',
    'ecdh-sha2-nistp521',
    'ssh-rsa',
    'ssh-ed25519',
    'diffie-hellman-group-exchange-sha256',
    'diffie-hellman-group14-sha256',
    'diffie-hellman-group-exchange-sha1',
    'diffie-hellman-group14-sha1',
    'diffie-hellman-group1-sha1',
)

# Logging básico
logging.basicConfig(level=logging.INFO, handlers=[logging.handlers.WatchedFileHandler(ruta_file_logs)], format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def formatear_tiempo(segundos: float) -> str:
    """Convertir segundos a un texto legible hh:mm:ss."""
    segundos = max(0, int(segundos))
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    segs = segundos % 60

    if horas > 0:
        return f"{horas}h {minutos}m {segs}s"
    elif minutos > 0:
        return f"{minutos}m {segs}s"
    return f"{segs}s"


def check_ping(host: str) -> bool:
    """Verificar que una dirección IP responde al ping."""
    try:
        resultado = subprocess.run(['ping', '-n', '1', host], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return resultado.returncode == 0
    except Exception as e:
        logger.warning("Error ejecutando ping para %s: %s", host, e)
        return False


def ConexionSSH_ProveedorX(ip: str, usuario: str, password: str, sem: threading.Semaphore) -> Optional[str]:
    """Conecta por SSH al dispositivo y descarga la información de productInfo al disco."""
    with sem:
        if not check_ping(ip):
            logger.warning('DOWN; %s', ip)
            return None

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.set_log_channel(f"paramiko.transport;{ip};")

        try:
            client.connect(ip, 22, usuario, password, look_for_keys=False, allow_agent=False, timeout=15)
            shell = client.invoke_shell()
            sleep(1)
            shell.recv(1024)

            # Abrir menú y modo shell
            shell.send(b'\n')
            sleep(1)
            shell.recv(1024)
            shell.send(b'\x13')  # CTRL+S para abrir Shell en algunos dispositivos
            sleep(1)
            shell.recv(1024)

            # Consultar nombre de sistema
            shell.send(b"sql select system Name from systemid \n")
            sleep(2)
            output = shell.recv(10000).decode('utf-8', errors='ignore')
            hostname_data = output.replace(" ", "").split(',')
            hostname = hostname_data[3][3:-1] if len(hostname_data) > 3 else f"{ip}"

            # Guardado de fichero de información
            ruta_txt = os.path.join(ruta_files, f"{hostname}_ProveedorX.txt")
            os.makedirs(os.path.dirname(ruta_txt), exist_ok=True)

            shell.send(b"sql select from productInfo \n")
            sleep(1)
            config_text = '\n'.join(shell.recv(102400).decode('utf-8', errors='ignore').splitlines()[1:-3])

            with open(ruta_txt, 'w', encoding='latin-1', errors='replace') as g:
                g.write(config_text)

            client.close()
            logger.info('OK-SSH; %s', ip)
            return ruta_txt

        except paramiko.AuthenticationException:
            logger.error('NOK-SSH-auth; %s', ip)
        except (paramiko.SSHException, NoValidConnectionsError, socket.error) as e:
            logger.error('SSH error %s; %s', ip, e)
        except Exception as e:
            logger.exception('Error no esperado en SSH %s: %s', ip, e)
        finally:
            client.close()

        return None


def lectura_fichero_ProveedorX(file_path: str):
    """Extrae información de inventario de un fichero .txt descargado."""
    nombre_equipo = os.path.basename(file_path).replace('.txt', '')
    datos_equipo = []

    if not os.path.exists(file_path):
        return False

    with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
        contenido = f.read()

    # Patrón típico para salida de productInfo: MAC, OrderCode, ..., Serial, BootVersion
    patron = r'([0-9A-F]{2}(?:-[0-9A-F]{2}){5})\s+(\S+)\s+(\S+)\s+(\S+)\s+(.+)'
    match = re.search(patron, contenido, re.IGNORECASE)

    if not match:
        logger.warning('No se halló patrón en fichero %s', file_path)
        return False

    mac = match.group(1)
    order_code = match.group(2)
    serial = match.group(4)
    version = match.group(5).strip()

    datos_equipo.append({
        'Nombre Archivo/Equipo': nombre_equipo,
        'MAC Address': mac,
        'Order Code': order_code,
        'Serial Number': serial,
        'Boot Version': version
    })

    df_inventario = pd.DataFrame(datos_equipo)
    csv_salida = os.path.join(os.path.dirname(file_path), f"{nombre_equipo}.csv")
    df_inventario.to_csv(csv_salida, index=False, sep=';', encoding='utf-8')

    return df_inventario


def generar_inventario_desde_resultados(resultados: List[Dict], output_dir: str = ruta_files):
    """Genera inventario consolidado desde el resultado de la ejecución de hilos."""
    inventario = []
    errores_lectura = []

    for resultado in resultados:
        if resultado.get('estado') != 'OK':
            continue

        ruta_txt = resultado.get('ruta_fichero') or os.path.join(output_dir, resultado.get('fichero', ''))

        if not ruta_txt or not os.path.exists(ruta_txt):
            errores_lectura.append({
                'ip': resultado.get('ip'),
                'fichero': resultado.get('fichero'),
                'detalle': 'No existe la ruta del fichero para procesar'
            })
            continue

        df_fila = lectura_fichero_ProveedorX(ruta_txt)
        if isinstance(df_fila, bool) and df_fila is False:
            errores_lectura.append({
                'ip': resultado.get('ip'),
                'fichero': os.path.basename(ruta_txt),
                'detalle': 'No se encontró patrón válido en el contenido del txt'
            })
        else:
            df_fila['IP'] = resultado.get('ip')
            inventario.append(df_fila)

    df_inventario = pd.concat(inventario, ignore_index=True) if inventario else pd.DataFrame()
    df_errores_lectura = pd.DataFrame(errores_lectura)

    return df_inventario, df_errores_lectura


def ejecutar_threads_ProveedorX(lista_ips: List[str], max_hilos: int, usuario: str, password: str):
    """Ejecuta el proceso de conexión SSH en múltiples hilos."""
    sem = threading.Semaphore(max_hilos)
    hilos = []
    cola_progreso = queue.Queue()
    resultados = []
    lock = threading.Lock()

    def worker(ip_local: str):
        try:
            ruta = ConexionSSH_ProveedorX(ip_local, usuario, password, sem)
            if ruta and os.path.exists(ruta):
                resultado = {
                    'ip': ip_local,
                    'estado': 'OK',
                    'ruta_fichero': ruta,
                    'fichero': os.path.basename(ruta),
                    'detalle': 'Fichero generado correctamente'
                }
            else:
                resultado = {
                    'ip': ip_local,
                    'estado': 'ERROR',
                    'ruta_fichero': None,
                    'fichero': None,
                    'detalle': 'No se pudo generar el fichero'
                }

            with lock:
                resultados.append(resultado)

        except Exception as e:
            with lock:
                resultados.append({'ip': ip_local, 'estado': 'ERROR', 'ruta_fichero': None, 'fichero': None, 'detalle': str(e)})
        finally:
            cola_progreso.put(ip_local)

    for ip_item in lista_ips:
        t = threading.Thread(target=worker, args=(ip_item,), daemon=True)
        t.start()
        hilos.append(t)

    return hilos, cola_progreso, resultados


# --- INTERFAZ DE STREAMLIT ---
st.set_page_config(page_title="Gestor de Descargas SSH", page_icon="")
st.title(" Gestor de Descargas de ProveedorX")

# Opciones de fabricante (genérico): el código es independiente de la marca en la actual implementación.
fabricantes = ["Proveedor A", "Proveedor B"]
fabricante_elegido = st.selectbox("Selecciona el fabricante:", fabricantes)

tipo_descarga = st.radio("Selecciona el tipo de descarga:", ["Individual", "Múltiple"])

if tipo_descarga == "Individual":
    st.divider()
    st.subheader(" Credenciales de Acceso")
    st.write("**Introduce las credenciales de Directorio Activo**")
    st.write(f"Configurando conexión para: **{fabricante_elegido}** (Modo: {tipo_descarga})")
    with st.form("ssh_form"):
        ip = st.text_input("Dirección IP del equipo:", value=st.secrets.get("APP_IP", ""), placeholder="192.168.1.100")
        usuario = st.text_input("Usuario:", value=st.secrets.get("APP_USER", ""))
        password = st.text_input("Contraseña:", value=st.secrets.get("APP_PASSWORD", ""), type="password")
        submit_button = st.form_submit_button("Conectar y Descargar")

    if submit_button:
        if not ip or not usuario or not password:
            st.warning(" Por favor, rellena todos los campos antes de continuar.")
        else:
            with st.spinner(f"Conectando a {ip} mediante SSH..."):
                contenido = ConexionSSH_ProveedorX(ip, usuario, password, sem=threading.Semaphore(1))
                if contenido:
                    st.success(" Fichero descargado con éxito.")
                    resultado_csv = lectura_fichero_ProveedorX(contenido)
                    if isinstance(resultado_csv, pd.DataFrame) and not resultado_csv.empty:
                        with st.expander(" Ver Resultados", expanded=True):
                            st.dataframe(resultado_csv)
                    else:
                        st.warning("No se pudieron extraer datos válidos del fichero descargado.")
                else:
                    st.error(" Error con la conexión SSH")

else:
    st.divider()
    st.subheader(" Credenciales de Acceso")
    st.write("**Introduce las credenciales de Directorio Activo**")
    st.write(f"Configurando conexión para: **{fabricante_elegido}** (Modo: {tipo_descarga})")

    uploaded_file = st.file_uploader("**Sube un CSV con una columna llamada IP**", type=["csv"], key="uploaded_file")

    lista_ips = []
    total_ips = 0

    if uploaded_file is not None:
        try:
            df_ips = pd.read_csv(uploaded_file)
            if "IP" not in df_ips.columns:
                st.error("El CSV debe contener una columna llamada 'IP'.")
            else:
                lista_ips = df_ips["IP"].dropna().astype(str).str.strip().tolist()
                lista_ips = list(dict.fromkeys(lista_ips))
                total_ips = len(lista_ips)
                st.success(f"Fichero cargado correctamente. IPs detectadas: {total_ips}")
        except Exception as e:
            st.error(f"Error leyendo el CSV: {e}")

    hilos = st.text_input("Introduce el número de equipos simultaneos a descargar:", placeholder="4, 6 ,8, 12, 16 ...")

    if hilos and total_ips > 0:
        try:
            max_simultaneos = max(int(hilos), 1)
            tandas = math.ceil(total_ips / max_simultaneos)
            tiempo_estimado = tandas * 30.00
            col1, col2, col3 = st.columns(3)
            col1.metric("IPs detectadas", total_ips)
            col2.metric("Hilos", max_simultaneos)
            col3.metric("Tiempo estimado", formatear_tiempo(tiempo_estimado))
        except ValueError:
            st.info("Introduce un número válido de hilos para calcular la estimación.")

    with st.form("ssh_form_multiple"):
        usuario = st.text_input("Usuario:", value=st.secrets.get("APP_USER", ""))
        password = st.text_input("Contraseña:", value=st.secrets.get("APP_PASSWORD", ""), type="password")
        submit_button = st.form_submit_button("Conectar y Descargar")

    if submit_button:
        if uploaded_file is None:
            st.warning(" Debes subir un CSV antes de continuar.")
        elif total_ips == 0:
            st.warning(" No se han encontrado IPs válidas en el fichero.")
        elif not usuario or not password:
            st.warning(" Por favor, rellena usuario y contraseña.")
        else:
            try:
                max_hilos = int(hilos)
                if max_hilos <= 0:
                    st.error("El número de hilos debe ser mayor que 0.")
                else:
                    tandas = math.ceil(total_ips / max_hilos)
                    tiempo_estimado = tandas * 30.00
                    st.info(f"Se van a procesar {total_ips} IPs con {max_hilos} hilos. Tiempo estimado inicial: {formatear_tiempo(tiempo_estimado)}")

                    progress_bar = st.progress(0, text="Iniciando proceso...")
                    estado = st.empty()
                    resumen = st.empty()
                    col1, col2, col3 = st.columns(3)
                    metric_procesadas = col1.empty()
                    metric_ok = col2.empty()
                    metric_error = col3.empty()

                    inicio = time.time()
                    hilos_activos, cola_progreso, resultados = ejecutar_threads_ProveedorX(lista_ips, max_hilos, usuario, password)

                    completadas = 0

                    while any(t.is_alive() for t in hilos_activos) or not cola_progreso.empty():
                        try:
                            ip_finalizada = cola_progreso.get(timeout=0.2)
                            completadas += 1

                            progreso = completadas / total_ips
                            progress_bar.progress(progreso, text=f"Procesadas {completadas}/{total_ips} IPs")

                            transcurrido = time.time() - inicio
                            promedio_real = transcurrido / completadas if completadas > 0 else 0
                            restantes = total_ips - completadas
                            eta = promedio_real * restantes

                            ok = sum(1 for r in resultados if r["estado"] == "OK")
                            errores = sum(1 for r in resultados if r["estado"] == "ERROR")
                            metric_procesadas.metric("Procesadas", completadas)
                            metric_ok.metric("OK", ok)
                            metric_error.metric("Errores", errores)

                            estado.write(f"Última IP procesada: `{ip_finalizada}` | Transcurrido: **{formatear_tiempo(transcurrido)}** | Restante estimado: **{formatear_tiempo(eta)}**")
                        except queue.Empty:
                            pass

                    for t in hilos_activos:
                        t.join()

                    fin = time.time()
                    duracion_total = fin - inicio
                    progress_bar.progress(1.0, text=f"Procesadas {total_ips}/{total_ips} IPs")
                    resumen.success(f" Proceso finalizado. IPs procesadas: {len(resultados)} | Tiempo total: {formatear_tiempo(duracion_total)}")

                    with st.expander(" Ver Resultados de conexiones SSH", expanded=True):
                        st.dataframe(pd.DataFrame(resultados))

                    df_inventario, df_errores_lectura = generar_inventario_desde_resultados(resultados, output_dir=ruta_files)

                    st.subheader("Inventario extraído desde los ficheros .txt")
                    if not df_inventario.empty:
                        st.success(f"Se han extraído datos de {len(df_inventario)} fichero(s).")
                        with st.expander(" Ver Resultados Modelo y version", expanded=True):
                            st.dataframe(df_inventario)

                        csv_inventario = df_inventario.to_csv(index=False).encode("utf-8-sig")
                        st.download_button("Descargar inventario CSV", data=csv_inventario, file_name="inventario_ProveedorX.csv", mime="text/csv")

                    else:
                        st.warning("No se pudieron extraer datos válidos de los ficheros .txt")

                    if not df_errores_lectura.empty:
                        st.subheader("Errores al leer ficheros")
                        st.dataframe(df_errores_lectura, use_container_width=True)
                        csv_errores = df_errores_lectura.to_csv(index=False).encode("utf-8-sig")
                        st.download_button("Descargar errores de lectura CSV", data=csv_errores, file_name="errores_lectura_ProveedorX.csv", mime="text/csv")
            except ValueError:
                st.error(" Error con el procesamiento de datos")
