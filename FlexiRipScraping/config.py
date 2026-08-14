import sys
from pathlib import Path


def _base():
    """Carpeta de la app: el .exe si está congelado, el paquete en desarrollo."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


BASE = _base()
RAIZ = BASE.parent

RUTA_LOG_DEBUG = RAIZ / "RIPLOG3.HTML"

RUTA_DB = BASE / "data" / "database.db"

# ============================================================
# EMISORES -> MÁQUINAS
# Mapea el valor "Emisor" que aparece en el RIPLOG al nombre de
# la máquina que envió el trabajo. Si un emisor no está acá,
# se guarda tal cual viene.
# ============================================================
EMISOR_MAQUINAS = {
    "maqui": "Maquina 4",
    "202502": "Maquina 3",
    "maquina": "Maquina 1",
    "user": "Maquina 2",
}

# ============================================================
# FUENTES DE RIPLOG
# Poné acá la ruta del RIPLOG.HTML de cada máquina de impresión.
# Puede ser local o de red (UNC). La 5ª máquina los lee y no los mueve.
# Ejemplo:
#   r"\\MAQUINA1\logs\RIPLOG.HTML"
# ============================================================
FUENTES = [
    RUTA_LOG_DEBUG,  # ← REEMPLAZAR por las rutas reales (puede haber varias)
]
