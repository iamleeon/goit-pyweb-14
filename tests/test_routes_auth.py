from unittest.mock import MagicMock

from src.database.models import User
from src.services.auth import auth_service


def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("/api/auth/signup", json=user,)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == user.get("email")
    assert "id" in data["user"]


def test_repeat_create_user(client, user):
    response = client.post("/api/auth/signup", json=user,)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Account already exists"


def test_login_user_not_confirmed(client, user):
    response = client.post("/api/auth/login", data={
        "username": user.get("email"),
        "password": user.get("password")
    })
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"


def test_login_user(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = True
    session.commit()
    response = client.post("/api/auth/login", data={
        "username": user.get("email"),
        "password": user.get("password")
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, user):
    response = client.post("/api/auth/login", data={
        "username": user.get("email"),
        "password": "password"
    })
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"


def test_login_wrong_email(client, user):
    response = client.post("/api/auth/login", data={
        "username": "email",
        "password": user.get("password")
    })
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"


def test_refresh_token(client, user):
    response = client.post("/api/auth/login", data={
        "username": user["email"],
        "password": user["password"],
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert "refresh_token" in data, response.text
    refresh_token = data["refresh_token"]
    response = client.get("/api/auth/refresh_token", headers={
        "Authorization": f"Bearer {refresh_token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer", response.text
    assert "refresh_token" in data, response.text


def test_refresh_token_invalid(client):
    response = client.get("/api/auth/refresh_token", headers={
        "Authorization": "Bearer invalid_token"
    })
    assert response.status_code == 401, response.text
    data = response.json()
    assert "detail" in data, response.text
    assert data["detail"] == "Could not validate credentials", response.text


def test_confirm_email(client, session, user, email_token):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = False
    session.commit()
    response = client.get(f"/api/auth/confirmed_email/{email_token}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Email confirmed"
    updated_user: User = session.query(User).filter(User.email == user.get("email")).first()
    assert updated_user.confirmed is True


def test_confirm_email_invalid_token(client):
    response = client.get("/api/auth/confirmed_email/invalid_token")
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Invalid token for email verification"


def test_request_email_confirmation(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = False
    session.commit()

    response = client.post("/api/auth/request_email", json={"email": user.get("email")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Check your email for confirmation."


def test_request_email_already_confirmed(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = True
    session.commit()

    response = client.post("/api/auth/request_email", json={"email": user.get("email")})
    data = response.json()
    assert data["message"] == "Your email is already confirmed."
