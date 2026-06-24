from datetime import datetime


from database.models.Base import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, String, TEXT, func
from typing import Optional


class BranchTopic(Base, TimestampMixin):
    """分支停车场主题，记录偏离主线但值得回收的学习问题。"""

    __tablename__ = "branch_topics"

    __table_args__ = (
        Index("ix_branch_topics_user_status", "user_id", "status"),
        Index("ix_branch_topics_goal_status", "goal_id", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="分支ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    goal_id: Mapped[int] = mapped_column(Integer, ForeignKey("learning_goals.id"), nullable=False, comment="所属学习目标ID")
    session_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("learning_sessions.id"), nullable=True, comment="来源学习记录ID")
    source_note_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("notes.id"), nullable=True, comment="来源笔记ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="分支标题")
    description: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="分支描述")
    reason: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="分支原因")
    status: Mapped[str] = mapped_column(
        Enum("pending", "limited_learning", "returned", "converted_to_goal", "archived", name="branch_topic_status"),
        default="pending",
        nullable=False,
        comment="分支状态",
    )
    priority: Mapped[int] = mapped_column(Integer, default=3, nullable=False, comment="分支优先级")
    timebox_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="建议限时学习分钟数")
    minimum_understanding: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="最低可用理解")
    return_summary: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="回归主线总结")

    user: Mapped["User"] = relationship(back_populates="branch_topics")
    goal: Mapped["LearningGoal"] = relationship(back_populates="branch_topics")
    source_session: Mapped[Optional["LearningSession"]] = relationship()
    source_note: Mapped[Optional["Note"]] = relationship()
    timer_sessions: Mapped[list["BranchTimerSession"]] = relationship(back_populates="branch_topic", cascade="all, delete-orphan")


class BranchTimerSession(Base, TimestampMixin):
    """一次分支限时溯源记录。"""

    __tablename__ = "branch_timer_sessions"

    __table_args__ = (
        Index("ix_branch_timer_sessions_user_started", "user_id", "started_at"),
        Index("ix_branch_timer_sessions_topic_started", "branch_topic_id", "started_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="分支限时学习记录ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    branch_topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("branch_topics.id"), nullable=False, comment="分支主题ID")
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="限时学习开始时间")
    ended_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, comment="限时学习结束时间")
    planned_minutes: Mapped[int] = mapped_column(Integer, nullable=False, comment="计划学习分钟数")
    actual_minutes: Mapped[int] = mapped_column(Integer, nullable=True, comment="实际学习分钟数")
    result_summary: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="学习结果摘要")
    return_to_mainline: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否返回主线")

    user: Mapped["User"] = relationship(back_populates="branch_timer_sessions")
    branch_topic: Mapped["BranchTopic"] = relationship(back_populates="timer_sessions")
