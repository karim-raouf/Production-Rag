import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from pydantic import UUID4


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID4] = mapped_column(primary_key=True, default=uuid.uuid4)
    github_id: Mapped[str | None] = mapped_column(
        String(length=255), unique=True, index=True
    )
    email: Mapped[str] = mapped_column(String(length=255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(length=255))
    hashed_password: Mapped[str] = mapped_column(String(length=255))
    is_active: Mapped[bool] = mapped_column(default=True)
    role: Mapped[str] = mapped_column(default="USER")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), insert_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        insert_default=func.now(),
        onupdate=func.now(),
    )

    tokens: Mapped[list["Token"]] = relationship("Token", back_populates="user")
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", back_populates="user"
    )

    # __table_args__ = (Index("ix_user_email", "email"),)


class Token(Base):
    __tablename__ = "tokens"

    id: Mapped[UUID4] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID4] = mapped_column(ForeignKey("users.id"), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(default=True)
    ip_address: Mapped[str | None] = mapped_column(String(length=255), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), insert_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        insert_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped["User"] = relationship("User", back_populates="tokens")

    # __table_args__ = (
    #     Index("ix_token_user_id", "user_id"),
    #     Index("ix_token_ip_address", "ip_address"),
    # )


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[UUID4] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column()
    model_type: Mapped[str] = mapped_column(index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), insert_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        insert_default=func.now(),
        onupdate=func.now(),
    )

    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )

    user: Mapped["User"] = relationship("User", back_populates="conversations")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE")
    )
    url_content: Mapped[str | None] = mapped_column()
    rag_content: Mapped[str | None] = mapped_column()
    request_content: Mapped[str] = mapped_column()
    response_content: Mapped[str] = mapped_column()
    thinking_content: Mapped[str | None] = mapped_column()
    prompt_token: Mapped[int | None] = mapped_column()
    response_token: Mapped[int | None] = mapped_column()
    total_token: Mapped[int | None] = mapped_column()
    is_success: Mapped[bool | None] = mapped_column()
    status_code: Mapped[int | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), insert_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        insert_default=func.now(),
        onupdate=func.now(),
    )

    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )
