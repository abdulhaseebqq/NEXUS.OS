import pytest

from src.core.rate_limit import limiter


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    limiter.reset()


def create_verified_user(
    client,
    email: str,
    password: str = "Test@12345",
    full_name: str = "Session Test User",
):
    signup_response = client.post(
        "/api/v1/users/signup",
        json={
            "full_name": full_name,
            "email": email,
            "password": password,
        },
    )

    assert signup_response.status_code == 201

    verification_token = signup_response.json()["data"]["verification"]["token"]

    verify_response = client.post(
        "/api/v1/users/verify-email",
        json={
            "token": verification_token,
        },
    )

    assert verify_response.status_code == 200

    return {
        "email": email,
        "password": password,
        "full_name": full_name,
    }


def login_user(
    client,
    email: str,
    password: str,
):
    response = client.post(
        "/api/v1/users/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    return response.json()["data"]


def authorization_headers(
    access_token: str,
) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {access_token}",
    }


def test_sessions_access_without_token_is_rejected(client):
    response = client.get(
        "/api/v1/users/me/sessions",
    )

    assert response.status_code == 401

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Not authenticated"
    assert body["error"]["code"] == "UNAUTHORIZED"


def test_user_can_list_active_sessions(client):
    user = create_verified_user(
        client=client,
        email="listsessions@example.com",
    )

    login_data = login_user(
        client=client,
        email=user["email"],
        password=user["password"],
    )

    response = client.get(
        "/api/v1/users/me/sessions",
        headers=authorization_headers(login_data["access_token"]),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Active sessions retrieved successfully"

    sessions = body["data"]

    assert isinstance(sessions, list)
    assert len(sessions) == 1

    session = sessions[0]

    assert session["id"] == login_data["session"]["id"]
    assert session["is_active"] is True
    assert session["device_name"] is not None
    assert session["ip_address"] is not None
    assert session["created_at"] is not None
    assert session["last_activity"] is not None
    assert session["logged_out_at"] is None


def test_multiple_logins_create_multiple_sessions(client):
    user = create_verified_user(
        client=client,
        email="multiplesessions@example.com",
    )

    first_login = login_user(
        client=client,
        email=user["email"],
        password=user["password"],
    )

    second_login = login_user(
        client=client,
        email=user["email"],
        password=user["password"],
    )

    response = client.get(
        "/api/v1/users/me/sessions",
        headers=authorization_headers(second_login["access_token"]),
    )

    assert response.status_code == 200

    sessions = response.json()["data"]

    assert len(sessions) == 2

    session_ids = {session["id"] for session in sessions}

    assert first_login["session"]["id"] in session_ids
    assert second_login["session"]["id"] in session_ids


def test_user_can_close_single_session(client):
    user = create_verified_user(
        client=client,
        email="closesession@example.com",
    )

    login_data = login_user(
        client=client,
        email=user["email"],
        password=user["password"],
    )

    session_id = login_data["session"]["id"]

    response = client.delete(
        f"/api/v1/users/me/sessions/{session_id}",
        headers=authorization_headers(login_data["access_token"]),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Session closed successfully"
    assert body["data"]["session_id"] == session_id
    assert body["data"]["logged_out_at"] is not None

    sessions_response = client.get(
        "/api/v1/users/me/sessions",
        headers=authorization_headers(login_data["access_token"]),
    )

    assert sessions_response.status_code == 200
    assert sessions_response.json()["data"] == []


def test_closed_session_refresh_token_is_rejected(client):
    user = create_verified_user(
        client=client,
        email="closedrefresh@example.com",
    )

    login_data = login_user(
        client=client,
        email=user["email"],
        password=user["password"],
    )

    session_id = login_data["session"]["id"]

    close_response = client.delete(
        f"/api/v1/users/me/sessions/{session_id}",
        headers=authorization_headers(login_data["access_token"]),
    )

    assert close_response.status_code == 200

    refresh_response = client.post(
        "/api/v1/users/refresh",
        json={
            "refresh_token": login_data["refresh_token"],
        },
    )

    assert refresh_response.status_code == 401

    body = refresh_response.json()

    assert body["success"] is False
    assert body["message"] == "Refresh token has been revoked"


def test_user_cannot_close_another_users_session(client):
    first_user = create_verified_user(
        client=client,
        email="sessionowner@example.com",
        full_name="Session Owner",
    )

    second_user = create_verified_user(
        client=client,
        email="sessionattacker@example.com",
        full_name="Second User",
    )

    first_login = login_user(
        client=client,
        email=first_user["email"],
        password=first_user["password"],
    )

    second_login = login_user(
        client=client,
        email=second_user["email"],
        password=second_user["password"],
    )

    first_session_id = first_login["session"]["id"]

    response = client.delete(
        f"/api/v1/users/me/sessions/{first_session_id}",
        headers=authorization_headers(second_login["access_token"]),
    )

    assert response.status_code == 403

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "You cannot manage another user's session"


def test_closing_inactive_session_is_rejected(client):
    user = create_verified_user(
        client=client,
        email="inactiveclose@example.com",
    )

    login_data = login_user(
        client=client,
        email=user["email"],
        password=user["password"],
    )

    session_id = login_data["session"]["id"]

    first_response = client.delete(
        f"/api/v1/users/me/sessions/{session_id}",
        headers=authorization_headers(login_data["access_token"]),
    )

    assert first_response.status_code == 200

    second_response = client.delete(
        f"/api/v1/users/me/sessions/{session_id}",
        headers=authorization_headers(login_data["access_token"]),
    )

    assert second_response.status_code == 400

    body = second_response.json()

    assert body["success"] is False
    assert body["message"] == "Session is already inactive"


def test_unknown_session_is_rejected(client):
    user = create_verified_user(
        client=client,
        email="unknownsession@example.com",
    )

    login_data = login_user(
        client=client,
        email=user["email"],
        password=user["password"],
    )

    response = client.delete(
        "/api/v1/users/me/sessions/999999",
        headers=authorization_headers(login_data["access_token"]),
    )

    assert response.status_code == 404

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Session not found"


def test_user_can_close_all_sessions(client):
    user = create_verified_user(
        client=client,
        email="closeallsessions@example.com",
    )

    first_login = login_user(
        client=client,
        email=user["email"],
        password=user["password"],
    )

    second_login = login_user(
        client=client,
        email=user["email"],
        password=user["password"],
    )

    response = client.delete(
        "/api/v1/users/me/sessions",
        headers=authorization_headers(second_login["access_token"]),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "All sessions closed successfully"
    assert body["data"]["closed_sessions"] == 2
    assert body["data"]["revoked_tokens"] == 2

    sessions_response = client.get(
        "/api/v1/users/me/sessions",
        headers=authorization_headers(second_login["access_token"]),
    )

    assert sessions_response.status_code == 200
    assert sessions_response.json()["data"] == []

    first_refresh_response = client.post(
        "/api/v1/users/refresh",
        json={
            "refresh_token": first_login["refresh_token"],
        },
    )

    second_refresh_response = client.post(
        "/api/v1/users/refresh",
        json={
            "refresh_token": second_login["refresh_token"],
        },
    )

    assert first_refresh_response.status_code == 401
    assert second_refresh_response.status_code == 401


def test_close_all_with_no_active_sessions_is_rejected(client):
    user = create_verified_user(
        client=client,
        email="noactivesessions@example.com",
    )

    login_data = login_user(
        client=client,
        email=user["email"],
        password=user["password"],
    )

    first_response = client.delete(
        "/api/v1/users/me/sessions",
        headers=authorization_headers(login_data["access_token"]),
    )

    assert first_response.status_code == 200

    second_response = client.delete(
        "/api/v1/users/me/sessions",
        headers=authorization_headers(login_data["access_token"]),
    )

    assert second_response.status_code == 404

    body = second_response.json()

    assert body["success"] is False
    assert body["message"] == "No active sessions found"
