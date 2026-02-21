def filtrar_campos(registros, claves):
    filtrados = []

    for r in registros:
        nuevo = {k: v for k, v in r.items() if k in claves}
        filtrados.append(nuevo)

    return filtrados