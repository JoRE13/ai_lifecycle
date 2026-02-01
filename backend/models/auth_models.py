from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import String, DateTime, Boolean, UniqueConstraint, Index


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)

    email: str = Field(
        sa_column=Column(String(320), nullable=False, unique=True, index=True)
    )

    # Store a bcrypt hash, never the raw password
    password_hash: str = Field(sa_column=Column(String(255), nullable=False))

    is_active: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))

    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    refresh_tokens: list["RefreshToken"] = Relationship(back_populates="user")


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)

    user_id: UUID = Field(foreign_key="users.id", index=True)

    # Store only a hash of the refresh token (like passwords)
    token_hash: str = Field(sa_column=Column(String(255), nullable=False))

    # Optional metadata (nice to have)
    user_agent: Optional[str] = Field(default=None, sa_column=Column(String(512)))
    ip_address: Optional[str] = Field(default=None, sa_column=Column(String(64)))

    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))

    revoked_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    user: User = Relationship(back_populates="refresh_tokens")

    # Helpful indexes/constraints
    __table_args__ = (
        Index("ix_refresh_tokens_user_id_expires_at", "user_id", "expires_at"),
        Index("ix_refresh_tokens_token_hash", "token_hash"),
    )