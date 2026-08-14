from lxml import html


def cargar_html(ruta):
    parser = html.HTMLParser(encoding="utf-8")
    doc = html.parse(ruta, parser)
    return doc.getroot()
