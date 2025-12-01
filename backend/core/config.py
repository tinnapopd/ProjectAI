"""
The environment variables for Google AI Studio are:
- GOOGLE_GENAI_USE_VERTEXAI=FALSE
- GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE

But, When using Google Cloud Vertex AI, you need to set the following
environment variables (Currently used in this project):
- GOOGLE_GENAI_USE_VERTEXAI=TRUE
- GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
- GOOGLE_CLOUD_LOCATION=LOCATION
"""

import warnings
from typing import Annotated, Any, Literal
from typing_extensions import Self

from pydantic import (
    AnyUrl,
    BeforeValidator,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    # This overrides the default settings for the Pydantic BaseSettings
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_ignore_empty=True,
        extra="ignore",
    )

    # General settings
    PROJECT_NAME: str = "A Hybrid AI-Powered Strategic Wargame"
    VERSION: str = "1"
    DESCRIPTION: str = """
    A Hybrid AI-Powered Strategic Wargame that combines Classical AI (MaxN 
    game-tree search) with Modern AI (LLMs) to simulate multi-player business 
    strategy scenarios and discover optimal strategic moves.
    """
    API_PREFIX_STR: str = f"/api/v{VERSION}"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    # Simulation settings
    DEFAULT_PLAYERS: int = 3
    DEFAULT_SEARCH_DEPTH: int = 4  # in time units (e.g., quarter, month, year)
    TIME_PERIOD_UNIT: str = "quarter"  # e.g., "month", "quarter", "year"
    DEFAULT_ACTION_SET_SIZE: int = 4  # Number of possible moves per turn
    MAX_SEARCH_DEPTH: int = 4  # Maximum allowed search depth

    CACHE_GAME_STATES: bool = True
    ENABLE_PRUNING: bool = True
    GENERATE_SEARCH_TREE: bool = True

    # Google Cloud settings
    GOOGLE_GENAI_USE_VERTEXAI: bool = False
    GOOGLE_API_KEY: str = "AIzaSyAQ7lif91PciSr4ZKJoPsohyIg3CrA4Uts"

    # Frontend and backend settings
    FRONTEND_HOST: str = "http://localhost:3000"
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    # Optional: Sentry settings
    SENTRY_DSN: str | None = None

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        return [
            str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS
        ] + [self.FRONTEND_HOST]

    @model_validator(mode="after")
    def _model_settings_validation(self) -> Self:
        # Validate simulation constraints
        if self.DEFAULT_SEARCH_DEPTH > self.MAX_SEARCH_DEPTH:
            raise ValueError(
                f"DEFAULT_SEARCH_DEPTH ({self.DEFAULT_SEARCH_DEPTH}) "
                f"cannot exceed MAX_SEARCH_DEPTH ({self.MAX_SEARCH_DEPTH})"
            )

        return self


settings = Settings()
