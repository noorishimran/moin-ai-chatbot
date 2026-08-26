"""
Database models for MoinSystems AI Chatbot.
"""

import uuid
from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ChatSession(Base):
    __tablename__ = "chat_session"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_token: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    source_page: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active")

    messages: Mapped[list["ChatMessage"]] = relationship(back_populates="session")
    lead: Mapped["LeadSubmission | None"] = relationship(back_populates="session", uselist=False)


class ChatMessage(Base):
    __tablename__ = "chat_message"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chat_session.id"), index=True)
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text)
    intent: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    session: Mapped["ChatSession"] = relationship(back_populates="messages")


class LeadSubmission(Base):
    __tablename__ = "lead_submission"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chat_session.id"), unique=True)

    full_name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(320))
    contact_number: Mapped[str] = mapped_column(String(64))

    company_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    project_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    service_interest: Mapped[str | None] = mapped_column(String(512), nullable=True)
    timeline: Mapped[str | None] = mapped_column(String(128), nullable=True)
    budget_range: Mapped[str | None] = mapped_column(String(128), nullable=True)
    source_page: Mapped[str | None] = mapped_column(String(512), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    session: Mapped["ChatSession"] = relationship(back_populates="lead")
    notifications: Mapped[list["EmailNotification"]] = relationship(back_populates="lead")


class EmailNotification(Base):
    __tablename__ = "email_notification"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lead_submission.id"), index=True)
    recipient: Mapped[str] = mapped_column(String(320))
    subject: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default="pending")
    provider_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    lead: Mapped["LeadSubmission"] = relationship(back_populates="notifications")


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_document"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_name: Mapped[str] = mapped_column(String(255))
    version: Mapped[str] = mapped_column(String(64))
    source_uri: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    chunks: Mapped[list["KnowledgeChunk"]] = relationship(back_populates="document")


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunk"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_document.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    tags: Mapped[str | None] = mapped_column(String(512), nullable=True)
    intents: Mapped[str | None] = mapped_column(String(255), nullable=True)

    embedding: Mapped[list[float]] = mapped_column(Vector(1536))

    document: Mapped["KnowledgeDocument"] = relationship(back_populates="chunks")