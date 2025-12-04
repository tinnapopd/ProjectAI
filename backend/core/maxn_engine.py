import json
from typing import List, Dict, Tuple, Optional, Any

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

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

    def _recursive_search(
        self,
        state: GameState,
        current_path: List[str],
        available_moves: List[str],
        turn_index: int,
        parent_id: str,
        move_label: str,
    ):
        my_node_id = f"node_{self.node_counter}"
        self.node_counter += 1

        current_node = TreeNode(
            id=my_node_id,
            label=move_label,
            player_index=turn_index - 1,
            parent_id=parent_id,
        )
        self.tree_nodes[my_node_id] = current_node

        # Add this node as child of parent
        if parent_id and parent_id in self.tree_nodes:
            self.tree_nodes[parent_id].children.append(my_node_id)

        # Check if we are at a leaf (All players have moved)
        if turn_index >= len(self.player_profiles):
            eval_prompt = f"""
            Given the current GameState (JSON): 
            {state.model_dump_json(indent=2)}

            Business Goal: 
            {self.business_goal}

            Player Profiles:
            {", ".join([p.model_dump_json(indent=2) for p in self.player_profiles])}
            """
            data = self.evaluator.call_agent(prompt=eval_prompt)
            if data and isinstance(data, dict):
                score = data.get("heuristic_score", 0.5)
            else:
                score = 0.5  # Default score if evaluation fails

            current_node.score = score
            return score, my_node_id

        # Opponent's turn
        current_player = self.player_profiles[turn_index]
        opp_prompt = f"""
        Given the current GameState (JSON):
        {state.model_dump_json(indent=2)}

        Business Goal:
        {self.business_goal}

        Company Profile:
        {current_player.model_dump_json(indent=2)}
        """

        opp_response = self.opponent.call_agent(prompt=opp_prompt)
        if opp_response and isinstance(opp_response, dict):
            opp_move = opp_response.get("selected_move", "Observe and wait")
        else:
            opp_move = "Observe and wait"

        new_path = current_path + [opp_move]

        # Recurse to next player (turn_index + 1)
        score, child_id = self._recursive_search(
            state=state,
            current_path=new_path,
            available_moves=available_moves,
            turn_index=turn_index + 1,
            parent_id=my_node_id,
            move_label=opp_move,
        )

        current_node.score = score
        return score, my_node_id

    def run_a_period_search(
        self,
        start_state: GameState,
        action_set: List[str],
        time_period_unit: str,
    ) -> Tuple[float, str, Dict[str, Any]]:
        # Reset tree for new search
        self.tree_nodes = {}
        self.node_counter = 0

        # Create root node
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

        best_score = -float("inf")
        best_move = None

        # Iterate through OUR moves
        for move in action_set:
            score, _ = self._recursive_search(
                state=start_state,
                current_path=[move],
                available_moves=action_set,
                turn_index=1,  # Start recursion at Player Index 1
                parent_id=root_id,
                move_label=move,
            )

            if score > best_score:
                best_score = score
                best_move = move

        # Return tree structure
        tree_structure = self.get_tree_structure()
        if best_move is None:
            best_move = "No move available"

        return best_score, best_move, tree_structure

    def get_tree_structure(self) -> Dict[str, Any]:
        return {
            node_id: node.model_dump()
            for node_id, node in self.tree_nodes.items()
        }
