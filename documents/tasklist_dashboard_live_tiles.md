Taskliste (mit Aufteilung Frontend/Backend)
🧩 Backend
🗂️ Template-Modell + Endpunkte
 [x] Neue SQLite DB mit sql_templates Tabelle erstellt
 [x] SQLAlchemy Model mit Feldern: id, query, source_question, widget_type, refresh_rate, created_at
 [x] Pydantic Schemas für API-Validierung
 [ ] POST /api/templates – Template speichern
 [ ] GET /api/templates – Templates auflisten
 [ ] DELETE /api/templates/{id} – Template löschen

🔁 Scheduler
 [ ] Starte beim App-Start einen BackgroundTask mit periodischem Scheduler (z. B. mit asyncio.create_task)
 [ ] Führe für jedes Template regelmäßig das SQL-Statement aus
 [ ] Speichere das Ergebnis in Memory
 [ ] Sende die Daten über WebSocket oder SSE an das Frontend
 [ ] Nutze bestehende Text2SQLService oder direkte DB-Verbindung

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