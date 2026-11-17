import hashlib
from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException
from sqlalchemy import func, select

from app.features.auth.models import AuthRateLimit, AuthSession, User
from app.features.auth.service import password_hasher

ACCOUNT = {"email": "owner@example.com", "password": "a long private passphrase"}
PREFIX = "/api/v1/auth"


def register(client, **overrides):
    return client.post(f"{PREFIX}/register", json=ACCOUNT | {"full_name": "Mouad Example"} | overrides)


def login(client, **overrides):
    return client.post(f"{PREFIX}/login", json=ACCOUNT | overrides)


def headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_registration_normalizes_email_and_hashes_password(client, db):
    response = register(client, email=" Owner@Example.COM ", full_name="  Mouad Example  ")
    assert response.status_code == 201
    assert response.json()["email"] == ACCOUNT["email"]
    assert response.json()["full_name"] == "Mouad Example"
    assert set(response.json()) == {"id", "full_name", "email", "created_at"}
    user = db.scalar(select(User))
    assert user.full_name == "Mouad Example"
    assert user.password_hash.startswith("$argon2id$")
    assert password_hasher.verify(ACCOUNT["password"], user.password_hash)
    assert ACCOUNT["password"] not in response.text


def test_duplicate_email_cannot_replace_existing_password(client, db):
    assert register(client).status_code == 201
    assert register(client, email="OWNER@EXAMPLE.COM", password="another long password").status_code == 409
    assert db.scalar(select(func.count()).select_from(User)) == 1
    assert login(client).status_code == 200


@pytest.mark.parametrize("override", [
    {"email": "not-an-email"},
    {"password": "short"},
    {"password": "x" * 129},
    {"is_active": True},
    {"full_name": ""},
    {"full_name": "   "},
    {"full_name": "x" * 101},
    {"full_name": None},
])
def test_invalid_registration_does_not_echo_input_or_create_user(client, db, override):
    response = register(client, **override)
    assert response.status_code == 422
    assert all("input" not in error for error in response.json()["detail"])
    assert ACCOUNT["password"] not in response.text
    assert db.scalar(select(func.count()).select_from(User)) == 0


def test_login_me_and_logout_revoke_session(client, db):
    user = register(client).json()
    response = login(client)
    assert response.status_code == 200
    assert response.json()["user"]["full_name"] == "Mouad Example"
    assert response.headers["cache-control"] == "no-store"
    token = response.json()["access_token"]
    stored = db.scalar(select(AuthSession))
    assert stored.token_hash == hashlib.sha256(token.encode()).hexdigest()
    assert stored.token_hash != token
    assert response.json()["expires_in"] == 86400
    assert client.get(f"{PREFIX}/me", headers=headers(token)).json() == user
    assert client.post(f"{PREFIX}/logout", headers=headers(token)).status_code == 204
    assert client.get(f"{PREFIX}/me", headers=headers(token)).status_code == 401


def test_full_name_required_for_registration_but_not_login(client):
    assert client.post(f"{PREFIX}/register", json=ACCOUNT).status_code == 422
    assert register(client, full_name="مُعاذ").status_code == 201
    assert login(client).json()["user"]["full_name"] == "مُعاذ"


def test_existing_account_without_name_can_still_login(client, db):
    register(client)
    user = db.scalar(select(User))
    user.full_name = None
    db.commit()
    response = login(client)
    assert response.status_code == 200
    assert response.json()["user"]["full_name"] is None


def test_wrong_password_and_unknown_account_have_same_error(client):
    register(client)
    wrong = login(client, password="incorrect password")
    missing = login(client, email="missing@example.com")
    assert wrong.status_code == missing.status_code == 401
    assert wrong.json() == missing.json()
    assert wrong.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize("token", [None, "bad-token", "A" * 43])
def test_missing_or_invalid_token_is_rejected(client, token):
    response = client.get(f"{PREFIX}/me", headers=headers(token) if token else {})
    assert response.status_code == 401


def test_expired_session_is_rejected(client, db):
    register(client)
    token = login(client).json()["access_token"]
    session = db.scalar(select(AuthSession))
    session.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    db.commit()
    assert client.get(f"{PREFIX}/me", headers=headers(token)).status_code == 401


def test_disabled_user_cannot_login_or_use_existing_session(client, db):
    register(client)
    token = login(client).json()["access_token"]
    user = db.scalar(select(User))
    user.is_active = False
    db.commit()
    assert login(client).status_code == 401
    assert client.get(f"{PREFIX}/me", headers=headers(token)).status_code == 401


def test_logout_only_revokes_current_session(client):
    register(client)
    first = login(client).json()["access_token"]
    second = login(client).json()["access_token"]
    client.post(f"{PREFIX}/logout", headers=headers(first))
    assert client.get(f"{PREFIX}/me", headers=headers(second)).status_code == 200


def test_user_identity_is_derived_from_token(client):
    first = register(client).json()
    second = register(client, email="second@example.com").json()
    token = login(client).json()["access_token"]
    response = client.get(f"{PREFIX}/me?user_id={second['id']}", headers=headers(token))
    assert response.json()["id"] == first["id"]


def test_login_throttle_is_persisted_and_returns_retry_after(client, db, monkeypatch):
    from app.features.auth import service

    # Use one future window throughout this test, independent of wall-clock boundaries.
    frozen = datetime.now(UTC) + timedelta(minutes=1)

    class FrozenDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return frozen

    monkeypatch.setattr(service, "datetime", FrozenDatetime)
    with pytest.raises(HTTPException) as result:
        service.enforce_rate_limit(db, "login-email", ACCOUNT["email"], 0)
    assert result.value.status_code == 429
    limit = db.scalar(select(AuthRateLimit))
    limit.attempts = 10
    db.commit()
    response = login(client)
    assert response.status_code == 429
    assert int(response.headers["retry-after"]) > 0


def test_cors_allows_frontend_but_not_unknown_origin(client):
    request_headers = {"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST",
                       "Access-Control-Request-Headers": "authorization,content-type"}
    response = client.options(f"{PREFIX}/login", headers=request_headers)
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    response = client.options(f"{PREFIX}/login", headers=request_headers | {"Origin": "https://untrusted.example"})
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
