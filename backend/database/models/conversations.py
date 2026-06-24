from datetime import datetime
from typing import Any, Optional

from sqlalchemy.dialects.mysql import LONGTEXT

from database.models.Base import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, JSON, String, UniqueConstraint, func


class Session(Base, TimestampMixin):
    """对话会话表。"""

    __tablename__ = "sessions"

    __table_args__ = (
        UniqueConstraint("public_id", name="uq_sessions_public_id"),
        Index("ix_sessions_user_status", "user_id", "status"),
        Index("ix_sessions_user_type", "user_id", "session_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="会话ID")
    public_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="会话公开ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="会话标题")
    session_type: Mapped[str] = mapped_column(
        Enum("chat", "study", "review", "emotion", name="session_type"),
        nullable=False,
        comment="会话类型",
    )
    status: Mapped[str] = mapped_column(
        Enum("active", "archived", name="session_status"),
        default="active",
        nullable=False,
        comment="会话状态",
    )

    user: Mapped["User"] = relationship(back_populates="sessions")
    messages: Mapped[list["Message"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    emotion_logs: Mapped[list["EmotionLog"]] = relationship(back_populates="session")
    agent_runs: Mapped[list["AgentRun"]] = relationship(back_populates="session")


class Message(Base):
    """会话消息表。"""

    __tablename__ = "messages"

    __table_args__ = (
        Index("ix_messages_session_created", "session_id", "created_at"),
        Index("ix_messages_user_created", "user_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="消息ID")
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("sessions.id"), nullable=False, comment="会话ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    role: Mapped[str] = mapped_column(
        Enum("system", "user", "assistant", "tool", name="message_role"),
        nullable=False,
        comment="消息角色",
    )
    content: Mapped[str] = mapped_column(LONGTEXT, nullable=False, comment="消息内容")
    message_type: Mapped[str] = mapped_column(
        Enum("text", "markdown", "tool_call", "tool_result", name="message_type"),
        default="text",
        nullable=False,
        comment="消息类型",
    )
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True, comment="元数据")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")

    session: Mapped["Session"] = relationship(back_populates="messages")
    user: Mapped["User"] = relationship(back_populates="messages")
