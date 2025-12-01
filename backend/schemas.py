from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class Move(BaseModel):
    """
    Model representing a strategic move made by a company.
    Attributes:
        move_id: Unique identifier for the move
        move_name: Short descriptive name of the strategic action
        description: Detailed explanation of the strategic action
        stratgic_category: Category of the strategy (e.g., Pricing,
            Product, Marketing, Acquisition, Partnership, Technology, Other)
        expected_score: AI-evaluated score indicating expected outcome (optional)
        score_explanation: Brief explanation of the score (optional)
    """

    move_id: str
    move_name: str
    description: str
    stratgic_category: str
    expected_score: Optional[float] = None
    score_explanation: Optional[str] = None


class StrategicMoves(BaseModel):
    """Model representing a collection of strategic moves."""

    strategic_moves: List[Move]


class OpponentMoves(BaseModel):
    """Model representing a collection of opponent moves."""

    opponent_moves: List[Move]


class ExecutedMove(BaseModel):
    """
    Model representing a move that has been executed by a player.

    Attributes:
        player_name: Name of the player/company executing the move
        move_id: ID of the executed move
        move_name: Name of the executed move
    """

    player_name: str
    move_id: str
    move_name: str


class ScoringDetails(BaseModel):
    """
    Model representing the scoring details after evaluation.

    Attributes:
        heuristic_score: Numeric score based on business goal
        score_explanation: Brief justification of the score
        key_changes: List of key changes in the game state
            that influenced the score
    """

    heuristic_score: float
    score_explanation: str
    key_changes: List[str]


class CompanyProfile(BaseModel):
    """
    Model representing a company's profile in the game.

    Attributes:
        name: Name of the company
        business_type: Industry or sector the company operates in
        company_size: Number of employees in the company
        products: List of products or services offered by the company
        target_customers: List of target customer segments
        others: Optional dictionary for any additional attributes

    """

    name: str
    business_type: str
    company_size: int  # Number of employees
    products: List[str]
    target_customers: List[str]
    others: Optional[Dict[str, Any]] = None


class GameState(BaseModel):
    """
    Model representing the state of the game/market.
    Attributes:
        time_period: Current time period in the simulation
        market_size: Size of the market in monetary terms
        others: Optional dictionary for any additional market metrics
    """

    time_period: int
    market_size: float
    others: Optional[Dict[str, Any]] = None


class EvaluationOutput(BaseModel):
    """
    Model representing the output of the evaluation.

    Attributes:
        moves_executed: List of moves executed by all players
        game_state: Current state of the game after moves
        scoring: Scoring details based on the evaluation
    """

    moves_executed: List[ExecutedMove]
    game_state: GameState
    players: List[CompanyProfile]
    scoring: ScoringDetails


class GameStartRequest(BaseModel):
    """
    Model representing the initial setup request to start a game simulation.

    Attributes:
        business_goal: The user-defined business objective to optimize
        our_company: Profile of the user's company
        competitors: List of competitor company profiles
        initial_game_state: Initial state of the game/market
        industry_context: Optional context about industry, market dynamics
    """

    business_goal: str
    our_company: CompanyProfile
    competitors: List[CompanyProfile]
    initial_game_state: GameState
    industry_context: Optional[str] = None
