"""
Level 5: API Endpoint Tests — Full request/response testing.

WHAT'S NEW HERE:
    - We test the actual HTTP layer: routes, status codes, and JSON responses
    - The 'client' fixture (from conftest.py) sends requests to the FastAPI app
      WITHOUT starting a real server — everything happens in memory
    - Dependencies (DB session, auth) are overridden in conftest.py
    - We use mocker.patch() instead of unittest.mock.patch()

HOW IT WORKS:
    1. conftest.py creates an AsyncClient connected to your FastAPI app
    2. It overrides get_db_session → returns a mock (no real PostgreSQL)
    3. It overrides get_current_user_dep → returns a fake user (no real auth)
    4. Your test calls client.get("/api/conversations") → hits the real route
    5. The route function runs, but uses fake dependencies
    6. We check the response status code and JSON body

IMPORTANT:
    These tests use the 'client', 'mock_session', and 'mocker' fixtures.
    pytest finds them automatically — no import needed!
"""

from datetime import datetime, timezone


# =============================================================================
# List Conversations Tests
# =============================================================================


class TestListConversations:
    """Tests for GET /api/conversations."""

    async def test_list_returns_empty(self, client, mock_session, mocker):
        """When there are no conversations, should return an empty list."""
        # mocker.patch() replaces ConversationService with a mock during this test.
        # It's automatically restored after the test finishes — no manual cleanup!
        MockService = mocker.patch(
            "app.core.database.routers.conversations.endpoints.ConversationService"
        )
        # Setup: the service instance's get_all returns an empty list
        mock_instance = mocker.AsyncMock()
        mock_instance.get_all.return_value = []
        MockService.return_value = mock_instance

        response = await client.get("/api/conversations")

        assert response.status_code == 200
        assert response.json() == []

    async def test_list_returns_conversations(self, client, mock_session, mocker):
        """When conversations exist, should return them as JSON."""
        now = datetime.now(timezone.utc)

        # Create fake conversation objects that look like ORM models
        fake_conv = mocker.MagicMock()
        fake_conv.id = 1
        fake_conv.title = "Test Chat"
        fake_conv.model_type = "gpt-4"
        fake_conv.created_at = now
        fake_conv.updated_at = now

        MockService = mocker.patch(
            "app.core.database.routers.conversations.endpoints.ConversationService"
        )
        mock_instance = mocker.AsyncMock()
        mock_instance.get_all.return_value = [fake_conv]
        MockService.return_value = mock_instance

        response = await client.get("/api/conversations")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Test Chat"
        assert data[0]["model_type"] == "gpt-4"


# =============================================================================
# Create Conversation Tests
# =============================================================================


class TestCreateConversation:
    """Tests for POST /api/conversations."""

    async def test_create_returns_201(self, client, mock_session, mocker):
        """Creating a conversation should return 201 and the new conversation."""
        now = datetime.now(timezone.utc)

        fake_conv = mocker.MagicMock()
        fake_conv.id = 42
        fake_conv.title = "New Chat"
        fake_conv.model_type = "gpt-4"
        fake_conv.created_at = now
        fake_conv.updated_at = now

        MockService = mocker.patch(
            "app.core.database.routers.conversations.endpoints.ConversationService"
        )
        mock_instance = mocker.AsyncMock()
        mock_instance.create.return_value = fake_conv
        MockService.return_value = mock_instance

        response = await client.post(
            "/api/conversations",
            json={"title": "New Chat", "model_type": "gpt-4"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Chat"
        assert data["id"] == 42

    async def test_create_missing_fields_returns_422(self, client, mock_session):
        """
        Sending incomplete data (missing model_type) should return 422.
        This is FastAPI's automatic validation — no test mock needed!
        """
        response = await client.post(
            "/api/conversations",
            json={"title": "Incomplete"},  # missing model_type
        )

        assert response.status_code == 422  # Unprocessable Entity


# =============================================================================
# Delete Conversation Tests
# =============================================================================


class TestDeleteConversation:
    """Tests for DELETE /api/conversations/{id}."""

    async def test_delete_returns_204(self, client, mock_session, mocker):
        """Deleting a conversation should return 204 No Content."""
        from app.main import app
        from app.core.database.routers.conversations.dependencies import (
            get_conversation,
        )

        now = datetime.now(timezone.utc)

        fake_conv = mocker.MagicMock()
        fake_conv.id = 1
        fake_conv.title = "To Delete"
        fake_conv.model_type = "gpt-4"
        fake_conv.created_at = now
        fake_conv.updated_at = now

        # Override get_conversation to skip the DB lookup AND auth check entirely.
        # This is needed because get_conversation internally depends on CurrentUserDep,
        # which triggers the full auth chain.
        app.dependency_overrides[get_conversation] = lambda: fake_conv

        try:
            MockService = mocker.patch(
                "app.core.database.routers.conversations.endpoints.ConversationService"
            )
            mock_instance = mocker.AsyncMock()
            mock_instance.delete.return_value = None
            MockService.return_value = mock_instance

            response = await client.delete("/api/conversations/1")

            assert response.status_code == 204
        finally:
            # Clean up: remove the override so other tests aren't affected
            app.dependency_overrides.pop(get_conversation, None)
