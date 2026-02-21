from datetime import datetime

def normalizar(datos):
    normalizados = []

    for registro in datos:
        nuevo = {}

        for k, v in registro.items():
            clave = k.strip().lower().replace(" ", "_")
            valor = v.strip()

            nuevo[clave] = valor

        normalizados.append(nuevo)

    return normalizados