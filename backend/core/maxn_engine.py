import json
import itertools
from typing import List, Dict, Tuple, Optional, Any

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from core.config import settings
from schemas import GameState, CompanyProfile, TreeNode

# Shared session service instance to maintain sessions across all agents
_shared_session_service = InMemorySessionService()


class Agent:
    def __init__(
        self,
        user_id: str,
        session_id: str,
        llm_agent: LlmAgent,
        session_service: Optional[InMemorySessionService] = None,
    ) -> None:
        self.user_id = user_id
        self.session_id = session_id
        self.llm_agent = llm_agent

        self.session_service = session_service or _shared_session_service
        self.session = None
        self.runner = Runner(
            agent=self.llm_agent,
            app_name=self.llm_agent.name,
            session_service=self.session_service,
        )

    async def initialize(self) -> "Agent":
        self.session = await self.session_service.create_session(
            app_name=self.llm_agent.name,
            user_id=self.user_id,
            session_id=self.session_id,
        )
        return self

    def _deserialize_response(self, response: str) -> Optional[Any]:
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return None

    @property
    def instruction(self) -> Any:
        return self.llm_agent.instruction

    def call_agent(self, prompt: str) -> Optional[Any]:
        content = types.Content(role="user", parts=[types.Part(text=prompt)])
        events = self.runner.run(
            user_id=self.user_id,
            session_id=self.session_id,
            new_message=content,
        )
        for event in events:
            if (
                event.is_final_response()
                and event.content
                and event.content.parts
            ):
                final_answer = event.content.parts[0].text
                if final_answer is not None:
                    return self._deserialize_response(final_answer.strip())
        return None


