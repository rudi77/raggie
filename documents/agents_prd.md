Hier ist der schrittweise Plan zur Integration des Manager Agents in Ihr Backend unter Verwendung von smolagents:

---

### **1. Verzeichnisstruktur erweitern**
```
backend/
├── services/
│   └── agent_service.py     # Factory für Agenten-Instanzen
agents/                  # Neue Agenten-Implementierungen
  ├── __init__.py
  ├── manager_agent.py   # Haupt-Implementierung
  ├── text2sql_agent.py    # Spezialisierter Agent
  └── interfaces.py        # Abstrakte Klassen für Agenten
```

---

### **2. Abstrakte Schnittstellen definieren** (`interfaces.py`)
```python
from abc import ABC, abstractmethod
from typing import Any, Dict

class IAgent(ABC):
    @abstractmethod
    async def execute(self, task: str) -> Dict[str, Any]:
        pass

class IAgentFactory(ABC):
    @abstractmethod
    def create_agent(self, agent_type: str) -> IAgent:
        pass
```

---

### **3. Manager Agent implementieren** (`manager_agent.py`)
```python
from smolagents import CodeAgent, HfApiModel
from .interfaces import IAgent
from typing import Dict, Any

class CognitiveAgent(IAgent):
    def __init__(self, llm_config: Dict):
        self.llm = HfApiModel(llm_config["model_id"])
        self.agent = CodeAgent(tools=[], model=self.llm)
    
    async def execute(self, task: str) -> Dict[str, Any]:
        result = await self.agent.run(task)
        return {
            "action": "text2sql",  # Delegiert an passenden Agenten
            "input": task,
            "output": result
        }
```

---

### **4. Agenten-Factory erstellen** (`agent_service.py`)
```python
from .agents.interfaces import IAgentFactory
from .agents.manager_agent import CognitiveAgent

class AgentFactory(IAgentFactory):
    def create_agent(self, agent_type: str) -> IAgent:
        if agent_type == "cognitive":
            return CognitiveAgent(llm_config={"model_id": "meta-llama/Llama-3-8B-Instruct"})
        raise ValueError(f"Unknown agent type: {agent_type}")
```

---

### **5. Text2SQL-Agent anpassen** (`text2sql_agent.py`)
```python
from smolagents import tool
from .interfaces import IAgent

@tool
def sql_query(query: str) -> str:
    # Implementierung aus vorhandenem Code übernehmen
    pass

class Text2SQLAgent(IAgent):
    async def execute(self, task: str) -> Dict[str, Any]:
        # Nutzt smolagents Tool-Decorator
        return await sql_query(task)
```

---

### **6. Dependency Injection anpassen** (`dependencies.py`)
```python
from ..services.agent_service import AgentFactory

def get_agent_factory() -> AgentFactory:
    return AgentFactory()

def get_manager_agent(factory: AgentFactory = Depends(get_agent_factory)) -> IAgent:
    return factory.create_agent("cognitive")
```

---

### **7. Route anpassen** (`text2sql.py`)
```python
from ..agents.interfaces import IAgent
from ..dependencies import get_manager_agent

@router.post("/query")
async def execute_query(
    request: QueryRequest,
    agent: IAgent = Depends(get_manager_agent)
):
    result = await agent.execute(request.question)
    if result["action"] == "text2sql":
        # Delegation an Text2SQL-Agent
        sql_agent = get_text2sql_service()
        return await sql_agent.query(result["output"])
```

---

### **8. Konfiguration erweitern** (`config.py`)
```python
class Settings(BaseSettings):
    agent_framework: str = "smolagents"  # Ermöglicht Framework-Wechsel
    llm_model: str = "meta-llama/Llama-3-8B-Instruct"
```

---

### **9. Migrationstests** (`test_agents.py`)
```python
def test_manager_agent_delegation():
    agent = CognitiveAgent(llm_config={"model_id": "test"})
    result = await agent.execute("Umsatz Q1")
    assert "action" in result
    assert result["action"] == "text2sql"
```

---

### **Key Points:**
1. **Abstraktionsebene**:
   - `IAgent` ermöglicht Austausch des Frameworks (z. B. zu LangChain oder andere Agents frameworks)
   - Factory-Pattern für zentrale Agenten-Erstellung

2. **Delegationslogik**:
   - Manager Agent entscheidet über Agenten-Typ (Text2SQL/RAG/Code)
   - Klare Trennung zwischen Entscheidung und Ausführung

3. **Erweiterbarkeit**:
   - Neue Agenten-Typen können einfach hinzugefügt werden
   - LLM-Konfiguration zentral in Settings

4. **Kompatibilität**:
   - Behält bestehende Text2SQL-Route bei
   - Schrittweise Migration möglich

---

### **Next Steps:**
1. Implementierung der `WorkflowService`-Klasse für persistente Workflows
2. WebSocket-Integration für Streaming-Ergebnisse
3. Monitoring-Endpunkt für Agenten-Performance

Möchten Sie dass ich eines dieser Elemente genauer ausarbeite?