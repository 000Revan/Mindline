from typing import Any, Optional

from sqlalchemy import Enum, ForeignKey, Index, Integer, JSON, String, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.Base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """用户账号基础信息。"""

    __tablename__ = "users"

    __table_args__ = (
        Index("ix_users_username", "username"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名")
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码哈希")
    nickname: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="昵称")
    avatar_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True, comment="头像URL")
    gender: Mapped[Optional[str]] = mapped_column(
        Enum("male", "female", "unknown", name="user_gender"),
        default="unknown",
        nullable=True,
        comment="性别",
    )
    bio: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="个人简介")
    status: Mapped[str] = mapped_column(
        Enum("active", "disabled", name="user_status"),
        default="active",
        nullable=False,
        comment="账号状态",
    )

    profile: Mapped[Optional["UserProfile"]] = relationship(back_populates="user", uselist=False)
    notes: Mapped[list["Note"]] = relationship(back_populates="user")
    note_chunks: Mapped[list["NoteChunk"]] = relationship(back_populates="user")
    knowledge_points: Mapped[list["KnowledgePoint"]] = relationship(back_populates="user")
    learning_goals: Mapped[list["LearningGoal"]] = relationship(back_populates="user")
    daily_tasks: Mapped[list["DailyTask"]] = relationship(back_populates="user")
    learning_sessions: Mapped[list["LearningSession"]] = relationship(back_populates="user")
    branch_topics: Mapped[list["BranchTopic"]] = relationship(back_populates="user")
    branch_timer_sessions: Mapped[list["BranchTimerSession"]] = relationship(back_populates="user")
    sessions: Mapped[list["Session"]] = relationship(back_populates="user")
    messages: Mapped[list["Message"]] = relationship(back_populates="user")
    daily_reviews: Mapped[list["DailyReview"]] = relationship(back_populates="user")
    weekly_reviews: Mapped[list["WeeklyReview"]] = relationship(back_populates="user")
    emotion_logs: Mapped[list["EmotionLog"]] = relationship(back_populates="user")
    agent_runs: Mapped[list["AgentRun"]] = relationship(back_populates="user")
    uploaded_files: Mapped[list["UploadedFile"]] = relationship(back_populates="user")


class UserProfile(Base, TimestampMixin):
    """用户长期画像，保存偏好、学习方向和情绪倾向等稳定信息。"""

    __tablename__ = "user_profiles"

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_user_profiles_user_id"),
        Index("ix_user_profiles_user_id", "user_id"),
        CheckConstraint(
            "anxiety_level IS NULL OR anxiety_level BETWEEN 1 AND 5",
            name="ck_user_profiles_anxiety_level_range",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="用户画像ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    target_direction: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="学习目标方向")
    anxiety_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="焦虑等级(1-5)")
    learning_level: Mapped[Optional[str]] = mapped_column(Enum("beginner","entry","advanced"),name="profile_learning_level", nullable=True, comment="学习水平：beginner=初学，entry=入门，advanced=进阶")
    support_style: Mapped[Optional[str]] = mapped_column(Enum("gentle", "direct", "coach", "warm_logic"), name="profile_support_style",nullable=True, comment="情绪陪伴风格")
    preference_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True, comment="偏好JSON")

    user: Mapped["User"] = relationship(back_populates="profile")





