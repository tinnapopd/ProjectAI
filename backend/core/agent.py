from google.adk.agents import LlmAgent

from .prompt import (
    STRATEGY_AGENT_PROMPT,
    OPPONENT_AGENT_PROMPT,
    BATCH_EVALUATOR_PROMPT,
)
from schemas import (
    StrategyAgentMoves,
    OpponentAgentMoves,
    BatchEvaluationResult,
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


def create_batch_evaluator_agent() -> LlmAgent:
    return LlmAgent(
        name="batch_evaluator_agent",
        model="gemini-2.0-flash-exp",
        instruction=BATCH_EVALUATOR_PROMPT,
        output_schema=BatchEvaluationResult,
        include_contents="none",
    )


# Instantiate agents: singletons
strategy_agent = create_strategy_agent()
opponent_agent = create_opponent_agent()
batch_evaluator_agent = create_batch_evaluator_agent()
