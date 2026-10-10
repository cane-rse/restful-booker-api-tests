import pytest
from jsonschema import validate

from api.schemas import TOKEN_SCHEMA


@pytest.mark.smoke
def test_api_is_up(client):
    resp = client.ping()
    assert resp.status_code == 201  # Restful-booker returns 201 "Created" on /ping


@pytest.mark.smoke
@pytest.mark.schema
def test_valid_credentials_return_token(client):
    resp = client.create_token("admin", "password123")

    assert resp.status_code == 200
    validate(instance=resp.json(), schema=TOKEN_SCHEMA)


@pytest.mark.negative
@pytest.mark.known_issue
def test_invalid_credentials_do_not_return_token(client):
    """Known quirk: the API answers 200 with a 'reason' field instead of 401."""
    resp = client.create_token("admin", "wrong-password")

    body = resp.json()
    assert "token" not in body
    assert body.get("reason") == "Bad credentials"


@pytest.mark.negative
@pytest.mark.parametrize(
    "username,password",
    [
        ("", ""),
        ("admin", ""),
        ("", "password123"),
        ("not-a-user", "password123"),
    ],
    ids=["both-empty", "empty-password", "empty-username", "unknown-user"],
)
def test_bad_login_combinations_never_return_token(client, username, password):
    resp = client.create_token(username, password)

    assert "token" not in resp.json()
