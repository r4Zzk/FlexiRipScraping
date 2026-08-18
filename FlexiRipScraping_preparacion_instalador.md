# Plan de migración y preparación para distribución de FlexiRipScraping

## Objetivo

Modificar el proyecto **FlexiRipScraping** para que quede preparado
para:

1.  Ejecutarse normalmente durante el desarrollo.
2.  Empaquetarse con **PyInstaller** sin depender de Python instalado en
    la PC destino.
3.  Generar posteriormente un instalador `.exe` con **Inno Setup**.
4.  Mantener `config.txt` y la base SQLite fuera de `Program Files`, en
    una ubicación escribible por el usuario.
5.  Permitir actualizar la aplicación sin perder la configuración ni la
    base de datos.
6.  Mantener la arquitectura actual del proyecto y evitar cambios
    innecesarios.

**IMPORTANTE:** antes de modificar código, inspeccionar el proyecto
completo y adaptar estas instrucciones al código existente. No
reemplazar archivos completos de forma ciega si ya contienen lógica
válida.

------------------------------------------------------------------------

# 1. Estructura deseada

La estructura de código debe quedar aproximadamente así:

``` text
FlexiRipScraping/
├── FlexiRipScraping/
│   ├── assets/
│   │   ├── icon.png
│   │   └── icon.ico
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── queries.py
│   │
│   ├── gui/
│   │   ├── __init__.py
│   │   └── app.py
│   │
│   ├── parser/
│   │   ├── __init__.py
│   │   └── ...
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── ...
│   │
│   ├── config.py
│   └── main.py
│
├── requirements.txt
├── README.md
└── Estructura.md
```

No distribuir:

-   `.venv/`
-   `__pycache__/`
-   archivos `.pyc`
-   la base SQLite de desarrollo
-   archivos temporales
-   archivos generados por PyInstaller (`build/`, `dist/`, `.spec`)
    salvo que se necesiten explícitamente para el proceso de build.

------------------------------------------------------------------------

# 2. Corregir paquetes Python

Verificar que existan estos archivos:

``` text
database/__init__.py
gui/__init__.py
parser/__init__.py
services/__init__.py
```

Si actualmente existe un archivo con un nombre incorrecto como:

``` text
__init_ .py
```

corregirlo a:

``` text
__init__.py
```

Los `__init__.py` pueden quedar vacíos si no necesitan contenido.

No modificar otros imports salvo que sea necesario para corregir rutas.

------------------------------------------------------------------------

# 3. No distribuir database.db dentro del programa

Actualmente existe:

``` text
FlexiRipScraping/data/database.db
```

La base de datos NO debe depender de esa ubicación cuando la aplicación
esté instalada.

La aplicación debe crear/usar la base SQLite en:

``` text
%LOCALAPPDATA%\FlexiRipScraping\database.db
```

Por ejemplo:

``` text
C:\Users\Usuario\AppData\Local\FlexiRipScraping\database.db
```

La carpeta debe crearse automáticamente si no existe.

La base de datos existente de desarrollo no debe copiarse
automáticamente a la instalación final, salvo que el código actual
demuestre que contiene datos iniciales imprescindibles.

Si se necesita una base inicial con tablas, mantener la lógica de
creación de tablas/migraciones y ejecutarla automáticamente cuando la
base no exista.

------------------------------------------------------------------------

# 4. Modificar config.py

`config.py` debe centralizar las rutas persistentes de usuario.

La lógica esperada es equivalente a:

``` python
from pathlib import Path
import os

APP_NAME = "FlexiRipScraping"

APP_DATA_DIR = Path(os.getenv("LOCALAPPDATA")) / APP_NAME

APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = APP_DATA_DIR / "config.txt"
DATABASE_FILE = APP_DATA_DIR / "database.db"
```

Adaptar esto al código existente en lugar de duplicar lógica.

## Requisitos

`config.py` debe proporcionar al menos:

``` python
APP_DATA_DIR
CONFIG_FILE
DATABASE_FILE
```

La aplicación debe utilizar estas constantes para acceder a
configuración y SQLite.

No usar rutas absolutas específicas del equipo de desarrollo.

No asumir que el programa se ejecuta desde el directorio del proyecto.

No depender del current working directory.

------------------------------------------------------------------------

# 5. Configuración de config.txt

`config.txt` debe vivir en:

