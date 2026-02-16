from dotenv import load_dotenv
from src.adapter.repository.neo4j_adapter import Neo4jDatabaseAdapter

load_dotenv()
db_instance = Neo4jDatabaseAdapter()

