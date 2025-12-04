from typing import List
from core.agent import strategy_agent, opponent_agent, evaluator_agent
from core.maxn_engine import Agent, MaxNController
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


async def get_evaluator_agent(user_id: str, session_id: str) -> Agent:
    agent = Agent(
        user_id=user_id,
        session_id=f"{session_id}_evaluator",
        llm_agent=evaluator_agent,
    )
    await agent.initialize()
    return agent


async def get_maxn_controller(
    user_id: str,
    session_id: str,
    business_goal: str,
    player_profiles: List[CompanyProfile],
) -> MaxNController:
    # Initialize agents
    evaluator = await get_evaluator_agent(user_id, session_id)
    opponent = await get_opponent_agent(user_id, session_id)

    return MaxNController(
        evaluator=evaluator,
        opponent=opponent,
        business_goal=business_goal,
        player_profiles=player_profiles,
    )
