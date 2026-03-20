# 🔍 Streamlit-Network-Tools

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)

## 📖 Descripción

**Streamlit-Network-Tools** es una aplicación web desarrollada con [Streamlit](https://streamlit.io/) diseñada para facilitar la **comprobación de conectividad TCP** en múltiples equipos de red y servidores.

La herramienta permite verificar si puertos TCP específicos están abiertos y respondiendo en las IPs indicadas, ofreciendo tres modos de prueba: individual, múltiple (pegando listados de IPs) y masiva mediante ficheros Excel. Incluye un sistema de autenticación, registro automático de resultados y logs diarios exportables en CSV.

---

## ✨ Características Principales

| Característica | Descripción |
|---|---|
| 🔒 **Autenticación** | Portal de login obligatorio que restringe el acceso al panel lateral |
| 📡 **Comprobación TCP** | Verifica puertos abiertos por IP mediante *sockets* con timeout configurable |
| 🧩 **Prueba Individual** | Selecciona modelo/fabricante e introduce una IP para probar un equipo |
| 📦 **Prueba Múltiple** | Pega un listado de IPs para probarlas todas en lote bajo un mismo modelo/puerto |
| 📁 **Carga Masiva (XLSX)** | Sube un archivo Excel con columnas `IP` y `MODELO` para comprobaciones automáticas |
| 📥 **Plantillas descargables** | Descarga plantillas Excel preformateadas para cada tipo de equipo |
| 📊 **Registro y Logs** | Historial de sesión visible en la app y guardado automático en CSV diario |
| ⬇️ **Exportación CSV** | Descarga de resultados y logs en formato CSV en cualquier momento |
| 📘 **Leyenda de Equipos** | Consulta integrada de modelos, fabricantes y sus puertos asociados |

---

## 📂 Estructura del Proyecto

```text
📁 Streamlit-Network-Tools/
│
├── index.py                             # Página principal: portal de Login
│
└── 📁 pages/                            # Carpeta obligatoria de Streamlit (multipágina)
    ├── equipoA.py                       # Comprobación de equipos tipo A
    ├── equipoB.py                       # Comprobación de equipos tipo B
    │
    ├── 📁 equipos/
    │   └── equipos.json                 # Configuración de modelos y puertos por tipo de equipo
    │
    ├── 📁 plantillas/
    │   ├── PLANTILLA_EQUIPOA.xlsx       # Plantilla Excel para carga masiva (Equipo A)
    │   └── PLANTILLA_EQUIPOB.xlsx       # Plantilla Excel para carga masiva (Equipo B)
    │
    └── 📁 logs/                         # Logs diarios generados automáticamente
        └── log_YYYY-MM-DD.csv           # Un fichero CSV por día con todas las comprobaciones
```

---

## 🚀 Instalación y Uso

### Requisitos Previos

- **Python 3.8** o superior

### 1. Clonar el repositorio

```bash
git clone https://github.com/Victor-AFT/Streamlit-Network-Tools.git
cd Streamlit-Network-Tools
```

### 2. Crear un entorno virtual (recomendado)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install streamlit pandas openpyxl
```

### 4. Ejecutar la aplicación

```bash
streamlit run index.py
```

La aplicación se abrirá en tu navegador en `http://localhost:8501`.

---

## 🔧 Configuración de Equipos

Los modelos de equipos y sus puertos asociados se definen en el archivo **`pages/equipos/equipos.json`**. La estructura soporta dos tipos:

- **`equipoA`**: Mapeo directo `modelo → puerto`
- **`equipoB`**: Mapeo jerárquico `fabricante → modelo → puerto`

Para añadir nuevos equipos, simplemente edita el fichero JSON siguiendo la estructura existente.

---

## 📚 Librerías Utilizadas

| Librería | Uso |
|---|---|
| [Streamlit](https://streamlit.io/) | Framework web para la interfaz de usuario |
| [Pandas](https://pandas.pydata.org/) | Manipulación de datos, lectura/escritura de CSV y Excel |
| [openpyxl](https://openpyxl.readthedocs.io/) | Lectura de archivos Excel (`.xlsx`) |
| `socket` *(stdlib)* | Comprobación de puertos TCP abiertos |
| `datetime` *(stdlib)* | Generación de timestamps para logs |
| `os` *(stdlib)* | Gestión de ficheros de log |

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.
