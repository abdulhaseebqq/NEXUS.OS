import pytest

from src.core.rate_limit import limiter
from src.database.models import User
from tests.conftest import TestingSessionLocal


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    limiter.reset()


def create_verified_user(
    client,
    email: str,
    password: str = "Test@12345",
    full_name: str = "Admin Test User",
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

    signup_body = signup_response.json()

    verification_token = signup_body["data"]["verification"]["token"]

    verify_response = client.post(
        "/api/v1/users/verify-email",
        json={
            "token": verification_token,
        },
    )

    assert verify_response.status_code == 200

    return {
        "id": signup_body["data"]["id"],
        "email": email,
        "password": password,
        "full_name": full_name,
    }


def set_user_role(
    email: str,
    role: str,
):
    db = TestingSessionLocal()

    try:
        user = db.query(User).filter(User.email == email).first()

        assert user is not None

        user.role = role

        db.commit()
        db.refresh(user)

        return user.id
    finally:
        db.close()


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


def create_admin_user(
    client,
    email: str = "admin@example.com",
):
    user = create_verified_user(
        client=client,
        email=email,
        full_name="Admin User",
    )

    set_user_role(
        email=user["email"],
        role="admin",
    )

    login_data = login_user(
        client=client,
        email=user["email"],
        password=user["password"],
    )

    return user, login_data


def create_super_admin_user(
    client,
    email: str = "superadmin@example.com",
):
    user = create_verified_user(
        client=client,
        email=email,
        full_name="Super Admin User",
    )

    set_user_role(
        email=user["email"],
        role="super_admin",
    )

    login_data = login_user(
        client=client,
        email=user["email"],
        password=user["password"],
    )

    return user, login_data


def test_admin_dashboard_requires_authentication(client):
    response = client.get(
        "/api/v1/admin/dashboard",
    )

    assert response.status_code == 401

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Not authenticated"
    assert body["error"]["code"] == "HTTP_ERROR"


def test_normal_user_cannot_access_admin_dashboard(client):
    user = create_verified_user(
        client=client,
        email="normaluser@example.com",
    )

    login_data = login_user(
        client=client,
        email=user["email"],
        password=user["password"],
    )

    response = client.get(
        "/api/v1/admin/dashboard",
        headers=authorization_headers(login_data["access_token"]),
    )

    assert response.status_code == 403

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Admin permission required"


def test_admin_can_access_dashboard(client):
    admin_user, login_data = create_admin_user(
        client=client,
        email="dashboardadmin@example.com",
    )

    create_verified_user(
        client=client,
        email="dashboardmember@example.com",
    )

    response = client.get(
        "/api/v1/admin/dashboard",
        headers=authorization_headers(login_data["access_token"]),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Admin dashboard retrieved successfully"

    current_user = body["data"]["current_user"]

    assert current_user["email"] == admin_user["email"]
    assert current_user["role"] == "admin"

    statistics = body["data"]["statistics"]

    assert statistics["total_users"] == 2
    assert statistics["active_users"] == 2
    assert statistics["inactive_users"] == 0


def test_admin_can_list_users(client):
    _, login_data = create_admin_user(
        client=client,
        email="listadmin@example.com",
    )

    create_verified_user(
        client=client,
        email="listeduser@example.com",
        full_name="Listed User",
    )

    response = client.get(
        "/api/v1/admin/users",
        headers=authorization_headers(login_data["access_token"]),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Users retrieved successfully"
    assert len(body["data"]) == 2

    emails = {user["email"] for user in body["data"]}

    assert "listadmin@example.com" in emails
    assert "listeduser@example.com" in emails


def test_admin_can_get_user_details(client):
    _, login_data = create_admin_user(
        client=client,
        email="detailsadmin@example.com",
    )

    target_user = create_verified_user(
        client=client,
        email="detailsuser@example.com",
        full_name="Details User",
    )

    response = client.get(
        f"/api/v1/admin/users/{target_user['id']}",
        headers=authorization_headers(login_data["access_token"]),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "User details retrieved successfully"
    assert body["data"]["id"] == target_user["id"]
    assert body["data"]["email"] == target_user["email"]
    assert body["data"]["full_name"] == "Details User"


def test_unknown_user_details_are_rejected(client):
    _, login_data = create_admin_user(
        client=client,
        email="unknownadmin@example.com",
    )

    response = client.get(
        "/api/v1/admin/users/999999",
        headers=authorization_headers(login_data["access_token"]),
    )

    assert response.status_code == 404

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "User not found"


def test_admin_can_view_activity_logs(client):
    _, login_data = create_admin_user(
        client=client,
        email="logsadmin@example.com",
    )

    create_verified_user(
        client=client,
        email="logsuser@example.com",
    )

    response = client.get(
        "/api/v1/admin/activity-logs",
        headers=authorization_headers(login_data["access_token"]),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Activity logs retrieved successfully"

    assert isinstance(body["data"], list)
    assert len(body["data"]) > 0

    actions = {log["action"] for log in body["data"]}

    assert "SIGNUP" in actions
    assert "EMAIL_VERIFIED" in actions


def test_admin_can_view_specific_user_logs(client):
    _, login_data = create_admin_user(
        client=client,
        email="userlogsadmin@example.com",
    )

    target_user = create_verified_user(
        client=client,
        email="specificlogs@example.com",
    )

    response = client.get(
        ("/api/v1/admin/activity-logs/" f"{target_user['email']}"),
        headers=authorization_headers(login_data["access_token"]),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "User activity logs retrieved successfully"
    assert body["data"]["user_email"] == target_user["email"]
    assert len(body["data"]["logs"]) >= 2


def test_admin_cannot_change_user_role(client):
    _, admin_login = create_admin_user(
        client=client,
        email="limitedadmin@example.com",
    )

    target_user = create_verified_user(
        client=client,
        email="roleuser@example.com",
    )

    response = client.put(
        (f"/api/v1/admin/users/" f"{target_user['id']}/role"),
        headers=authorization_headers(admin_login["access_token"]),
        json={
            "role": "admin",
        },
    )

    assert response.status_code == 403

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Super admin permission required"


def test_super_admin_can_change_user_role(client):
    _, super_admin_login = create_super_admin_user(
        client=client,
        email="rolesuperadmin@example.com",
    )

    target_user = create_verified_user(
        client=client,
        email="promoteduser@example.com",
    )

    response = client.put(
        (f"/api/v1/admin/users/" f"{target_user['id']}/role"),
        headers=authorization_headers(super_admin_login["access_token"]),
        json={
            "role": "admin",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "User role updated successfully"
    assert body["data"]["previous_role"] == "user"
    assert body["data"]["user"]["role"] == "admin"


def test_super_admin_cannot_change_own_role(client):
    super_admin_user, login_data = create_super_admin_user(
        client=client,
        email="selfrolesuperadmin@example.com",
    )

    response = client.put(
        (f"/api/v1/admin/users/" f"{super_admin_user['id']}/role"),
        headers=authorization_headers(login_data["access_token"]),
        json={
            "role": "admin",
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "You cannot change your own role"


def test_invalid_role_is_rejected(client):
    _, super_admin_login = create_super_admin_user(
        client=client,
        email="invalidrolesuperadmin@example.com",
    )

    target_user = create_verified_user(
        client=client,
        email="invalidroleuser@example.com",
    )

    response = client.put(
        (f"/api/v1/admin/users/" f"{target_user['id']}/role"),
        headers=authorization_headers(super_admin_login["access_token"]),
        json={
            "role": "owner",
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Invalid role"


def test_super_admin_can_deactivate_user(client):
    _, super_admin_login = create_super_admin_user(
        client=client,
        email="statussuperadmin@example.com",
    )

    target_user = create_verified_user(
        client=client,
        email="statususer@example.com",
    )

    response = client.put(
        (f"/api/v1/admin/users/" f"{target_user['id']}/status"),
        headers=authorization_headers(super_admin_login["access_token"]),
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "User account status updated successfully"
    assert body["data"]["previous_is_active"] is True
    assert body["data"]["user"]["is_active"] is False

    login_response = client.post(
        "/api/v1/users/login",
        json={
            "email": target_user["email"],
            "password": target_user["password"],
        },
    )

    assert login_response.status_code == 401


def test_super_admin_cannot_change_own_status(client):
    super_admin_user, login_data = create_super_admin_user(
        client=client,
        email="selfstatussuperadmin@example.com",
    )

    response = client.put(
        (f"/api/v1/admin/users/" f"{super_admin_user['id']}/status"),
        headers=authorization_headers(login_data["access_token"]),
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "You cannot change your own account status"


def test_super_admin_can_delete_user(client):
    _, super_admin_login = create_super_admin_user(
        client=client,
        email="deletesuperadmin@example.com",
    )

    target_user = create_verified_user(
        client=client,
        email="deleteuser@example.com",
        full_name="Delete User",
    )

    response = client.delete(
        f"/api/v1/admin/users/{target_user['id']}",
        headers=authorization_headers(super_admin_login["access_token"]),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "User deleted successfully"

    deleted_user = body["data"]["deleted_user"]

    assert deleted_user["id"] == target_user["id"]
    assert deleted_user["email"] == target_user["email"]

    details_response = client.get(
        f"/api/v1/admin/users/{target_user['id']}",
        headers=authorization_headers(super_admin_login["access_token"]),
    )

    assert details_response.status_code == 404


def test_super_admin_cannot_delete_own_account(client):
    super_admin_user, login_data = create_super_admin_user(
        client=client,
        email="selfdeletesuperadmin@example.com",
    )

    response = client.delete(
        f"/api/v1/admin/users/{super_admin_user['id']}",
        headers=authorization_headers(login_data["access_token"]),
    )

    assert response.status_code == 400

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "You cannot delete your own account"
