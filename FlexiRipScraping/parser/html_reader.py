from pathlib import Path
from bs4 import BeautifulSoup

def cargar_html(ruta):
    texto = Path(ruta).read_text(encoding="utf-8", errors="ignore")
    return BeautifulSoup(texto, "lxml")