``` text
%LOCALAPPDATA%\FlexiRipScraping\config.txt
```

La aplicación debe leerlo desde `CONFIG_FILE`.

Evitar patrones como:

``` python
open("config.txt")
```

o:

``` python
open("./config.txt")
```

cuando se trate del archivo de configuración persistente de la
aplicación.

Utilizar:

``` python
from config import CONFIG_FILE
```

o el import equivalente correcto según la arquitectura actual.

Abrir el archivo con UTF-8:

``` python
with open(CONFIG_FILE, "r", encoding="utf-8") as file:
    ...
```

Mantener exactamente el formato de configuración que ya utiliza la
aplicación, salvo que sea necesario modificarlo.

------------------------------------------------------------------------

# 6. Primera ejecución

Si:

``` text
%LOCALAPPDATA%\FlexiRipScraping\config.txt
```

no existe, la aplicación debe poder iniciar correctamente.

No asumir que el archivo ya existe.

Si el programa actual necesita un `config.txt` inicial, crear uno
automáticamente con valores vacíos o valores predeterminados apropiados,
sin sobrescribir uno existente.

Ejemplo conceptual:

``` python
if not CONFIG_FILE.exists():
    CONFIG_FILE.write_text("", encoding="utf-8")
```

Adaptar esto a la lógica real del proyecto.

IMPORTANTE:

Nunca sobrescribir `config.txt` automáticamente si ya existe.

------------------------------------------------------------------------

# 7. Modificar database/connection.py

Localizar cómo se crea actualmente la conexión SQLite.

Si existe algo similar a:

``` python
sqlite3.connect("data/database.db")
```

o:

``` python
sqlite3.connect("./data/database.db")
```

reemplazar la ruta fija por `DATABASE_FILE`.

Conceptualmente:

``` python
import sqlite3
from ..config import DATABASE_FILE

def get_connection():
    return sqlite3.connect(DATABASE_FILE)
```

Sin embargo, adaptar el import a la forma en que actualmente está
organizado el proyecto.

El objetivo es que la conexión siempre utilice:

``` text
%LOCALAPPDATA%\FlexiRipScraping\database.db
```

La función de conexión existente debe conservar su API si otros módulos
ya la utilizan.

No romper `queries.py`, servicios, parser ni GUI.

------------------------------------------------------------------------

# 8. Creación automática de la base

En una instalación nueva:

``` text
database.db
```

no existirá.

La aplicación debe poder crearla automáticamente.

Revisar el código actual y comprobar si ya existe una función de:

-   inicialización de base
-   creación de tablas
-   migraciones
-   seed inicial

Si existe, reutilizarla.

Si no existe, implementar una inicialización mínima y segura para que
las tablas requeridas se creen al arrancar.

No eliminar datos existentes cuando la base ya existe.

------------------------------------------------------------------------

# 9. Rutas de archivos externos

Las rutas que el usuario configura en `config.txt` son rutas externas a
la aplicación.

Ejemplos:

``` text
C:\Documentos
D:\Proyectos
\\Servidor\Compartido
```

El instalador NO debe copiar estas carpetas.

La aplicación simplemente debe leerlas desde `config.txt` y trabajar
sobre ellas como lo hace actualmente.

No transformar estas rutas en rutas relativas al ejecutable.

------------------------------------------------------------------------

# 10. Assets

Mantener:

``` text
assets/
└── icon.png
```

si la aplicación lo utiliza en CustomTkinter.

Agregar/preparar:

``` text
assets/
└── icon.ico
```

para el ejecutable de Windows.

El `.ico` debe contener resoluciones apropiadas para Windows,
idealmente:

-   16x16
-   32x32
-   48x48
-   64x64
-   128x128
-   256x256

No eliminar `icon.png` si la GUI lo utiliza.

------------------------------------------------------------------------

# 11. Rutas de assets dentro de PyInstaller

Revisar cómo se cargan actualmente imágenes y otros recursos.

Evitar asumir que el current working directory es la raíz del proyecto.

Preparar una función para resolver recursos empaquetados si es
necesario.

Una solución habitual es:

``` python
from pathlib import Path
import sys

def resource_path(relative_path):
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    return base_path / relative_path
```

Adaptar la ubicación de `assets` a la arquitectura real del proyecto.

