from models import crear_registros


def extraer_registros(doc):
    """Recorre las tablas del log y devuelve objetos RegistroRip directamente."""
    registros = []
    tablas = doc.xpath("//table[contains(@class, 'tab1')]")

    for tabla in tablas:
        registro = {}

        for h1 in tabla.iter("h1"):
            registro["evento"] = h1.text_content().strip()
            break

        for fila in tabla.iter("tr"):
            th = fila.find("th")
            td = fila.find("td")

            if th is not None and td is not None:
                clave = th.text_content().strip().replace(":", "")
                valor = td.text_content().strip()
                registro[clave] = valor

        if registro:
            registros.append(registro)

    return crear_registros(registros)
