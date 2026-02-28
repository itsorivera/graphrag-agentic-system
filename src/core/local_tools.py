from typing import Any
from src.adapter.repository.graph_database.neo4j_adapter import Neo4jDatabaseAdapter

db_instance = Neo4jDatabaseAdapter()

def get_schema() -> list[dict[str,Any]]:
  """Get the schema of the database, returns node-types(labels) with their types and attributes and relationships between node-labels
  Args: None
  Returns:
    list[dict[str,Any]]: A list of dictionaries representing the schema of the database
    For example
    ```
    [{'label': 'Person','attributes': {'summary': 'STRING','id': 'STRING unique indexed', 'name': 'STRING indexed'},
      'relationships': {'HAS_PARENT': 'Person', 'HAS_CHILD': 'Person'}}]
    ```
  """
  if not db_instance:
      return [{"error": "Database not initialized"}]
  try:
      # Use the method on the adapter which encapsulates the query
      # Note: The adapter implementation of get_schema returns the result directly.
      # However, the tool docstring implies it returns a list of dicts.
      # The adapter implementation I wrote calls execute_query which returns list of dicts.
      return db_instance.get_schema()
  except Exception as e:
      return [{"error":str(e)}]

def execute_read_query(query: str, params: dict[str, Any] = {}) -> list[dict[str, Any]]:
    """
    Execute a Neo4j Cypher query and return results as a list of dictionaries
    Args:
        query (str): The Cypher query to execute
        params (dict[str, Any], optional): The parameters to pass to the query or None.
    Raises:
        Exception: If there is an error executing the query
    Returns:
        list[dict[str, Any]]: A list of dictionaries representing the query results
    """
    if not db_instance:
        return [{"error": "Database not initialized"}]
    try:
        if params is None:
            params = {}
        # The adapter's method is execute_query, not _execute_query
        return db_instance.execute_query(query, params)
    except Exception as e:
        return [{"error":str(e)}]

def get_investors(company: str) -> list[dict[str, Any]]:
    """
    Returns the investor in the company with this name or id.
    Args:
        company (str): name of the company to find investors in
    Returns:
        list[dict[str, Any]]: A list of investor ids, names (and their types Organization or Person)
    """
    if not db_instance:
        return [{"error": "Database not initialized"}]
    try:
        query = """
        MATCH p=(o:Organization)<-[r:HAS_INVESTOR]-(i)
        WHERE o.name=$company OR o.id=$company
          AND NOT exists { (o)<-[:SUBSIDARY_OF]-() } 
        RETURN i.id as id, i.name as name, head(labels(i)) as type
        """
        return db_instance.execute_query(query, {"company":company})
    except Exception as e:
        return [{"error":str(e)}]
 
GRAPH_DATABASE_AGENT_LOCAL_TOOLS = [get_schema, execute_read_query]
INVESTOR_RESEARCH_AGENT_LOCAL_TOOLS = [get_schema, get_investors]