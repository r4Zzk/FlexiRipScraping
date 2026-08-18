import json
import os
import sys
from pathlib import Path

APP_NAME = "FlexiRipScraping"


def _app_data_dir():
    """Carpeta de datos del usuario (persistente, fuera del ejecutable)."""
    local = os.getenv("LOCALAPPDATA")
    if local:
        return Path(local) / APP_NAME
    return Path.home() / ".config" / APP_NAME


APP_DATA_DIR = _app_data_dir()
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = APP_DATA_DIR / "config.txt"
DATABASE_FILE = APP_DATA_DIR / "database.db"


def resource_path(relativa):
    """Resuelve recursos empaquetados (PyInstaller) o del código fuente.

    Usar solo para recursos de la aplicación (assets). La configuración
    y la base de datos viven en APP_DATA_DIR, no acá.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent
    return base / relativa


# ============================================================
# EMISORES -> MÁQUINAS
# Mapea el valor "Emisor" que aparece en el RIPLOG al nombre de la
# máquina que envió el trabajo. Si un emisor no está mapeado, se
# guarda tal cual viene.
# Se pueden agregar/sobreescribir en config.txt.
# ============================================================
_DEFAULT_EMISORES = {
    "maqui": "Maquina 4",
    "202502": "Maquina 3",
    "maquina": "Maquina 1",
    "user": "Maquina 2",
}


def _guardar_config():
    contenido = {
        "FUENTES": [],
        "EMISOR_MAQUINAS": dict(_DEFAULT_EMISORES),
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as archivo:
        json.dump(contenido, archivo, ensure_ascii=False, indent=4)


def _cargar_config():
    """Lee config.txt sin sobrescribirlo si ya existe."""
    if not CONFIG_FILE.exists():
        _guardar_config()
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        return datos if isinstance(datos, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


_config = _cargar_config()

# ============================================================
# FUENTES DE RIPLOG
# Ruta del RIPLOG.HTML de cada máquina de impresión (local o UNC).
# Se editan en config.txt. Vacío = no hay fuentes configuradas.
# ============================================================
FUENTES = list(_config.get("FUENTES") or [])

emisores_archivo = _config.get("EMISOR_MAQUINAS") or {}
EMISOR_MAQUINAS = {**_DEFAULT_EMISORES, **emisores_archivo}

# Ruta del log de pruebas (solo desarrollo).
RUTA_LOG_DEBUG = Path(__file__).resolve().parent.parent / "RIPLOG3.HTML"
