Taskliste (mit Aufteilung Frontend/Backend)
🧩 Backend
🗂️ Template-Modell + Endpunkte
 [x] Neue SQLite DB mit sql_templates Tabelle erstellt
 [x] SQLAlchemy Model mit Feldern: id, query, source_question, widget_type, refresh_rate, created_at
 [x] Pydantic Schemas für API-Validierung
 [x] POST /api/templates – Template speichern
 [x] GET /api/templates – Templates auflisten
 [x] DELETE /api/templates/{id} – Template löschen

🔁 Scheduler
 [x] Starte beim App-Start einen BackgroundTask mit periodischem Scheduler (asyncio.create_task)
 [x] Führe für jedes Template regelmäßig das SQL-Statement aus (Basis-Implementierung)
 [x] Speichere das Ergebnis in Memory
 [ ] Implementiere tatsächliche Query-Ausführung mit Text2SQLService
 [ ] Implementiere Broadcast an WebSocket-Clients

📡 WebSocket/SSE
 [ ] Endpunkt: GET /api/live (WebSocket oder /events für SSE)
 [ ] Broadcast der neuen Ergebnisse (z. B. als JSON { template_id, result })

🎨 Frontend
🧱 Komponenten
 [ ] Neue Komponente LiveTileGrid mit mehreren LiveTile-Instanzen

 [ ] LiveTile zeigt:
    [ ] Titel aus source_question
    [ ] Widget (Chart, Table, etc.)
    [ ] Live-Daten

🌐 Verbindung zu Server
 [ ] WebSocket-/SSE-Client in LiveTileGrid.tsx
 [ ] Zuordnung der Ergebnisse zu template_id
 [ ] Aktualisierung der zugehörigen Kachel bei eingehendem Event

📦 Integration
 [ ] Neue Schaltfläche „Als Live-Tile speichern" beim SQL-Ergebnis
 [ ] Dialog zur Auswahl von widget_type und refresh_rate
 [ ] POST an /api/templates senden