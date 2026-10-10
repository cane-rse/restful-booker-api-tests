"""Thin wrapper around the Restful-booker API.

Keeping HTTP details in one place means the tests read like test cases
instead of request plumbing.
"""
import os

import requests

BASE_URL = os.getenv("BASE_URL", "https://restful-booker.herokuapp.com")
TIMEOUT = 15


class BookingClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    # --- auth -------------------------------------------------------------
    def create_token(self, username: str, password: str) -> requests.Response:
        return self.session.post(
            self._url("/auth"),
            json={"username": username, "password": password},
            timeout=TIMEOUT,
        )

    # --- bookings ---------------------------------------------------------
    def list_bookings(self, **filters) -> requests.Response:
        return self.session.get(self._url("/booking"), params=filters, timeout=TIMEOUT)

    def get_booking(self, booking_id) -> requests.Response:
        return self.session.get(self._url(f"/booking/{booking_id}"), timeout=TIMEOUT)

    def create_booking(self, payload: dict) -> requests.Response:
        return self.session.post(self._url("/booking"), json=payload, timeout=TIMEOUT)

    def update_booking(self, booking_id, payload: dict, token: str | None = None) -> requests.Response:
        return self.session.put(
            self._url(f"/booking/{booking_id}"),
            json=payload,
            headers=self._auth_header(token),
            timeout=TIMEOUT,
        )

    def partial_update_booking(self, booking_id, payload: dict, token: str | None = None) -> requests.Response:
        return self.session.patch(
            self._url(f"/booking/{booking_id}"),
            json=payload,
            headers=self._auth_header(token),
            timeout=TIMEOUT,
        )

    def delete_booking(self, booking_id, token: str | None = None) -> requests.Response:
        return self.session.delete(
            self._url(f"/booking/{booking_id}"),
            headers=self._auth_header(token),
            timeout=TIMEOUT,
        )

    def ping(self) -> requests.Response:
        return self.session.get(self._url("/ping"), timeout=TIMEOUT)

    @staticmethod
    def _auth_header(token: str | None) -> dict:
        return {"Cookie": f"token={token}"} if token else {}
