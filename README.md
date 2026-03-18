# 🔍 Streamlit-Network-Tools

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)

## 📖 Descripción

**NetCheck Portal** es una aplicación web desarrollada con Streamlit diseñada para facilitar la comprobación de conectividad (puertos TCP abiertos) en múltiples equipos de red, servidores y relés de protección. 

La herramienta incluye un sistema de autenticación, la capacidad de realizar pruebas unitarias o masivas, y la generación automática de logs diarios exportables en formato CSV.

## ✨ Características Principales

* **🔒 Autenticación Segura:** Portal de login obligatorio que restringe el acceso a las herramientas del panel lateral.
* **📡 Comprobación de Puertos TCP:** Verifica si un puerto específico está abierto y respondiendo en la IP indicada mediante *sockets*.
* **🔄 Pruebas Múltiples:** Permite pegar un listado de IPs para probarlas todas en lote bajo un mismo modelo/puerto.
* **📁 Carga Masiva (CSV/TXT):** Sube un archivo con columnas `IP` y `MODELO` para realizar comprobaciones automáticas de diferentes equipos a la vez.
* **📊 Registro y Logs:** Historial de sesión visible en la app y guardado automático en un archivo local (`log_YYYY-MM-DD.csv`).

## 📂 Estructura del Proyecto

Para que Streamlit detecte la navegación multipágina correctamente, los archivos deben estar organizados de esta manera:

```text
📁 tu-repositorio/
│
├── Index.py                    # Página principal y portal de Login
├── requirements.txt            # Dependencias del proyecto
│
└── 📁 pages/                   # Carpeta obligatoria de Streamlit
    ├── Equipos_IT.py       # Pestaña: Otros Equipos (IT)

