import pytest

from src.core.rate_limit import limiter


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    limiter.reset()


def signup_user(
    client,
    email: str,
    password: str = "Test@12345",
    full_name: str = "Test User",
):
    return client.post(
        "/api/v1/users/signup",
        json={
            "full_name": full_name,
            "email": email,
            "password": password,
        },
    )


def verify_signup_email(
    client,
    signup_response,
):
    signup_body = signup_response.json()

    verification_token = signup_body["data"]["verification"]["token"]

    return client.post(
        "/api/v1/users/verify-email",
        json={
            "token": verification_token,
        },
    )


def test_signup_success(client):
    response = signup_user(
        client=client,
        email="signup@example.com",
    )

    assert response.status_code == 201

    body = response.json()

    assert body["success"] is True
    assert body["message"] == (
        "User account created successfully. " "Please verify your email."
    )

    assert body["data"]["email"] == "signup@example.com"
    assert body["data"]["role"] == "user"
    assert body["data"]["is_active"] is True
    assert body["data"]["is_email_verified"] is False

    verification = body["data"]["verification"]

    assert verification["token"] is not None
    assert len(verification["token"]) >= 32
    assert verification["expires_at"] is not None


def test_duplicate_signup_is_rejected(client):
    signup_user(
        client=client,
        email="duplicate@example.com",
    )

    response = signup_user(
        client=client,
        email="duplicate@example.com",
    )

    assert response.status_code == 400

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Email already registered"
    assert body["error"]["code"] == "HTTP_ERROR"


def test_unverified_user_cannot_login(client):
    signup_user(
        client=client,
        email="unverified@example.com",
    )

    response = client.post(
        "/api/v1/users/login",
        json={
            "email": "unverified@example.com",
            "password": "Test@12345",
        },
    )

    assert response.status_code == 403

    body = response.json()

    assert body["success"] is False
    assert "not verified" in body["message"].lower()


def test_email_verification_success(client):
    signup_response = signup_user(
        client=client,
        email="verify@example.com",
    )

    response = verify_signup_email(
        client=client,
        signup_response=signup_response,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Email verified successfully"
    assert body["data"]["email"] == "verify@example.com"
    assert body["data"]["is_email_verified"] is True


def test_verified_user_can_login(client):
    signup_response = signup_user(
        client=client,
        email="login@example.com",
    )

    verify_response = verify_signup_email(
        client=client,
        signup_response=signup_response,
    )

    assert verify_response.status_code == 200

    login_response = client.post(
        "/api/v1/users/login",
        json={
            "email": "login@example.com",
            "password": "Test@12345",
        },
    )

    assert login_response.status_code == 200

    body = login_response.json()

    assert body["success"] is True
    assert body["message"] == "Login successful"

    assert body["data"]["access_token"] is not None
    assert body["data"]["refresh_token"] is not None
    assert body["data"]["token_type"] == "bearer"

    user = body["data"]["user"]

    assert user["email"] == "login@example.com"
    assert user["is_email_verified"] is True

    session = body["data"]["session"]

    assert session["id"] is not None
    assert session["device_name"] is not None
    assert session["ip_address"] is not None


def test_invalid_login_password_is_rejected(client):
    signup_response = signup_user(
        client=client,
        email="wrongpassword@example.com",
    )

    verify_signup_email(
        client=client,
        signup_response=signup_response,
    )

    response = client.post(
        "/api/v1/users/login",
        json={
            "email": "wrongpassword@example.com",
            "password": "WrongPassword@123",
        },
    )

    assert response.status_code == 401

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Invalid email or password"


def test_forgot_password_generates_reset_token(client):
    signup_response = signup_user(
        client=client,
        email="forgot@example.com",
    )

    verify_signup_email(
        client=client,
        signup_response=signup_response,
    )

    response = client.post(
        "/api/v1/users/forgot-password",
        json={
            "email": "forgot@example.com",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == (
        "If an account exists for this email, "
        "password reset instructions have been generated."
    )

    assert body["data"]["email"] == "forgot@example.com"

    reset_data = body["data"]["reset"]

    assert reset_data["token"] is not None
    assert len(reset_data["token"]) >= 32
    assert reset_data["expires_at"] is not None


def test_forgot_password_hides_unknown_email(client):
    response = client.post(
        "/api/v1/users/forgot-password",
        json={
            "email": "unknown@example.com",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["data"] is None


def test_password_reset_success(client):
    old_password = "OldTest@12345"
    new_password = "NewTest@12345"

    signup_response = signup_user(
        client=client,
        email="reset@example.com",
        password=old_password,
    )

    verify_signup_email(
        client=client,
        signup_response=signup_response,
    )

    forgot_response = client.post(
        "/api/v1/users/forgot-password",
        json={
            "email": "reset@example.com",
        },
    )

    assert forgot_response.status_code == 200

    reset_token = forgot_response.json()["data"]["reset"]["token"]

    reset_response = client.post(
        "/api/v1/users/reset-password",
        json={
            "token": reset_token,
            "new_password": new_password,
        },
    )

    assert reset_response.status_code == 200

    reset_body = reset_response.json()

    assert reset_body["success"] is True
    assert reset_body["message"] == "Password reset successfully"
    assert reset_body["data"]["email"] == "reset@example.com"

    old_login_response = client.post(
        "/api/v1/users/login",
        json={
            "email": "reset@example.com",
            "password": old_password,
        },
    )

    assert old_login_response.status_code == 401

    new_login_response = client.post(
        "/api/v1/users/login",
        json={
            "email": "reset@example.com",
            "password": new_password,
        },
    )

    assert new_login_response.status_code == 200


def test_password_reset_token_is_single_use(client):
    signup_response = signup_user(
        client=client,
        email="singleuse@example.com",
        password="OldTest@12345",
    )

    verify_signup_email(
        client=client,
        signup_response=signup_response,
    )

    forgot_response = client.post(
        "/api/v1/users/forgot-password",
        json={
            "email": "singleuse@example.com",
        },
    )

    assert forgot_response.status_code == 200

    reset_token = forgot_response.json()["data"]["reset"]["token"]

    first_response = client.post(
        "/api/v1/users/reset-password",
        json={
            "token": reset_token,
            "new_password": "FirstNew@12345",
        },
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/api/v1/users/reset-password",
        json={
            "token": reset_token,
            "new_password": "SecondNew@12345",
        },
    )

    assert second_response.status_code == 400

    body = second_response.json()

    assert body["success"] is False
    assert body["message"] == "Invalid password reset token"


def test_invalid_reset_token_is_rejected(client):
    response = client.post(
        "/api/v1/users/reset-password",
        json={
            "token": ("invalid-reset-token-value-" "12345678901234567890"),
            "new_password": "NewTest@12345",
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Invalid password reset token"
