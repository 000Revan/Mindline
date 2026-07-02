from datetime import datetime, date

from database.models.Base import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, TEXT, func, Date, CheckConstraint
from typing import Optional


class LearningGoal(Base, TimestampMixin):
    """学习目标/主线表。"""

    __tablename__ = "learning_goals"

    __table_args__ = (
        Index("ix_learning_goals_user_status", "user_id", "status"),
        Index("ix_learning_goals_user_priority", "user_id", "priority"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="学习目标ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="学习目标标题")
    description: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="学习目标描述")
    direction: Mapped[str] = mapped_column(String(255), nullable=False, comment="学习目标方向")
    status: Mapped[str] = mapped_column(
        Enum("pending", "active", "paused", "completed", "archived", name="learning_goal_status"),
        default="pending",
        nullable=False,
        comment="学习目标状态",
    )
    priority: Mapped[int] = mapped_column(Integer, default=3, nullable=False, comment="学习目标优先级")
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="学习目标开始时间")
    target_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="学习目标完成时间")
    current_stage: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="学习目标当前阶段")
    current_principle: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="当前学习原则")

    user: Mapped["User"] = relationship(back_populates="learning_goals")
    daily_tasks: Mapped[list["DailyTask"]] = relationship(back_populates="goal", cascade="all, delete-orphan")
    learning_sessions: Mapped[list["LearningSession"]] = relationship(back_populates="goal")
    branch_topics: Mapped[list["BranchTopic"]] = relationship(back_populates="goal")


class DailyTask(Base, TimestampMixin):
    """每日学习任务，不包含题库/每日题功能。"""

    __tablename__ = "daily_tasks"

    __table_args__ = (
        Index("ix_daily_tasks_user_status", "user_id", "task_date","status"),
        Index("ix_daily_tasks_goal_status", "goal_id", "task_date"),
        CheckConstraint(
            "estimated_time IS NULL OR estimated_time BETWEEN 1 AND 1440",
            name="daily_tasks_estimated_time_range",
        )
    )



    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="任务ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    goal_id: Mapped[int] = mapped_column(Integer, ForeignKey("learning_goals.id"), nullable=False,index=True, comment="所属学习目标ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="任务标题")
    description: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="任务描述")
    task_type: Mapped[str] = mapped_column(
        Enum("study", "review", "branch", "reflection", name="daily_task_type"),
        default="study",
        nullable=False,
        comment="任务类型",
    )
    status: Mapped[str] = mapped_column(
        Enum("pending", "in_progress", "completed", "cancelled", name="daily_task_status"),
        nullable=False,
        default="pending",
        comment="任务状态",
    )
    estimated_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="预计耗时(分钟)")
    task_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="计划执行日期",
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="完成时间")

    user: Mapped["User"] = relationship(back_populates="daily_tasks")
    goal: Mapped["LearningGoal"] = relationship(back_populates="daily_tasks")
    learning_sessions: Mapped[list["LearningSession"]] = relationship(back_populates="task")


class LearningSession(Base, TimestampMixin):
    """学习记录表，保存一次具体学习过程。"""

    __tablename__ = "learning_sessions"

    __table_args__ = (
        Index("ix_learning_sessions_user_started", "user_id", "started_at"),
        Index("ix_learning_sessions_goal_started", "goal_id", "started_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="学习记录ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    goal_id: Mapped[int] = mapped_column(Integer, ForeignKey("learning_goals.id"), nullable=False, comment="所属学习目标ID")
    task_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("daily_tasks.id"), nullable=True, comment="对应每日任务ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="学习记录标题")
    content: Mapped[str] = mapped_column(TEXT, nullable=False, comment="学习过程记录")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), comment="开始时间")
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="结束时间")
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="学习时长(分钟)")
    focus_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="专注度得分")
    status: Mapped[str] = mapped_column(
        Enum("active", "completed", "cancelled", name="learning_session_status"),
        default="active",
        nullable=False,
        comment="学习记录状态",
    )
    summary: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="学习总结")

    user: Mapped["User"] = relationship(back_populates="learning_sessions")
    goal: Mapped["LearningGoal"] = relationship(back_populates="learning_sessions")
    task: Mapped[Optional["DailyTask"]] = relationship(back_populates="learning_sessions")
