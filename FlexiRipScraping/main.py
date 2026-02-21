from parser.html_reader import cargar_html
from parser.extractor import extraer_registros
from parser.normalizer import normalizar
from parser.filter import filtrar_campos

ruta = r"C:\Program Files\SAi\FlexiPRINT 22 Inkjetprinter Edition\Jobs and Settings\RIPLOG.HTML"
ruta_debug = r"E:\Demian\Buscador\RIPLOG2.HTML"

soup = cargar_html(ruta_debug)
raw = extraer_registros(soup)
data = normalizar(raw)
data = filtrar_campos(data, { "evento","archivo", "dimensión", "número_de_copias", "fecha_de_envío", "duración_de_rip"})

for item in data[:7]:
    print(item)

    