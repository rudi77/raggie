## Taskliste zur Implementierung der Text2SQL-Komponente

1. **Projektstruktur anlegen**  
   - [x] Erstelle einen neuen Ordner `text2sql/` auf derselben Ebene wie `rag/`.  
   - [x] Lege Unterverzeichnisse an:  
     - `core/`  
     - `db/`  
     - `agent/`  
     - `execution/`  
     - `cli/`  
     - `tests/`  

2. **Core-Abstraktionen definieren**  
   - [x] In `text2sql/core/interfaces.py` die Interfaces anlegen:  
     - [x] `SchemaLoader`  
     - [x] `DatabaseConnector`  
     - [x] `QueryEngine`  
     - [x] `SQLExecutor`  
     - [x] `ResultFormatter`  
   - [x] In `text2sql/core/schema.py` Schema-Modelle erstellen:  
     - [x] `Column`  
     - [x] `Table`  
     - [x] `DatabaseSchema`  
   - [x] In `text2sql/core/config.py` Konfigurationsmodelle:  
     - [x] `DatabaseConfig`  
     - [x] `LLMConfig`  
     - [x] `Text2SQLConfig`  
   - [x] In `text2sql/core/exceptions.py` Fehlerklassen:  
     - [x] `Text2SQLError`  
     - [x] `SchemaError`  
     - [x] `ConnectionError`  
     - [x] `QueryGenerationError`  
     - [x] `QueryExecutionError`  
     - [x] `FormattingError`  

3. **Basis-Implementierungen**  
   - [x] In `text2sql/core/base.py` Basisklassen erstellen:  
     - [x] `BaseSchemaLoader`  
     - [x] `BaseDatabaseConnector`  
     - [x] `BaseQueryEngine`  
     - [x] `BaseSQLExecutor`  
     - [x] `BaseResultFormatter`  

4. **SQLite-Implementierung**  
   - [x] In `text2sql/core/sqlite.py` SQLite-spezifische Klassen:  
     - [x] `SQLiteSchemaLoader`  
     - [x] `SQLiteConnector`  
     - [x] `SQLiteExecutor`  
   - [x] Unit-Tests in `tests/test_sqlite.py`:
     - [x] Test-Datenbank-Setup
     - [x] Connector-Tests
     - [x] Executor-Tests
     - [x] Fehlerbehandlung

5. **Query Generation Engine**  
   - [x] In `text2sql/agent/sql_agent.py`:
     - [x] LlamaIndex's NLSQLTableQueryEngine Integration für SQL-Generierung
     - [x] Schema-Kontext-Integration
     - [x] Query-Validierung
   - [ ] Unit-Tests in `tests/test_engine.py`

6. **Result Formatter**  
   - [x] In `text2sql/formatters/`:
     - [x] `TextFormatter` für lesbare Ausgabe
     - [x] `JSONFormatter` für API-Integration
     - [x] `CSVFormatter` für Datenexport
   - [ ] Unit-Tests in `tests/test_formatters.py`

7. **CLI & SDK**  
   - [ ] In `text2sql/cli/main.py`:
     - [ ] Typer-Befehle definieren:
       - [ ] `t2s query "<Frage>"` → Rückgabe von `QueryResult`
       - [ ] `t2s explain "<Frage>"` → zeigt generierten SQL
       - [ ] `t2s status` → prüft DB-Verbindung
       - [ ] `t2s config` → Konfiguration verwalten
   - [ ] In `text2sql/__init__.py` SDK-Funktionen:
     - [ ] `query(nl: str) -> QueryResult`
     - [ ] `explain(nl: str) -> str`
     - [ ] `configure(config: Text2SQLConfig)`
   - [ ] CLI-Tests in `tests/test_cli.py`

8. **Integration & Tests**  
   - [ ] Kompletten Workflow in `tests/test_integration.py`:
     - [ ] NL-Frage → Agent → SQL → Executor → Ergebnisformat
     - [ ] Fehlerbehandlung und Edge Cases
     - [ ] Performance-Tests
   - [ ] Beispiel-Datenbank und Beispieldaten:
     - [ ] SQLite-Schema für Tests
     - [ ] Beispieldaten für verschiedene Anwendungsfälle
     - [ ] Dokumentation der Testfälle

9. **Dokumentation**  
   - [ ] README-Abschnitt "Text2SQL":
     - [ ] Quickstart-Guide
     - [ ] Konfigurationsoptionen
     - [ ] API-Dokumentation
     - [ ] Beispiele und Use Cases
   - [ ] Code-Dokumentation:
     - [ ] Docstrings vervollständigen
     - [ ] Typ-Annotationen prüfen
     - [ ] Beispiele in Docstrings

10. **CI/CD & Qualität**  
    - [ ] GitHub Actions erweitern:
      - [ ] Text2SQL-spezifische Tests
      - [ ] Linting und Type-Checking
      - [ ] Coverage-Reports
    - [ ] Code-Qualität:
      - [ ] Ruff-Konfiguration anpassen
      - [ ] MyPy-Konfiguration prüfen
      - [ ] Black-Formatierung sicherstellen

---

**Nächste Schritte:**
1. ~~Query Generation Engine implementieren~~ ✓ (Implementiert mit LlamaIndex's NLSQLTableQueryEngine)
2. ~~Result Formatter entwickeln~~ ✓ (Implementiert mit Text, JSON und CSV Formatter)
3. CLI & SDK aufbauen

**Tipp:** Arbeite erst am nächsten Feature nachdem alle Test- und Lint-Stati grün sind.