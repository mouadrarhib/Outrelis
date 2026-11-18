from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.features.onboarding.models import UserOnboarding


def find_by_user_id(db: Session, user_id: UUID) -> UserOnboarding | None:
    return db.scalar(select(UserOnboarding).where(UserOnboarding.user_id == user_id))


def save_starting_path(
    db: Session,
    user_id: UUID,
    starting_path: str,
    completed_at: datetime,
) -> UserOnboarding:
    statement = insert(UserOnboarding).values(
        id=uuid4(),
        user_id=user_id,
        starting_path=starting_path,
        completed_at=completed_at,
        updated_at=completed_at,
    )
    statement = statement.on_conflict_do_update(
        index_elements=[UserOnboarding.user_id],
        set_={
            "starting_path": starting_path,
            "completed_at": completed_at,
            "updated_at": completed_at,
        },
    ).returning(UserOnboarding)
    onboarding = db.scalars(statement).one()
    db.commit()
    db.refresh(onboarding)
    return onboarding
