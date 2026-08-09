from pathlib import Path

import pytest

from src.core.rate_limit import limiter


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    limiter.reset()


def create_verified_user(
    client,
    email: str = "profile@example.com",
    password: str = "Test@12345",
    full_name: str = "Profile User",
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

    return response.json()["data"]["access_token"]


def authorization_headers(
    access_token: str,
) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {access_token}",
    }


def test_profile_access_without_token_is_rejected(client):
    response = client.get(
        "/api/v1/users/me",
    )

    assert response.status_code == 401

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Not authenticated"
    assert body["error"]["code"] == "UNAUTHORIZED"


def test_verified_user_can_get_profile(client):
    user = create_verified_user(
        client=client,
        email="getprofile@example.com",
        full_name="Get Profile User",
    )

    access_token = login_user(
        client=client,
        email=user["email"],
        password=user["password"],
    )

    response = client.get(
        "/api/v1/users/me",
        headers=authorization_headers(access_token),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Profile retrieved successfully"

    profile = body["data"]

    assert profile["full_name"] == "Get Profile User"
    assert profile["email"] == "getprofile@example.com"
    assert profile["role"] == "user"
    assert profile["is_active"] is True
    assert profile["profile_image"] is None
    assert profile["created_at"] is not None


def test_user_can_update_profile(client):
    user = create_verified_user(
        client=client,
        email="updateprofile@example.com",
        full_name="Old Profile Name",
    )

    access_token = login_user(
        client=client,
        email=user["email"],
        password=user["password"],
    )

    response = client.put(
        "/api/v1/users/me",
        headers=authorization_headers(access_token),
        json={
            "full_name": "Updated Profile Name",
            "email": "updatedprofile@example.com",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Profile updated successfully"
    assert body["data"]["full_name"] == "Updated Profile Name"
    assert body["data"]["email"] == "updatedprofile@example.com"

    login_response = client.post(
        "/api/v1/users/login",
        json={
            "email": "updatedprofile@example.com",
            "password": user["password"],
        },
    )

    assert login_response.status_code == 200


def test_profile_update_rejects_duplicate_email(client):
    first_user = create_verified_user(
        client=client,
        email="firstprofile@example.com",
        full_name="First User",
    )

    create_verified_user(
        client=client,
        email="secondprofile@example.com",
        full_name="Second User",
    )

    access_token = login_user(
        client=client,
        email=first_user["email"],
        password=first_user["password"],
    )

    response = client.put(
        "/api/v1/users/me",
        headers=authorization_headers(access_token),
        json={
            "full_name": "First User",
            "email": "secondprofile@example.com",
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Email already registered"


def test_wrong_current_password_is_rejected(client):
    user = create_verified_user(
        client=client,
        email="wrongcurrent@example.com",
    )

    access_token = login_user(
        client=client,
        email=user["email"],
        password=user["password"],
    )

    response = client.put(
        "/api/v1/users/me/password",
        headers=authorization_headers(access_token),
        json={
            "current_password": "WrongPassword@123",
            "new_password": "NewTest@12345",
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Current password is incorrect"


def test_user_can_change_password(client):
    old_password = "OldTest@12345"
    new_password = "NewTest@12345"

    user = create_verified_user(
        client=client,
        email="changepassword@example.com",
        password=old_password,
    )

    access_token = login_user(
        client=client,
        email=user["email"],
        password=old_password,
    )

    change_response = client.put(
        "/api/v1/users/me/password",
        headers=authorization_headers(access_token),
        json={
            "current_password": old_password,
            "new_password": new_password,
        },
    )

    assert change_response.status_code == 200

    change_body = change_response.json()

    assert change_body["success"] is True
    assert change_body["message"] == "Password changed successfully"
    assert change_body["data"] is None

    old_login_response = client.post(
        "/api/v1/users/login",
        json={
            "email": user["email"],
            "password": old_password,
        },
    )

    assert old_login_response.status_code == 401

    new_login_response = client.post(
        "/api/v1/users/login",
        json={
            "email": user["email"],
            "password": new_password,
        },
    )

    assert new_login_response.status_code == 200


def test_same_password_change_is_rejected(client):
    password = "SameTest@12345"

    user = create_verified_user(
        client=client,
        email="samepassword@example.com",
        password=password,
    )

    access_token = login_user(
        client=client,
        email=user["email"],
        password=password,
    )

    response = client.put(
        "/api/v1/users/me/password",
        headers=authorization_headers(access_token),
        json={
            "current_password": password,
            "new_password": password,
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["success"] is False
    assert body["message"] == (
        "New password must be different " "from current password"
    )


def test_invalid_profile_image_type_is_rejected(client):
    user = create_verified_user(
        client=client,
        email="invalidimage@example.com",
    )

    access_token = login_user(
        client=client,
        email=user["email"],
        password=user["password"],
    )

    response = client.post(
        "/api/v1/users/me/profile-image",
        headers=authorization_headers(access_token),
        files={
            "image": (
                "profile.txt",
                b"This is not an image",
                "text/plain",
            ),
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Only JPG, PNG, and WEBP images are allowed"


def test_user_can_upload_profile_image(client):
    user = create_verified_user(
        client=client,
        email="uploadimage@example.com",
    )

    access_token = login_user(
        client=client,
        email=user["email"],
        password=user["password"],
    )

    png_content = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01"
        b"\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00"
        b"\x90wS\xde"
        b"\x00\x00\x00\x0cIDAT"
        b"\x08\xd7c\xf8\xcf\xc0\x00\x00"
        b"\x03\x01\x01\x00"
        b"\x18\xdd\x8d\xb4"
        b"\x00\x00\x00\x00IEND"
        b"\xaeB`\x82"
    )

    response = client.post(
        "/api/v1/users/me/profile-image",
        headers=authorization_headers(access_token),
        files={
            "image": (
                "profile.png",
                png_content,
                "image/png",
            ),
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Profile image updated successfully"

    profile_image = body["data"]["profile_image"]

    assert profile_image is not None
    assert profile_image.startswith("/uploads/profile_images/")
    assert profile_image.endswith(".png")

    project_root = Path(__file__).resolve().parent.parent

    saved_image_path = project_root / profile_image.lstrip("/")

    assert saved_image_path.exists()

    saved_image_path.unlink()
