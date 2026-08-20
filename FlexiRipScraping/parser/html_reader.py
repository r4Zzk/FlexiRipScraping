import re
from pathlib import Path


def cargar_html(ruta):
    """Lee el RIPLOG.HTML y devuelve una lista de dicts (sin lxml).

    Parser rapido para el formato especifico de los RIPLOG:
      <table class="tab1">
        <h1>Evento</h1>
        <tr><th>Clave:</th><td>Valor</td></tr>
        ...
      </table>
    """
    texto = Path(ruta).read_text(encoding="utf-8", errors="replace")
    return _extraer_tablas(texto)


_RE_TABLE = re.compile(
    r"<table\s[^>]*class\s*=\s*[\"']tab1[\"'][^>]*>(.*?)</table>",
    re.IGNORECASE | re.DOTALL,
)
_RE_H1 = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
_RE_TR = re.compile(
    r"<tr[^>]*>\s*<th[^>]*>(.*?)</th>\s*<td[^>]*>(.*?)</td>\s*</tr>",
    re.IGNORECASE | re.DOTALL,
)
_RE_TAG = re.compile(r"<[^>]+>")
_RE_NBSP = re.compile(r"&nbsp;|&#160;|&#xa0;")


def _limpiar(texto):
    """Elimina tags HTML y entidades, limpia espacios."""
    texto = _RE_NBSP.sub(" ", texto)
    texto = _RE_TAG.sub("", texto)
    return " ".join(texto.split()).strip()


def _extraer_tablas(texto):
    """Extrae tablas tab1 como lista de dicts."""
    registros = []
    for match in _RE_TABLE.finditer(texto):
        bloque = match.group(1)
        registro = {}

        h1 = _RE_H1.search(bloque)
        if h1:
            registro["evento"] = _limpiar(h1.group(1))

        for tr_match in _RE_TR.finditer(bloque):
            clave = _limpiar(tr_match.group(1)).replace(":", "")
            valor = _limpiar(tr_match.group(2))
            if clave:
                registro[clave] = valor

        if registro:
            registros.append(registro)
    return registros
