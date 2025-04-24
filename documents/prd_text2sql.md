## Zusammenfassung

Die **Text2SQL-Komponente** ergänzt dein bestehendes RAG-System um die Fähigkeit, natürlicher Spracheingaben direkt in SQL-Abfragen zu übersetzen und gegen eine relationale Datenbank auszuführen. Dafür nutzt sie den **LlamaIndex SQL Agent** (z. B. `NLSQLTableQueryEngine` oder `SQLTableRetrieverQueryEngine`) als Kern, verbindet sich mittels **SQLAlchemy** mit beliebigen Datenbanken und gibt das Ergebnis der Abfrage in lesbarer Form zurück. Die Komponente wird in einem neuen Verzeichnis `text2sql/` auf derselben Ebene wie `rag/` organisiert, folgt ebenfalls den **SOLID-Prinzipien** und bietet sowohl eine **Python-SDK-API** als auch ein **CLI-Interface**.

---

## Architekturüberblick

```mermaid
flowchart TD
    U[User] -->|NL-Frage| CLI2[CLI / SDK (text2sql)]
    CLI2 --> A[Schema Loader]  
    A --> B[SQLDatabaseConnector]  
    B --> C[NLSQLTableQueryEngine]  
    C --> D[SQLExecutor]  
    D --> E[ResultFormatter]  
    E --> U  
```

1. **Schema Loader** liest die Datenbankstruktur ein und baut einen `SQLDatabase`-Wrapper um deine DB auf. citeturn0search0  
2. **SQLDatabaseConnector** nutzt SQLAlchemy, um sich mit der DB zu verbinden und Metadaten (Tabellen, Spalten) bereitzustellen. citeturn0search9  
3. **NLSQLTableQueryEngine** (oder `SQLTableRetrieverQueryEngine`) formt aus der NL-Eingabe eine SQL-Abfrage. citeturn1search0turn1search1  
4. **SQLExecutor** führt die generierte Abfrage aus und holt die rohen Datensätze. citeturn0search3  
5. **ResultFormatter** wandelt die rohen Zeilen in ein lesbares Text- oder JSON-Format um. citeturn0search4  

---

## Komponenten & Ordnerstruktur

```text
C:.
├───data
├───documents
├───rag
└───text2sql
    ├───__init__.py
    ├───core
    │   ├───interfaces.py     # IText2SQLAgent, ISchemaLoader, IExecutor
    │   └───models.py         # NLQuery, SQLQuery, QueryResult DTOs
    ├───db
    │   ├───connector.py      # SQLDatabaseConnector (SQLAlchemy + llama_index.SQLDatabase) citeturn0search0
    │   └───schema_loader.py  # SchemaLoader: lädt Tabellen/Spalten citeturn1search5
    ├───agent
    │   ├───sql_agent.py      # Text2SQLAgent: Wrapper um NLSQLTableQueryEngine citeturn1search3
    │   └───prompt_templates.py # Anpassen von Text2SQL-Prompts
    ├───execution
    │   └───executor.py       # Executor: führt SQL aus, gibt QueryResult zurück
    ├───cli
    │   └───main.py           # Typer-CLI: Befehle `t2s query`, `t2s status` etc. citeturn0search6
    └───tests
        ├───test_connector.py
        ├───test_agent.py
        └───test_executor.py
```

- **`core/`**  
  - `interfaces.py`: Definiert Abstraktionen nach SOLID (z. B. `IText2SQLAgent`, `ISchemaLoader`, `IExecutor`) citeturn0search6  
  - `models.py`: Data-Transfer-Objects wie `NLQuery`, `SQLQuery`, `QueryResult` citeturn0search5  

- **`db/connector.py`**  
  - Implementiert `SQLDatabaseConnector` mit SQLAlchemy und `llama_index.SQLDatabase` citeturn0search0  

- **`db/schema_loader.py`**  
  - Introspektiert das Schema (Tabellen, Spalten) und liefert Kontext für den Agent citeturn1search5  

- **`agent/sql_agent.py`**  
  - Nutzt `NLSQLTableQueryEngine` bzw. `SQLTableRetrieverQueryEngine` aus LlamaIndex, um NL in SQL zu konvertieren citeturn1search1turn1search0  

- **`execution/executor.py`**  
  - Führt SQL-Abfragen sicher aus, holt Ergebnisse per SQLAlchemy (z. B. `engine.execute(text(sql_query))`) citeturn1search2  

- **`cli/main.py`**  
  - Bietet Typer-Befehle wie  
    - `t2s query "<Frage>"`  
    - `t2s status` (DB-Verbindung prüfen)  
    - `t2s explain "<Frage>"` (zeigt generierte SQL-Query) citeturn0search6  

---

## Umsetzungsschritte

1. **Abstraktionen und DTOs** (`core/`) anlegen – Interfaces und Models definieren. citeturn0search6  
2. **DB-Connector** (`db/connector.py`)  
   - SQLAlchemy-Engine und LlamaIndex `SQLDatabase` instanziieren. citeturn0search0  
3. **Schema Loader** (`db/schema_loader.py`)  
   - Tabellenmetadaten laden und dem Agent übergeben. citeturn1search5  
4. **Text2SQL Agent** (`agent/sql_agent.py`)  
   - Konfiguration von `NLSQLTableQueryEngine`, Prompt-Templates anpassen. citeturn0search3  
5. **Executor** (`execution/executor.py`)  
   - SQL-Ausführung und Mapping auf `QueryResult`. citeturn1search2  
6. **CLI & SDK** (`cli/main.py`)  
   - Typer-Befehle schreiben, SDK-Funktionen in `text2sql/__init__.py` bereitstellen. citeturn0search6  
7. **Tests** (`tests/`)  
   - Unit-Tests für alle Module und Integrationstest von `query → SQL → Ergebnis`. citeturn0search4  

Damit erhältst du eine saubere, modular aufgebaute Text2SQL-Komponente, die sich nahtlos neben deinem bestehenden `rag/`-Verzeichnis einfügt und dank LlamaIndex SQL Agent zuverlässig NL-Fragen in SQL übersetzt und ausführt.