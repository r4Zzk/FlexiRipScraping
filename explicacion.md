# FlexiRipScraping — Documentacion completa

## 1. Que es esta aplicacion

FlexiRipScraping es un buscador de registros de impresion que lee archivos `RIPLOG.HTML` generados por 4 maquinas de impresion en una red LAN, los parsea, normaliza, almacena en una base de datos SQLite y permite buscarlos desde una interfaz grafica con tema dark/light.

**Flujo basico:**
```
Maquinas 1-4 (RIPLOG.HTML por red) → Escanear → Parser HTML → Normalizacion → SQLite → Buscar en GUI
```

**Filosofia de diseño:**
- Solo lectura sobre los archivos de las maquinas (nunca mueve ni borra)
- Los archivos se copian a un temporal antes de parsear para evitar lecturas parciales
- Anti-duplicados por `UNIQUE(tipo, archivo, fecha_inicio)` + `INSERT OR IGNORE`
- Configuracion externa en `config.txt` (nunca se sobrescribe)
- Tema dark/light persistente

---

## 2. Arquitectura general

```
FlexiRipScraping/
├── main.py                    # Punto de entrada
├── config.py                  # Rutas, configuracion, mapeo emisores→maquinas
├── models.py                  # Dataclasses y mapeo de campos
├── theme_manager.py           # Gestor de temas dark/light
│
├── parser/                    # Capa de parsing HTML
│   ├── html_reader.py         # lxml → arbol DOM
│   ├── extractor.py           # DOM → diccionarios → dataclasses
│   └── normalizer.py          # Conversion de campos (fechas, medidas, etc.)
│
├── database/                  # Capa de persistencia SQLite
│   ├── connection.py          # Esquema, indices, obtener_conexion()
│   └── queries.py             # INSERT OR IGNORE
│
├── services/                  # Capa de logica de negocio
│   ├── sync_service.py        # Escaneo: copiar→parsear→normalizar→guardar
│   └── search_service.py      # Busqueda con filtros
│
├── gui/                       # Capa de interfaz grafica
│   └── app.py                 # Ventana principal (CTk)
│
├── themes/                    # Paletas de colores
│   ├── dark.json
│   └── light.json
│
├── assets/                    # Iconos de la aplicacion
│   ├── icon.png
│   ├── icon.ico
│   └── Icon.png
│
└── FlexiRipScraping.spec      # Configuracion de PyInstaller
```

**Flujo de datos durante un escaneo:**
```
config.py (FUENTES) → sync_service.sincronizar()
  → shutil.copy2() a temporal
  → html_reader.cargar_html() → arbol DOM lxml
  → extractor.extraer_registros() → lista de diccionarios
  → models.crear_registros() → dataclasses (TrabajoRip / SalidaImpresion)
  → normalizer.normalizar() → campos convertidos
  → queries.guardar_registros() → INSERT OR IGNORE en SQLite
```

**Flujo de datos durante una busqueda:**
```
gui/app.py (filtros) → search_service.buscar()
  → SQL dinamica con filtros opcionales
  → lista de dicts → Treeview con zebra striping
```

---

## 3. Descripcion de cada archivo

### 3.1. Archivos raiz

#### `main.py`
Punto de entrada. Solo hace dos cosas: crear la tabla SQLite (si no existe) y lanzar la ventana.

```python
from database.connection import crear_tabla
from gui.app import App

if __name__ == "__main__":
    crear_tabla()
    App().mainloop()
```

#### `config.py`
Centro de configuracion de toda la app. Define:

