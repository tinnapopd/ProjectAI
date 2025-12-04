from uuid import uuid4

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class CompanyProfile(BaseModel):
    id: str
    name: str
    business_goal: str
    about_us: str = ""
    customers: List[str] = Field(default_factory=list)
    isUserCompany: bool = False


class StrategyAgentMoves(BaseModel):
    moves: List[str]


class OpponentAgentMoves(BaseModel):
    moves: List[str]


class ScenarioScore(BaseModel):
    scenario_id: str
    score: float


class BatchEvaluationResult(BaseModel):
    scores: List[ScenarioScore]


class GameState(BaseModel):
    metrics: Dict[str, Any]
    history: List[Dict[str, Any]] = Field(default_factory=list)
    time_periods: Optional[int] = None
    time_period_unit: Optional[str] = None


class TreeNode(BaseModel):
    id: str
    label: str
    score: Optional[float] = None
    player_index: Optional[int] = None
    parent_id: Optional[str] = None
    children: List[str] = Field(default_factory=list)


class WargameRequest(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid4()))
    business_goal: str
    player_profiles: List[CompanyProfile]
    game_state: GameState
    action_set: List[str] = Field(default_factory=list)


class WargameResponse(BaseModel):
    best_score: float
    best_move: str
    tree_structure: Dict[str, Any]
    time_periods: int
    time_period_unit: str
