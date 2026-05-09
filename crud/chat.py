"""
AI 会话 CRUD 操作
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from models.chat import ChatSession, ChatMessage


async def create_session(
    db: AsyncSession,
    user_id: int,
    session_id: str,
    title: str = "新对话"
) -> ChatSession:
    """
    创建新的聊天会话
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        session_id: 会话UUID
        title: 会话标题
        
    Returns:
        创建的会话对象
    """
    session = ChatSession(
        user_id=user_id,
        session_id=session_id,
        title=title
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_session(
    db: AsyncSession,
    session_id: str
) -> Optional[ChatSession]:
    """
    获取会话信息
    
    Args:
        db: 数据库会话
        session_id: 会话UUID
        
    Returns:
        会话对象或None
    """
    stmt = select(ChatSession).where(
        ChatSession.session_id == session_id,
        ChatSession.is_deleted == 0
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_sessions(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 50
) -> List[ChatSession]:
    """
    获取用户的会话列表
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        skip: 跳过数量
        limit: 限制数量
        
    Returns:
        会话列表
    """
    stmt = (
        select(ChatSession)
        .where(
            ChatSession.user_id == user_id,
            ChatSession.is_deleted == 0
        )
        .order_by(ChatSession.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def delete_session(
    db: AsyncSession,
    session_id: str
) -> bool:
    """
    删除会话（软删除）
    
    Args:
        db: 数据库会话
        session_id: 会话UUID
        
    Returns:
        是否删除成功
    """
    stmt = (
        update(ChatSession)
        .where(ChatSession.session_id == session_id)
        .values(is_deleted=1)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def save_message(
    db: AsyncSession,
    session_id: str,
    role: str,
    content: str,
    sources: Optional[List[Dict[str, Any]]] = None,
    question_type: Optional[str] = None
) -> ChatMessage:
    """
    保存消息
    
    Args:
        db: 数据库会话
        session_id: 会话UUID
        role: 角色（user/assistant）
        content: 消息内容
        sources: 信息来源
        question_type: 问题类型
        
    Returns:
        创建的消息对象
    """
    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        sources=sources,
        question_type=question_type
    )
    db.add(message)
    
    # 更新会话的更新时间
    stmt = (
        update(ChatSession)
        .where(ChatSession.session_id == session_id)
        .values(updated_at=datetime.now())
    )
    await db.execute(stmt)
    
    await db.commit()
    await db.refresh(message)
    return message


async def get_session_messages(
    db: AsyncSession,
    session_id: str,
    limit: int = 100
) -> List[ChatMessage]:
    """
    获取会话的消息历史
    
    Args:
        db: 数据库会话
        session_id: 会话UUID
        limit: 限制数量
        
    Returns:
        消息列表
    """
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_session_title(
    db: AsyncSession,
    session_id: str,
    title: str
) -> bool:
    """
    更新会话标题
    
    Args:
        db: 数据库会话
        session_id: 会话UUID
        title: 新标题
        
    Returns:
        是否更新成功
    """
    stmt = (
        update(ChatSession)
        .where(ChatSession.session_id == session_id)
        .values(title=title)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0
