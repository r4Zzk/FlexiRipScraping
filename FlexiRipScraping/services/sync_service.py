import tempfile
import shutil
import time
from pathlib import Path

from parser.html_reader import cargar_html
from parser.extractor import extraer_registros
from parser.normalizer import normalizar
from database.queries import guardar_registros
from config import FUENTES


def sincronizar(fuentes=None, on_progreso=None):
    """Lee cada RIPLOG de las fuentes, crea objetos y los guarda en la DB.

    Copia cada archivo a un temporal antes de parsear para evitar
    lecturas parciales si el archivo se esta escribiendo.
    on_progreso(mensaje) se llama con el progreso de cada fuente.
    """
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
        tmp_path = Path(tempfile.mktemp(suffix=ruta.suffix))
        try:
            t0 = time.perf_counter()
            shutil.copy2(ruta, tmp_path)
            t1 = time.perf_counter()
            _log(f"Copia: {t1-t0:.1f}s ({tmp_path.stat().st_size / 1024 / 1024:.1f}MB)")

            doc = cargar_html(tmp_path)
            t2 = time.perf_counter()
            _log(f"Parse HTML: {t2-t1:.1f}s")

            objetos = extraer_registros(doc)
            t3 = time.perf_counter()
            _log(f"Extraccion: {t3-t2:.1f}s ({len(objetos)} registros)")

            objetos = normalizar(objetos)
            t4 = time.perf_counter()
            _log(f"Normalizacion: {t4-t3:.1f}s")

            guardar_registros(objetos)
            t5 = time.perf_counter()
            _log(f"Guardado: {t5-t4:.1f}s")

            total += len(objetos)
            _log(f"{ruta.name}: {len(objetos)} registros (total: {t5-t0:.1f}s)")
        except Exception as e:
            _log(f"Error al leer {ruta}: {e}")
        finally:
            tmp_path.unlink(missing_ok=True)
    return total
