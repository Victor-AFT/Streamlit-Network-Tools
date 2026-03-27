# Documentación de páginas

Este archivo describe los scripts disponibles en la carpeta `pages/` del proyecto Streamlit-Network-Tools.

## Lista de scripts y su rol

### `equipoA.py`
- Comprobación de conectividad TCP por IP para dispositivos tipo A.
- Permite selección de fabricante y modelo desde `equipos/equipos.json`.
- Modo individual (1 IP), modo múltiple (lista) y modo desde archivo Excel.
- Verifica puertos y guarda resultados en `pages/logs/check_sesion` y tabla de resultados.
- Permite descargar CSV de resultados.

### `equipoB.py`
- Similar a `equipoA.py` pero para la colección de dispositivos tipo B.
- Mapeo jerárquico fabricante -> modelo -> puerto.
- Ofrece comprobación individual y por lotes.

### `ssh_info.py`
- Antes `Get_info_threads.py`.
- Realiza conexiones SSH en hilos (multithread) usando `paramiko`.
- Ejecuta comandos SQL en dispositivos (Ruggedcom) para obtener `productInfo`.
- Guarda archivos `.txt` en `pages/files` y parsea información (MAC, serial, versión, etc.).
- Genera inventario consolidado y permite exportar CSV de inventario y errores.
- Modo individual y modo masivo desde CSV con columna `IP`.

### `equipos/equipos.json`
- Contiene datos de configuración de puertos por fabricante y modelo.
- `equipoA` y `equipoB` leen este JSON para el form de selección.

### `plantillas/` 
- `PLANTILLA_EQUIPOA.xlsx` y `PLANTILLA_EQUIPOB.xlsx`: plantillas para carga masiva de IPs y modelos.

### `logs/`
- Carpeta de logs de ejecuciones: `check_sesion/registros_<fecha>.csv` y logs sistema.

### `files/`
- Archivos generados por `ssh_info.py`: `*_ProveedorX.txt` y `*_ProveedorX.csv`.

## Cómo usar

1. Ejecutar `streamlit run index.py`.
2. Iniciar sesión y navegar en el menú lateral.
3. Elegir la página de interés (`equipoA`, `equipoB`, `ssh_info`).
4. Seguir el flujo de formulario, cargar CSV o ingresar IPs.

## Recomendaciones

- Mantén `pages/logs` y `pages/files` accesibles para escritura.
- Asegura que `requirements.txt` contenga `paramiko` y `cryptography` para `ssh_info`.
- Este documento es complementario al README general del proyecto en la raíz.
