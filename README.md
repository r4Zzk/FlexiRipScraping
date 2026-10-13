# FlexiRipScraping

Buscador de registros de RIP. Lee los `RIPLOG.HTML` de las máquinas de impresión
(por red), los procesa y los guarda en una base de datos SQLite local para poder
buscarlos desde una interfaz gráfica.

## Arquitectura

- Cada Pc genera un `RIPLOG.HTML` (se comparte por red, solo lectura).
- La máquina control corre esta app: lee cada RIPLOG por red, parsea los eventos, los normaliza
  y los guarda en SQLite. **Solo lectura**: no mueve ni borra los archivos de origen.
- Los archivos se limpian/mueven manualmente en cada máquina cuando sea necesario.

## Estructura

```
FlexiRipScraping/
├── main.py              ← lanza la GUI (crea la base si no existe)
├── config.py            ← rutas persistentes + carga de config.txt
├── assets/              ← icon.png (GUI) e icon.ico (ejecutable)
├── gui/                 ← interfaz (CustomTkinter)
├── parser/              ← html_reader, extractor, normalizer, filter
├── database/            ← connection, queries (SQLite)
├── services/            ← sync_service (escaneo), search_service (búsqueda)
└── models.py            ← objetos TrabajoRip / SalidaImpresion
```

## Datos persistentes del usuario

La configuración y la base de datos **NO** viven en la carpeta del programa
(soporta instalación en `Program Files` y actualizaciones sin perder nada):

```
Windows:  %LOCALAPPDATA%\FlexiRipScraping\
Linux:    ~/.config/FlexiRipScraping/

├── config.txt    ← se crea solo la primera vez (nunca se sobrescribe)
└── database.db   ← se crea solo al arrancar (tabla registros)
```

### config.txt (formato JSON)

```json
{
  "FUENTES": ["\\\\MAQUINA1\\logs\\RIPLOG.HTML", "D:\\Logs\\RIPLOG.HTML"],
  "EMISOR_MAQUINAS": {
    "maqui": "Maquina 4",
    "202502": "Maquina 3",
    "maquina": "Maquina 1",
    "user": "Maquina 2"
  }
}
```

- `FUENTES` → rutas del `RIPLOG.HTML` de cada máquina (local o UNC). Vacío = sin fuentes.
- `EMISOR_MAQUINAS` → mapea el emisor del log al nombre de máquina. Si un emisor
  no está mapeado, se guarda tal cual.
- El archivo se lee en UTF-8 al iniciar; si falta, se crea con los valores
  predeterminados. Editar a mano las rutas reales.

## Base de datos

- SQLite en `%LOCALAPPDATA%\FlexiRipScraping\database.db`
- Tabla `registros` con anti-duplicados: `UNIQUE(tipo, archivo, fecha_inicio)` + `INSERT OR IGNORE`
- Índices: `archivo`, `fecha_envio`, `tipo`


## Instalación en la máquina control

```
C:\Program Files\FlexiRipScraping\
└── FlexiRipScraping.exe          

C:\Users\Usuario\AppData\Local\FlexiRipScraping\
├── config.txt                    ← rutas de red + máquinas (editar a mano)
└── database.db                   ← se crea sola
```

### Configurar las máquinas de impresión

- Compartir la carpeta del RIPLOG (solo lectura).
- Verificar desde la máquina 5: `\\MAQUINA1\...\RIPLOG.HTML`.
- Editar `config.txt` con las 4 rutas UNC.