- **`APP_DATA_DIR`**: Carpeta persistente del usuario. En Windows: `%LOCALAPPDATA%\FlexiRipScraping\`. En Linux: `~/.config/FlexiRipScraping/`.
- **`CONFIG_FILE`**: Ruta a `config.txt` (JSON). Se crea automaticamente si no existe.
- **`DATABASE_FILE`**: Ruta a `database.db`.
- **`resource_path(relativa)`**: Resuelve rutas de assets. Si esta empaquetado con PyInstaller, busca en `sys._MEIPASS`. Si no, busca junto al archivo.
- **`FUENTES`**: Lista de rutas RIPLOG.HTML leidas de `config.txt["FUENTES"]`.
- **`EMISOR_MAQUINAS`**: Diccionario que mapea el campo "Emisor" del RIPLOG al nombre de la maquina. Se carga de `config.txt["EMISOR_MAQUINAS"]` y se fusiona con los defaults.

**Ejemplo de config.txt:**
```json
{
    "FUENTES": [
        "\\\\pc-1\\RIP2\\RIPLOG.HTML",
        "\\\\pc-2\\RIP2\\RIPLOG.HTML"
    ],
    "EMISOR_MAQUINAS": {
        "maqui": "Maquina 4",
        "202502": "Maquina 3",
        "maquina": "Maquina 1",
        "user": "Maquina 2"
    }
}
```

**Nota importante:** Los paths UNC en JSON requieren doble escape: `\\\\pc-1\\RIP2\\RIPLOG.HTML`. Es `\\` por cada `\` real.

#### `models.py`
Define las dataclasses que representan los registros y el mapeo de campos del HTML.

- **`MAPEO_CAMPOS`**: Diccionario que traduce las claves en espanol del RIPLOG (ej: "Fecha y hora de inicio de RIP") a nombres de campo internos (ej: "fecha_inicio"). Nota que "Fecha y hora de inicio de RIP" y "Fecha y hora de inicio de la salida" mapean al mismo campo `fecha_inicio`.

- **`RegistroRip`**: Dataclass base con los campos comunes a ambos tipos de evento.

- **`TrabajoRip(RegistroRip)`**: Hereda de RegistroRip. Tipo fijo: `"inicio_rip"`. Campo adicional: `tipo_archivo`.

- **`SalidaImpresion(RegistroRip)`**: Hereda de RegistroRip. Tipo fijo: `"inicio_impresion"`. Campos adicionales: `numero_copias`, `numero_pagina`, `notas_etiqueta`.

- **`crear_registros(datos)`**: Recibe una lista de diccionarios (del extractor) y devuelve una lista de dataclasses. Clasifica segun el campo `evento`:
  - `"Empezar trabajo de RIP"` o `"Terminar trabajo RIP"` → `TrabajoRip`
  - `"Iniciar impresion"` o `"Fin de salida"` → `SalidaImpresion`
  - Cualquier otro → `RegistroRip` (tipo generico)

#### `theme_manager.py`
Gestor de temas. Funciones y clase:

- **`_cargar_json(ruta)`**: Lee un archivo JSON y devuelve un dict.
- **`_guardar_tema(nombre)`**: Guarda el tema seleccionado en `config.txt` sin sobrescribir el resto.
- **`_cargar_tema_guardado()`**: Lee que tema esta seleccionado en `config.txt`. Default: `"dark"`.

**Clase `ThemeManager`:**
- `__init__(app)`: Recibe la referencia a la ventana. Carga los JSONs y el tema guardado.
- `colors`: Property que devuelve el dict de colores del tema actual.
- `_color(key)`: Busca un color en el JSON, con fallback a defaults hardcodeados.
- `_ttk_val(key)`: Busca un valor en la seccion `treeview` del JSON.
- `_switch_val(key)`: Busca un valor en la seccion `switch` del JSON.
- `toggle()`: Alterna entre dark y light, guarda en config, aplica.
- `_aplicar()`: Aplica colores a todos los widgets de la ventana (frames, entries, buttons, labels, switch, treeview).
- `_aplicar_ttk()`: Configura el estilo del ttk.Treeview y scrollbars con el tema "clam".

**Sistema de defaults:** Los JSONs solo necesitan contener las secciones `treeview` y `switch`. El resto de colores (background, text, primary, etc.) se toman de los defaults hardcodeados en `_DARK_DEFAULTS` y `_LIGHT_DEFAULTS`. Esto permite personalizar solo los componentes que se quieran sin definir toda la paleta.

**Zebra striping:** Las filas del Treeview usan tags `row_even` y `row_odd` con colores diferentes. Se aplican al insertar filas en `app.py` y se re-configuran al cambiar de tema en `_aplicar_ttk()`.

---

### 3.2. parser/ (Capa de parsing HTML)

#### `html_reader.py`
Lee un archivo HTML con lxml y devuelve el elemento raiz del DOM.

```python
def cargar_html(ruta):
    parser = html.HTMLParser(encoding="utf-8")
    doc = html.parse(ruta, parser)
    return doc.getroot()
