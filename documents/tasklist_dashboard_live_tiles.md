Taskliste (mit Aufteilung Frontend/Backend)
🧩 Backend
🗂️ Template-Modell + Endpunkte
 [x] Neue SQLite DB mit sql_templates Tabelle erstellt
 [x] SQLAlchemy Model mit Feldern: id, query, source_question, widget_type, refresh_rate, created_at, last_execution
 [x] Pydantic Schemas für API-Validierung
 [x] POST /api/templates – Template speichern
 [x] GET /api/templates – Templates auflisten
 [x] DELETE /api/templates/{id} – Template löschen

🔁 Scheduler
 [x] Starte beim App-Start einen BackgroundTask mit periodischem Scheduler (asyncio.create_task)
 [x] Führe für jedes Template regelmäßig das SQL-Statement aus (Basis-Implementierung)
 [x] Speichere das Ergebnis in Memory mit Cleanup-Mechanismus
 [x] Implementiere tatsächliche Query-Ausführung mit Text2SQLService
 [x] Implementiere strukturiertes Result-Format (ExecutionResult)
 [x] Implementiere Broadcast an WebSocket-Clients

📡 WebSocket/SSE
 [x] Endpunkt: GET /api/live (WebSocket)
 [x] Broadcast der neuen Ergebnisse (als JSON { template_id, result })
 [x] Connection Management (connect/disconnect handling)
 [x] Health Check System (Ping/Pong)
 [x] Initiale Datenübertragung bei Verbindung
 [x] Manuelle Aktualisierung via get_results Message

🎨 Frontend
🧱 Komponenten
 [ ] Neue Komponente LiveTileGrid mit mehreren LiveTile-Instanzen
    [ ] Grid-Layout mit responsivem Design
    [ ] Automatische Anordnung der Tiles
    [ ] Loading States für Tiles

 [ ] LiveTile Komponente:
    [ ] Titel aus source_question
    [ ] Widget basierend auf widget_type
    [ ] Error Handling & Display
    [ ] Refresh-Indikator
    [ ] Aktualisierungszeitpunkt
    [ ] Optionaler Reload-Button

 [ ] Widget Komponenten:
    [ ] Tabellen-Widget
    [ ] Linien-Diagramm
    [ ] Balken-Diagramm
    [ ] Erweiterbar für neue Widget-Typen

🌐 Verbindung zu Server
 [ ] WebSocket-Client Service
    [ ] Verbindungsaufbau & Auto-Reconnect
    [ ] Health Check Handling
    [ ] Event System für Updates
 [ ] Template Service
    [ ] CRUD Operationen für Templates
    [ ] Caching der Template-Daten
 [ ] State Management
    [ ] Template-Zustand
    [ ] Live-Daten Zustand
    [ ] Verbindungsstatus

📦 Integration
 [ ] Neue Schaltfläche „Als Live-Tile speichern" beim SQL-Ergebnis
 [ ] Dialog zur Template-Konfiguration:
    [ ] Widget-Typ Auswahl mit Preview
    [ ] Refresh-Rate Einstellung
    [ ] Titel/Beschreibung bearbeiten
 [ ] Template Management:
    [ ] Liste aller Templates
    [ ] Bearbeiten/Löschen von Templates
    [ ] Status-Anzeige (aktiv/inaktiv)

🔧 Zusätzliche Features
 [ ] Fehlerbehandlung & Retry-Mechanismen
    [ ] Automatischer Reconnect bei Verbindungsverlust
    [ ] Retry bei fehlgeschlagenen Queries
 [ ] Performance Optimierungen
    [ ] Virtualisierte Liste für viele Tiles
    [ ] Lazy Loading für Widget-Komponenten
 [ ] Benutzerfreundlichkeit
    [ ] Drag & Drop für Tile-Anordnung
    [ ] Größenänderung der Tiles
    [ ] Filter & Suche für Templates