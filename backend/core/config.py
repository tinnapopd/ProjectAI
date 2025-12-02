from typing import Annotated, Any, Literal
from typing_extensions import Self

from pydantic import (
    AnyUrl,
    BeforeValidator,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_ignore_empty=True,
        extra="ignore",
    )

    # General settings
    PROJECT_NAME: str = "A Hybrid AI-Powered Strategic Wargame"
    API_PREFIX_STR: str = "/api/v1"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    # Simulation settings
    DEFAULT_PLAYERS: int = 3
    TIME_PERIODS: int = 4
    TIME_PERIOD_UNIT: str = "quarter"
    DEFAULT_ACTION_SET_SIZE: int = 4  # Number of possible moves per turn
    MAX_SEARCH_DEPTH: int = 4  # Maximum allowed search depth

    CACHE_GAME_STATES: bool = True
    ENABLE_PRUNING: bool = True
    GENERATE_SEARCH_TREE: bool = True

    # Google Cloud settings
    GOOGLE_GENAI_USE_VERTEXAI: bool = False
    GOOGLE_API_KEY: str = ""

    # Frontend and backend settings
    FRONTEND_HOST: str = "http://localhost:3000"
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        return [
            str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS
        ] + [self.FRONTEND_HOST]

    @model_validator(mode="after")
    def _game_settings_validation(self) -> Self:
        if self.TIME_PERIODS > self.MAX_SEARCH_DEPTH:
            raise ValueError(
                f"TIME_PERIODS ({self.TIME_PERIODS}) "
                f"cannot exceed MAX_SEARCH_DEPTH ({self.MAX_SEARCH_DEPTH})"
            )
        return self

    @model_validator(mode="after")
    def _google_credentials_validation(self) -> Self:
        if not self.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY must be set.")
        return self


# Instantiate settings singleton
settings = Settings()
