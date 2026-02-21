## Logica del programa

RIPLOG.HTML -> Watcher detecta cambio (watchdog)
      ↓
parser -> beautifulsoup4
      ↓
SQLite.db -> sqlite3
      ↓
búsquedas instantáneas

## Arquitectura

riplog_parser/
│
├── main.py
├── config.py
│
├── data/
│   └── database.db
│
├── parser/
│   ├── html_reader.py
│   ├── extractor.py
│   └── normalizer.py
│
├── database/
│   ├── connection.py
│   └── queries.py
│
├── services/
│   ├── sync_service.py
│   └── search_service.py
│
└── utils/
    └── helpers.py


## Instalaciones

python -m pip install beautifulsoup4 lxml

## Estructura de Tablas

<Table>
      <TR>
            <H1>Titulo
            <TH>Clave</TH>
            <TD>Valor</TD>    
      </TR>
</Table>