No aplicar esta función indiscriminadamente a `config.txt` ni a
`database.db`.

Diferenciar:

### Recursos de la aplicación

Ejemplos:

``` text
icon.png
icon.ico
imágenes
fuentes
```

Estos pueden estar empaquetados con PyInstaller.

### Datos persistentes del usuario

Ejemplos:

``` text
config.txt
database.db
```

Estos deben permanecer en:

``` text
%LOCALAPPDATA%\FlexiRipScraping\
```

------------------------------------------------------------------------

# 12. Revisar imports

Antes de empaquetar, inspeccionar:

``` text
main.py
gui/
parser/
services/
database/
```

y detectar:

-   imports relativos
-   imports absolutos
-   módulos cargados dinámicamente
-   imports condicionales
-   recursos externos
-   dependencias que PyInstaller pueda no detectar automáticamente.

Mantener los imports consistentes.

No cambiar toda la arquitectura a otro sistema de imports salvo que sea
imprescindible.

------------------------------------------------------------------------

# 13. requirements.txt

Revisar `requirements.txt`.

Debe contener las dependencias necesarias para ejecutar la aplicación.

Por ejemplo, si actualmente utiliza CustomTkinter:

``` text
customtkinter
```

No agregar dependencias innecesarias.

`sqlite3` NO debe agregarse a `requirements.txt` porque forma parte de
la biblioteca estándar de Python.

PyInstaller sí puede agregarse como dependencia de desarrollo/build si
se considera conveniente:

``` text
pyinstaller
```

No es necesario que el usuario final instale PyInstaller.

------------------------------------------------------------------------

# 14. Preparar PyInstaller

Una vez que el código funcione correctamente, crear un archivo:

``` text
FlexiRipScraping.spec
```

preferentemente mediante PyInstaller y luego ajustarlo.

Inicialmente se busca generar una aplicación:

``` text
dist/
└── FlexiRipScraping/
    ├── FlexiRipScraping.exe
    └── ...
```

Preferir inicialmente modo `onedir` en lugar de `onefile`.

Motivo:

-   mejor manejo de assets
-   arranque más simple
-   menos problemas con recursos externos
-   más práctico para una aplicación de escritorio instalada
-   facilita el instalador con Inno Setup.

No incluir:

``` text
config.txt
database.db
```

como datos persistentes dentro del directorio de instalación.

------------------------------------------------------------------------

# 15. Comando inicial de build

Después de preparar el código, el build conceptual será:

``` bash
pyinstaller --onedir --windowed --name "FlexiRipScraping" --icon="FlexiRipScraping/assets/icon.ico" FlexiRipScraping/main.py
```

Pero si se crea un `.spec`, preferir:

``` bash
pyinstaller FlexiRipScraping.spec
```

El `.spec` debe incluir los assets necesarios.

------------------------------------------------------------------------

# 16. Importante: no confundir instalación con datos

La aplicación instalada debería quedar conceptualmente:

``` text
C:\Program Files\FlexiRipScraping\
├── FlexiRipScraping.exe
└── ...
```

Mientras que los datos del usuario deberían quedar:

``` text
C:\Users\Usuario\AppData\Local\FlexiRipScraping\
├── config.txt
└── database.db
```

Esto permite:

-   actualizar el programa
-   desinstalar/reinstalar el programa
-   conservar configuración
-   conservar índice/base SQLite
-   evitar problemas de permisos de Windows.

------------------------------------------------------------------------

# 17. No implementar todavía Inno Setup

En esta etapa NO crear todavía el instalador de Inno Setup.

Primero verificar que:

``` text
python main.py
```

funcione.

Después verificar que:

``` text
pyinstaller FlexiRipScraping.spec
```

produzca una aplicación funcional.

Luego probar:

``` text
dist/FlexiRipScraping/FlexiRipScraping.exe
```

en una máquina/entorno donde no esté disponible el entorno virtual del
proyecto.

Una vez que esto funcione, se puede crear el instalador con Inno Setup.

------------------------------------------------------------------------

# 18. Pruebas obligatorias

Después de modificar el proyecto, comprobar:

## Desarrollo

``` text
python main.py
```

Debe:

-   abrir CustomTkinter
-   leer configuración
-   acceder a SQLite
-   buscar/indexar archivos
-   mostrar resultados
-   guardar cambios.

## Primera ejecución sin datos