```

El encoding esta hardcodeado a UTF-8 porque los RIPLOG se generan en UTF-8 sin declaracion. Si los archivos tuvieran otro encoding, habria que agregar un fallback.

#### `extractor.py`
Recorre el DOM y extrae los registros.

1. Busca todas las tablas con `class="tab1"` via XPath: `//table[contains(@class, 'tab1')]`
2. Para cada tabla:
   - Lee el `<h1>` como tipo de evento (ej: "Empezar trabajo de RIP")
   - Recorre cada `<tr>`, extrae `<th>` (clave) y `<td>` (valor)
   - Guarda los pares clave-valor en un diccionario
3. Pasa la lista de diccionarios a `models.crear_registros()` para obtener dataclasses

**Ejemplo de RIPLOG y como se parsea:**
```html
<table class="tab1">
  <h1>Empezar trabajo de RIP</h1>
  <tr><th>Archivo:</th><td>C:\Users\maqui\a.tif</td></tr>
  <tr><th>Emisor:</th><td>maqui</td></tr>
</table>
```
Resultado: `{"evento": "Empezar trabajo de RIP", "Archivo": "C:\\Users\\maqui\\a.tif", "Emisor": "maqui"}`

#### `normalizer.py`
Convierte los campos a formato normalizado. Modifica los objetos in-place.

| Funcion | Entrada | Salida | Descripcion |
|---|---|---|---|
| `solo_nombre()` | `C:\Users\maqui\a.tif` | `a.tif` | Extrae solo el nombre del archivo |
| `a_maquina()` | `maqui` | `Maquina 4` | Mapea emisor a nombre de maquina (case-insensitive) |
| `a_cm()` | `22,8 x 19,3 in` | `57.9 x 49.0cm` | Convierte pulgadas a cm (x2.54) |
| `a_iso_fecha_envio()` | `8/13/2025 1:23 PM` | `2025-08-13 13:23:00` | Convierte formato US a ISO |
| `a_iso_fecha_rip()` | `13:26:28 13/8/2025` | `2025-08-13 13:26:28` | Convierte formato europeo a ISO |
| `a_segundos()` | `1 minutos 31 segundos` | `91` | Convierte duracion a segundos |
| `a_int()` | `3` | `3` | Convierte texto a entero |

---

### 3.3. database/ (Capa de persistencia)

#### `connection.py`
Define el esquema SQLite y la funcion de conexion.

**Esquema de la tabla `registros`:**
```sql
CREATE TABLE IF NOT EXISTS registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,           -- 'inicio_rip' o 'inicio_impresion'
    impresora TEXT,
    archivo TEXT,
    tamano TEXT,
    emisor TEXT,
    tipo_trabajo TEXT,
    tipo_archivo TEXT,
    dimension TEXT,
    resolucion TEXT,
    numero_copias INTEGER,
    numero_pagina INTEGER,
    fecha_envio TEXT,
    info TEXT,
    notas_etiqueta TEXT,
    fecha_inicio TEXT,            -- formato ISO: '2025-08-13 13:26:28'
    fecha_fin TEXT,
    duracion INTEGER,             -- segundos
    UNIQUE(tipo, archivo, fecha_inicio)  -- anti-duplicados
);
```

