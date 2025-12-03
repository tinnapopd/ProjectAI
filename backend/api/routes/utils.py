from fastapi import APIRouter

router = APIRouter(prefix="/utils", tags=["Utilities"])


@router.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}
