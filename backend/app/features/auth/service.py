import hashlib
import re
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from pwdlib import PasswordHash
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.features.auth import repository
from app.features.auth.models import AuthSession, User
from app.features.auth.schemas import LoginRequest, RegisterRequest

password_hasher = PasswordHash.recommended()
dummy_hash = password_hasher.hash(secrets.token_urlsafe(32))


def unauthorized() -> HTTPException:
    return HTTPException(401, "Invalid or expired credentials", headers={"WWW-Authenticate": "Bearer"})


def enforce_rate_limit(db: Session, category: str, identity: str, maximum: int) -> None:
    now = datetime.now(UTC)
    window = int(now.timestamp()) // 60
    key = hashlib.sha256(f"{category}:{identity}:{window}".encode()).hexdigest()
    expiry = datetime.fromtimestamp((window + 1) * 60, UTC)
    if repository.increment_rate_limit(db, key, expiry) > maximum:
        raise HTTPException(429, "Too many attempts. Try again shortly.", headers={
            "Retry-After": str(max(1, int((expiry - now).total_seconds()) + 1)),
        })


def register(db: Session, data: RegisterRequest) -> User:
    user = User(
        full_name=data.full_name,
        email=str(data.email),
        password_hash=password_hasher.hash(data.password.get_secret_value()),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        if repository.find_user_by_email(db, str(data.email)):
            raise HTTPException(409, "An account with this email already exists") from None
        raise
    db.refresh(user)
    return user


def login(db: Session, data: LoginRequest) -> tuple[User, str, int]:
    user = repository.find_user_by_email(db, str(data.email))
    valid, updated_hash = password_hasher.verify_and_update(
        data.password.get_secret_value(), user.password_hash if user else dummy_hash,
    )
    if not user or not valid or not user.is_active:
        raise unauthorized()
    if updated_hash:
        user.password_hash = updated_hash
    token = secrets.token_urlsafe(32)
    lifetime = get_settings().session_lifetime_seconds
    db.add(AuthSession(
        user_id=user.id,
        token_hash=hashlib.sha256(token.encode()).hexdigest(),
        expires_at=datetime.now(UTC) + timedelta(seconds=lifetime),
    ))
    db.commit()
    return user, token, lifetime


def authenticate(db: Session, token: str) -> tuple[User, AuthSession]:
    if not re.fullmatch(r"[A-Za-z0-9_-]{43}", token):
        raise unauthorized()
    session = repository.find_session(db, hashlib.sha256(token.encode()).hexdigest())
    if not session or session.revoked_at or session.expires_at <= datetime.now(UTC):
        raise unauthorized()
    user = db.get(User, session.user_id)
    if not user or not user.is_active:
        raise unauthorized()
    return user, session


def logout(db: Session, session: AuthSession) -> None:
    session.revoked_at = datetime.now(UTC)
    db.commit()
