import sqlite3

from config import DATABASE_FILE

ESQUEMA = """
CREATE TABLE IF NOT EXISTS registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    impresora TEXT,
    archivo TEXT,
    tamano TEXT,
    emisor TEXT,
    tipo_trabajo TEXT,
    tipo_archivo TEXT,
    dimension TEXT,
    resolucion TEXT,
    numero_copias INTEGER,
    numero_pagina INTEGER,
    fecha_envio TEXT,
    info TEXT,
    notas_etiqueta TEXT,
    fecha_inicio TEXT,
    fecha_fin TEXT,
    duracion INTEGER,
    UNIQUE(tipo, archivo, fecha_inicio)
);
"""


def obtener_conexion():
    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def crear_tabla():
    conn = obtener_conexion()
    with conn:
        conn.execute(ESQUEMA)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_registros_archivo ON registros(archivo)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_registros_fecha_envio ON registros(fecha_envio)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_registros_tipo ON registros(tipo)")
    conn.close()
