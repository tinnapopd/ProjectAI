from fastapi import APIRouter, HTTPException
import uuid

from api.deps import get_maxn_controller, get_strategy_agent
from core.config import settings
from schemas import WargameRequest, WargameResponse


router = APIRouter(prefix="/wargame", tags=["Business Wargame"])


@router.post("/run", response_model=WargameResponse)
async def run_wargame(request: WargameRequest):
    try:
        session_id = str(uuid.uuid4())
        action_set = request.action_set
        time_periods = request.game_state.time_periods or settings.TIME_PERIODS
        time_period_unit = (
            request.game_state.time_period_unit or settings.TIME_PERIOD_UNIT
        )
        if not action_set:
            # Generate action set using strategy agent
            strategy = await get_strategy_agent(request.user_id, session_id)
            company_profile = next(
                (
                    profile
                    for profile in request.player_profiles
                    if profile.isUserCompany
                ),
                None,
            )
            prompt = f"""
            Given the current GameState (JSON):
            {request.game_state.model_dump_json(indent=2)}
            
            Business Goal:
            {request.business_goal}

            Company Profile:
            {company_profile.model_dump_json(indent=2) if company_profile else "N/A"}
            
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

        # Create MaxN controller
        controller = await get_maxn_controller(
            user_id=request.user_id,
            session_id=session_id,
            business_goal=request.business_goal,
            player_profiles=request.player_profiles,
        )

        # Run the search
        best_score, best_move, tree_structure = controller.run_a_period_search(
            start_state=request.game_state,
            action_set=action_set,
            time_period_unit=time_period_unit,
        )

        return WargameResponse(
            best_score=best_score,
            best_move=best_move,
            tree_structure=tree_structure,
            time_periods=time_periods,
            time_period_unit=time_period_unit,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error running wargame simulation: {str(e)}",
        )
