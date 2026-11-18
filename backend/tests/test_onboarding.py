from datetime import UTC, datetime

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.features.auth.models import User
from app.features.onboarding.models import UserOnboarding

PREFIX = "/api/v1/onboarding"
PASSWORD = "a long private passphrase"


def register_and_login(client, email: str = "owner@example.com") -> tuple[dict, str]:
    registration = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Mouad Example", "email": email, "password": PASSWORD},
    )
    assert registration.status_code == 201
    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": PASSWORD},
    )
    assert login.status_code == 200
    return registration.json(), login.json()["access_token"]


def headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def choose(client, token: str, starting_path: str):
    return client.put(
        f"{PREFIX}/starting-path",
        headers=headers(token),
        json={"starting_path": starting_path},
    )


def test_onboarding_requires_authentication(client):
    assert client.get(PREFIX).status_code == 401
    assert client.put(
        f"{PREFIX}/starting-path",
        json={"starting_path": "find_first_leads"},
    ).status_code == 401


def test_new_user_has_an_incomplete_onboarding_state(client, db):
    _, token = register_and_login(client)

    response = client.get(PREFIX, headers=headers(token))

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.json() == {
        "starting_path": None,
        "completed": False,
        "completed_at": None,
        "updated_at": None,
    }
    assert db.scalar(select(func.count()).select_from(UserOnboarding)) == 0


@pytest.mark.parametrize("starting_path", ["find_first_leads", "grow_pipeline"])
def test_authenticated_user_can_save_each_starting_path(client, db, starting_path):
    registered_user, token = register_and_login(client)

    response = choose(client, token, starting_path)

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.json()["starting_path"] == starting_path
    assert response.json()["completed"] is True
    assert response.json()["completed_at"] is not None
    assert response.json()["updated_at"] is not None
    onboarding = db.scalar(select(UserOnboarding))
    assert str(onboarding.user_id) == registered_user["id"]
    assert onboarding.starting_path == starting_path


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"starting_path": None},
        {"starting_path": "unsupported_path"},
        {"starting_path": "find_first_leads", "unexpected": True},
    ],
)
def test_invalid_starting_path_is_rejected_without_creating_a_record(client, db, payload):
    _, token = register_and_login(client)

    response = client.put(
        f"{PREFIX}/starting-path",
        headers=headers(token),
        json=payload,
    )

    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"
    assert db.scalar(select(func.count()).select_from(UserOnboarding)) == 0


def test_repeating_the_choice_updates_one_record(client, db):
    _, token = register_and_login(client)
    assert choose(client, token, "find_first_leads").status_code == 200
    first = db.scalar(select(UserOnboarding))
    first_id = first.id
    first_created_at = first.created_at
    first_updated_at = first.updated_at

    assert choose(client, token, "find_first_leads").status_code == 200
    db.expire_all()
    saved = db.scalar(select(UserOnboarding))

    assert db.scalar(select(func.count()).select_from(UserOnboarding)) == 1
    assert saved.id == first_id
    assert saved.created_at == first_created_at
    assert saved.updated_at >= first_updated_at


def test_user_can_change_the_existing_starting_path(client, db):
    _, token = register_and_login(client)
    choose(client, token, "find_first_leads")
    record_id = db.scalar(select(UserOnboarding.id))

    response = choose(client, token, "grow_pipeline")
    db.expire_all()
    saved = db.scalar(select(UserOnboarding))

    assert response.status_code == 200
    assert response.json()["starting_path"] == "grow_pipeline"
    assert saved.id == record_id
    assert saved.starting_path == "grow_pipeline"


def test_onboarding_state_is_isolated_by_authenticated_user(client, db):
    first_user, first_token = register_and_login(client, "first@example.com")
    second_user, second_token = register_and_login(client, "second@example.com")
    assert choose(client, first_token, "find_first_leads").status_code == 200

    second_state = client.get(PREFIX, headers=headers(second_token))
    assert second_state.json()["completed"] is False
    assert choose(client, second_token, "grow_pipeline").status_code == 200

    first_state = client.get(
        f"{PREFIX}?user_id={second_user['id']}",
        headers=headers(first_token),
    )
    assert first_state.json()["starting_path"] == "find_first_leads"
    rows = db.scalars(select(UserOnboarding)).all()
    paths_by_user = {str(row.user_id): row.starting_path for row in rows}
    assert paths_by_user == {
        first_user["id"]: "find_first_leads",
        second_user["id"]: "grow_pipeline",
    }


def test_client_cannot_supply_a_user_id(client, db):
    first_user, first_token = register_and_login(client, "first@example.com")
    second_user, _ = register_and_login(client, "second@example.com")

    response = client.put(
        f"{PREFIX}/starting-path",
        headers=headers(first_token),
        json={
            "starting_path": "find_first_leads",
            "user_id": second_user["id"],
        },
    )

    assert response.status_code == 422
    assert db.scalar(select(func.count()).select_from(UserOnboarding)) == 0
    assert first_user["id"] != second_user["id"]


def test_deleting_a_user_cascades_to_onboarding(client, db):
    _, token = register_and_login(client)
    assert choose(client, token, "find_first_leads").status_code == 200
    assert db.scalar(select(func.count()).select_from(UserOnboarding)) == 1

    user = db.scalar(select(User).where(User.email == "owner@example.com"))
    db.delete(user)
    db.commit()

    assert db.scalar(select(func.count()).select_from(UserOnboarding)) == 0


def test_database_constraint_rejects_an_unknown_starting_path(client, db):
    registered_user, _ = register_and_login(client)
    db.add(UserOnboarding(
        user_id=registered_user["id"],
        starting_path="unknown",
        completed_at=datetime.now(UTC),
    ))

    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_cors_allows_onboarding_put_from_the_frontend(client):
    response = client.options(
        f"{PREFIX}/starting-path",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "PUT",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "PUT" in response.headers["access-control-allow-methods"]
