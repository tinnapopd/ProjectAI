from typing import List
from core.agent import strategy_agent, opponent_agent, batch_evaluator_agent
from core.minimax_engine import Agent, MinimaxController
from schemas import CompanyProfile


async def get_strategy_agent(user_id: str, session_id: str) -> Agent:
    agent = Agent(
        user_id=user_id,
        session_id=f"{session_id}_strategy",
        llm_agent=strategy_agent,
    )
    await agent.initialize()
    return agent


async def get_opponent_agent(user_id: str, session_id: str) -> Agent:
    agent = Agent(
        user_id=user_id,
        session_id=f"{session_id}_opponent",
        llm_agent=opponent_agent,
    )
    await agent.initialize()
    return agent


async def get_batch_evaluator_agent(user_id: str, session_id: str) -> Agent:
    """Get batch evaluator agent for evaluating all scenarios at once."""
    agent = Agent(
        user_id=user_id,
        session_id=f"{session_id}_batch_evaluator",
        llm_agent=batch_evaluator_agent,
    )
    await agent.initialize()
    return agent


async def get_minimax_controller(
    user_id: str,
    session_id: str,
    business_goal: str,
    player_profiles: List[CompanyProfile],
) -> MinimaxController:
    """Get Minimax controller for multi-turn game tree search."""
    # Initialize agents
    evaluator = await get_batch_evaluator_agent(user_id, session_id)
    opponent = await get_opponent_agent(user_id, session_id)

    return MinimaxController(
        evaluator=evaluator,
        opponent=opponent,
        business_goal=business_goal,
        player_profiles=player_profiles,
    )
