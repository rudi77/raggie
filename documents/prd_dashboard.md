Hier ist die vollständige Projektstruktur, die alle bestehenden Komponenten (**RAG**, **Text2SQL**) sowie die neuen Komponenten (**Dashboard Frontend** und **Backend**) übersichtlich integriert:

```text
projekt_root/
├── .venv/
├── data/                       # Beispieldatenbanken & andere Rohdaten
├── documents/                  # Dokumente für RAG-System
├── frontend/                   # Dashboard-Frontend (React)
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── DynamicRenderer.tsx
│   │   │   └── ...
│   │   ├── App.tsx
│   │   ├── index.tsx
│   │   └── ...
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   ├── vite.config.ts (oder webpack.config.js)
│   └── tsconfig.json
├── backend/                    # FastAPI-Backend
│   ├── main.py                 # API-Entrypoint
│   ├── api/
│   │   ├── __init__.py
│   │   ├── sql_queries.py      # Text2SQL API-Endpunkte
│   │   ├── rag_queries.py      # (zukünftig) RAG API-Endpunkte
│   │   └── components.py       # LLM-generierter React-Code
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llamaindex_service.py  # Integration des Text2SQL-Agent
│   │   └── rag_service.py         # (zukünftig) RAG-Service
│   └── core/
│       ├── __init__.py
│       └── models.py           # API Models & DTOs
├── rag/                        # Vorhandene RAG-Komponente
│   ├── chunking/
│   ├── cli/
│   ├── core/
│   ├── embedding/
│   ├── ingestion/
│   ├── llm/
│   ├── store/
│   └── __init__.py
├── text2sql/                   # Vorhandene Text2SQL-Komponente
│   ├── agent/
│   ├── cli/
│   ├── core/
│   ├── db/
│   ├── execution/
│   ├── tests/
│   └── __init__.py
├── tests/                      # Übergreifende Tests
│   ├── test_rag/
│   ├── test_text2sql/
│   └── test_backend/
├── scripts/                    # Skripte für Verwaltung & Deployment
│   └── db_init.sql             # Beispiel-Skript für DB-Initialisierung
├── Dockerfile                  # Backend Docker-Container
├── docker-compose.yml          # Lokale Entwicklungsumgebung
├── pyproject.toml              # Python-Projektdefinition (uv)
└── README.md                   # Projektdokumentation
```

---

### Erläuterungen zur Struktur:

**`frontend/` (React Dashboard)**  
- React-Komponenten für Chat-Oberfläche und dynamische Widget-Darstellung.
- Bestehender Code aus deinem bisherigen Dashboard-Ansatz (`DynamicRenderer.tsx`, `ChatInterface.tsx`).

**`backend/` (FastAPI Backend)**  
- Bindeglied zwischen Frontend, RAG und Text2SQL.
- API-Routen:
  - `/api/sql_queries`: Schnittstelle zum Text2SQL-Agent.
  - `/api/rag_queries`: Schnittstelle zur RAG-Komponente (zukünftige Erweiterung).
- Services integrieren bestehende Komponenten aus `rag` und `text2sql`.

**`rag/` & `text2sql/` (Vorhanden)**  
- Bleiben eigenständige Module.
- Werden vom Backend über ihre öffentlichen Schnittstellen (API-Funktionen) aufgerufen.

**`tests/`**  
- Übergreifende Integrationstests, zusätzlich zu komponentenspezifischen Tests in den jeweiligen Modulen.

**Docker & Deployment**  
- `Dockerfile` und `docker-compose.yml` für einfache lokale Ausführung (Backend, Frontend, DB).

---

### Abhängigkeiten und Integration:

Das **Backend** (FastAPI) greift via Python-Importe direkt auf die Module in den Ordnern **`rag`** und **`text2sql`** zu:

```python
# backend/services/llamaindex_service.py
from text2sql.agent.sql_agent import Text2SQLAgent

# backend/services/rag_service.py (zukünftig)
from rag import answer
```

---

### Lokale Entwicklungsumgebung (Docker Compose Beispiel):

**docker-compose.yml**
```yaml
version: "3.8"

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - OPENAI_API_KEY=your-api-key

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app/frontend
    depends_on:
      - backend

  db:
    image: sqlite:latest  # oder andere DB
    volumes:
      - ./data:/data
```

---

### Typischer Ablauf des PoC:

1. **Start der Umgebung:**
   ```bash
   docker-compose up --build
   ```

2. **Frage stellen:**  
   Nutzer stellt über das Frontend eine natürliche Sprache-Frage.

3. **Backend-Verarbeitung:**  
   - Frage wird zu SQL übersetzt.
   - SQL-Query ausgeführt.
   - Ergebnis (Text, Tabelle oder Chart-Code) zurückgegeben.

4. **Frontend-Darstellung:**  
   - React-Code (vom Backend geliefert) wird kompiliert & dargestellt.

---

### Nächste Erweiterungsschritte nach dem PoC:

- Integration der RAG-Komponente für dokumentenbasierte Anfragen.
- Authentifizierung und Autorisierung (via Security & Audit Service).
- Persistierung von User-Interaktionen und erstellten Widgets.

---

**Fazit:**  
Diese Struktur bietet dir eine solide, skalierbare Basis für die Weiterentwicklung deines CxO-Dashboards. Du hast klare Trennungen, saubere Schnittstellen und maximale Flexibilität für künftige Erweiterungen.