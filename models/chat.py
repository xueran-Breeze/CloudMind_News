"""
AI 会话模型
用于存储用户的对话会话和消息历史
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Index, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

# 使用与 User 相同的 Base
from models.users import Base


class ChatSession(Base):
    """
    AI 聊天会话表
    每个会话属于一个用户，包含多条消息
    """
    __tablename__ = 'chat_session'

    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_session_id', 'session_id'),
        Index('idx_created_at', 'created_at'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="会话记录ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False, comment="用户ID")
    session_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, comment="会话UUID")
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="会话标题（自动生成）")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    is_deleted: Mapped[bool] = mapped_column(Integer, default=0, comment="是否删除：0-否，1-是")

    def __repr__(self):
        return f"<ChatSession(id={self.id}, session_id='{self.session_id}', user_id={self.user_id})>"


class ChatMessage(Base):
    """
    AI 聊天消息表
    存储每条对话消息
    """
    __tablename__ = 'chat_message'

    __table_args__ = (
        Index('idx_session_id', 'session_id'),
        Index('idx_created_at', 'created_at'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="消息ID")
    session_id: Mapped[str] = mapped_column(String(64), ForeignKey('chat_session.session_id'), nullable=False, comment="会话ID")
    role: Mapped[str] = mapped_column(String(20), nullable=False, comment="角色：user/assistant")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")
    sources: Mapped[Optional[str]] = mapped_column(JSON, comment="信息来源（JSON格式）")
    question_type: Mapped[Optional[str]] = mapped_column(String(50), comment="问题类型：realtime/knowledge/chat")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, session_id='{self.session_id}', role='{self.role}')>"
