from google.adk.agents import LlmAgent

from .prompt import STRATEGY_PROMPT, OPPONENT_PROMPT, EVALUATOR_PROMPT
from schemas import EvaluationOutput, StrategicMoves


def create_strategy_agent() -> LlmAgent:
    return LlmAgent(
        name="strategy_agent",
        model="gemini-2.0-flash-exp",
        description=(
            "Creative strategic consultant generating "
            "moves to maximize market share."
        ),
        instruction=STRATEGY_PROMPT,
        output_schema=StrategicMoves,
    )


def create_opponent_agent() -> LlmAgent:
    return LlmAgent(
        name="opponent_agent",
        model="gemini-2.0-flash-exp",
        description="Rational competitor simulator maximizing own utility.",
        instruction=OPPONENT_PROMPT,
        output_schema=StrategicMoves,
    )


def create_evaluator_agent() -> LlmAgent:
    return LlmAgent(
        name="evaluator_agent",
        model="gemini-2.0-flash-exp",
        description="Physics engine scoring outcomes based on business goals.",
        instruction=EVALUATOR_PROMPT,
        output_schema=EvaluationOutput,
    )


# Instantiate agents: singletons
strategy_agent = create_strategy_agent()
opponent_agent = create_opponent_agent()
evaluator_agent = create_evaluator_agent()
