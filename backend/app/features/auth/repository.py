from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.features.auth.models import AuthRateLimit, AuthSession, User


def find_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def find_session(db: Session, token_hash: str) -> AuthSession | None:
    return db.scalar(select(AuthSession).where(AuthSession.token_hash == token_hash))


def increment_rate_limit(db: Session, key: str, expires_at: datetime) -> int:
    db.execute(delete(AuthRateLimit).where(AuthRateLimit.expires_at <= datetime.now(UTC)))
    statement = insert(AuthRateLimit).values(key=key, attempts=1, expires_at=expires_at)
    count = db.scalar(statement.on_conflict_do_update(
        index_elements=[AuthRateLimit.key],
        set_={"attempts": AuthRateLimit.attempts + 1},
    ).returning(AuthRateLimit.attempts))
    db.commit()
    return count
