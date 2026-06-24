from database.models.Base import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum, ForeignKey, Index, Integer, String
from typing import Optional


class UploadedFile(Base, TimestampMixin):
    """上传文件表，用于追踪文件导入笔记和后续 RAG 处理来源。"""

    __tablename__ = "uploaded_files"

    __table_args__ = (
        Index("ix_uploaded_files_user_created", "user_id", "created_at"),
        Index("ix_uploaded_files_created_note_id", "created_note_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="上传文件ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    original_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="原始文件名")
    file_path: Mapped[str] = mapped_column(String(255), nullable=False, comment="文件路径")
    file_type: Mapped[str] = mapped_column(Enum("pdf", "md", "txt", "docx", name="uploaded_file_type"), nullable=False, comment="文件类型")
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, comment="文件大小")
    file_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="文件哈希")
    status: Mapped[str] = mapped_column(
        Enum("uploaded", "parsed", "failed", name="uploaded_file_status"),
        default="uploaded",
        nullable=False,
        comment="处理状态",
    )
    created_note_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("notes.id"), nullable=True, comment="生成的笔记ID")

    user: Mapped["User"] = relationship(back_populates="uploaded_files")
    created_note: Mapped[Optional["Note"]] = relationship(back_populates="uploaded_files")
