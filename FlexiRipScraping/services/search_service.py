from database.connection import obtener_conexion


def buscar(termino="", tipo="", emisor="", fecha_desde="", fecha_hasta="", limite=9999):
    """Busca registros con filtros opcionales."""
    conn = obtener_conexion()
    sql = "SELECT * FROM registros WHERE 1=1"
    params = []

    if termino:
        sql += " AND (archivo LIKE ? OR impresora LIKE ? OR info LIKE ?)"
        params.extend([f"%{termino}%"] * 3)

    if tipo:
        sql += " AND tipo = ?"
        params.append(tipo)

    if emisor:
        sql += " AND emisor = ?"
        params.append(emisor)

    if fecha_desde:
        sql += " AND fecha_inicio >= ?"
        params.append(fecha_desde)

    if fecha_hasta:
        sql += " AND fecha_inicio <= ?"
        params.append(fecha_hasta + " 23:59:59")

    sql += " ORDER BY fecha_inicio DESC LIMIT ?"
    params.append(limite)

    filas = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(f) for f in filas]


def contar():
    conn = obtener_conexion()
    fila = conn.execute("SELECT COUNT(*) AS total FROM registros").fetchone()
    conn.close()
    return fila["total"]
