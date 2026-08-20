from models import crear_registros


def extraer_registros(datos):
    """Recibe lista de dicts del parser y devuelve objetos RegistroRip."""
    return crear_registros(datos)
