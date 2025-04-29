Product Requirements Document (PRD)
Feature Name: Live SQL Dashboard Tiles
Ziel:
Ermögliche es Nutzern, SQL-Templates aus ihren generierten Abfragen zu speichern und diese periodisch im Backend auszuführen. Die Ergebnisse werden per WebSocket oder SSE live im Dashboard angezeigt.

Anforderungen
1. SQL Template Spezifikation
Ein Template besteht aus:

query: SQL-Statement (z. B. "SELECT * FROM invoices WHERE currency = 'EUR'")

source_question: ursprüngliche natürliche Spracheingabe

widget_type: Art der Darstellung (z. B. "table", "line_chart", "bar_chart")

refresh_rate: Intervall in Sekunden zur Ausführung des Queries

2. Template Management API
POST /api/templates: Speichert ein neues Template in der Datenbank

GET /api/templates: Listet alle gespeicherten Templates

DELETE /api/templates/{id}: Entfernt ein Template

3. Background Scheduler
Führt gespeicherte Queries alle refresh_rate Sekunden aus

Speichert das Ergebnis in Memory

Sendet die Daten über WebSocket oder SSE an das Frontend

4. Frontend Integration
Neue Komponente „LiveTileGrid“, die alle aktiven Tiles darstellt

Jedes Tile zeigt:

Titel (basierend auf Frage)

Widget (entsprechend widget_type)

Live-Daten

Verwendung von WebSocket oder SSE zum Empfang

