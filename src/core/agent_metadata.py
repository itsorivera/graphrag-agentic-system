# Agent Descriptions
GRAPH_DATABASE_AGENT_DESC = """
The graph_database_agent is able to fetch the schema of a neo4j graph database and execute read queries.
It will generate Cypher queries using the schema to fulfill the information requests and repeatedly
try to re-create and fix queries that error or don't return the expected results.
When passing requests to this agent, make sure to have clear specific instructions what data should be retrieved, how,
if aggregation is required or path expansion.
Don't use this generic query agent if other, more specific agents are available that can provide the requested information.
This is meant to be a fallback for structural questions (e.g. number of entities, or aggregation of values or very specific sorting/filtering)
Or when no other agent provides access to the data (inputs, results and shape) that is needed.
"""

INVESTOR_RESEARCH_AGENT_DESC = """
This investment research agent has the sole purpose of finding investors in
an company or organization which id identified by a single EXACT name or id,
which should have been retrieved before from the database.
"""

INVESTMENT_RESEARCH_AGENT_DESC = """
This investment research agent has access to a number of tools on a companies and news database.
It can find industries, companies in industries, articles in a certain month, article details,
organizations mentioned in articles and people working there.
"""