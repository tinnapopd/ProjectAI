"""
Agent factory functions for the Hybrid AI-Powered Strategic Wargame.

This module provides factory functions to create specialized agents that work
together in a symbiotic architecture combining Classical AI (MaxN search) with
Modern AI (LLMs):

1. Strategy Agent - Creative move generation (Strategic Refresh Loop)
2. Opponent Agent - Competitor simulation (MaxN Player Logic)
3. Evaluator Agent - State evaluation and scoring (Dynamic Heuristic Function)

All agents are parameterized with the user-defined business goal to ensure
the entire system optimizes toward the same objective.
"""

# --------------------------------------------------------------------------- #
#                              Import Libraries                               #
# --------------------------------------------------------------------------- #
from google.adk.agents.llm_agent import Agent
from core.prompt import (
    return_strategy_agent_instruction,
    return_opponent_agent_instruction,
    return_evaluator_agent_instruction,
)

# --------------------------------------------------------------------------- #
#                          Agent Factory Functions                            #
# --------------------------------------------------------------------------- #


def create_strategy_agent(
    business_goal: str = "maximize market share",
) -> Agent:
    """
    Create the Strategy Agent with user-defined business goal.

    Args:
        business_goal: The specific business objective to optimize for

    Returns:
        Agent configured for creative strategic move generation
    """
    return Agent(
        name="strategy_agent",
        model="gemini-2.0-flash-exp",
        description=f"Creative strategic consultant generating moves to {business_goal}.",
        instruction=return_strategy_agent_instruction(business_goal),
    )


def create_opponent_agent(
    business_goal: str = "maximize market share",
) -> Agent:
    """
    Create the Opponent Agent with awareness of player's business goal.

    Args:
        business_goal: The player's business objective (for context)

    Returns:
        Agent configured to simulate rational competitor behavior
    """
    return Agent(
        name="opponent_agent",
        model="gemini-1.5-flash",
        description="Rational competitor simulator maximizing own utility.",
        instruction=return_opponent_agent_instruction(business_goal),
    )


def create_evaluator_agent(
    business_goal: str = "maximize market share",
) -> Agent:
    """
    Create the Evaluator Agent to score states against business goal.

    Args:
        business_goal: The specific business objective to evaluate against

    Returns:
        Agent configured as physics engine and scorekeeper
    """
    return Agent(
        name="evaluator_agent",
        model="gemini-2.0-flash-exp",
        description=f"Physics engine scoring outcomes based on: {business_goal}.",
        instruction=return_evaluator_agent_instruction(business_goal),
    )


# --------------------------------------------------------------------------- #
#                      Default Agents (for backward compatibility)            #
# --------------------------------------------------------------------------- #

# Default agents using "maximize market share" as the goal
# For production use, call the factory functions with user's actual goal
strategy_agent = create_strategy_agent()
opponent_agent = create_opponent_agent()
evaluator_agent = create_evaluator_agent()
