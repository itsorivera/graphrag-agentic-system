from typing import Optional
from dotenv import load_dotenv
import traceback
from core.agent_metadata import (
    GRAPH_DATABASE_AGENT_DESC,
    INVESTOR_RESEARCH_AGENT_DESC,
    INVESTMENT_RESEARCH_AGENT_DESC)
from core.prompts import (
    ROOT_AGENT_PROMPT,
    GRAPH_DATABASE_AGENT_PROMPT,
    INVESTOR_RESEARCH_AGENT_PROMPT,
    INVESTMENT_RESEARCH_AGENT_PROMPT
)
from config.app_config import AppConfig
from core.ports.llm_provider_port import LLMProviderPort
from core.ports.mcp_client_port import MCPClientPort
from core.ports.agent_port import AgentPort
from adapter.repository.llm_provider.LiteLLMProviderAdapter import LiteLLMProviderAdapter
from adapter.repository.mcp_client.GoogleADKMCPAdapter import GoogleADKMCPAdapter
from adapter.repository.agent.agent_adk_adapter import ADKAgentAdapter, ADKSubAgentConfig
from core.tools import GRAPH_DATABASE_AGENT_TOOLS, INVESTOR_RESEARCH_AGENT_TOOLS, get_schema
from functools import lru_cache
import os

load_dotenv()

class DependencyContainer:
    def __init__(self):
        self._llm_adapter: Optional[LLMProviderPort] = None
        self._adk_mcp_client: Optional[MCPClientPort] = None
    
    @property
    def investment_agent_llm(self) -> LLMProviderPort:
        if self._llm_adapter is None:
            self._llm_adapter = LiteLLMProviderAdapter()
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
) -> AgentPort:
    
    try:
        mcp_tools = await dependencies.adk_mcp_client.get_tools()
    except Exception as e:
        traceback.print_exc()
        print(f"Error loading tools from MCP: {str(e)}")
    
    all_research_tools = mcp_tools + [get_schema]
    
    GROQ_MODEL = "groq/llama-3.3-70b-versatile"

    sub_agents_config = [
        ADKSubAgentConfig(
            name="graph_database_agent",
            model=GROQ_MODEL,
            description=GRAPH_DATABASE_AGENT_DESC,
            instruction=GRAPH_DATABASE_AGENT_PROMPT,
            tools=GRAPH_DATABASE_AGENT_TOOLS,
        ),
        ADKSubAgentConfig(
            name="investor_research_agent",
            model=GROQ_MODEL,
            description=INVESTOR_RESEARCH_AGENT_DESC,
            instruction=INVESTOR_RESEARCH_AGENT_PROMPT,
            tools=INVESTOR_RESEARCH_AGENT_TOOLS
        ),
        ADKSubAgentConfig(
            name="investment_research_agent",
            model=GROQ_MODEL,
            description=INVESTMENT_RESEARCH_AGENT_DESC,
            instruction=INVESTMENT_RESEARCH_AGENT_PROMPT,
            tools=all_research_tools,
        )
    ]
    
    agent_adapter = ADKAgentAdapter(
        agent_name="investment_root_agent",
        llm_port=dependencies.investment_agent_llm,
        model=GROQ_MODEL,
        instruction=ROOT_AGENT_PROMPT,
        sub_agent_configs=sub_agents_config,
    )
    
    await agent_adapter.create_agent()
    
    return agent_adapter