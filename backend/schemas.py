from pydantic import BaseModel
from typing import Optional, List, Dict, Any


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


class StrategyMove(BaseModel):
    """
    Model representing a strategic move made by a company.
    Attributes:
        move_id: Unique identifier for the move
        move_name: Short descriptive name of the strategic action
        description: Detailed explanation of the strategic action
        stratgic_category: Category of the strategy
        (e.g., Pricing, Product, Marketing, Acquisition,
        Partnership, Technology, Other)
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

    strategic_moves: List[StrategyMove]


class PlayerState(BaseModel):
    """
    Model representing a player's state in the game.

    Attributes:
        player_id: Unique identifier for the player
            (e.g., "OurCompany", "Competitor_A")
        market_share: Player's market share (0.0 to 1.0)
        revenue: Player's revenue in the current period
        brand_sentiment: Brand perception score (0.0 to 1.0)
        resources: Available resources/capital
        additional_metrics: Optional dictionary for custom metrics
    """

    player_id: str
    market_share: float
    revenue: float
    brand_sentiment: float
    resources: float
    additional_metrics: Optional[Dict[str, Any]] = None


class GameState(BaseModel):
    """
    Model representing the current state of the game simulation.

    Attributes:
        period: Current time period number
            (quarter/month/year depending on TIME_PERIOD_UNIT)
        market_size: Total market size/value
        players: List of all player states in the game
        market_conditions: Optional dictionary for market trends,
            economic indicators, etc.
    """

    period: int
    market_size: float
    players: List[PlayerState]
    market_conditions: Optional[Dict[str, Any]] = None


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


class OpponentMoveSelection(BaseModel):
    """
    Model representing an opponent's move selection.

    Attributes:
        selected_move_id: ID of the chosen move from available options
        reasoning: Brief explanation of why this move was chosen
    """

    selected_move_id: str
    reasoning: str


class EvaluationResult(BaseModel):
    """
    Model representing the evaluation result from the Evaluator Agent.

    Attributes:
        new_game_state: Updated game state after all moves are applied
        heuristic_score: Numeric score based on business goal
        score_explanation: Brief justification of the score
    """

    new_game_state: GameState
    heuristic_score: float
    score_explanation: str


class UserActionRequest(BaseModel):
    """
    Model representing the user's action request.

    Attributes:
        user_id: Unique identifier for the user
        business_goal: The user-defined business objective
        company_profile: Profile of the user's company
    """

    user_id: str
    business_goal: str
    company_profile: CompanyProfile


class ActionResponse(BaseModel):
    """
    Model representing the user's action response.

    Attributes:
        selected_move_id: ID of the move selected by the user
        reasoning: Brief explanation of why this move was chosen
    """

    selected_move_id: str
    reasoning: str
