import json
import itertools
import time
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


class MinimaxController:
    """
    Minimax game tree controller with multi-turn support.

    Implements classic Minimax algorithm:
    - Player 0 (You): Maximizer - tries to maximize score
    - Opponents: Minimizer - combined as adversary trying to minimize your score

    Supports multiple time periods (turns) where each turn consists of:
    - Your move (MAX)
    - Opponent responses (MIN)

    The tree shows the full game progression across all time periods.
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
        current_period: int,
        move_history: List[Dict[str, str]],
    ) -> List[str]:
        """Generate moves for an opponent using LLM."""
        player = self.player_profiles[player_index]

        history_text = ""
        if move_history:
            history_text = f"""
        Move History (previous turns):
        {json.dumps(move_history, indent=2)}
        """

        prompt = f"""
        Current GameState (JSON):
        {state.model_dump_json(indent=2)}

        Business Goal (of main player - use this to understand the competitive context):
        {self.business_goal}

        Your Company Profile:
        {player.model_dump_json(indent=2)}
        
        Current Time Period: {current_period}
        {history_text}
        
        Number of Moves to Generate: {num_moves}
        
        Generate exactly {num_moves} DIFFERENT strategic moves for {player.name}.
        Each move must represent a distinct strategic direction that responds to the current game state.
        Consider the move history when deciding on responses.
        """

        response = self.opponent.call_agent(prompt=prompt)

        moves: List[str] = []
        if response and isinstance(response, dict):
            if "moves" in response and isinstance(response["moves"], list):
                moves = [str(m) for m in response["moves"][:num_moves]]

        # Fallback if LLM didn't return enough moves
        while len(moves) < num_moves:
            moves.append(f"{player.name} Strategy {len(moves) + 1}")

        return moves[:num_moves]

    def _batch_evaluate_scenarios(
        self,
        state: GameState,
        scenarios: List[Tuple[str, List[Dict[str, Any]]]],
        total_periods: int,
    ) -> Dict[str, float]:
        """Evaluate scenarios in batched LLM calls to handle large scenario counts."""

        BATCH_SIZE = (
            100  # Balance between speed per batch and number of batches
        )
        all_scores: Dict[str, float] = {}

        # Split into chunks
        num_batches = (len(scenarios) + BATCH_SIZE - 1) // BATCH_SIZE
        print(
            f"[Minimax] Evaluating {len(scenarios)} scenarios in {num_batches} batches"
        )

        for i in range(0, len(scenarios), BATCH_SIZE):
            chunk = scenarios[i : i + BATCH_SIZE]
            start = time.time()
            chunk_scores = self._evaluate_scenario_chunk(
                state, chunk, total_periods
            )
            all_scores.update(chunk_scores)

            print(
                f"[Minimax] Batch {i // BATCH_SIZE + 1}/{num_batches} ({time.time() - start:.1f}s)"
            )

        return all_scores

    def _evaluate_scenario_chunk(
        self,
        state: GameState,
        scenarios: List[Tuple[str, List[Dict[str, Any]]]],
        total_periods: int,
    ) -> Dict[str, float]:
        """Evaluate a chunk of scenarios in ONE LLM call with simplified prompt."""

        # Compact scenario format to reduce tokens
        scenarios_text = []
        for scenario_id, move_sequence in scenarios:
            moves_desc = "→".join(
                [
                    f"{m['move'][:30]}" for m in move_sequence
                ]  # Truncate long moves
            )
            scenarios_text.append(f"{scenario_id}:[{moves_desc}]")

        # Simplified prompt for faster evaluation
        prompt = f"""Goal: {self.business_goal}
Player: {self.player_profiles[0].name}
Periods: {total_periods}

Rate each scenario (0.0-1.0) for achieving the goal:
{chr(10).join(scenarios_text)}

