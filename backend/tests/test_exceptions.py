import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    UnauthorizedError,
    register_exception_handlers,
)


@pytest.fixture
def error_client():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/errors/{case}")
    def raise_expected_error(case: str):
        errors = {
            "bad-request": BadRequestError("Bad input"),
            "unauthorized": UnauthorizedError(),
            "forbidden": ForbiddenError(),
            "not-found": NotFoundError(),
            "conflict": ConflictError(),
            "rate-limit": RateLimitError(retry_after=12),
        }
        raise errors[case]

    @app.get("/validation")
    def validate_query(value: int):
        return {"value": value}

    @app.get("/database-error")
    def raise_database_error():
        raise SQLAlchemyError("private database details")

    @app.get("/unexpected-error")
    def raise_unexpected_error():
        raise RuntimeError("private application details")

    with TestClient(app, raise_server_exceptions=False) as client:
        yield client


@pytest.mark.parametrize(
    ("case", "status_code", "code"),
    [
        ("bad-request", 400, "bad_request"),
        ("unauthorized", 401, "unauthorized"),
        ("forbidden", 403, "forbidden"),
        ("not-found", 404, "not_found"),
        ("conflict", 409, "conflict"),
        ("rate-limit", 429, "rate_limited"),
    ],
)
def test_expected_errors_use_the_global_response_contract(
    error_client,
    case,
    status_code,
    code,
):
    response = error_client.get(f"/errors/{case}")

    assert response.status_code == status_code
    assert response.json()["code"] == code
    assert isinstance(response.json()["detail"], str)
    assert response.headers["cache-control"] == "no-store"


def test_authentication_and_rate_limit_headers_are_preserved(error_client):
    unauthorized = error_client.get("/errors/unauthorized")
    rate_limited = error_client.get("/errors/rate-limit")

    assert unauthorized.headers["www-authenticate"] == "Bearer"
    assert rate_limited.headers["retry-after"] == "12"


def test_validation_errors_do_not_echo_submitted_values(error_client):
    response = error_client.get("/validation", params={"value": "private-value"})

    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"
    assert "private-value" not in response.text


def test_framework_http_errors_use_the_same_contract(error_client):
    response = error_client.get("/route-that-does-not-exist")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found", "code": "not_found"}
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.parametrize(
    ("path", "code", "private_detail"),
    [
        ("/database-error", "database_error", "private database details"),
        ("/unexpected-error", "internal_error", "private application details"),
    ],
)
def test_unexpected_errors_hide_internal_details(error_client, path, code, private_detail):
    response = error_client.get(path)

    assert response.status_code == 500
    assert response.json() == {
        "detail": "The request could not be completed",
        "code": code,
    }
    assert private_detail not in response.text
    assert response.headers["cache-control"] == "no-store"
