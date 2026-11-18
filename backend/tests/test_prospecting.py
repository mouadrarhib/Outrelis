from sqlalchemy import func, select

from app.features.auth.models import User
from app.features.prospecting.models import (
    OfferProfile,
    SearchDraft,
    SearchDraftLocation,
)

ENDPOINT = "/api/v1/prospecting/setup"
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


def setup_payload(**overrides):
    payload = {
        "service_name": "Website design",
        "outreach_language": "en-US",
        "business_category": "Dental clinics",
        "locations": ["New York, NY", "Austin, TX"],
        "result_limit_per_location": 20,
    }
    payload.update(overrides)
    return payload


def save(client, token: str, payload: dict | None = None):
    return client.put(
        ENDPOINT,
        headers=headers(token),
        json=payload or setup_payload(),
    )


def test_prospecting_setup_requires_authentication(client):
    assert client.get(ENDPOINT).status_code == 401
    assert client.put(ENDPOINT, json=setup_payload()).status_code == 401


def test_new_user_has_no_prospecting_setup(client, db):
    _, token = register_and_login(client)

    response = client.get(ENDPOINT, headers=headers(token))

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.json() == {
        "configured": False,
        "offer_profile": None,
        "search_draft": None,
    }
    assert db.scalar(select(func.count()).select_from(OfferProfile)) == 0


def test_user_can_save_a_multi_location_setup(client, db):
    registered_user, token = register_and_login(client)
    payload = setup_payload(
        service_name="  Website   design  ",
        business_category=" Dental   clinics ",
        locations=[" New York,   NY ", " Austin, TX "],
    )

    response = save(client, token, payload)

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    body = response.json()
    assert body["configured"] is True
    assert body["offer_profile"]["service_name"] == "Website design"
    assert body["offer_profile"]["outreach_language"] == "en-US"
    assert body["search_draft"]["business_category"] == "Dental clinics"
    assert body["search_draft"]["result_limit_per_location"] == 20
    assert [item["location_query"] for item in body["search_draft"]["locations"]] == [
        "New York, NY",
        "Austin, TX",
    ]
    assert [item["position"] for item in body["search_draft"]["locations"]] == [1, 2]

    offer = db.scalar(select(OfferProfile))
    draft = db.scalar(select(SearchDraft))
    locations = list(db.scalars(
        select(SearchDraftLocation).order_by(SearchDraftLocation.position)
    ))
    assert str(offer.user_id) == registered_user["id"]
    assert draft.user_id == offer.user_id
    assert draft.offer_profile_id == offer.id
    assert [item.normalized_location for item in locations] == [
        "new york, ny",
        "austin, tx",
    ]


def test_saved_setup_can_be_loaded(client):
    _, token = register_and_login(client)
    saved = save(client, token).json()

    response = client.get(ENDPOINT, headers=headers(token))

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.json() == saved


def test_repeated_save_updates_the_same_offer_and_draft(client, db):
    _, token = register_and_login(client)
    first = save(client, token).json()

    response = save(client, token, setup_payload(
        service_name="SEO audits",
        outreach_language="en",
        business_category="Independent hotels",
        locations=["Chicago, IL"],
        result_limit_per_location=None,
    ))

    assert response.status_code == 200
    updated = response.json()
    assert updated["offer_profile"]["id"] == first["offer_profile"]["id"]
    assert updated["search_draft"]["id"] == first["search_draft"]["id"]
    assert updated["offer_profile"]["service_name"] == "SEO audits"
    assert updated["search_draft"]["business_category"] == "Independent hotels"
    assert updated["search_draft"]["result_limit_per_location"] is None
    assert [item["location_query"] for item in updated["search_draft"]["locations"]] == [
        "Chicago, IL"
    ]
    assert db.scalar(select(func.count()).select_from(OfferProfile)) == 1
    assert db.scalar(select(func.count()).select_from(SearchDraft)) == 1
    assert db.scalar(select(func.count()).select_from(SearchDraftLocation)) == 1


def test_prospecting_setup_is_isolated_by_authenticated_user(client, db):
    first_user, first_token = register_and_login(client, "first@example.com")
    second_user, second_token = register_and_login(client, "second@example.com")
    save(client, first_token, setup_payload(service_name="First service"))
    save(client, second_token, setup_payload(
        service_name="Second service",
        locations=["Seattle, WA"],
    ))

    first = client.get(
        f"{ENDPOINT}?user_id={second_user['id']}",
        headers=headers(first_token),
    ).json()
    second = client.get(ENDPOINT, headers=headers(second_token)).json()

    assert first["offer_profile"]["service_name"] == "First service"
    assert second["offer_profile"]["service_name"] == "Second service"
    offers = list(db.scalars(select(OfferProfile)))
    assert {str(offer.user_id) for offer in offers} == {
        first_user["id"],
        second_user["id"],
    }


def test_client_cannot_choose_the_setup_owner(client, db):
    first_user, first_token = register_and_login(client, "first@example.com")
    second_user, _ = register_and_login(client, "second@example.com")
    payload = setup_payload(user_id=second_user["id"])

    response = save(client, first_token, payload)

    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"
    assert db.scalar(select(func.count()).select_from(OfferProfile)) == 0
    assert first_user["id"] != second_user["id"]


def test_invalid_setup_is_rejected_without_writes(client, db):
    _, token = register_and_login(client)
    invalid_payloads = [
        setup_payload(service_name="   "),
        setup_payload(outreach_language="not a language"),
        setup_payload(business_category=""),
        setup_payload(locations=[]),
        setup_payload(locations=["Boston", " boston "]),
        setup_payload(locations=[f"Location {index}" for index in range(11)]),
        setup_payload(locations=["x" * 201]),
        setup_payload(result_limit_per_location=0),
        setup_payload(result_limit_per_location=101),
    ]

    for payload in invalid_payloads:
        response = save(client, token, payload)
        assert response.status_code == 422
        assert response.json()["code"] == "validation_error"

    assert db.scalar(select(func.count()).select_from(OfferProfile)) == 0
    assert db.scalar(select(func.count()).select_from(SearchDraft)) == 0
    assert db.scalar(select(func.count()).select_from(SearchDraftLocation)) == 0


def test_deleting_user_cascades_to_all_prospecting_setup_rows(client, db):
    _, token = register_and_login(client)
    assert save(client, token).status_code == 200

    user = db.scalar(select(User).where(User.email == "owner@example.com"))
    db.delete(user)
    db.commit()

    assert db.scalar(select(func.count()).select_from(OfferProfile)) == 0
    assert db.scalar(select(func.count()).select_from(SearchDraft)) == 0
    assert db.scalar(select(func.count()).select_from(SearchDraftLocation)) == 0
