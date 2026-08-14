def filtrar_campos(objetos, campos):
    """Devuelve una lista de dicts con los campos pedidos de cada objeto."""
    return [{c: getattr(o, c, None) for c in campos} for o in objetos]


def campos_importantes(objetos):
    claves_fijas = [
        "tipo",
        "impresora",
        "archivo",
        "tipo_trabajo",
        "dimension",
        "resolucion",
        "fecha_envio",
        "fecha_inicio",
        "fecha_fin",
        "duracion",
    ]
    return filtrar_campos(objetos, claves_fijas)
