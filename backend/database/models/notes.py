from sqlalchemy.dialects.mysql import LONGTEXT

from database.models.Base import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, Enum, ForeignKey, Index, Integer, JSON, String, TEXT, UniqueConstraint
from typing import Any, Optional


class Note(Base, TimestampMixin):
    """笔记主表，保存原始内容、优化内容和可追溯来源。"""

    __tablename__ = "notes"

    __table_args__ = (
        Index("ix_notes_user_status", "user_id", "status"),
        Index("ix_notes_user_created", "user_id", "created_at"),
        Index("ix_notes_source", "source_type", "source_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="笔记ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="笔记标题")
    raw_content: Mapped[str] = mapped_column(LONGTEXT, nullable=False, comment="原始笔记内容")
    optimized_content: Mapped[Optional[str]] = mapped_column(LONGTEXT, nullable=True, comment="AI优化后的结构化内容")
    summary: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True, comment="AI笔记摘要")
    note_type: Mapped[str] = mapped_column(
        Enum("manual", "ai_answer", "branch_summary", "file_import", name="note_type"),
        default="manual",
        nullable=False,
        comment="笔记类型",
    )
    source_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="来源类型")
    source_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="来源ID")
    tags: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True, comment="笔记标签")
    status: Mapped[str] = mapped_column(
        Enum("draft", "active", "archived", name="note_status"),
        default="draft",
        nullable=False,
        comment="笔记状态",
    )
    is_vectorized: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="笔记是否已向量化")

    user: Mapped["User"] = relationship(back_populates="notes")
    chunks: Mapped[list["NoteChunk"]] = relationship(back_populates="note", cascade="all, delete-orphan")
    knowledge_links: Mapped[list["NoteKnowledgePoint"]] = relationship(back_populates="note", cascade="all, delete-orphan")
    uploaded_files: Mapped[list["UploadedFile"]] = relationship(back_populates="created_note")


class NoteChunk(Base, TimestampMixin):
    """笔记切片表，保存 Chroma 向量文档回查所需元数据。"""

    __tablename__ = "note_chunks"

    __table_args__ = (
        UniqueConstraint("note_id", "chunk_index", name="uq_note_chunks_note_index"),
        Index("ix_note_chunks_user_note", "user_id", "note_id"),
        Index("ix_note_chunks_chroma_document", "chroma_collection", "chroma_document_id"),
        Index("ix_note_chunks_content_hash", "content_hash"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="笔记切片ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    note_id: Mapped[int] = mapped_column(Integer, ForeignKey("notes.id"), nullable=False, comment="笔记ID")
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False, comment="切片索引")
    content: Mapped[str] = mapped_column(TEXT, nullable=False, comment="切片内容")
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, comment="切片内容哈希")
    token_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="切片token数量")
    chroma_collection: Mapped[str] = mapped_column(String(100), nullable=False, comment="Chroma集合名")
    chroma_document_id: Mapped[str] = mapped_column(String(255), nullable=False, comment="Chroma文档ID")
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True, comment="向量元数据")

    user: Mapped["User"] = relationship(back_populates="note_chunks")
    note: Mapped["Note"] = relationship(back_populates="chunks")


class KnowledgePoint(Base, TimestampMixin):
    """用户个人知识点。"""

    __tablename__ = "knowledge_points"

    __table_args__ = (
        UniqueConstraint("user_id", "name", "domain", name="uq_knowledge_points_user_name_domain"),
        Index("ix_knowledge_points_user_domain", "user_id", "domain"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="知识点ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="知识点名称")
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="知识点描述")
    domain: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="知识点所属领域")
    mastery_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="知识点掌握程度(1-5)")
    importance_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="知识点重要程度(1-5)")

    user: Mapped["User"] = relationship(back_populates="knowledge_points")
    note_links: Mapped[list["NoteKnowledgePoint"]] = relationship(back_populates="knowledge_point", cascade="all, delete-orphan")


class NoteKnowledgePoint(Base, TimestampMixin):
    """笔记与知识点的关系表。"""

    __tablename__ = "note_knowledge_points"

    __table_args__ = (
        UniqueConstraint("note_id", "knowledge_point_id", name="uq_note_knowledge_points_note_point"),
        Index("ix_note_knowledge_points_note_id", "note_id"),
        Index("ix_note_knowledge_points_point_id", "knowledge_point_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="笔记知识点关系ID")
    note_id: Mapped[int] = mapped_column(Integer, ForeignKey("notes.id"), nullable=False, comment="笔记ID")
    knowledge_point_id: Mapped[int] = mapped_column(Integer, ForeignKey("knowledge_points.id"), nullable=False, comment="知识点ID")
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="关系类型(例如提到、解释、前置依赖)")

    note: Mapped["Note"] = relationship(back_populates="knowledge_links")
    knowledge_point: Mapped["KnowledgePoint"] = relationship(back_populates="note_links")
