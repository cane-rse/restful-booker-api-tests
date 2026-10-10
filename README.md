# Restful-booker API Test Suite

![API Tests](https://github.com/cane-rse/restful-booker-api-tests/actions/workflows/tests.yml/badge.svg)

Automated and manual-style API tests for [Restful-booker](https://restful-booker.herokuapp.com/), a public practice API built for testers. The suite covers authentication, full booking CRUD, negative cases, and response schema validation, and it documents real defects found in the API.

## What's tested

| Area | Examples | Where |
|------|----------|-------|
| Smoke | API is up, token issued, booking created and fetched | `tests/` (`-m smoke`) |
| Auth | Valid login, bad credentials, empty and unknown users | `tests/test_auth.py` |
| CRUD | Create, read, list, filter, full update, partial update, delete | `tests/test_booking_crud.py` |
| Negative | Missing token, invalid token, missing fields, wrong types, bad dates | `tests/test_negative.py` |
| Contract | JSON Schema validation of every response shape | `api/schemas.py` |
| Postman | Same flow as a collection with assertions, run by Newman in CI | `postman/` |

## Findings

Tests tagged `known_issue` document behavior a tester would flag as a defect. They are marked `xfail`, so CI stays meaningful while the defects stay visible in the report.

| # | Finding | Expected | Actual (observed on the practice API) |
|---|---------|----------|----------------------------------------|
| 1 | Invalid login | 401 Unauthorized | 200 OK with `{"reason": "Bad credentials"}` |
| 2 | Missing required field on create | 400 Bad Request | Server error or unvalidated response |
| 3 | Check-out date before check-in | 400 Bad Request | Accepted |
| 4 | Negative total price | 400 Bad Request | Accepted |
| 5 | DELETE success | 200 or 204 | 201 Created |

> Confirm each row against your own run before you publish it, and turn each into a proper bug report (steps to reproduce, expected vs. actual, severity). The `XFAIL` and `XPASS` lines in the pytest summary show you which rows still hold.

## Tech stack

Python 3.12, pytest, requests, jsonschema, pytest-html, Postman, Newman, GitHub Actions.

## Project structure

```
api/
  client.py          # API wrapper, keeps HTTP details out of the tests
  schemas.py         # JSON Schemas for contract checks
tests/
  conftest.py        # fixtures: client, auth token, booking with cleanup
  test_auth.py
  test_booking_crud.py
  test_negative.py
postman/
  restful-booker.postman_collection.json
.github/workflows/tests.yml
pytest.ini           # markers: smoke, regression, negative, schema, known_issue
```

## Run it locally

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest --html=reports/report.html --self-contained-html
```

Useful variations:

```bash
pytest -m smoke                 # quick sanity check
pytest -m "negative"            # only negative tests
pytest -m "not known_issue"     # skip documented defects
BASE_URL=https://example.test pytest   # point at another environment
```

Postman: import `postman/restful-booker.postman_collection.json`, or run `npx newman run postman/restful-booker.postman_collection.json`.

## Design decisions

- **Client wrapper:** tests describe behavior, not request plumbing.
- **Fixtures with cleanup:** every test creates its own booking and removes it, so tests stay independent and the shared practice API stays tidy.
- **Markers:** you can run the suite by purpose (smoke, regression, negative) instead of by file.
- **Known issues as `xfail`:** expected defects don't break the build, and a fix shows up as `XPASS`.
- **CI:** runs on every push and pull request, plus weekly, and uploads HTML reports as build artifacts.

## Notes

Restful-booker is a shared practice site that resets periodically, so a failure can come from the service rather than the tests. Rerun before assuming a regression.
