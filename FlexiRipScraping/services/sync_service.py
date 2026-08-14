from pathlib import Path

from parser.html_reader import cargar_html
from parser.extractor import extraer_registros
from parser.normalizer import normalizar
from database.connection import crear_tabla
from database.queries import guardar_registros
from config import FUENTES


def sincronizar(fuentes=None):
    """Lee cada RIPLOG de las fuentes, crea objetos y los guarda en la DB.

    Solo lee: no mueve ni borra los archivos de origen. Los duplicados
    se descartan por el UNIQUE(tipo, archivo, fecha_inicio).
    """
    crear_tabla()
    fuentes = fuentes if fuentes is not None else FUENTES

    total = 0
    for ruta in fuentes:
        if not Path(ruta).exists():
            continue
        objetos = extraer_registros(cargar_html(ruta))
        objetos = normalizar(objetos)
        guardar_registros(objetos)
        total += len(objetos)
    return total
