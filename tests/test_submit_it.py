from fastapi import status
from algobio.auth.security import get_current_user
from algobio.model.domain import User
from main import app


def test_unauthorized_submission(client, test_engine):
    payload = {
        "source_code": "print('hello')",
        "language_id": "python",
        "problem_id": "ce94202d-48ab-4d7c-b5b4-35ac31ece4eb",
    }
    response = client.post("/submit", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text


def test_correct_submission(client, test_engine):
    payload = {
        "source_code": "print('hello')",
        "language_id": "python",
        "problem_id": "ce94202d-48ab-4d7c-b5b4-35ac31ece4eb",
    }

    app.dependency_overrides[get_current_user] = lambda: User(
        id="1b2b8c9d-8f3e-4b7a-9a4c-5d6e7f8a9b0c", email="test@test.com", username="test"
    )

    # WHEN
    response = client.post("/submit", json=payload)

    app.dependency_overrides.pop(get_current_user, None)

    # THEN
    assert response.status_code == status.HTTP_201_CREATED, (
        f"Expected {status.HTTP_201_CREATED}, got {response.status_code}:{response.text}"
    )

    body = response.json()
    assert "id" in body, (
        f"Response is missing the 'id' key, body: {body}"
    )


def test_incorrect_input_data(client, test_engine):
    # GIVEN
    payload = {
        "source_code": "print('hello')",
        "language_id": 25,
        "problem_id": "ce94202d-48ab-4d7c-b5b4-35ac31ece4eb",
    }

    app.dependency_overrides[get_current_user] = lambda: User(
        id="1b2b8c9d-8f3e-4b7a-9a4c-5d6e7f8a9b0c", email="test@test.com", username="test"
    )

    # WHEN
    response = client.post("/submit", json=payload)

    app.dependency_overrides.pop(get_current_user, None)

    # THEN
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, (
        f"Expected {status.HTTP_422_UNPROCESSABLE_CONTENT}, got {response.status_code}:{response.text}"
    )
