from datetime import datetime
from typing import Any, Optional

from database.models.Base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, JSON, String, TEXT, func


class AgentRun(Base):
    """智能体运行记录，追踪 LangGraph/Agent 的输入、输出和中断恢复信息。"""

    __tablename__ = "agent_runs"

    __table_args__ = (
        Index("ix_agent_runs_user_status", "user_id", "status"),
        Index("ix_agent_runs_session_created", "session_id", "created_at"),
        Index("ix_agent_runs_thread_id", "thread_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="智能体运行记录ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    session_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sessions.id"), nullable=True, comment="会话ID")
    agent_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="智能体名称")
    graph_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="图名称")
    thread_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="LangGraph线程ID")
    checkpoint_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="Checkpointer检查点ID")
    parent_run_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("agent_runs.id"), nullable=True, comment="父运行ID")
    intent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="用户意图")
    status: Mapped[str] = mapped_column(
        Enum("running", "interrupted", "completed", "failed", "cancelled", name="agent_run_status"),
        nullable=False,
        default="running",
        comment="运行状态",
    )
    interrupt_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="中断原因")
    input_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True, comment="输入参数")
    output_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True, comment="输出参数")
    resume_payload: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True, comment="恢复执行参数")
    error_message: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="错误信息")
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, comment="开始时间")
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="结束时间")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")

    user: Mapped["User"] = relationship(back_populates="agent_runs")
    session: Mapped[Optional["Session"]] = relationship(back_populates="agent_runs")
    parent_run: Mapped[Optional["AgentRun"]] = relationship(remote_side=[id])
