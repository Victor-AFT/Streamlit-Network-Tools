# 🔍 Streamlit-Network-Tools

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)

## 📖 Descripción

**Streamlit-Network-Tools** es una aplicación multipágina construida con Streamlit para gestionar comprobaciones de red y extracción de información de hardware vía SSH. Su objetivo principal es:

- comprobar puertos TCP en múltiples equipos (equipoA, equipoB, etc.)
- extraer `productInfo` desde dispositivos por SSH y generar inventario CSV
- proporcionar un panel seguro con autenticación de usuario
- ofrecer resultados de logs y descargas de CSV/XLSX

---

## ✨ Características principales

- 🔒 Autenticación de sesión (login en `index.py`) con panel lateral oculto si no está autenticado
- 🧩 `equipoA` y `equipoB`: comprobación por fabricante-modelo-puerto con CSV y listado manual
- 🛠️ `ssh_info` : conexión SSH masiva con hilos, lectura de `productInfo`, parseo y CSV
dataset
- 📁 Logs automáticos en `pages/logs/`, con archivo diario por fecha
- ⬇️ Descarga de resultados como CSV desde interfaz
- 🎨 Interfaz mejorada con tema, colores y layout `wide`

---

## 📂 Estructura del proyecto

```text
Streamlit-Network-Tools/
├── index.py
├── README.md
├── requirements.txt
├── pages/
│   ├── equipoA.py
│   ├── equipoB.py
│   ├── ssh_info.py
│   ├── equipos/
│   │   └── equipos.json
│   ├── plantillas/
│   │   ├── PLANTILLA_EQUIPOA.xlsx
│   │   └── PLANTILLA_EQUIPOB.xlsx
│   ├── logs/
│   └── files/
└── LICENSE
```

---

## 🚀 Instalar y ejecutar

### 1. Clona el repositorio

```bash
git clone https://github.com/Victor-AFT/Streamlit-Network-Tools.git
cd Streamlit-Network-Tools
```

### 2. Crea y activa entorno virtual

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Instala dependencias

```bash
pip install -r requirements.txt
# o en caso de no existir requirements:
pip install streamlit pandas openpyxl paramiko
```

### 4. Ejecuta la app

```bash
streamlit run index.py
```

Navega a `http://localhost:8501` (o `http://localhost:45850` si usas certificados en `index.py`).

---

## 🔒 Usuario de prueba

- Usuario: `admin`
- Contraseña: `admin`

---

## ⚙️ Página `ssh_info` (antes `Get_info_threads`)

- usa `paramiko` para SSH
- verifica conectividad con `ping`
- descarga `productInfo` a `pages/files/` en texto
- parsea datos y genera CSV con `pandas`
- ejecuta en varios hilos (configurable desde UI)

---

## 📝 Consejos

- Asegúrate de que las carpetas `pages/logs` y `pages/files` existen, o la app las creará automáticamente.
- Para una ejecución de producción, quita el bloque `subprocess.run(["streamlit", "run", "index.py", ...])` en `index.py`.
- Ajusta credenciales y rutas de certificados si usas SSL.

---

## 📄 Licencia

MIT © 2026
