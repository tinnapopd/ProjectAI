from google.adk.agents import LlmAgent

from .prompt import (
    STRATEGY_AGENT_PROMPT,
    OPPONENT_AGENT_PROMPT,
    EVALUATOR_AGENT_PROMPT,
)
from schemas import (
    StrategyAgentMoves,
    OpponentAgentMoves,
    EvaluatorAgentFeedback,
)


def create_strategy_agent() -> LlmAgent:
    return LlmAgent(
        name="strategy_agent",
        model="gemini-2.0-flash-exp",
        instruction=STRATEGY_AGENT_PROMPT,
        output_schema=StrategyAgentMoves,
        include_contents="none",
    )


def create_opponent_agent() -> LlmAgent:
    return LlmAgent(
        name="opponent_agent",
        model="gemini-2.0-flash-exp",
        instruction=OPPONENT_AGENT_PROMPT,
        output_schema=OpponentAgentMoves,
        include_contents="none",
    )


def create_evaluator_agent() -> LlmAgent:
    return LlmAgent(
        name="evaluator_agent",
        model="gemini-2.0-flash-exp",
        instruction=EVALUATOR_AGENT_PROMPT,
        output_schema=EvaluatorAgentFeedback,
        include_contents="none",
    )


# Instantiate agents: singletons
strategy_agent = create_strategy_agent()
opponent_agent = create_opponent_agent()
evaluator_agent = create_evaluator_agent()
