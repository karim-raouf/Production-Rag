"""
conftest.py — Shared fixtures for all tests.

WHAT IS A FIXTURE?
    A fixture is a function that provides test data or setup/teardown logic.
    When a test function has a parameter that matches a fixture name,
    pytest automatically calls the fixture and passes the result to the test.

    Example:
        @pytest.fixture
        def greeting():
            return "hello"

        def test_greeting(greeting):   # <-- pytest sees "greeting" and calls the fixture
            assert greeting == "hello"

WHAT IS conftest.py?
    Any fixture defined here is automatically available to ALL test files
    in this directory (and subdirectories) — no imports needed!

WHAT IS THE 'mocker' FIXTURE?
    The 'mocker' fixture comes from the pytest-mock plugin. It provides:
        - mocker.MagicMock()  → creates a fake regular object
        - mocker.AsyncMock()  → creates a fake async function/object
        - mocker.patch()      → temporarily replaces a real object with a fake
    These are the same tools as unittest.mock, but delivered the "pytest way"
    — as a fixture, so everything gets cleaned up automatically after each test.
"""

import uuid
from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database.models import User


# =============================================================================
# FIXTURE: Fake User
# =============================================================================
# This creates a fake User object that looks like it came from the database.
# Many tests need a "logged-in user", so we define it here once.


@pytest.fixture
def fake_user(mocker):
    """A fake User object simulating a database record."""
    user = mocker.MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.email = "test@example.com"
    user.username = "testuser"
    user.hashed_password = "fakehashed"
    user.is_active = True
    user.role = "USER"
    user.github_id = None
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)
    return user


# =============================================================================
# FIXTURE: Mock Database Session
# =============================================================================
# Instead of connecting to a real PostgreSQL database, we create a fake
# session using mocker.AsyncMock. This makes tests fast and isolated.


@pytest.fixture
def mock_session(mocker):
    """A mocked AsyncSession — no real database needed."""
    return mocker.AsyncMock()


# =============================================================================
# FIXTURE: Test Client (for API endpoint tests)
# =============================================================================
# This creates an HTTP client that talks to your FastAPI app IN MEMORY.
# We override two dependencies:
#   1. get_db_session → returns our mock session (no real DB)
#   2. get_current_user_dep → returns our fake user (no real auth)


@pytest.fixture
async def client(fake_user, mock_session):
    """Async HTTP client that sends requests to the FastAPI app."""
    # Import app here to avoid loading the real database at import time
    from app.main import app
    from app.core.database.dependencies import get_db_session
    from app.modules.auth.dependencies import get_current_user_dep

    # --- Dependency Overrides ---
    # These replace real dependencies with fakes during testing.
    # Think of it as "when the app asks for a DB session, give it our mock instead"
    async def override_db_session():
        yield mock_session

    def override_current_user():
        return fake_user

    app.dependency_overrides[get_db_session] = override_db_session
    app.dependency_overrides[get_current_user_dep] = override_current_user

    # Create the test client
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac

    # Clean up: remove overrides after tests
    app.dependency_overrides.clear()
