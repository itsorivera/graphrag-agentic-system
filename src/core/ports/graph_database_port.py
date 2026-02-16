from abc import ABC, abstractmethod
from typing import Any, List, Dict

class GraphDatabasePort(ABC):
    """Abstract port defining the contract for graph database operations.
    
    Only exposes business-level operations (query execution, schema retrieval).
    Connection management is an internal responsibility of the concrete adapter.
    """

    @abstractmethod
    def execute_query(self, query: str, params: dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        """Execute a read query against the graph database."""
        pass

    @abstractmethod
    def get_schema(self) -> List[Dict[str, Any]]:
        """Retrieve the database schema."""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Clean up any resources (e.g., close connections)"""
        pass