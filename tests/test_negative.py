import pytest


@pytest.mark.negative
def test_get_nonexistent_booking_returns_404(client):
    resp = client.get_booking(99999999)

    assert resp.status_code == 404


@pytest.mark.negative
def test_update_without_token_is_forbidden(client, created_booking, booking_payload):
    resp = client.update_booking(created_booking, booking_payload, token=None)

    assert resp.status_code == 403


@pytest.mark.negative
def test_update_with_invalid_token_is_forbidden(client, created_booking, booking_payload):
    resp = client.update_booking(created_booking, booking_payload, token="not-a-real-token")

    assert resp.status_code == 403


@pytest.mark.negative
def test_delete_without_token_is_forbidden(client, created_booking):
    resp = client.delete_booking(created_booking, token=None)

    assert resp.status_code == 403
    assert client.get_booking(created_booking).status_code == 200  # still there


@pytest.mark.negative
@pytest.mark.known_issue
@pytest.mark.xfail(reason="Known API defect: invalid input is not rejected with a 4xx", strict=False)
@pytest.mark.parametrize(
    "missing_field", ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"]
)
def test_create_booking_missing_required_field_is_rejected(client, booking_payload, missing_field):
    """A tester would expect a 4xx. Restful-booker is known to return 500 here."""
    payload = {k: v for k, v in booking_payload.items() if k != missing_field}

    resp = client.create_booking(payload)

    assert 400 <= resp.status_code < 500, f"Expected 4xx, got {resp.status_code}"


@pytest.mark.negative
@pytest.mark.known_issue
@pytest.mark.xfail(reason="Known API defect: invalid input is not rejected with a 4xx", strict=False)
def test_create_booking_with_wrong_types_is_rejected(client, booking_payload):
    payload = {**booking_payload, "totalprice": "not-a-number", "depositpaid": "maybe"}

    resp = client.create_booking(payload)

    assert 400 <= resp.status_code < 500, f"Expected 4xx, got {resp.status_code}"


@pytest.mark.negative
@pytest.mark.known_issue
@pytest.mark.xfail(reason="Known API defect: invalid input is not rejected with a 4xx", strict=False)
def test_checkout_before_checkin_is_rejected(client, booking_payload):
    payload = {
        **booking_payload,
        "bookingdates": {"checkin": "2026-11-10", "checkout": "2026-11-01"},
    }

    resp = client.create_booking(payload)

    assert 400 <= resp.status_code < 500, f"Expected 4xx, got {resp.status_code}"


@pytest.mark.negative
@pytest.mark.known_issue
@pytest.mark.xfail(reason="Known API defect: invalid input is not rejected with a 4xx", strict=False)
def test_negative_total_price_is_rejected(client, booking_payload):
    payload = {**booking_payload, "totalprice": -50}

    resp = client.create_booking(payload)

    assert 400 <= resp.status_code < 500, f"Expected 4xx, got {resp.status_code}"
