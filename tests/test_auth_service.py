"""
Level 3: Auth Service Tests — Introduces mocking.

WHAT IS MOCKING?
    When AuthService calls self.user_service.get_user_by_email(), we don't
    want it to hit a real database. Instead, we replace user_service with a
    "mock" — a fake object that pretends to be the real thing.

    We control what the mock returns, so we can test different scenarios:
    - "What happens if the user exists?" → mock returns a fake user
    - "What happens if the user doesn't exist?" → mock returns None

WHY MOCK?
    1. Speed — no database connection needed
    2. Isolation — we test ONLY the AuthService logic, not the DB
    3. Control — we can simulate any scenario (errors, edge cases)

KEY TOOLS (via the 'mocker' fixture from pytest-mock):
    - mocker.AsyncMock(): creates a fake async function
    - mocker.MagicMock(): creates a fake regular object
    - mock.return_value = X: makes the mock return X when called
    - pytest.raises(SomeError): checks that an error was raised
"""

import uuid

import pytest
from fastapi import HTTPException

from app.modules.auth.services.auth import AuthService
from app.core.database.models import User


# =============================================================================
# Helper: create a mock AuthService with fake sub-services
# =============================================================================


def create_mock_auth_service(mocker):
    """
    Creates an AuthService with mocked dependencies.

    Instead of a real DB session, we pass a mock. Then we replace the
    internal services (user_service, token_service, password_service)
    with mocks too, so we can control their behavior per test.

    The 'mocker' fixture is passed in from the test method.
    """
    mock_session = mocker.AsyncMock()
    service = AuthService(mock_session)

    # Replace real services with mocks
    service.user_service = mocker.AsyncMock()
    service.token_service = mocker.AsyncMock()
    service.password_service = mocker.AsyncMock()

    return service


def create_fake_user(mocker, **overrides):
    """Creates a fake User-like object with sensible defaults."""
    user = mocker.MagicMock(spec=User)
    user.id = overrides.get("id", uuid.uuid4())
    user.email = overrides.get("email", "test@example.com")
    user.username = overrides.get("username", "testuser")
    user.hashed_password = overrides.get("hashed_password", "fakehashed")
    user.is_active = overrides.get("is_active", True)
    user.role = overrides.get("role", "USER")
    user.github_id = overrides.get("github_id", None)
    return user


# =============================================================================
# Registration Tests
# =============================================================================


class TestRegisterUser:
    """Tests for AuthService.register_user()."""

    async def test_register_success(self, mocker):
        """Registering a new user should call user_service.create and return the user."""
        service = create_mock_auth_service(mocker)
        from app.core.database.schemas import UserCreate

        user_data = UserCreate(
            email="new@example.com", username="newuser", password="StrongPass1"
        )
        expected_user = create_fake_user(mocker, email="new@example.com")

        # Setup mocks:
        # - get_user_by_email returns None (no existing user with this email)
        # - get_password_hash returns a fake hash
        # - create returns our expected user
        service.user_service.get_user_by_email.return_value = None
        service.password_service.get_password_hash.return_value = "hashed_pass"
        service.user_service.create.return_value = expected_user

        # ACT
        result = await service.register_user(user_data)

        # ASSERT
        assert result == expected_user
        service.user_service.get_user_by_email.assert_called_once_with(
            "new@example.com"
        )
        service.password_service.get_password_hash.assert_called_once_with(
            "StrongPass1"
        )

    async def test_register_duplicate_email_raises_error(self, mocker):
        """Trying to register with an email that already exists should raise an error."""
        service = create_mock_auth_service(mocker)
        from app.core.database.schemas import UserCreate

        user_data = UserCreate(
            email="existing@example.com", username="user", password="StrongPass1"
        )
        existing_user = create_fake_user(mocker, email="existing@example.com")

        # Mock: user already exists in the database
        service.user_service.get_user_by_email.return_value = existing_user

        # ACT & ASSERT: should raise HTTPException (400)
        with pytest.raises(HTTPException) as exc_info:
            await service.register_user(user_data)

        assert exc_info.value.status_code == 400


