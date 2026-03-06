"""
Level 1: Schema Tests — Pure Pydantic validation, no async, no mocking.

START HERE if you're new to testing! These are the simplest tests because:
    - They test pure data validation (no database, no HTTP, no async)
    - Each test creates a Pydantic model and checks if it validates correctly
    - You'll learn the basic pattern: Arrange → Act → Assert

KEY CONCEPTS:
    - pytest.raises(SomeError): checks that a block of code raises an error
    - ValidationError: Pydantic's error when data doesn't match the schema
"""

import pytest
from pydantic import ValidationError

from app.core.database.schemas.conversations import (
    ConversationCreateRequest,
    ConversationCreate,
    ConversationUpdate,
    ConversationOut,
)
from app.core.database.schemas.messages import MessageCreate, MessageOut
from app.core.database.schemas.users import UserCreate, validate_password


# =============================================================================
# Conversation Schema Tests
# =============================================================================


class TestConversationCreateRequest:
    """Tests for the ConversationCreateRequest schema (what the client sends)."""

    def test_valid_creation(self):
        """A valid request with all required fields should work."""
        # ARRANGE: prepare the input data
        data = {"title": "My Chat", "model_type": "gpt-4"}

        # ACT: create the schema instance
        conversation = ConversationCreateRequest(**data)

        # ASSERT: check the values are correct
        assert conversation.title == "My Chat"
        assert conversation.model_type == "gpt-4"

    def test_missing_title_raises_error(self):
        """Missing 'title' should raise a ValidationError."""
        with pytest.raises(ValidationError):
            ConversationCreateRequest(model_type="gpt-4")  # no title!

    def test_missing_model_type_raises_error(self):
        """Missing 'model_type' should raise a ValidationError."""
        with pytest.raises(ValidationError):
            ConversationCreateRequest(title="My Chat")  # no model_type!


class TestConversationCreate:
    """Tests for ConversationCreate (internal schema that includes user_id)."""

    def test_valid_with_user_id(self):
        """Should accept title, model_type, AND user_id."""
        import uuid

        user_id = uuid.uuid4()
        conversation = ConversationCreate(
            title="My Chat", model_type="gpt-4", user_id=user_id
        )
        assert conversation.user_id == user_id
        assert conversation.title == "My Chat"

    def test_missing_user_id_raises_error(self):
        """user_id is required for internal use — should fail without it."""
        with pytest.raises(ValidationError):
            ConversationCreate(title="My Chat", model_type="gpt-4")


class TestConversationOut:
    """Tests for ConversationOut (what the API returns to the client)."""

    def test_valid_output(self):
        """Should include id, created_at, and updated_at on top of base fields."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        conv = ConversationOut(
            id=1,
            title="Chat",
            model_type="gpt-4",
            created_at=now,
            updated_at=now,
        )
        assert conv.id == 1
        assert conv.title == "Chat"
        assert conv.created_at == now

    def test_missing_id_raises_error(self):
        """ConversationOut requires an 'id' field — should fail without it."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError):
            ConversationOut(
                title="Chat", model_type="gpt-4", created_at=now, updated_at=now
            )


# =============================================================================
# Message Schema Tests
# =============================================================================


class TestMessageCreate:
    """Tests for the MessageCreate schema."""

    def test_valid_message(self):
        """A message with all required fields should work."""
        msg = MessageCreate(
            request_content="Hello!",
            response_content="Hi there!",
            conversation_id=1,
        )
        assert msg.request_content == "Hello!"
        assert msg.response_content == "Hi there!"
        assert msg.conversation_id == 1

    def test_optional_fields_default_to_none(self):
        """Optional fields like url_content, rag_content should default to None."""
        msg = MessageCreate(
            request_content="Hello!",
            response_content="Hi!",
            conversation_id=1,
        )
        assert msg.url_content is None
        assert msg.rag_content is None
        assert msg.thinking_content is None
        assert msg.prompt_token is None

    def test_missing_required_field_raises_error(self):
        """Missing request_content should raise a ValidationError."""
        with pytest.raises(ValidationError):
            MessageCreate(response_content="Hi!", conversation_id=1)


# =============================================================================
# User Schema Tests
# =============================================================================


class TestUserCreate:
    """Tests for the UserCreate schema and password validation."""

    def test_valid_user(self):
        """A user with valid email, username, and strong password should work."""
        user = UserCreate(
            email="user@example.com",
            username="testuser",
            password="StrongPass1",
        )
        assert user.email == "user@example.com"
        assert user.username == "testuser"

    def test_weak_password_no_digit(self):
        """Password must contain at least one digit."""
        with pytest.raises(ValidationError, match="digit"):
            UserCreate(
                email="user@example.com",
                username="testuser",
                password="NoDigitHere",
            )

    def test_weak_password_no_uppercase(self):
        """Password must contain at least one uppercase letter."""
        with pytest.raises(ValidationError, match="uppercase"):
            UserCreate(
                email="user@example.com",
                username="testuser",
                password="nouppercase1",
            )

    def test_weak_password_no_lowercase(self):
        """Password must contain at least one lowercase letter."""
        with pytest.raises(ValidationError, match="lowercase"):
            UserCreate(
                email="user@example.com",
                username="testuser",
                password="NOLOWERCASE1",
            )

    def test_password_too_short(self):
        """Password must be at least 8 characters."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="user@example.com",
                username="testuser",
                password="Ab1",  # only 3 chars
            )

    def test_invalid_email(self):
        """Invalid email format should raise a ValidationError."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="not-an-email",
                username="testuser",
                password="StrongPass1",
            )


class TestValidatePassword:
    """Tests for the standalone validate_password function."""

    def test_valid_password(self):
        """A password meeting all criteria should pass."""
        result = validate_password("GoodPass1")
        assert result == "GoodPass1"

    def test_missing_digit(self):
        """Should raise ValueError when no digit is present."""
        with pytest.raises(ValueError, match="digit"):
            validate_password("NoDigitHere")

    def test_missing_uppercase(self):
        """Should raise ValueError when no uppercase letter is present."""
        with pytest.raises(ValueError, match="uppercase"):
            validate_password("nouppercase1")

    def test_missing_lowercase(self):
        """Should raise ValueError when no lowercase letter is present."""
        with pytest.raises(ValueError, match="lowercase"):
            validate_password("NOLOWERCASE1")
