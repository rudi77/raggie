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
 [x] Neue Komponente LiveTileGrid mit mehreren LiveTile-Instanzen
    [x] Grid-Layout mit responsivem Design
    [x] Automatische Anordnung der Tiles
    [x] Loading States für Tiles

 [x] LiveTile Komponente:
    [x] Titel aus source_question
    [x] Widget basierend auf widget_type
    [x] Error Handling & Display
    [x] Refresh-Indikator
    [x] Aktualisierungszeitpunkt
    [x] Optionaler Reload-Button

 [x] Widget Komponenten:
    [x] Tabellen-Widget
    [x] Linien-Diagramm
    [x] Balken-Diagramm
    [x] Pie-Chart Widget
    [x] Number-Widget
    [x] Text-Widget
    [ ] Erweiterbar für neue Widget-Typen

🌐 Verbindung zu Server
 [x] WebSocket-Client Service
    [x] Verbindungsaufbau & Auto-Reconnect
    [x] Health Check Handling
    [x] Event System für Updates
 [x] Template Service
    [x] CRUD Operationen für Templates
    [x] Caching der Template-Daten
 [x] State Management
    [x] Template-Zustand
    [x] Live-Daten Zustand
    [x] Verbindungsstatus

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