class MaxNController:
    """
    Optimized Max-N game tree controller.

    Uses batch evaluation: ONE LLM call evaluates ALL scenarios at once.

    LLM Calls:
    - 1 call per opponent to generate their moves
    - 1 call to batch-evaluate all leaf scenarios

    For 3 players with 2 moves each: 2 + 1 = 3 LLM calls total (instead of 8+)
    """

    def __init__(
        self,
        evaluator: Agent,
        opponent: Agent,
        business_goal: str,
        player_profiles: List[CompanyProfile],
    ) -> None:
        self.evaluator = evaluator
        self.opponent = opponent
        self.business_goal = business_goal
        self.player_profiles = player_profiles
        self.tree_nodes: Dict[str, TreeNode] = {}
        self.node_counter = 0

    def _generate_opponent_moves(
        self,
        state: GameState,
        player_index: int,
        num_moves: int,
    ) -> List[str]:
        """Generate moves for an opponent using LLM (1 call per opponent)."""
        player = self.player_profiles[player_index]

        prompt = f"""
        Given the current GameState (JSON):
        {state.model_dump_json(indent=2)}

        Business Goal (of main player - use this to understand the competitive context):
        {self.business_goal}

        Your Company Profile:
        {player.model_dump_json(indent=2)}
        
        Generate exactly {num_moves} distinct strategic moves this company might take.
        Consider both aggressive and defensive options.
        """

        response = self.opponent.call_agent(prompt=prompt)

        if response and isinstance(response, dict):
            if "selected_move" in response:
                base_move = response["selected_move"]
                # Create variations
                moves = [base_move]
                if num_moves > 1:
                    moves.append(f"Aggressive variant: {base_move}")
                if num_moves > 2:
                    moves.append(f"Defensive variant: Focus on core business")
            elif "moves" in response:
                moves = response["moves"][:num_moves]
            else:
                moves = [f"Strategy {i + 1}" for i in range(num_moves)]
        else:
            moves = [f"Strategy {i + 1}" for i in range(num_moves)]

        # Ensure exactly num_moves
        while len(moves) < num_moves:
            moves.append(f"Alternative {len(moves) + 1}")

        return moves[:num_moves]

    def _generate_all_scenarios(
        self,
        player0_moves: List[str],
        all_opponent_moves: List[List[str]],
    ) -> List[Tuple[str, List[str]]]:
        """Generate all possible move combinations (scenarios)."""
        scenarios = []

        # Create cartesian product of all player moves
        all_moves = [player0_moves] + all_opponent_moves

        for idx, combo in enumerate(itertools.product(*all_moves)):
            scenario_id = f"s{idx}"
            scenarios.append((scenario_id, list(combo)))

        return scenarios

    def _batch_evaluate_scenarios(
        self,
        state: GameState,
        scenarios: List[Tuple[str, List[str]]],
    ) -> Dict[str, float]:
        """Evaluate ALL scenarios in ONE LLM call."""

        # Build scenarios description
        scenarios_text = []
        for scenario_id, moves in scenarios:
            moves_desc = ", ".join(
                [
                    f"{self.player_profiles[i].name}: {move}"
                    for i, move in enumerate(moves)
                ]
            )
            scenarios_text.append(f"  {scenario_id}: [{moves_desc}]")

        prompt = f"""
Current GameState:
{state.model_dump_json(indent=2)}

Business Goal (for Player 0 - {self.player_profiles[0].name}):
{self.business_goal}

Player Profiles:
{json.dumps([p.model_dump() for p in self.player_profiles], indent=2)}

Scenarios to evaluate (each shows all players' moves):
{chr(10).join(scenarios_text)}

Evaluate each scenario: How well does this combination of moves achieve Player 0's business goal?
Return a score (0.0 to 1.0) for EACH scenario.
"""

        response = self.evaluator.call_agent(prompt=prompt)

        # Parse response
        scores: Dict[str, float] = {}

        if response and isinstance(response, dict):
            if "scores" in response:
                for item in response["scores"]:
                    if isinstance(item, dict):
                        sid = item.get("scenario_id", "")
                        score = item.get("score", 0.5)
                        scores[sid] = float(score) if score else 0.5

        # Fill in any missing scores with default
        for scenario_id, _ in scenarios:
            if scenario_id not in scores:
                scores[scenario_id] = 0.5

        return scores

    def _build_tree_with_scores(
        self,
        root_id: str,
        player0_moves: List[str],
        all_opponent_moves: List[List[str]],
        scenario_scores: Dict[str, float],
    ) -> str:
        """Build the tree structure and propagate scores using Max-N."""

        # Map from move sequence to scenario score
        all_moves = [player0_moves] + all_opponent_moves
        scenario_map: Dict[Tuple[str, ...], float] = {}

        for idx, combo in enumerate(itertools.product(*all_moves)):
            scenario_id = f"s{idx}"
            scenario_map[combo] = scenario_scores.get(scenario_id, 0.5)

        # Build tree recursively
        def build_subtree(
            player_index: int,
            parent_id: str,
            move_prefix: Tuple[str, ...],
        ) -> float:
            """Build subtree and return propagated score."""

            if player_index >= len(self.player_profiles):
                # Leaf node - get score from scenario_map
                score = scenario_map.get(move_prefix, 0.5)

                leaf_id = f"node_{self.node_counter}"
                self.node_counter += 1

                leaf_node = TreeNode(
                    id=leaf_id,
                    label=f"Score: {score:.2f}",
                    player_index=None,
                    parent_id=parent_id,
                    score=score,
                )
                self.tree_nodes[leaf_id] = leaf_node
                self.tree_nodes[parent_id].children.append(leaf_id)

                return score

            # Get moves for this player
            moves = all_moves[player_index]

            best_score = -float("inf") if player_index == 0 else float("inf")

            for move in moves:
                node_id = f"node_{self.node_counter}"
                self.node_counter += 1

                node = TreeNode(
                    id=node_id,
                    label=move,
                    player_index=player_index,
                    parent_id=parent_id,
                )
                self.tree_nodes[node_id] = node
                self.tree_nodes[parent_id].children.append(node_id)

                # Recurse
                new_prefix = move_prefix + (move,)
                child_score = build_subtree(
                    player_index + 1, node_id, new_prefix
                )

                node.score = child_score

                # Max for player 0, Min for opponents (they hurt us)
                if player_index == 0:
                    best_score = max(best_score, child_score)
                else:
                    best_score = min(best_score, child_score)

            return best_score

        # Build from root
        root_score = build_subtree(0, root_id, ())
        self.tree_nodes[root_id].score = root_score

        # Find best move
        best_move = player0_moves[0] if player0_moves else "No move"
        best_child_score = -float("inf")

        for child_id in self.tree_nodes[root_id].children:
            child = self.tree_nodes[child_id]
            if child.score is not None and child.score > best_child_score:
                best_child_score = child.score
                best_move = child.label

        return best_move

    def run_a_period_search(
        self,
        start_state: GameState,
        action_set: List[str],
        time_period_unit: str,
        moves_per_opponent: Optional[int] = None,
    ) -> Tuple[float, str, Dict[str, Any]]:
        """
        Run Max-N search for one time period.

        Optimized: Only 3 LLM calls total for 3 players:
        - 2 calls to generate opponent moves
        - 1 call to batch-evaluate all scenarios
        """
        if moves_per_opponent is None:
            moves_per_opponent = settings.MOVES_PER_PLAYER

        # Reset
        self.tree_nodes = {}
        self.node_counter = 0

        # Create root
        root_id = f"node_{self.node_counter}"
        self.node_counter += 1
        root_node = TreeNode(
            id=root_id,
            label=time_period_unit,
            score=None,
            player_index=None,
            parent_id=None,
            children=[],
        )
        self.tree_nodes[root_id] = root_node

        # Step 1: Generate opponent moves (1 LLM call per opponent)
        all_opponent_moves: List[List[str]] = []
        for i in range(1, len(self.player_profiles)):
            moves = self._generate_opponent_moves(
                state=start_state,
                player_index=i,
                num_moves=moves_per_opponent,
            )
            all_opponent_moves.append(moves)

        # Step 2: Generate all scenarios
        scenarios = self._generate_all_scenarios(
            action_set, all_opponent_moves
        )

        # Step 3: Batch evaluate ALL scenarios (1 LLM call)
        scenario_scores = self._batch_evaluate_scenarios(
            start_state, scenarios
        )

        # Step 4: Build tree with scores
        best_move = self._build_tree_with_scores(
            root_id,
            action_set,
            all_opponent_moves,
            scenario_scores,
        )

        # Get root score
        root_score = self.tree_nodes[root_id].score or 0.5

        return root_score, best_move, self.get_tree_structure()

    def get_tree_structure(self) -> Dict[str, Any]:
        return {
            node_id: node.model_dump()
            for node_id, node in self.tree_nodes.items()
        }