# =============================================================================
# Authentication Tests
# =============================================================================


class TestAuthenticateUser:
    """Tests for AuthService.authenticate_user()."""

    async def test_login_success(self, mocker):
        """Valid email + password should return a token."""
        service = create_mock_auth_service(mocker)

        user = create_fake_user(
            mocker, email="user@example.com", hashed_password="hashedpw"
        )
        mock_token = mocker.MagicMock()
        mock_token.id = uuid.uuid4()

        # Mock the form data that FastAPI's login endpoint receives
        form_data = mocker.MagicMock()
        form_data.username = "user@example.com"  # FastAPI uses 'username' for email
        form_data.password = "CorrectPass1"

        # Setup mocks
        service.user_service.get_user_by_email.return_value = user
        service.password_service.verify_password.return_value = True
        service.token_service.create_access_token.return_value = mock_token

        # ACT
        result = await service.authenticate_user(form_data)

        # ASSERT
        assert result == mock_token
        service.user_service.get_user_by_email.assert_called_once_with(
            "user@example.com"
        )
        service.password_service.verify_password.assert_called_once_with(
            "CorrectPass1", "hashedpw"
        )

    async def test_login_user_not_found(self, mocker):
        """Login with a non-existent email should raise HTTPException(401)."""
        service = create_mock_auth_service(mocker)

        form_data = mocker.MagicMock()
        form_data.username = "ghost@example.com"
        form_data.password = "SomePass1"

        # Mock: no user found
        service.user_service.get_user_by_email.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await service.authenticate_user(form_data)

        assert exc_info.value.status_code == 401

    async def test_login_wrong_password(self, mocker):
        """Login with wrong password should raise HTTPException(401)."""
        service = create_mock_auth_service(mocker)

        user = create_fake_user(mocker, hashed_password="hashedpw")
        form_data = mocker.MagicMock()
        form_data.username = "user@example.com"
        form_data.password = "WrongPass1"

        service.user_service.get_user_by_email.return_value = user
        service.password_service.verify_password.return_value = False  # Wrong!

        with pytest.raises(HTTPException) as exc_info:
            await service.authenticate_user(form_data)

        assert exc_info.value.status_code == 401


# =============================================================================
# Get Current User Tests
# =============================================================================


class TestGetCurrentUser:
    """Tests for AuthService.get_current_user()."""

    async def test_empty_token_raises_error(self, mocker):
        """An empty token string should raise HTTPException(401)."""
        service = create_mock_auth_service(mocker)

        with pytest.raises(HTTPException) as exc_info:
            await service.get_current_user("")

        assert exc_info.value.status_code == 401

    async def test_valid_token_returns_user(self, mocker):
        """A valid token with correct jti and email should return the user."""
        service = create_mock_auth_service(mocker)
        user = create_fake_user(mocker, email="valid@example.com")
        jti = str(uuid.uuid4())

        # Mock: token decodes to a payload with jti and email
        # NOTE: decode() is a SYNC method, so we use MagicMock (not AsyncMock)
        # If we used AsyncMock, it would return a coroutine instead of a dict!
        service.token_service.decode = mocker.MagicMock(
            return_value={
                "jti": jti,
                "email": "valid@example.com",
            }
        )
        service.token_service.validate.return_value = True
        service.user_service.get_user_by_email.return_value = user

        # ACT
        result = await service.get_current_user("valid.jwt.token")

        # ASSERT
        assert result == user

    async def test_invalid_jti_raises_error(self, mocker):
        """A token with an invalid jti should raise HTTPException(401)."""
        service = create_mock_auth_service(mocker)

        # decode() is sync, so use MagicMock instead of AsyncMock
        service.token_service.decode = mocker.MagicMock(
            return_value={
                "jti": str(uuid.uuid4()),
                "email": "user@example.com",
            }
        )
        service.token_service.validate.return_value = False  # Invalid!

        with pytest.raises(HTTPException) as exc_info:
            await service.get_current_user("bad.jwt.token")

        assert exc_info.value.status_code == 401