Eliminar temporalmente:

``` text
%LOCALAPPDATA%\FlexiRipScraping\
```

y ejecutar la aplicación.

Debe crear:

``` text
%LOCALAPPDATA%\FlexiRipScraping\
├── config.txt
└── database.db
```

según corresponda a la lógica de inicialización.

## Segunda ejecución

Cerrar y volver a abrir.

Debe conservar:

-   configuración
-   base SQLite
-   datos indexados.

## Rutas externas

Probar una ruta local y, si la aplicación lo soporta actualmente, una
ruta de red como:

``` text
\\Servidor\Compartido
```

No modificar la lógica de acceso a estas rutas salvo que sea necesario.

## Build

Generar con PyInstaller y comprobar que:

-   abre la GUI
-   aparece el icono
-   CustomTkinter funciona
-   SQLite funciona
-   config.txt funciona
-   las rutas configuradas funcionan
-   la indexación funciona
-   las consultas funcionan
-   los assets funcionan.

------------------------------------------------------------------------

# 19. Compatibilidad con futuras actualizaciones

La aplicación debe estar preparada para que en el futuro:

``` text
FlexiRipScraping v1
```

pueda actualizarse a:

``` text
FlexiRipScraping v2
```

sin eliminar:

``` text
%LOCALAPPDATA%\FlexiRipScraping\config.txt
%LOCALAPPDATA%\FlexiRipScraping\database.db
```

No colocar datos persistentes del usuario dentro de la carpeta del
ejecutable.

------------------------------------------------------------------------

# 20. Reglas importantes para realizar los cambios

1.  Primero inspeccionar todo el proyecto.
2.  Identificar exactamente cómo se leen actualmente las rutas.
3.  Identificar exactamente cómo se abre SQLite.
4.  Identificar cómo se cargan los assets.
5.  Identificar cómo se inicializan las tablas.
6.  Mantener la funcionalidad existente.
7.  No reescribir módulos completos sin necesidad.
8.  No cambiar nombres de funciones públicas si otros módulos dependen
    de ellas.
9.  No eliminar código existente sin comprobar sus referencias.
10. No eliminar la base de desarrollo automáticamente.
11. No sobrescribir un `config.txt` existente.
12. No utilizar rutas absolutas específicas del equipo de desarrollo.
13. No depender del current working directory.
14. No almacenar `database.db` dentro de `Program Files`.
15. No almacenar `config.txt` dentro de `Program Files`.
16. No distribuir `.venv`.
17. No distribuir `__pycache__`.
18. No incluir datos personales o rutas específicas del equipo de
    desarrollo en el código.
19. Mantener CustomTkinter y SQLite funcionando como actualmente.
20. Al finalizar, informar claramente qué archivos fueron modificados y
    qué cambió en cada uno.

------------------------------------------------------------------------

# 21. Resultado esperado

Al finalizar esta etapa, el proyecto debe quedar listo para el siguiente
flujo:

``` text
Código fuente
     │
     ▼
PyInstaller
     │
     ▼
dist/FlexiRipScraping/
     │
     ▼
FlexiRipScraping.exe
     │
     ▼
Inno Setup
     │
     ▼
FlexiRipScraping_Setup.exe
```

Cuando el usuario instale el programa:

``` text
Program Files
└── FlexiRipScraping
    └── FlexiRipScraping.exe
```

y los datos:

``` text
AppData
└── Local
    └── FlexiRipScraping
        ├── config.txt
        └── database.db
```

La aplicación debe funcionar desde cero sin que el usuario tenga que
instalar:

-   Python
-   pip
-   CustomTkinter
-   SQLite
-   PyInstaller
-   ninguna dependencia de desarrollo.

------------------------------------------------------------------------

# 22. Tarea para OpenCode

Ejecutar los cambios anteriores sobre el proyecto actual.

**No limitarse a crear archivos nuevos:** inspeccionar primero el código
existente y adaptar las modificaciones.

Al terminar:

1.  Mostrar un resumen de los archivos modificados.
2.  Mostrar los cambios importantes realizados.
3.  Indicar si quedaron archivos que requieren revisión manual.
4.  Verificar que `python main.py` siga funcionando.
5.  Preparar el proyecto para el siguiente paso: creación del `.spec` de
    PyInstaller.
6.  No crear todavía el instalador de Inno Setup.
