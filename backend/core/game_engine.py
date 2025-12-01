"""
Game Engine for the Hybrid AI-Powered Strategic Wargame.

This module implements the Classical AI component - the MaxN game-tree search
algorithm for multi-player, general-sum strategic decision-making.
"""

# --------------------------------------------------------------------------- #
#                              Import Libraries                               #
# --------------------------------------------------------------------------- #
import json
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

from schemas import (
    GameState,
    StrategyMove,
    StrategicMoves,
    OpponentMoveSelection,
    EvaluationResult,
)
from core.config import settings
from core.agent import (
    create_strategy_agent,
    create_opponent_agent,
    create_evaluator_agent,
)
from google.genai import Client


# --------------------------------------------------------------------------- #
#                          Data Structures                                    #
# --------------------------------------------------------------------------- #


@dataclass
class SearchNode:
    """Represents a node in the MaxN game tree."""

    game_state: GameState
    depth: int
    player_id: str
    move: Optional[StrategyMove] = None
    score: float = 0.0
    best_path: List[StrategyMove] = field(default_factory=list)


# --------------------------------------------------------------------------- #
#                          Game Engine Class                                  #
# --------------------------------------------------------------------------- #


class GameEngine:
    """
    The Classical AI Controller - manages the MaxN game-tree search.

    This engine orchestrates the interaction between classical search
    algorithms and modern LLM agents to find optimal strategic moves.
    """

    def __init__(self, business_goal: str, num_players: int = 3):
        """
        Initialize the game engine.

        Args:
            business_goal: The user-defined business objective
            num_players: Number of players in the game (default: 3)
        """
        self.business_goal = business_goal
        self.num_players = num_players
        self.search_depth = settings.DEFAULT_SEARCH_DEPTH
        self.action_set_size = settings.DEFAULT_ACTION_SET_SIZE

        # Initialize agents with business goal
        self.strategy_agent = create_strategy_agent(business_goal)
        self.opponent_agent = create_opponent_agent(business_goal)
        self.evaluator_agent = create_evaluator_agent(business_goal)

        # Initialize Google GenAI client
        self.client = Client(api_key=settings.GOOGLE_API_KEY)

        # Cache for game states (optional optimization)
        self.state_cache: Dict[str, float] = {}

    async def generate_strategic_moves(
        self, game_state: GameState, context: str = ""
    ) -> List[StrategyMove]:
        """
        Strategic Refresh Loop - Generate creative moves using Strategy Agent.

        Args:
            game_state: Current state of the game
            context: Additional context about the business environment

        Returns:
            List of strategic moves
        """
        # Prepare the prompt for the strategy agent
        state_json = game_state.model_dump_json(indent=2)

        prompt = f"""
        {self.strategy_agent.instruction}
        
        Current Game State:
        {state_json}

        Additional Context:
        {context}

        Please generate {self.action_set_size} creative strategic moves.
        Return ONLY valid JSON in this exact format:
        {{
            "strategic_moves": [
                {{
                    "move_id": "MOVE_001",
                    "move_name": "Example Move",
                    "description": "Description of the move",
                    "stratgic_category": "Category"
                }}
            ]
        }}
        """

        try:
            # Use the agent's model configuration
            model_name = (
                self.strategy_agent.model
                if isinstance(self.strategy_agent.model, str)
                else "gemini-2.0-flash-exp"
            )
            print(
                f"Calling strategy agent ({model_name}) with business goal: {self.business_goal}"
            )

            response = self.client.models.generate_content(
                model=model_name, contents=prompt
            )

            response_text = response.text if response.text else ""
            print(
                f"Strategy agent response: {response_text[:500] if len(response_text) > 500 else response_text}"
            )

            # Parse the response
            moves_data = self._extract_json_from_response(response_text)
            print(f"Parsed moves data: {moves_data}")

            if moves_data and "strategic_moves" in moves_data:
                strategic_moves = StrategicMoves(**moves_data)
                print(
                    f"Successfully created {len(strategic_moves.strategic_moves)} moves"
                )

                # Evaluate each move to assign scores
                scored_moves = []
                for move in strategic_moves.strategic_moves:
                    score_result = await self._evaluate_single_move(
                        game_state, move
                    )
                    move.expected_score = score_result["score"]
                    move.score_explanation = score_result["explanation"]
                    scored_moves.append(move)
                    print(
                        f"Move {move.move_id}: Score = {move.expected_score}"
                    )

                return scored_moves
            else:
                # Fallback: return empty list
                print("Warning: Could not parse moves from response")
                return []

        except Exception as e:
            print(f"Error generating strategic moves: {e}")
            import traceback

            traceback.print_exc()
            return []

    async def select_opponent_move(
        self,
        game_state: GameState,
        available_moves: List[StrategyMove],
        player_id: str,
        player_move: Optional[StrategyMove] = None,
    ) -> StrategyMove:
        """
        Simulate opponent move selection using Opponent Agent.

        Args:
            game_state: Current game state
            available_moves: List of possible moves
            player_id: ID of the opponent player
            player_move: The move made by the main player (for context)

        Returns:
            Selected strategic move
        """
        state_json = game_state.model_dump_json(indent=2)
        moves_json = json.dumps(
            [move.model_dump() for move in available_moves], indent=2
        )

        player_move_desc = (
            f"Player's move: {player_move.model_dump_json(indent=2)}"
            if player_move
            else "This is the first move."
        )

        prompt = f"""
        You are playing as: {player_id}

        Current Game State:
        {state_json}

        {player_move_desc}

        Available Moves:
        {moves_json}

        Select the best move for your company and return it in the specified JSON format:
        {{
            "selected_move_id": "MOVE_XXX",
            "reasoning": "Your explanation"
        }}
        """

        try:
            model_name = (
                self.opponent_agent.model
                if isinstance(self.opponent_agent.model, str)
                else "gemini-1.5-flash"
            )
            response = self.client.models.generate_content(
                model=model_name, contents=prompt
            )
            response_text = response.text if response.text else ""

            # Extract JSON from response
            selection_data = self._extract_json_from_response(response_text)

            if selection_data and "selected_move_id" in selection_data:
                selection = OpponentMoveSelection(**selection_data)

                # Find the move with the selected ID
                for move in available_moves:
                    if move.move_id == selection.selected_move_id:
                        return move

            # Fallback: return first move
            return available_moves[0]

        except Exception as e:
            print(f"Error selecting opponent move: {e}")
            return available_moves[0]

    async def evaluate_state(
        self,
        game_state: GameState,
        moves_made: List[Tuple[str, StrategyMove]],
    ) -> EvaluationResult:
        """
        Evaluate a game state using the Evaluator Agent.

        Args:
            game_state: Current game state
            moves_made: List of (player_id, move) tuples for this turn

        Returns:
            Evaluation result with new state and score
        """
        state_json = game_state.model_dump_json(indent=2)
        moves_desc = "\n".join(
            [
                f"- {player_id}: {move.model_dump_json(indent=2)}"
                for player_id, move in moves_made
            ]
        )

        prompt = f"""
        Current Game State:
        {state_json}

        Moves Made This Turn:
        {moves_desc}

        Please:
        1. Simulate the state changes resulting from these moves
        2. Calculate a heuristic score based on the business goal: {self.business_goal}
        3. Return the evaluation in the specified JSON format:
        {{
            "new_game_state": {{ ... }},
            "heuristic_score": 0.0,
            "score_explanation": "..."
        }}
        """

        try:
            model_name = (
                self.evaluator_agent.model
                if isinstance(self.evaluator_agent.model, str)
                else "gemini-2.0-flash-exp"
            )
            response = self.client.models.generate_content(
                model=model_name, contents=prompt
            )
            response_text = response.text if response.text else ""

            # Extract JSON from response
            eval_data = self._extract_json_from_response(response_text)

            if eval_data:
                return EvaluationResult(**eval_data)
            else:
                # Fallback: return current state with neutral score
                return EvaluationResult(
                    new_game_state=game_state,
                    heuristic_score=0.0,
                    score_explanation="Error in evaluation",
                )

        except Exception as e:
            print(f"Error evaluating state: {e}")
            return EvaluationResult(
                new_game_state=game_state,
                heuristic_score=0.0,
                score_explanation=f"Error: {str(e)}",
            )

    async def find_optimal_strategy(
        self, initial_state: GameState, context: str = ""
    ) -> Tuple[List[StrategyMove], float]:
        """
        Main entry point - find the optimal strategic path.

        Args:
            initial_state: Initial game state
            context: Additional business context

        Returns:
            Tuple of (optimal_move_sequence, expected_score)
        """
        # Step 1: Strategic Refresh - Generate creative moves
        print("Generating strategic moves...")
        available_moves = await self.generate_strategic_moves(
            initial_state, context
        )

        if not available_moves:
            print("No moves generated!")
            return [], 0.0

        print(f"Generated {len(available_moves)} strategic moves")

        # Step 2: For now, return the first move with evaluation
        # TODO: Implement full MaxN search
        first_move = available_moves[0]
        eval_result = await self.evaluate_state(
            initial_state, [("OurCompany", first_move)]
        )

        return [first_move], eval_result.heuristic_score

    async def _evaluate_single_move(
        self, game_state: GameState, move: StrategyMove
    ) -> Dict[str, any]:
        """
        Evaluate a single strategic move to determine its expected score.

        Args:
            game_state: Current game state
            move: Strategic move to evaluate

        Returns:
            Dictionary with 'score' and 'explanation'
        """
        state_json = game_state.model_dump_json(indent=2)
        move_json = move.model_dump_json(indent=2)

        prompt = f"""
        Evaluate this strategic move based on the business goal: {self.business_goal}

        Current Game State:
        {state_json}

        Proposed Move:
        {move_json}

        Analyze how well this move would help achieve the business goal: "{self.business_goal}"

        Return your evaluation in this exact JSON format:
        {{
            "heuristic_score": 75.5,
            "score_explanation": "Brief explanation of why this score"
        }}

        Score Guidelines:
        - 90-100: Excellent move, directly achieves the goal
        - 75-89: Very good move, significant progress toward goal
        - 60-74: Good move, moderate progress toward goal
        - 40-59: Fair move, some progress toward goal
        - 20-39: Poor move, minimal progress toward goal
        - 0-19: Bad move, little to no progress toward goal
        """

        try:
            model_name = (
                self.evaluator_agent.model
                if isinstance(self.evaluator_agent.model, str)
                else "gemini-2.0-flash-exp"
            )
            response = self.client.models.generate_content(
                model=model_name, contents=prompt
            )
            response_text = response.text if response.text else ""

            # Extract JSON from response
            eval_data = self._extract_json_from_response(response_text)

            if eval_data and "heuristic_score" in eval_data:
                return {
                    "score": float(eval_data["heuristic_score"]),
                    "explanation": eval_data.get(
                        "score_explanation", "No explanation provided"
                    ),
                }
            else:
                # Fallback: neutral score
                return {
                    "score": 50.0,
                    "explanation": "Could not evaluate move",
                }

        except Exception as e:
            print(f"Error evaluating move {move.move_id}: {e}")
            return {
                "score": 50.0,
                "explanation": f"Error in evaluation: {str(e)}",
            }

    def _extract_response_text(self, response) -> str:
        """
        Extract text from ADK response.

        Args:
            response: Response from agent run

        Returns:
            Extracted text
        """
        # Response is typically an Event or similar object
        # Try to get text content from it
        if hasattr(response, "text"):
            return str(response.text)
        elif hasattr(response, "content"):
            return str(response.content)
        else:
            return str(response)

    def _extract_json_from_response(self, response: str) -> Optional[Dict]:
        """
        Extract JSON from LLM response text.

        Args:
            response: Raw response text from LLM

        Returns:
            Parsed JSON dict or None
        """
        try:
            # Try direct JSON parse
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON in markdown code blocks
            json_match = re.search(
                r"```json\s*\n(.*?)\n```", response, re.DOTALL
            )
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass

            # Try to find JSON object in text
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass

            return None

    async def close(self):
        """Clean up resources."""
        # Agents handle their own cleanup
        pass
