import os
import re
from typing import Any, List, Dict
from neo4j import GraphDatabase, Driver
from core.ports.graph_database_port import GraphDatabasePort
from utils.neo4j_serializer import serialize_neo4j_value
import traceback

class Neo4jDatabaseAdapter(GraphDatabasePort):
    def __init__(self, 
                 neo4j_uri: str = None,
                 neo4j_username: str = None,
                 neo4j_password: str = None):
        self.neo4j_uri = neo4j_uri or os.getenv('NEO4J_URI')
        self.neo4j_username = neo4j_username or os.getenv('NEO4J_USERNAME')
        self.neo4j_password = neo4j_password or os.getenv('NEO4J_PASSWORD')

        self._driver = None

    def _get_driver(self) -> Driver:
        """Lazy-initialize and return the Neo4j driver instance.
        Creates the connection on first call, reuses it on subsequent calls.
        This is an internal detail — not part of the public port contract.
        """
        if self._driver is None:
            if not self.neo4j_uri or not self.neo4j_username or not self.neo4j_password:
                raise ValueError("Neo4j configuration missing (NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)")
            
            print("Initializing Neo4j driver")
            self._driver = GraphDatabase.driver(
                self.neo4j_uri, 
                auth=(self.neo4j_username, self.neo4j_password)
            )
            self._driver.verify_connectivity()
            print("Neo4j driver connected successfully")
        
        return self._driver

    def is_write_query(self, query: str) -> bool:
        return re.search(r"\b(MERGE|CREATE|SET|DELETE|REMOVE|ADD)\b", query, re.IGNORECASE) is not None

    def execute_query(self, query: str, params: dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        if self.is_write_query(query):
            raise ValueError("Write Queries are not supported in this agent")
        try:
            driver = self._get_driver()
            result = driver.execute_query(query, params)
            return [serialize_neo4j_value(dict(r)) for r in result.records]
        except Exception as e:
            print(f"Error executing query: {e}")
            traceback.print_exc()
            raise e

    def get_schema(self) -> List[Dict[str, Any]]:
        query = """
        call apoc.meta.data() yield label, property, type, other, unique, index, elementType
        where elementType = 'node' and not label starts with '_'
        with label,
        collect(case when type = 'RELATIONSHIP' then [property, head(other)] end) as relationships,
        collect(case when type <> 'RELATIONSHIP' then [property, type + case when unique 
                then " unique" else "" end + case when index then " indexed" else "" end] end) 
        as attributes,

        RETURN label, apoc.map.fromPairs(attributes) as attributes, apoc.map.fromPairs(relationships) as relationships
        """
        return self.execute_query(query)

    def cleanup(self):
        if self._driver is not None:
            self._driver.close()
            self._driver = None
            print("Neo4j driver cleaned up")