**Indices:**
- `idx_registros_archivo` sobre `archivo` (para busquedas por nombre)
- `idx_registros_fecha_envio` sobre `fecha_envio`
- `idx_registros_tipo` sobre `tipo`

**`obtener_conexion()`**: Abre una conexion SQLite con `row_factory = sqlite3.Row` (permite acceder a columnas por nombre).

**`crear_tabla()`**: Ejecuta el CREATE TABLE IF NOT EXISTS y los CREATE INDEX IF NOT EXISTS. Se llama una vez al inicio en `main.py`.

#### `queries.py`
Funcion de insercion.

**`guardar_registros(registros)`**:
1. Obtiene una conexion
2. Construye SQL: `INSERT OR IGNORE INTO registros (columnas) VALUES (marcadores)`
3. Extrae los valores de cada dataclass con `getattr(r, c, None)`
4. Ejecuta `executemany()` en una transaccion
5. Cierra la conexion

El `INSERT OR IGNORE` asegura que si ya existe un registro con el mismo `(tipo, archivo, fecha_inicio)`, se ignora silenciosamente.

---

### 3.4. services/ (Capa de logica de negocio)

#### `sync_service.py`
Servicio de escaneo/sincronizacion.

**`sincronizar(fuentes, on_progreso)`**:
1. Para cada fuente (ruta RIPLOG.HTML):
   - Verifica que el archivo exista
   - Crea una copia temporal con `tempfile.mktemp()` + `shutil.copy2()` (evita lecturas parciales si el archivo se esta escribiendo)
   - Parsea el HTML copiado
   - Normaliza los registros
   - Guarda en SQLite (duplicados se ignoran automaticamente)
   - Elimina el temporal
2. Llama a `on_progreso(mensaje)` con el progreso de cada fuente
3. Retorna el total de registros procesados

**Por que se copia a temporal?** Las maquinas de impresion escriben el RIPLOG continuamente. Si lo leemos directamente mientras se esta escribiendo, podriamos obtener un HTML incompleto. La copia atomiza la lectura.

#### `search_service.py`
Servicio de busqueda.

**`buscar(termino, tipo, emisor, fecha_desde, fecha_hasta)`**:
- Construye SQL dinamicamente segun los filtros proporcionados
- `termino`: Busca en `archivo`, `impresora` e `info` con `LIKE %term%`
- `emisor`: Filtra por nombre de maquina exacto
- `fecha_desde` / `fecha_hasta`: Filtra por rango de `fecha_inicio`
- Ordena por `fecha_inicio DESC` (mas recientes primero)
- Retorna lista de diccionarios

**`contar()`**: Retorna el total de registros en la tabla.

---

### 3.5. gui/ (Capa de interfaz grafica)

#### `app.py`
Ventana principal. Usa `customtkinter` (CTk) para widgets modernos y `tkinter.ttk.Treeview` para la tabla.

**Componentes de la interfaz:**
```
┌─────────────────────────────────────────────────────┐
│ [Buscar archivo...]  [Buscar] [Escanear]            │ ← frame_busqueda
├─────────────────────────────────────────────────────┤
│ Máquina: [Todas ▼]  Desde: [AAAA-MM-DD]  Hasta:    │ ← frame_filtros
│ [AAAA-MM-DD]  Tema: [○────────]                     │
├─────────────────────────────────────────────────────┤
│ Fecha │ Tipo │ Archivo │ Emisor │ ... │ Estado      │ ← Treeview
│───────┼──────┼─────────┼────────┼─────┼────────────│   (frame_tabla)
│       │      │         │        │     │             │
│       │      │         │        │     │             │
├─────────────────────────────────────────────────────┤
│ Último escaneo: 0 nuevos · Total: 4    4 resultados │ ← frame_estado
└─────────────────────────────────────────────────────┘
```

