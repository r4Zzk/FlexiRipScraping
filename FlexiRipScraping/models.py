from dataclasses import dataclass, fields

# Mapeo clave del HTML -> campo del modelo (solo los campos que nos interesan)
MAPEO_CAMPOS = {
    "Impresora": "impresora",
    "Nombre de dispositivo": "impresora",
    "Archivo": "archivo",
    "Tamaño": "tamano",
    "Emisor": "emisor",
    "Tipo de trabajo": "tipo_trabajo",
    "Tipo Archivo": "tipo_archivo",
    "Dimensión": "dimension",
    "Resolución": "resolucion",
    "Número de copias": "numero_copias",
    "Número de página": "numero_pagina",
    "Fecha de envío": "fecha_envio",
    "Info": "info",
    "Notas de etiqueta": "notas_etiqueta",
    "Fecha y hora de inicio de RIP": "fecha_inicio",
    "Fecha y hora de finalización de RIP": "fecha_fin",
    "Duración de RIP": "duracion",
    "Fecha y hora de inicio de la salida": "fecha_inicio",
    "Fecha y hora de finalización de la salida": "fecha_fin",
    "Duración de la salida": "duracion",
}

EVENTOS_RIP = {"Empezar trabajo de RIP", "Terminar trabajo RIP"}
EVENTOS_SALIDA = {"Iniciar impresión", "Fin de salida"}


@dataclass
class RegistroRip:
    """Campos comunes a ambos tipos de eventos."""

    tipo: str = ""
    impresora: str = ""
    archivo: str = ""
    tamano: str = ""
    emisor: str = ""
    tipo_trabajo: str = ""
    dimension: str = ""
    resolucion: str = ""
    fecha_envio: str = ""
    fecha_inicio: str = ""
    fecha_fin: str = ""
    duracion: str = ""
    info: str = ""

    @classmethod
    def desde_dict(cls, datos):
        """Construye el objeto usando el mapeo clave del HTML -> campo."""
        kwargs = {}
        nombres = {f.name for f in fields(cls)}
        for clave, campo in MAPEO_CAMPOS.items():
            if campo in nombres and datos.get(clave):
                kwargs[campo] = datos[clave]
        return cls(**kwargs)


@dataclass
class TrabajoRip(RegistroRip):
    """Inicio de RIP."""

    tipo: str = "inicio_rip"
    tipo_archivo: str = ""


@dataclass
class SalidaImpresion(RegistroRip):
    """Inicio de Impresión."""

    tipo: str = "inicio_impresion"
    numero_copias: str = ""
    numero_pagina: str = ""
    notas_etiqueta: str = ""


def crear_registros(datos):
    """Clasifica cada tabla del log y devuelve el objeto correspondiente."""
    registros = []
    for d in datos:
        evento = d.get("evento", "")
        if evento in EVENTOS_RIP:
            registros.append(TrabajoRip.desde_dict(d))
        elif evento in EVENTOS_SALIDA:
            registros.append(SalidaImpresion.desde_dict(d))
        else:
            registros.append(RegistroRip.desde_dict(d))
    return registros
