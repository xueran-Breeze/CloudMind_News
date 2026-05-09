"""
AI 聊天路由
集成 LangGraph Agent，提供智能问答功能
支持会话持久化和多会话管理
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from agents.graph import run_agent
from services.memory_service import memory_service
from config.db_conf import get_db
from utils.auth import get_current_user_id
from crud import chat as chat_crud

# 创建API实例
router = APIRouter(prefix="/api/ai", tags=["ai"])


class Message(BaseModel):
    """消息模型"""
    role: str  # "user" 或 "assistant"
    content: str


class ChatRequest(BaseModel):
    """聊天请求模型（支持两种格式）"""
    # 新格式：单条消息
    message: Optional[str] = None  # 用户消息
    session_id: Optional[str] = None  # 会话ID（可选，不提供则自动生成）
    
    # 旧格式：消息数组（兼容前端）
    messages: Optional[List[Message]] = None  # 消息历史
    model: Optional[str] = None  # 模型名称（可选，不使用）


class ChatResponse(BaseModel):
    """聊天响应模型"""
    code: int
    message: str
    data: dict


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    与AI助手进行对话（使用 LangGraph Agent）
    
    功能：
    - 智能路由：自动判断问题类型（实时新闻/本地知识/闲聊）
    - 多轮对话：基于 Redis + MySQL 保存对话历史
    - 来源标注：标明信息来源（联网搜索URL或本地数据库）
    - 上下文理解：结合对话历史生成回答
    - 会话持久化：长期存储，用户重新登录仍可访问
    
    支持两种请求格式：
    1. 新格式：{message: "你好", session_id: "xxx"}
    2. 旧格式：{messages: [{role: "user", content: "你好"}], model: "qwen-plus"}
    """
    try:
        # 兼容两种请求格式
        if request.message:
            # 新格式：直接使用 message
            user_message = request.message
            session_id = request.session_id or str(uuid.uuid4())
        elif request.messages:
            # 旧格式：从 messages 数组中提取
            user_messages = [msg for msg in request.messages if msg.role == "user"]
            if not user_messages:
                raise HTTPException(status_code=400, detail="没有用户消息")
            
            user_message = user_messages[-1].content
            session_id = request.session_id or str(uuid.uuid4())
        else:
            raise HTTPException(status_code=400, detail="缺少 message 或 messages 字段")
        
        # 检查或创建会话（数据库）
        session_record = await chat_crud.get_session(db, session_id)
        if not session_record:
            # 如果是新会话，创建记录
            await chat_crud.create_session(db, user_id, session_id)
        
        # 从 Redis 获取短期记忆（最近20条）
        chat_history = await memory_service.get_history(session_id, limit=20)
        
        # 如果 Redis 中没有，从数据库加载
        if not chat_history:
            db_messages = await chat_crud.get_session_messages(db, session_id, limit=20)
            chat_history = [
                {"role": msg.role, "content": msg.content}
                for msg in db_messages
            ]
        
        # 运行 Agent
        result = await run_agent(
            session_id=session_id,
            user_input=user_message,
            chat_history=chat_history
        )
        
        # 检查是否有错误
        if result.get("error"):
            raise HTTPException(
                status_code=500,
                detail=result["error"]
            )
        
        # 获取答案和来源
        answer = result.get("answer", "")
        sources = result.get("sources", [])
        question_type = result.get("question_type", "unknown")
        
        if not answer:
            raise HTTPException(
                status_code=500,
                detail="未能生成回答"
            )
        
        # 保存到 Redis（短期记忆）
        await memory_service.save_message(session_id, "user", user_message)
        await memory_service.save_message(session_id, "assistant", answer)
        
        # 保存到 MySQL（长期持久化）
        await chat_crud.save_message(
            db=db,
            session_id=session_id,
            role="user",
            content=user_message
        )
        await chat_crud.save_message(
            db=db,
            session_id=session_id,
            role="assistant",
            content=answer,
            sources=sources,
            question_type=question_type
        )
        
        # 如果是第一条消息，自动生成标题
        if len(chat_history) == 0:
            auto_title = user_message[:30] + "..." if len(user_message) > 30 else user_message
            await chat_crud.update_session_title(db, session_id, auto_title)
        
        # 构建响应
        return {
            "code": 200,
            "message": "成功",
            "data": {
                "reply": answer,
                "session_id": session_id,
                "sources": sources,
                "question_type": question_type
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )


@router.post("/chat/new-session")
async def create_new_session(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    创建新的会话
    
    Returns:
        新的 session_id
    """
    session_id = str(uuid.uuid4())
    await chat_crud.create_session(db, user_id, session_id)
    
    return {
        "code": 200,
        "message": "成功",
        "data": {
            "session_id": session_id
        }
    }


@router.get("/chat/sessions")
async def get_sessions(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    skip: int = 0,
    limit: int = 50
):
    """
    获取用户的会话列表
    
    Args:
        skip: 跳过数量
        limit: 限制数量
        
    Returns:
        会话列表
    """
    try:
        sessions = await chat_crud.get_user_sessions(db, user_id, skip, limit)
        
        return {
            "code": 200,
            "message": "成功",
            "data": {
                "sessions": [
                    {
                        "session_id": s.session_id,
                        "title": s.title,
                        "created_at": s.created_at.isoformat(),
                        "updated_at": s.updated_at.isoformat()
                    }
                    for s in sessions
                ],
                "total": len(sessions)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取会话列表失败: {str(e)}"
        )


@router.get("/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    获取会话历史
    
    Args:
        session_id: 会话ID
        
    Returns:
        对话历史列表
    """
    try:
        # 验证会话属于当前用户
        session_record = await chat_crud.get_session(db, session_id)
        if not session_record or session_record.user_id != user_id:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 从数据库获取消息
        messages = await chat_crud.get_session_messages(db, session_id, limit=100)
        
        history = [
            {
                "role": msg.role,
                "content": msg.content,
                "sources": msg.sources,
                "question_type": msg.question_type,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
        
        return {
            "code": 200,
            "message": "成功",
            "data": {
                "session_id": session_id,
                "history": history,
                "message_count": len(history)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取历史失败: {str(e)}"
        )


@router.delete("/chat/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    删除会话
    
    Args:
        session_id: 会话ID
        
    Returns:
        操作结果
    """
    try:
        # 验证会话属于当前用户
        session_record = await chat_crud.get_session(db, session_id)
        if not session_record or session_record.user_id != user_id:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 软删除会话
        success = await chat_crud.delete_session(db, session_id)
        
        # 同时清除 Redis 缓存
        await memory_service.clear_history(session_id)
        
        if success:
            return {
                "code": 200,
                "message": "成功",
                "data": {
                    "session_id": session_id,
                    "deleted": True
                }
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="删除会话失败"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除会话失败: {str(e)}"
        )