**Columnas del Treeview:**
| ID | Texto | Ancho |
|---|---|---|
| `fecha_inicio` | Fecha | 160 |
| `tipo` | Tipo | 150 |
| `archivo` | Archivo | 360 |
| `emisor` | Emisor | 90 |
| `tipo_trabajo` | Tipo de trabajo | 150 |
| `numero_copias` | Copias | 70 |
| `dimension` | Dimension | 130 |
| `resolucion` | Resolucion | 130 |
| `info` | Estado | 220 |

**Funcionalidades:**
- **Busqueda por texto**: Filtra por nombre de archivo, impresora o estado
- **Filtro por maquina**: ComboBox con las maquinas mapeadas en config
- **Filtro por fechas**: Campos Desde/Hasta en formato AAAA-MM-DD
- **Ordenamiento por columna**: Click en cualquier header de columna para ordenar. Click de nuevo para invertir
- **Zebra striping**: Filas alternadas con colores diferentes para facilitar la lectura
- **Toggle dark/light**: Switch que cambia el tema en tiempo real sin reiniciar

**Threading:**
Tanto `buscar()` como `escanear()` corren en hilos separados (`threading.Thread`) para no congelar la UI. La comunicacion con el hilo principal se hace via `queue.Queue` + `_poll_callbacks()` cada 50ms. Esto es necesario porque Python 3.14 prohibe llamar a `self.after()` desde hilos no principales.

**Barra de estado:**
- `lbl_escaneo` (izquierda): Muestra resultado del ultimo escaneo (permanece)
- `lbl_estado` (derecha): Muestra cantidad de resultados de la busqueda actual

---

### 3.6. themes/ (Paletas de colores)

#### `dark.json` y `light.json`
Archivos JSON con las secciones `treeview` y `switch`. El resto de colores se toma de los defaults hardcodeados en `theme_manager.py`.

**Estructura de dark.json:**
```json
{
  "treeview": {
    "background": "#163832",
    "foreground": "#DAF1DE",
    "row_even_background": "#163832",
    "row_odd_background": "#0B2B26",
    "heading_background": "#235347",
    "heading_foreground": "#F3E9D2",
    "selected_background": "#397563",
    "selected_foreground": "#F3E9D2",
    "field_background": "#163832",
    "border": "#235347",
    "row_height": 28
  },
  "switch": {
    "on": "#235347",
    "off": "#B8A98A",
    "button": "#F3E9D2",
    "button_hover": "#DAF1DE"
  }
}
```

**Paleta de colores base:**
| Color | Dark | Light | Uso |
|---|---|---|---|
| background | `#051F20` | `#F3E9D2` | Fondo principal |
| surface | `#0B2B26` | `#E8DCC4` | Fondo de inputs |
| card | `#163832` | `#FFFFFF` | Fondo de frames/secciones |
| primary | `#235347` | `#235347` | Botones, headers |
| primary_hover | `#397563` | `#397563` | Hover de botones |
| text | `#DAF1DE` | `#051F20` | Texto principal |
| text_secondary | `#8EB69B` | `#397563` | Texto secundario, placeholders |
| border | `#B8A98A` | `#B8A98A` | Bordes de inputs |

---

### 3.7. Archivos de configuracion y build

#### `assets/icon.png`, `icon.ico`, `Icon.png`
Iconos de la aplicacion. `icon.ico` se usa en Windows (ventana y taskbar). `icon.png` se usa en Linux. `Icon.png` (1024px) es la fuente original de la que se generaron los demas.

#### `FlexiRipScraping.spec`
Archivo de configuracion de PyInstaller:
- **Modo onedir** (no onefile) para mejor rendimiento
- **`console=False`**: No abre ventana de consola
- **Icono**: `assets/icon.ico`
- **Datas**: Incluye la carpeta `assets/` en el empaquetado

