# 🔍 Streamlit-Network-Tools

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)

## 📖 Descripción

Streamlit-Network-Tools es una aplicación web multipágina para comprobaciones de red, extracción SSH y generación de inventarios.

### Funcionalidades principales

- 🔒 Autenticación de usuario (login/logout)
- 📡 Comprobación de puertos TCP por IP (equipoA/equipoB)
- 🛠️ Conexión SSH por IP y extracción de `productInfo` (ssh_info)
- 📁 Descarga de inventarios CSV y errores
- 📋 Logs diarios automáticos
- 🧩 UI con barra de progreso y métricas en tiempo real

---

## 📚 Estructura de carpetas

- `index.py`: página de inicio (login, control de sesiones, navegación)
- `pages/`: páginas multipágina de Streamlit
  - `equipoA.py`: comprobación máx. 3 modos (individual, múltiple, CSV)
  - `equipoB.py`: equivalente para otros modelos (mapeo fabricante-modelo-puerto)
  - `ssh_info.py`: nuevo módulo de descarga SSH con hilos y reportes
  - `equipos/equipos.json`: configuración de equipos y puertos
  - `plantillas/PLANTILLA_EQUIPOA.xlsx` y `PLANTILLA_EQUIPOB.xlsx`
  - `logs/`: logs de acciones (CSV diarios)
  - `files/`: archivos generados por SSH (`.txt`, `.csv`)
  - `ssl/`: certificados ossl utilizados por el servidor local opcional

---

## 🚀 Requisitos e instalación

1. Clonar repositorio

```bash
git clone https://github.com/Victor-AFT/Streamlit-Network-Tools.git
cd Streamlit-Network-Tools-main/Streamlit-Network-Tools-main
```

2. Crear entorno virtual

```bash
python -m venv venv
# Windows
venv\\Scripts\\activate
# Linux/macOS
source venv/bin/activate
```

3. Instalar dependencias

```bash
pip install -r requirements.txt
# Si no existe requirements:
pip install streamlit pandas openpyxl paramiko cryptography
```

4. Ejecución

```bash
streamlit run index.py
```

Abrir en el navegador: `http://localhost:8501`.

---

## 🔧 Uso de la app

1. En `index.py`, iniciar sesión con usuario y contraseña.
2. Seleccionar una página de `pages` desde el menú lateral.
3. En `ssh_info`, elegir modo:
   - `Individual`: IP + usuario + contraseña.
   - `Múltiple`: subir CSV con columna `IP` + definir hilos.
4. Revisar resultados y descargar inventarios.

### `ssh_info` extra:

- Genera archivos .txt de `productInfo` en `pages/files/`.
- Parseo de información (MAC, order_code, serial, version).
- Crea inventario consolidado y descarga CSV.
- Genera reportes de errores de lectura.

---

## 🗂️ Descripción detallada de carpeta y archivos

### `index.py`
- Autenticación básica (admin/admin por defecto).
- Mensajes de sesión y estado.
- Opcional: check y ocultación de sidebar si no autenticado.

### `pages/equipoA.py` y `pages/equipoB.py`
- `equipoA`: comprobación de un equipo o cientos con puerto asociado.
- `equipoB`: equivalente con fabricante y modelo.
- Log en `pages/logs/check_sesion/...`.
- Descarga CSV de resultados.

### `pages/ssh_info.py`
- Conexión via `paramiko` con KEX ampliado.
- Comandos SQL específicos del dispositivo Ruggedcom.
- Guarda `productInfo` en `pages/files/`.
- Parseo y puede generar `inventario_ProveedorX.csv`.

### `pages/equipos/equipos.json`
Estructura de datos:
```json
{
  "equipoA": [{"Proveedor1": {"modeloA": 22, ...}}],
  "equipoB": [{"Proveedor2": {"modeloX": 23, ...}}]
}
```

### `pages/plantillas`:
- Plantillas de ejemplo para carga masiva del tipo `equipoA` y `equipoB`.

### `pages/logs`:
- Archivos CSV diarios con todas las comprobaciones:
  - IP, tipo, fabricante, modelo, puerto, estado, fecha.

### `pages/files`:
- Archivos TXT descargados por SSH.
- Archivos CSV generados por parsing.


## 📄 Licencia

MIT © 2026
