from typing import Optional
from dotenv import load_dotenv
from core.adk.agent import MCP_TOOLBOX_URL
from src.core.ports.llm_provider_port import LlmProviderPort
from src.core.ports.mcp_client_port import MCPClientPort
from src.adapter.repository.llm_provider.AWSLlmProviderAdapter import AWSLlmProviderAdapter
from src.adapter.repository.graph_database.neo4j_adapter import Neo4jDatabaseAdapter
from src.adapter.repository.mcp_client.GoogleADKMCPAdapter import GoogleADKMCPAdapter
from functools import lru_cache
import os

load_dotenv()
db_instance = Neo4jDatabaseAdapter()

class DependencyContainer:
    def __init__(self):
        self._llm_adapter = Optional[LlmProviderPort] = None
        self._adk_mcp_client = Optional[MCPClientPort] = None
    
    @property
    def bedrock_llm(self) -> LlmProviderPort:
        if self._llm_adapter is None:
            self._llm_adapter = AWSLlmProviderAdapter()
        return self._llm_adapter
    
    @property
    def adk_mcp_client(self) -> MCPClientPort:
        if self._adk_mcp_client is None:
            mcp_url = os.getenv("MCP_TOOLBOX_URL")
            mcp_name = os.getenv("MCP_TOOLBOX_NAME", "MCP_TOOLBOX")
            self._adk_mcp_client = GoogleADKMCPAdapter(server_url=mcp_url, name=mcp_name)
        return self._adk_mcp_client
    

@lru_cache()
def get_dependencies_container() -> DependencyContainer:
    return DependencyContainer()

async def get_agent_investment_root(
        dependencies: DependencyContainer = get_dependencies_container()
):
    