#### `.github/workflows/build.yml`
GitHub Actions para compilar el .exe en Windows:
1. Se ejecuta en `windows-latest`
2. Instala Python 3.12
3. Instala dependencias + PyInstaller
4. Ejecuta `pyinstaller FlexiRipScraping.spec`
5. Sube el resultado como artifact

Se ejecuta automaticamente al hacer push a `main`/`master`, o manualmente via `workflow_dispatch`.

#### `requirements.txt`
Dependencias:
- `lxml`: Parser HTML rapido
- `customtkinter`: Widgets modernos para tkinter

#### `.gitignore`
Excluye: `.venv/`, `__pycache__/`, `build/`, `dist/`, `*.db`

---

## 4. Base de datos

**Ubicacion:**
- Windows: `%LOCALAPPDATA%\FlexiRipScraping\database.db`
- Linux: `~/.config/FlexiRipScraping/database.db`

**Tabla unica `registros`** con 18 campos. No se crean tablas adicionales. Los 2 tipos de eventos (RIP e Impresion) conviven en la misma tabla, diferenciados por el campo `tipo`.

**Anti-duplicados:** `UNIQUE(tipo, archivo, fecha_inicio)` + `INSERT OR IGNORE`. Si se vuelve a escanear el mismo RIPLOG, los registros existentes se ignoran.

**Indices:** `archivo`, `fecha_envio`, `tipo`. Se crean una sola vez con `CREATE INDEX IF NOT EXISTS`.

---

## 5. Configuracion

El archivo `config.txt` se encuentra en:
- Windows: `%LOCALAPPDATA%\FlexiRipScraping\config.txt`
- Linux: `~/.config/FlexiRipScraping/config.txt`

**Campos:**
```json
{
    "FUENTES": [],
    "EMISOR_MAQUINAS": {
        "maqui": "Maquina 4",
        "202502": "Maquina 3",
        "maquina": "Maquina 1",
        "user": "Maquina 2"
    },
    "tema": "dark"
}
```

- **`FUENTES`**: Lista de rutas UNC o locales de los RIPLOG.HTML. Se deben editar manualmente.
- **`EMISOR_MAQUINAS`**: Mapeo de emisores del RIPLOG a nombres de maquina. Se fusiona con los defaults.
- **`tema`**: Tema seleccionado (`"dark"` o `"light"`). Se actualiza automaticamente al usar el switch.

**Reglas importantes:**
- El archivo se crea automaticamente en la primera ejecucion
- Nunca se sobrescribe si ya existe
- Los paths UNC requieren doble escape JSON: `\\\\pc-1\\RIP2\\RIPLOG.HTML`
- El campo `tema` se escribe automaticamente pero no se debe editar manualmente (aunque no pasa nada si se hace)

---

## 6. Instalacion y ejecucion

### Desde codigo fuente
```bash
# Clonar el repositorio
git clone https://github.com/usuario/FlexiRipScraping.git
cd FlexiRipScraping

# Crear entorno virtual
python -m venv FlexiRipScraping/.venv
source FlexiRipScraping/.venv/bin/activate  # Linux
# o FlexiRipScraping\.venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
cd FlexiRipScraping
python main.py
```

### Desde el .exe (Windows)
1. Descargar el artifact de GitHub Actions
2. Extraer la carpeta `FlexiRipScraping/`
3. Editar `%LOCALAPPDATA%\FlexiRipScraping\config.txt` con las rutas UNC
4. Ejecutar `FlexiRipScraping.exe`

### Compilar el .exe
```bash
pip install pyinstaller
pyinstaller FlexiRipScraping.spec
# El resultado queda en dist/FlexiRipScraping/
```

---

## 7. Diseno y decisiones tecnicas

### Por que SQLite y no CSV/JSON?
- Permite busquedas con filtros rapidas (SQL)
- Anti-duplicados nativos con UNIQUE
- Un solo archivo, sin dependencias externas
- Maneja miles de registros sin problemas

