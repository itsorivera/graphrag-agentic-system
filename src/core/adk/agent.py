from google.adk.agents import Agent
import os
import asyncio
from dotenv import load_dotenv
from typing import Any
from src.config.database import db_instance as db
from src.core.tools import get_schema, execute_read_query, get_investors
from src.core.prompts import GRAPH_DATABASE_AGENT_PROMPT, INVESTMENT_RESEARCH_AGENT_PROMPT, INVESTOR_RESEARCH_AGENT_PROMPT, ROOT_AGENT_PROMPT

load_dotenv()

# Nodes in the database
if db:
    # {'nodes': 237358 }
    try:
        db.execute_query("MATCH () RETURN count(*) as nodes")
    except Exception as e:
        print(f"Warning: Could not connect to DB for initial check: {e}")

MODEL = os.getenv("GOOGLE_ADK_MODEL")

# Agent Mesh
graph_database_agent = Agent(
    model=MODEL,
    name='graph_database_agent',
    description="""
    The graph_database_agent is able to fetch the schema of a neo4j graph database and execute read queries.
    It will generate Cypher queries using the schema to fulfill the information requests and repeatedly
    try to re-create and fix queries that error or don't return the expected results.
    When passing requests to this agent, make sure to have clear specific instructions what data should be retrieved, how,
    if aggregation is required or path expansion.
    Don't use this generic query agent if other, more specific agents are available that can provide the requested information.
    This is meant to be a fallback for structural questions (e.g. number of entities, or aggregation of values or very specific sorting/filtering)
    Or when no other agent provides access to the data (inputs, results and shape) that is needed.
    """,
    instruction=GRAPH_DATABASE_AGENT_PROMPT,
    tools=[
        get_schema, execute_read_query
    ]
)

investor_research_agent = Agent(
    model=MODEL,
    name='investor_research_agent',
    description="""
    This investment research agent has the sole purpose of finding investors in
    an company or organization which id identified by a single EXACT name or id,
    which should have been retrieved before from the database.
    """,
    instruction=INVESTOR_RESEARCH_AGENT_PROMPT,
    tools=[
        get_schema, get_investors
    ]
)

from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams

# Get MCP Toolbox URL from environment
MCP_TOOLBOX_URL = os.getenv("MCP_TOOLBOX_URL")

async def load_tools(mcp_url):
    async with MCPToolset(connection_params=SseConnectionParams(url=mcp_url)) as toolset:
      tools = await toolset.load_tools()
      tools.extend([get_schema])
      return tools

# Initialize tools - load from MCP if URL is provided
if MCP_TOOLBOX_URL:
    try:
        tools = asyncio.run(load_tools(MCP_TOOLBOX_URL))    
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            # Already in an event loop, fall back to basic tools
            tools = [get_schema]
        else:
            raise
else:
    tools = [get_schema]

investment_research_agent = Agent(
    model=MODEL,
    name='investment_research_agent',
    description="""
    This investment research agent has access to a number of tools on a companies and news database.
    It can find industries, companies in industries, articles in a certain month, article details,
    organizations mentioned in articles and people working there.
    """,
    instruction=INVESTMENT_RESEARCH_AGENT_PROMPT,
    tools=tools
)

root_agent = Agent(
    model=MODEL,
    name='investment_agent',
    global_instruction = "",
    instruction=ROOT_AGENT_PROMPT,

    sub_agents=[investor_research_agent, investment_research_agent, graph_database_agent]
)