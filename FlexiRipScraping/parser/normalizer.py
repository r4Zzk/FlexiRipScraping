import re
from datetime import datetime

from config import EMISOR_MAQUINAS


def normalizar(registros):
    """Normaliza los campos de cada objeto. Modifica in-place."""
    for r in registros:
        r.archivo = solo_nombre(r.archivo)
        r.emisor = a_maquina(r.emisor)
        r.dimension = a_cm(r.dimension)
        r.fecha_envio = a_iso_fecha_envio(r.fecha_envio)
        r.fecha_inicio = a_iso_fecha_rip(r.fecha_inicio)
        r.fecha_fin = a_iso_fecha_rip(r.fecha_fin)
        r.duracion = a_segundos(r.duracion)
        if hasattr(r, "numero_copias"):
            r.numero_copias = a_int(r.numero_copias)
        if hasattr(r, "numero_pagina"):
            r.numero_pagina = a_int(r.numero_pagina)
    return registros


def a_maquina(emisor):
    """Mapea el emisor del log al nombre de máquina (case-insensitive)."""
    if not emisor:
        return emisor
    return EMISOR_MAQUINAS.get(emisor.strip().lower(), emisor)


def a_cm(dimension):
    """Convierte dimensiones en pulgadas a cm: '22,8 x 19,3 in' -> '57.9 x 49.0cm'"""
    if not dimension or "cm" in dimension:
        return dimension
    if "in" in dimension:
        partes = dimension.replace(",", ".").replace("in", "").split("x")
        if len(partes) == 2:
            try:
                ancho = float(partes[0]) * 2.54
                alto = float(partes[1]) * 2.54
                return f"{ancho:.1f} x {alto:.1f}cm"
            except ValueError:
                return dimension
    return dimension


def solo_nombre(ruta):
    """'C:\\Users\\maqui\\a.tif' o 'C:/Users/maqui/a.tif' -> 'a.tif'"""
    if not ruta:
        return ruta
    return ruta.replace("\\", "/").split("/")[-1]


def a_iso_fecha_envio(texto):
    """'8/13/2025 1:23 PM' -> '2025-08-13 13:23:00'"""
    if not texto:
        return None
    try:
        return datetime.strptime(texto, "%m/%d/%Y %I:%M %p").strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return texto


def a_iso_fecha_rip(texto):
    """'13:26:28 13/8/2025' -> '2025-08-13 13:26:28'"""
    if not texto:
        return None
    try:
        return datetime.strptime(texto, "%H:%M:%S %d/%m/%Y").strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return texto


def a_segundos(texto):
    """'1 minutos 31 segundos' -> 91, '18 segundos' -> 18"""
    if not texto:
        return None
    minutos = re.search(r"(\d+)\s*minutos?", texto)
    segundos = re.search(r"(\d+)\s*segundos?", texto)
    total = 0
    if minutos:
        total += int(minutos.group(1)) * 60
    if segundos:
        total += int(segundos.group(1))
    return total


def a_int(texto):
    if not texto:
        return None
    try:
        return int(texto)
    except ValueError:
        return texto