### Por que copiar a temporal antes de parsear?
Las maquinas de impresion escriben el RIPLOG continuamente. Si lo leemos directamente mientras se esta escribiendo, podriamos obtener un HTML incompleto o corrupto. La copia a temporal atomiza la operacion de lectura.

### Por que threading en la GUI?
Las operaciones de escaneo (lectura de red) y busqueda (SQLite) pueden tardar. Sin threading, la ventana se congelaria durante esa tiempo. El patron usado es:
1. El hilo secundario ejecuta la operacion pesada
2. Encola un callback via `queue.Queue`
3. El hilo principal revisa la cola cada 50ms y ejecuta los callbacks

### Por que no se usa FTS5 (Full-Text Search)?
Para el volumen actual (~2000 registros) las busquedas `LIKE %term%` son suficientes. Si la base de datos creciera significativamente (>100k registros), FTS5 seria una mejora值得考虑.

### Separacion de capas
- **parser/**: Solo parsea HTML, no sabe nada de la DB
- **database/**: Solo persiste, no sabe nada del HTML
- **services/**: Orquesta parser + database
- **gui/**: Solo presenta, delega a services

Esto facilita testing, mantenimiento y cambios futuros.

---

## 8. Flujo completo de un escaneo

```
1. Usuario hace click en "Escanear"
2. app.escanear() deshabilita el boton, muestra "Escaneando..."
3. Lanza un Thread daemon
4. sync_service.sincronizar() itera cada fuente de config.txt
5. Para cada fuente:
   a. Verifica que el archivo exista en la red
   b. Copia a un archivo temporal local (shutil.copy2)
   c. html_reader.cargar_html() parsea con lxml (UTF-8)
   d. extractor.extraer_registros() extrae tablas class="tab1"
   e. models.crear_registros() clasifica y crea dataclasses
   f. normalizer.normalizer() convierte campos
   g. queries.guardar_registros() INSERT OR IGNORE en SQLite
   h. Elimina el temporal
6. Retorna total de registros procesados
7. app._programar() encola callback en la queue
8. _poll_callbacks() ejecuta en el hilo principal
9. Muestra "Último escaneo: X nuevos · Total en DB: Y"
10. Llama a app.buscar() para refrescar la tabla
```

---

## 9. Flujo completo de una busqueda

```
1. Usuario escribe un termino y/o selecciona filtros
2. Presiona "Buscar" o Enter
3. app.buscar() verifica que no haya otra busqueda en curso
4. Lanza un Thread daemon
5. search_service.buscar() construye SQL dinamica:
   - Si hay termino: LIKE %term% en archivo, impresora, info
   - Si hay maquina: emisor = ?
   - Si hay fechas: fecha_inicio BETWEEN ? AND ?
6. Ejecuta SQL, retorna lista de dicts
7. app._mostrar_resultados() ejecuta en el hilo principal
8. Ordena si es necesario (por columna seleccionada)
9. Limpia el Treeview
10. Inserta filas con tags row_even/row_odd (zebra striping)
11. Muestra "X resultados"
```

---

## 10. Troubleshooting

| Problema | Causa | Solucion |
|---|---|---|
| "No encontrado: \\\\pc-1\RIP2\RIPLOG.HTML" | Path UNC incorrecto o sin permisos | Verificar accesso a la red, probar el path en el explorador |
| "0 registros" despues de escanear | El RIPLOG esta vacio o el encoding no es UTF-8 | Verificar que el archivo tiene contenido |
| La app se congela al escanear | Esta leyendo por red muy lenta | Ya usa threading, verificar conexion de red |
| El tema no persiste | `config.txt` no se puede escribir | Verificar permisos en `%LOCALAPPDATA%\FlexiRipScraping\` |
| Duplicados en la DB | UNIQUE constraint no funciona | Verificar que no se esta usando la DB vieja, eliminar `database.db` y re-escanear |
| Labels no se actualizan al cambiar tema | Version vieja del codigo | Actualizar a la version con zebra striping |
