import tempfile
import shutil
from pathlib import Path

from parser.html_reader import cargar_html
from parser.extractor import extraer_registros
from parser.normalizer import normalizar
from database.connection import crear_tabla
from database.queries import guardar_registros
from config import FUENTES


def sincronizar(fuentes=None, on_progreso=None):
    """Lee cada RIPLOG de las fuentes, crea objetos y los guarda en la DB.

    Copia cada archivo a un temporal antes de parsear para evitar
    lecturas parciales si el archivo se está escribiendo.
    on_progreso(mensaje) se llama con el progreso de cada fuente.
    """
    crear_tabla()
    fuentes = fuentes if fuentes is not None else FUENTES

    def _log(msg):
        if on_progreso:
            on_progreso(msg)

    total = 0
    for ruta in fuentes:
        ruta = Path(ruta)
        if not ruta.exists():
            _log(f"No encontrado: {ruta}")
            continue
        _log(f"Leyendo {ruta.name}...")
        try:
            with tempfile.NamedTemporaryFile(suffix=ruta.suffix, delete=False) as tmp:
                tmp_path = Path(tmp.name)
            shutil.copy2(ruta, tmp_path)
            objetos = extraer_registros(cargar_html(tmp_path))
            objetos = normalizar(objetos)
            guardar_registros(objetos)
            total += len(objetos)
            _log(f"{ruta.name}: {len(objetos)} registros")
        except Exception as e:
            _log(f"Error al leer {ruta}: {e}")
        finally:
            tmp_path.unlink(missing_ok=True)
    return total
