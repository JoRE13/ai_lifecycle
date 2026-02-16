from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import String, DateTime, Boolean, Index
from sqlalchemy.orm import relationship


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

    refresh_tokens: list["RefreshToken"] = Relationship(
        sa_relationship=relationship("RefreshToken", back_populates="user")
    )
    problems: list["Problem"] = Relationship(
        sa_relationship=relationship("Problem", back_populates="user")
    )
    attempts: list["Attempt"] = Relationship(
        sa_relationship=relationship("Attempt", back_populates="user")
    )


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)

    user_id: UUID = Field(foreign_key="users.id", index=True)

    # Public token identifier (stored in cookie + DB lookup)
    selector: str = Field(sa_column=Column(String(128), nullable=False))

    # Secret token hash (validator portion); never store validator in plaintext
    validator_hash: str = Field(sa_column=Column(String(255), nullable=False))

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

    user: User = Relationship(
        sa_relationship=relationship("User", back_populates="refresh_tokens")
    )

    # Helpful indexes/constraints
    __table_args__ = (
        Index("ix_refresh_tokens_user_id_expires_at", "user_id", "expires_at"),
        Index("ix_refresh_tokens_selector", "selector", unique=True),
    )


class Problem(SQLModel, table=True):
    __tablename__ = "problems"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: Optional[str] = Field(default=None, sa_column=Column(String(255)))
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    user: User = Relationship(
        sa_relationship=relationship("User", back_populates="problems")
    )
    attempts: list["Attempt"] = Relationship(
        sa_relationship=relationship("Attempt", back_populates="problem")
    )


class Attempt(SQLModel, table=True):
    __tablename__ = "attempts"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    problem_id: UUID = Field(foreign_key="problems.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    mode: str = Field(sa_column=Column(String(32), nullable=False))

    problem_image_key: Optional[str] = Field(default=None, sa_column=Column(String(1024)))
    solution_image_key: Optional[str] = Field(default=None, sa_column=Column(String(1024)))
    drawing_data_key: Optional[str] = Field(default=None, sa_column=Column(String(1024)))

    verdict: Optional[str] = Field(default=None, sa_column=Column(String(64)))
    response_type: Optional[str] = Field(default=None, sa_column=Column(String(64)))
    message_is: Optional[str] = Field(default=None, sa_column=Column(String))
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    problem: Problem = Relationship(
        sa_relationship=relationship("Problem", back_populates="attempts")
    )
    user: User = Relationship(
        sa_relationship=relationship("User", back_populates="attempts")
    )