Return scores for all scenarios."""

        response = self.evaluator.call_agent(prompt=prompt)

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

    def _build_multi_turn_tree(
        self,
        root_id: str,
        player0_moves: List[str],
        opponent_moves_by_period: List[
            List[List[str]]
        ],  # [period][opponent_idx][moves]
        scenario_scores: Dict[str, float],
        time_periods: int,
        time_period_labels: List[str],
    ) -> str:
        """
        Build a multi-turn Minimax tree.

        Structure for each time period:
        - Time Period Node (root for that period)
          - Your Move (MAX node)
            - Opponent Response (MIN node)
              - Next Time Period...
        """

        num_opponents = len(self.player_profiles) - 1
        print(f"[Minimax] Building tree with {num_opponents} opponents, {len(player0_moves)} user moves")
        print(f"[Minimax] Player profiles: {[p.name for p in self.player_profiles]}")

        # Generate all possible game paths
        def generate_paths(
            period: int,
            prefix: List[Tuple[int, int, str]],  # (period, player_idx, move)
        ) -> List[List[Tuple[int, int, str]]]:
            """Generate all possible paths through the game tree."""
            if period >= time_periods:
                return [prefix]

            paths = []
            # Your moves for this period
            for p0_move in player0_moves:
                # All opponent combinations for this period
                opponent_move_options = [
                    opponent_moves_by_period[period][opp_idx]
                    for opp_idx in range(num_opponents)
                ]

                for opp_combo in itertools.product(*opponent_move_options):
                    new_prefix = prefix + [(period, 0, p0_move)]
                    for opp_idx, opp_move in enumerate(opp_combo):
                        new_prefix = new_prefix + [
                            (period, opp_idx + 1, opp_move)
                        ]
                    paths.extend(generate_paths(period + 1, new_prefix))

            return paths

        all_paths = generate_paths(0, [])

        # Map paths to scenario scores
        path_scores: Dict[Tuple, float] = {}
        for idx, path in enumerate(all_paths):
            scenario_id = f"s{idx}"
            path_key = tuple(path)
            path_scores[path_key] = scenario_scores.get(scenario_id, 0.5)

        # Build tree with Minimax propagation
        def build_subtree(
            period: int,
            is_max_turn: bool,  # True for your turn, False for opponent
            parent_id: str,
            path_prefix: List[Tuple[int, int, str]],
            opponent_idx: int,  # Which opponent is playing (for MIN turns)
        ) -> float:
            """Build subtree and return minimax score."""

            # Terminal: all periods done
            if period >= time_periods:
                path_key = tuple(path_prefix)
                score = path_scores.get(path_key, 0.5)

                leaf_id = f"node_{self.node_counter}"
                self.node_counter += 1

                leaf_node = TreeNode(
                    id=leaf_id,
                    label=f"Final: {score:.2f}",
                    player_index=None,
                    parent_id=parent_id,
                    score=score,
                    time_period=period - 1,
                    is_leaf=True,
                )
                self.tree_nodes[leaf_id] = leaf_node
                self.tree_nodes[parent_id].children.append(leaf_id)

                return score

            if is_max_turn:
                # MAX turn: Your moves (parent selects MAX among these children)
                best_score = -float("inf")

                for move in player0_moves:
                    node_id = f"node_{self.node_counter}"
                    self.node_counter += 1

                    # This node's children will be MIN nodes (opponent chooses)
                    node = TreeNode(
                        id=node_id,
                        label=move,
                        player_index=0,
                        parent_id=parent_id,
                        time_period=period,
                        is_max_node=False,  # This node's children are chosen by MIN
                    )
                    self.tree_nodes[node_id] = node
                    self.tree_nodes[parent_id].children.append(node_id)

                    new_prefix = path_prefix + [(period, 0, move)]

                    # Next: MIN turn (first opponent)
                    child_score = build_subtree(
                        period=period,
                        is_max_turn=False,
                        parent_id=node_id,
                        path_prefix=new_prefix,
                        opponent_idx=0,
                    )

                    node.score = child_score
                    best_score = max(best_score, child_score)

                return best_score

            else:
                # MIN turn: Opponent moves (parent selects MIN among these children)
                
                # Handle case with no opponents - skip directly to next period
                if num_opponents == 0:
                    return build_subtree(
                        period=period + 1,
                        is_max_turn=True,
                        parent_id=parent_id,
                        path_prefix=path_prefix,
                        opponent_idx=0,
                    )
                
                worst_score = float("inf")

                opp_moves = opponent_moves_by_period[period][opponent_idx]

                for move in opp_moves:
                    node_id = f"node_{self.node_counter}"
                    self.node_counter += 1

                    # This node's children will be MAX nodes (you choose)
                    node = TreeNode(
                        id=node_id,
                        label=move,
                        player_index=opponent_idx + 1,
                        parent_id=parent_id,
                        time_period=period,
                        is_max_node=True,  # This node's children are chosen by MAX
                    )
                    self.tree_nodes[node_id] = node
                    self.tree_nodes[parent_id].children.append(node_id)

                    new_prefix = path_prefix + [
                        (period, opponent_idx + 1, move)
                    ]

                    if opponent_idx + 1 < num_opponents:
                        # More opponents to play in this period
                        child_score = build_subtree(
                            period=period,
                            is_max_turn=False,
                            parent_id=node_id,
                            path_prefix=new_prefix,
                            opponent_idx=opponent_idx + 1,
                        )
                    else:
                        # All opponents played, move to next period (MAX turn)
                        child_score = build_subtree(
                            period=period + 1,
                            is_max_turn=True,
                            parent_id=node_id,
                            path_prefix=new_prefix,
                            opponent_idx=0,
                        )

                    node.score = child_score
                    worst_score = min(worst_score, child_score)

                return worst_score

        # Build from root (start with MAX turn at period 0)
        root_score = build_subtree(
            period=0,
            is_max_turn=True,
            parent_id=root_id,
            path_prefix=[],
            opponent_idx=0,
        )

        self.tree_nodes[root_id].score = root_score

        # Find best move (first MAX move with best score)
        best_move = player0_moves[0] if player0_moves else "No move"
        best_child_score = -float("inf")

        for child_id in self.tree_nodes[root_id].children:
            child = self.tree_nodes[child_id]
            if child.score is not None and child.score > best_child_score:
                best_child_score = child.score
                best_move = child.label

        return best_move

    def run_minimax_search(
        self,
        start_state: GameState,
        action_set: List[str],
        time_periods: int,
        time_period_unit: str,
        moves_per_opponent: Optional[int] = None,
    ) -> Tuple[float, str, Dict[str, Any], int]:
        """
        Run Minimax search across multiple time periods.

        Creates a tree showing:
        - Multiple turns (time periods)
        - MAX nodes (your moves) alternating with MIN nodes (opponent responses)
        - Scores propagated using Minimax algorithm
        """
        if moves_per_opponent is None:
            moves_per_opponent = settings.MOVES_PER_PLAYER

        # Limit time periods to prevent too many scenarios
        # With chunked evaluation (150 per batch), we can handle 1500 scenarios in ~10 batches
        # Max scenarios = (user_moves * opp_moves^num_opps)^periods
        # For 3 actions, 2 opp moves, 4 periods: 6^4 = 1296 scenarios
        MAX_SCENARIOS = 1500  # Supports 4 quarters with 3 actions
        num_opponents = len(self.player_profiles) - 1
        user_moves = len(action_set)

        # Calculate max safe periods
        scenarios_per_period = user_moves * (
            moves_per_opponent ** max(num_opponents, 1)
        )

        # Calculate how many periods we can support
        max_safe_periods = 1
        total_scenarios = scenarios_per_period
        while total_scenarios <= MAX_SCENARIOS:
            max_safe_periods += 1
            total_scenarios *= scenarios_per_period
        max_safe_periods -= 1  # Go back to last valid count

        # Ensure at least 1 period
        max_safe_periods = max(max_safe_periods, 1)

        if time_periods > max_safe_periods:
            print(
                f"[Minimax] WARNING: Reducing time_periods from {time_periods} to {max_safe_periods} to stay under {MAX_SCENARIOS} scenarios"
            )
            time_periods = max_safe_periods

        print(
            f"[Minimax] Using {time_periods} periods, {scenarios_per_period}^{time_periods} = {scenarios_per_period**time_periods} scenarios"
        )

        # Reset
        self.tree_nodes = {}
        self.node_counter = 0

        # Create root
        root_id = f"node_{self.node_counter}"
        self.node_counter += 1
        root_node = TreeNode(
            id=root_id,
            label=f"Game Start ({time_periods} {time_period_unit}s)",
            score=None,
            player_index=None,
            parent_id=None,
            children=[],
            time_period=-1,
            is_root=True,
            is_max_node=True,  # Root selects MAX among children
        )
        self.tree_nodes[root_id] = root_node

        # Generate time period labels
        time_period_labels = []
        for i in range(time_periods):
            time_period_labels.append(
                f"{time_period_unit.capitalize()} {i + 1}"
            )

        # Generate opponent moves for each period
        num_opponents = len(self.player_profiles) - 1
        opponent_moves_by_period: List[List[List[str]]] = []

        print(
            f"[Minimax] Starting opponent move generation for {time_periods} periods, {num_opponents} opponents"
        )
        total_start = time.time()

        for period in range(time_periods):
            period_moves: List[List[str]] = []
            move_history = []  # Could track history across periods

            for opp_idx in range(num_opponents):
                start = time.time()
                moves = self._generate_opponent_moves(
                    state=start_state,
                    player_index=opp_idx + 1,
                    num_moves=moves_per_opponent,
                    current_period=period,
                    move_history=move_history,
                )
                print(
                    f"[Minimax] Period {period + 1}, Opponent {opp_idx + 1}: {time.time() - start:.2f}s"
                )
                period_moves.append(moves)

            opponent_moves_by_period.append(period_moves)

        print(
            f"[Minimax] Opponent moves generated in {time.time() - total_start:.2f}s"
        )

        # Generate all leaf scenarios for batch evaluation
        scenarios: List[Tuple[str, List[Dict[str, Any]]]] = []

        def generate_scenario_paths(
            period: int,
            move_sequence: List[Dict[str, Any]],
        ) -> List[List[Dict[str, Any]]]:
            if period >= time_periods:
                return [move_sequence]

            paths: List[List[Dict[str, Any]]] = []
            for p0_move in action_set:
                opponent_combos = list(
                    itertools.product(
                        *[
                            opponent_moves_by_period[period][i]
                            for i in range(num_opponents)
                        ]
                    )
                )

                for opp_combo in opponent_combos:
                    new_seq: List[Dict[str, Any]] = move_sequence + [
                        {
                            "period": period + 1,
                            "player": self.player_profiles[0].name,
                            "move": p0_move,
                        }
                    ]
                    for opp_idx, opp_move in enumerate(opp_combo):
                        new_seq = new_seq + [
                            {
                                "period": period + 1,
                                "player": self.player_profiles[
                                    opp_idx + 1
                                ].name,
                                "move": opp_move,
                            }
                        ]
                    paths.extend(generate_scenario_paths(period + 1, new_seq))

            return paths

        all_scenario_paths = generate_scenario_paths(0, [])
        for idx, path in enumerate(all_scenario_paths):
            scenarios.append((f"s{idx}", path))

        print(f"[Minimax] Generated {len(scenarios)} scenarios to evaluate")

        # Batch evaluate all scenarios
        start = time.time()
        scenario_scores = self._batch_evaluate_scenarios(
            start_state, scenarios, time_periods
        )
        print(
            f"[Minimax] Batch evaluation completed in {time.time() - start:.2f}s"
        )

        # Build the multi-turn tree
        best_move = self._build_multi_turn_tree(
            root_id=root_id,
            player0_moves=action_set,
            opponent_moves_by_period=opponent_moves_by_period,
            scenario_scores=scenario_scores,
            time_periods=time_periods,
            time_period_labels=time_period_labels,
        )

        root_score = self.tree_nodes[root_id].score or 0.5

        # Return actual time_periods used (may be limited)
        return root_score, best_move, self.get_tree_structure(), time_periods

    def get_tree_structure(self) -> Dict[str, Any]:
        return {
            node_id: node.model_dump()
            for node_id, node in self.tree_nodes.items()
        }
