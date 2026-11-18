from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.features.onboarding import repository
from app.features.onboarding.models import UserOnboarding
from app.features.onboarding.schemas import StartingPath


def get_state(db: Session, user_id: UUID) -> UserOnboarding | None:
    return repository.find_by_user_id(db, user_id)


def choose_starting_path(
    db: Session,
    user_id: UUID,
    starting_path: StartingPath,
) -> UserOnboarding:
    return repository.save_starting_path(
        db,
        user_id,
        starting_path.value,
        datetime.now(UTC),
    )
