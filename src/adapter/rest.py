from fastapi import APIRouter, Depends
from src.config.dependencies import get_agent_investment_root
import traceback

router = APIRouter(prefix="/api/v1/investments",
                   tags=["investments"])

@router.post(
        path="/query",
        description="Endpoint to query the investment research agent with a natural language question about investors, companies, industries or news.")
async def query_investment_agent(
    question: str,
    agent=Depends(get_agent_investment_root)
    ):
    try:
        response = await agent.run(question)
        return {"response": response}
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}