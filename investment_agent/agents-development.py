from google.adk.agents import Agent
import base64

import os
import random
import sys
from neo4j import GraphDatabase
from typing import Any
import re
from dotenv import load_dotenv
import asyncio

class neo4jDatabase:
    def __init__(self,  neo4j_uri: str, neo4j_username: str, neo4j_password: str):
        d = GraphDatabase.driver(neo4j_uri, auth=(neo4j_username, neo4j_password))
        d.verify_connectivity()
        self.driver = d

    def is_write_query(self, query: str) -> bool:
        return re.search(r"\b(MERGE|CREATE|SET|DELETE|REMOVE|ADD)\b", query, re.IGNORECASE) is not None

    def _execute_query(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        if self.is_write_query(query):
            raise "Write Queries are not supported in this agent"
        else:
            result = self.driver.execute_query(query, params)
            return [serialize_neo4j_value(dict(r)) for r in result.records]

# Load environment variables
load_dotenv()

db = neo4jDatabase(
    os.getenv("NEO4J_URI"),
    os.getenv("NEO4J_USERNAME"),
    os.getenv("NEO4J_PASSWORD")
)

# Nodes in the database
db._execute_query("MATCH () RETURN count(*) as nodes")

# {'nodes': 237358 }

def get_schema() -> list[dict[str,Any]]:
  """Get the schema of the database, returns node-types(labels) with their types and attributes and relationships between node-labels
  Args: None
  Returns:
    list[dict[str,Any]]: A list of dictionaries representing the schema of the database
  """
  try:
      results = db._execute_query(
              """
              call apoc.meta.data() yield label, property, type, other, unique, index, elementType
              where elementType = 'node' and not label starts with '_'
              with label,
              collect(case when type = 'RELATIONSHIP' then [property, head(other)] end) as relationships,
              collect(case when type <> 'RELATIONSHIP' then [property, type + case when unique 
                      then " unique" else "" end + case when index then " indexed" else "" end] end) 
              as attributes,

              RETURN label, apoc.map.fromPairs(attributes) as attributes, apoc.map.fromPairs(relationships) as relationships
              """
          )
      return results
  except Exception as e:
      return [{"error":str(e)}]

def execute_read_query(query: str, params: dict[str, Any] = {}) -> list[dict[str, Any]]:
    """
    Execute a Neo4j Cypher query and return results as a list of dictionaries
    Args:
        query (str): The Cypher query to execute
        params (dict[str, Any], optional): The parameters to pass to the query or None.
    Returns:
        list[dict[str, Any]]: A list of dictionaries representing the query results
    """
    try:
        if params is None:
            params = {}
        results = db._execute_query(query, params)
        return results
    except Exception as e:
        return [{"error":str(e)}]

# get_schema()
# execute_read_query("RETURN 1", None)

def get_investors(company: str) -> list[dict[str, Any]]:
    """
    Returns the investor in the company with this name or id.
    Args:
        company (str): name of the company to find investors in
    Returns:
        list[dict[str, Any]]: A list of investor ids, names (and their types Organization or Person)
    """
    try:
        results = db._execute_query("""
        MATCH p=(o:Organization)<-[r:HAS_INVESTOR]-(i)
        WHERE o.name=$company OR o.id=$company
          AND NOT exists { (o)<-[:SUBSIDARY_OF]-() } 
        RETURN i.id as id, i.name as name, head(labels(i)) as type
        """, {"company":company})
        return results
    except Exception as e:
        return [{"error":str(e)}]