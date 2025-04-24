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
   - [ ] In `text2sql/core/interfaces.py` die Interfaces anlegen:  
     - `ISchemaLoader`  
     - `IText2SQLAgent`  
     - `IExecutor`  
   - [ ] In `text2sql/core/models.py` DTO-Klassen erstellen:  
     - `NLQuery`  
     - `SQLQuery`  
     - `QueryResult`  

3. **Datenbank-Connector implementieren**  
   - [ ] In `text2sql/db/connector.py`  
     - SQLAlchemy-Engine initialisieren.  
     - Einen `SQLDatabaseConnector` schreiben, der eine Verbindung herstellt und Metadaten lädt.  
   - [ ] Unit-Test in `tests/test_connector.py` für Verbindungsaufbau und Metadaten-Abfrage.  

4. **Schema Loader umsetzen**  
   - [ ] In `text2sql/db/schema_loader.py`  
     - Tabellen und Spalten aus der Datenbank introspektieren.  
     - Ergebnis als Schema-Beschreibung bereitstellen.  
   - [ ] Unit-Test in `tests/test_schema_loader.py` schreiben.  

5. **Text2SQL Agent**  
   - [ ] In `text2sql/agent/sql_agent.py`  
     - `NLSQLTableQueryEngine` (LlamaIndex) konfigurieren und in eine Klasse `Text2SQLAgent` kapseln.  
     - Prompt-Templates in `agent/prompt_templates.py` anpassen (z. B. System- und User-Prompts).  
   - [ ] Unit-Test in `tests/test_agent.py` zum Generieren von SQL aus Beispiel-NL-Fragen.  

6. **SQL-Executor bauen**  
   - [ ] In `text2sql/execution/executor.py`  
     - Methode `execute(sql_query: SQLQuery) -> QueryResult` implementieren.  
     - SQL sicher ausführen und Ergebnisse (Rows, Spaltennamen) sammeln.  
   - [ ] Unit-Test in `tests/test_executor.py` für einfache SELECT-Queries.  

7. **CLI & SDK**  
   - [ ] In `text2sql/cli/main.py`  
     - Typer-Befehle definieren:  
       - `t2s query "<Frage>"` → Rückgabe von `QueryResult`.  
       - `t2s explain "<Frage>"` → zeigt generierten SQL.  
       - `t2s status` → prüft DB-Verbindung.  
   - [ ] In `text2sql/__init__.py` SDK-Funktionen bereitstellen:  
     - `query(nl: str) -> QueryResult`  
     - `explain(nl: str) -> str`  
   - [ ] CLI-Tests in `tests/test_cli_text2sql.py` schreiben.  

8. **Integrationstest**  
   - [ ] Kompletten Workflow in einem Test validieren:  
     - NL-Frage → Agent → SQL → Executor → Ergebnisformat.  
   - [ ] Beispiel-Datenbank (z. B. SQLite) für Tests anlegen und einbinden.  

9. **Dokumentation & Demo**  
   - [ ] README-Abschnitt „Text2SQL" ergänzen (Quickstart, Beispiele).  
   - [ ] Beispiel-Datenbank und Beispiel-Fragen im Repository bereitstellen.  

10. **Optional: CI-Integration**  
   - [ ] CI-Jobs (z. B. GitHub Actions) um Tasks für Text2SQL-Tests erweitern.  

---

**Tipp:** Arbeite erst am nächsten Feature nachdem alle Test Lint-Stati grün sind.