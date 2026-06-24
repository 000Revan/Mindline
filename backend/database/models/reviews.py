from datetime import datetime


from database.models.Base import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, String, TEXT, UniqueConstraint, func
from typing import Optional


class DailyReview(Base, TimestampMixin):
    """每日复盘表。"""

    __tablename__ = "daily_reviews"

    __table_args__ = (
        UniqueConstraint("user_id", "review_date", name="uq_daily_reviews_user_date"),
        Index("ix_daily_reviews_user_date", "user_id", "review_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="每日复盘ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    review_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="复盘日期")
    mainline_progress: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="主线推进情况")
    learned_summary: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="今日学习总结")
    problems: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="今日问题")
    branch_summary: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="今日分支情况")
    emotion_summary: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="今日情绪状态")
    tomorrow_plan: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="明日计划")
    ai_feedback: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="AI反馈")

    user: Mapped["User"] = relationship(back_populates="daily_reviews")


class WeeklyReview(Base, TimestampMixin):
    """每周复盘表。"""

    __tablename__ = "weekly_reviews"

    __table_args__ = (
        UniqueConstraint("user_id", "week_start_date", name="uq_weekly_reviews_user_week_start"),
        Index("ix_weekly_reviews_user_week", "user_id", "week_start_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="每周复盘ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    week_start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="周开始时间")
    week_end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="周结束时间")
    mainline_summary: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="本周主线总结")
    learned_summary: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="本周学习总结")
    completed_goals: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="本周完成目标")
    unfinished_goals: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="本周未完成目标")
    repeated_problems: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="反复卡点")
    emotion_pattern: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="情绪模式")
    next_week_plan: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="下周计划")
    ai_feedback: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="AI反馈")

    user: Mapped["User"] = relationship(back_populates="weekly_reviews")


class EmotionLog(Base):
    """情绪陪伴日志，只记录支持过程，不做医疗诊断。"""

    __tablename__ = "emotion_logs"

    __table_args__ = (
        Index("ix_emotion_logs_user_created", "user_id", "created_at"),
        Index("ix_emotion_logs_session_created", "session_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="心情日志ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    session_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sessions.id"), nullable=True, comment="会话ID")
    emotion_type: Mapped[str] = mapped_column(
        Enum("happy", "anxious", "sad", "stressed", "confused", "angry", "numb", name="emotion_type"),
        nullable=False,
        comment="心情类型",
    )
    intensity: Mapped[int] = mapped_column(Integer, nullable=False, comment="心情强度(1-5)")
    trigger_text: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="触发原因")
    ai_response_summary: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="AI回复摘要")
    action_suggestion: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="行动建议")
    support_mode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="支持方式")
    risk_level: Mapped[str] = mapped_column(
        Enum("none", "low", "medium", "high", name="emotion_risk_level"),
        default="none",
        nullable=False,
        comment="风险等级",
    )
    follow_up_needed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否需要后续跟进")
    is_sensitive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否敏感")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")

    user: Mapped["User"] = relationship(back_populates="emotion_logs")
    session: Mapped[Optional["Session"]] = relationship(back_populates="emotion_logs")
