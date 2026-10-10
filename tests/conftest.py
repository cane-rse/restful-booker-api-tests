import os

import pytest

from api.client import BookingClient

ADMIN_USER = os.getenv("RB_USERNAME", "admin")
ADMIN_PASS = os.getenv("RB_PASSWORD", "password123")  # public demo credentials


@pytest.fixture(scope="session")
def client() -> BookingClient:
    return BookingClient()


@pytest.fixture(scope="session")
def token(client) -> str:
    resp = client.create_token(ADMIN_USER, ADMIN_PASS)
    assert resp.status_code == 200, f"Auth failed: {resp.status_code} {resp.text}"
    value = resp.json().get("token")
    assert value, f"No token in auth response: {resp.text}"
    return value


@pytest.fixture
def booking_payload() -> dict:
    return {
        "firstname": "Courtney",
        "lastname": "Tester",
        "totalprice": 250,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-11-01", "checkout": "2026-11-05"},
        "additionalneeds": "Breakfast",
    }


@pytest.fixture
def created_booking(client, token, booking_payload):
    """Create a booking for a test, then clean it up afterwards."""
    resp = client.create_booking(booking_payload)
    assert resp.status_code == 200, f"Setup failed: {resp.status_code} {resp.text}"
    booking_id = resp.json()["bookingid"]
    yield booking_id
    client.delete_booking(booking_id, token)
