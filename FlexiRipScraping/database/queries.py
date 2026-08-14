from database.connection import obtener_conexion

COLUMNAS = [
    "tipo",
    "impresora",
    "archivo",
    "tamano",
    "emisor",
    "tipo_trabajo",
    "tipo_archivo",
    "dimension",
    "resolucion",
    "numero_copias",
    "numero_pagina",
    "fecha_envio",
    "info",
    "notas_etiqueta",
    "fecha_inicio",
    "fecha_fin",
    "duracion",
]


def guardar_registros(registros):
    """Inserta objetos en la tabla. Omite duplicados (INSERT OR IGNORE)."""
    conn = obtener_conexion()
    columnas = ", ".join(COLUMNAS)
    marcadores = ", ".join("?" for _ in COLUMNAS)
    sql = f"INSERT OR IGNORE INTO registros ({columnas}) VALUES ({marcadores})"

    valores = [tuple(getattr(r, c, None) for c in COLUMNAS) for r in registros]
    with conn:
        conn.executemany(sql, valores)
    conn.close()
