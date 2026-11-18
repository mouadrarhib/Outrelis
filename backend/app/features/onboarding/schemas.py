from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class StartingPath(StrEnum):
    FIND_FIRST_LEADS = "find_first_leads"
    GROW_PIPELINE = "grow_pipeline"


class StartingPathRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    starting_path: StartingPath


class OnboardingStateResponse(BaseModel):
    starting_path: StartingPath | None
    completed: bool
    completed_at: datetime | None
    updated_at: datetime | None
