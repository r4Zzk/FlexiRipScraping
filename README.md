# FlexiRipScraping

Buscador de registros de RIP. Lee los `RIPLOG.HTML` de las máquinas de impresión
(por red), los procesa y los guarda en una base de datos SQLite local para poder
buscarlos desde una interfaz gráfica.

## Arquitectura

- 4 máquinas de impresión generan su propio `RIPLOG.HTML` (se comparte por red, solo lectura).
- La 5ª máquina corre esta app: lee cada RIPLOG por red, parsea los eventos, los normaliza
  y los guarda en `data/database.db`. **Solo lectura**: no mueve ni borra los archivos de origen.
- Los archivos se limpian/mueven manualmente en cada máquina cuando sea necesario.

## Estructura

```
FlexiRipScraping/
├── main.py              ← lanza la GUI
├── config.py            ← rutas y mapeos (config.json externo PENDIENTE)
├── gui/                 ← interfaz (CustomTkinter)
├── parser/              ← html_reader, extractor, normalizer, filter
├── database/            ← connection, queries (SQLite)
├── services/            ← sync_service (escaneo), search_service (búsqueda)
└── models.py            ← objetos TrabajoRip / SalidaImpresion
```

## Base de datos

- SQLite en `data/database.db`
- Tabla `registros` con anti-duplicados: `UNIQUE(tipo, archivo, fecha_inicio)` + `INSERT OR IGNORE`
- Índices: `archivo`, `fecha_envio`, `tipo`

## Configuración (antes de producción)

`config.py`:
- `FUENTES` → rutas del `RIPLOG.HTML` de cada máquina (local o UNC `\\MAQUINA\carpeta\RIPLOG.HTML`)
- `EMISOR_MAQUINAS` → mapea el emisor del log al nombre de máquina
  (ej: `"maqui"` → `"Maquina 4"`). Si no matchea, se guarda el valor original.

**PENDIENTE**: mover `FUENTES` y `EMISOR_MAQUINAS` a un `config.json` externo
(se lee al iniciar) para no tener que recompilar el `.exe` cuando cambien las rutas.

## Paso a paso para producción

### Paso 1 — Preparar el código (en desarrollo)

Sacar `FUENTES` y `EMISOR_MAQUINAS` a un `config.json` externo para no recompilar
el exe ante cambios de rutas. (PENDIENTE)

### Paso 2 — Generar el `.exe` (en una PC con Windows)

```
pip install -r requirements.txt pyinstaller
pyinstaller --onefile --windowed --name FlexiRip main.py
```

Queda en `dist\FlexiRip.exe`.

### Paso 3 — Instalar en la máquina 5

```
C:\FlexiRip\
├── FlexiRip.exe
├── config.json          ← las rutas de red y máquinas (se edita a mano)
└── data\                ← se crea sola (database.db)
```

### Paso 4 — Configurar las 4 máquinas de impresión

- Compartir la carpeta del RIPLOG (solo lectura).
- Verificar desde la máquina 5: `\\MAQUINA1\...\RIPLOG.HTML`.
- Editar `config.json` con las 4 rutas UNC.

### Paso 5 — Probar

- Doble clic en `FlexiRip.exe` → "Escanear" → deberían aparecer los registros.
- Acceso directo en el escritorio para el día a día.

## Dependencias

`beautifulsoup4`, `lxml`, `customtkinter` (ver `requirements.txt`).
Nota: el parseo usa `lxml` directo (más rápido que BeautifulSoup); `beautifulsoup4`
quedó como dependencia histórica.
