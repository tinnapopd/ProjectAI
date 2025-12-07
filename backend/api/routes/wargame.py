from fastapi import APIRouter, HTTPException
import uuid

from api.deps import get_minimax_controller, get_strategy_agent
from core.config import settings
from schemas import WargameRequest, WargameResponse, CompanyProfile


router = APIRouter(prefix="/wargame", tags=["Business Wargame"])


def generate_opponent_profiles(
    user_company: CompanyProfile,
    num_opponents: int,
    business_goal: str,
) -> list[CompanyProfile]:
    """Generate synthetic opponent profiles based on the user's company."""
    opponent_names = [
        "Alpha Dynamics",
        "Beta Industries",
        "Gamma Corp",
        "Delta Solutions",
        "Epsilon Tech",
        "Zeta Global",
    ]

    opponent_goals = [
        "Maximize market share through aggressive pricing",
        "Focus on premium segment and brand differentiation",
        "Expand through strategic partnerships and acquisitions",
        "Innovate with cutting-edge technology and R&D",
        "Optimize operational efficiency and cost leadership",
        "Build customer loyalty through superior service",
    ]

    opponents = []
    for i in range(num_opponents):
        opponent = CompanyProfile(
            id=f"opponent_{i + 1}",
            name=opponent_names[i % len(opponent_names)],
            business_goal=opponent_goals[i % len(opponent_goals)],
            about_us=f"A competitive company in the same market as {user_company.name}.",
            customers=user_company.customers[:2]
            if user_company.customers
            else ["General consumers"],
            isUserCompany=False,
        )
        opponents.append(opponent)

    return opponents


@router.post("/run", response_model=WargameResponse)
async def run_wargame(request: WargameRequest):
    try:
        session_id = str(uuid.uuid4())
        action_set = request.action_set
        time_periods = request.game_state.time_periods or settings.TIME_PERIODS
        time_period_unit = (
            request.game_state.time_period_unit or settings.TIME_PERIOD_UNIT
        )

        # Find user company profile
        user_company = next(
            (
                profile
                for profile in request.player_profiles
                if profile.isUserCompany
            ),
            None,
        )

        if not user_company:
            # Create a default user company if none provided
            user_company = CompanyProfile(
                id="user_company",
                name="Your Company",
                business_goal=request.business_goal,
                about_us="",
                customers=[],
                isUserCompany=True,
            )

        # Auto-generate opponent profiles based on DEFAULT_PLAYERS
        # Total players = user + opponents, so opponents = DEFAULT_PLAYERS - 1
        num_opponents = settings.DEFAULT_PLAYERS - 1

        # Check if opponents already provided in request
        existing_opponents = [
            p for p in request.player_profiles if not p.isUserCompany
        ]

        if len(existing_opponents) < num_opponents:
            # Generate missing opponents
            additional_opponents = generate_opponent_profiles(
                user_company=user_company,
                num_opponents=num_opponents - len(existing_opponents),
                business_goal=request.business_goal,
            )
            all_opponents = existing_opponents + additional_opponents
        else:
            all_opponents = existing_opponents[:num_opponents]

        # Combine user company with opponents
        player_profiles = [user_company] + all_opponents

        if not action_set:
            # Generate action set using strategy agent
            strategy = await get_strategy_agent(request.user_id, session_id)
            prompt = f"""
            Given the current GameState (JSON):
            {request.game_state.model_dump_json(indent=2)}
            
            Business Goal:
            {request.business_goal}

            Company Profile:
            {user_company.model_dump_json(indent=2)}
            
            Number of Time Periods: {time_periods} {time_period_unit}(s)
            """
            result = strategy.call_agent(prompt=prompt)
            if result and isinstance(result, dict):
                action_set = result.get("moves", [])

            if not action_set:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to generate action set. "
                    + "Please provide action_set in request.",
                )

        # Create Minimax controller with all player profiles
        controller = await get_minimax_controller(
            user_id=request.user_id,
            session_id=session_id,
            business_goal=request.business_goal,
            player_profiles=player_profiles,
        )

        # Run the minimax search across all time periods
        best_score, best_move, tree_structure, actual_time_periods = (
            controller.run_minimax_search(
                start_state=request.game_state,
                action_set=action_set,
                time_periods=time_periods,
                time_period_unit=time_period_unit,
            )
        )

        return WargameResponse(
            best_score=best_score,
            best_move=best_move,
            tree_structure=tree_structure,
            time_periods=actual_time_periods,  # Use actual (possibly limited) periods
            time_period_unit=time_period_unit,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error running wargame simulation: {str(e)}",
        )
