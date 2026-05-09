"""
Redis 对话记忆服务
用于存储和检索多轮对话历史
"""
import json
import redis.asyncio as redis
from typing import List, Dict, Any, Optional
from config.ai_conf import REDIS_HOST, REDIS_PORT, REDIS_DB, CONVERSATION_TTL, MAX_HISTORY_ROUNDS


class MemoryService:
    """Redis 对话记忆服务类"""
    
    def __init__(self):
        """初始化 Redis 连接"""
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )
        self.ttl = CONVERSATION_TTL  # 会话过期时间（秒）
        self.max_rounds = MAX_HISTORY_ROUNDS  # 最大保留轮数
    
    async def save_message(self, session_id: str, role: str, content: str) -> bool:
        """
        保存单条消息到会话历史
        
        Args:
            session_id: 会话ID
            role: 角色（"user" 或 "assistant"）
            content: 消息内容
            
        Returns:
            是否保存成功
        """
        try:
            key = f"chat:{session_id}"
            
            # 获取现有历史
            history = await self.get_history(session_id)
            
            # 添加新消息
            history.append({
                "role": role,
                "content": content
            })
            
            # 限制历史记录长度（保留最近 N 轮，每轮 2 条消息）
            max_messages = self.max_rounds * 2
            if len(history) > max_messages:
                history = history[-max_messages:]
            
            # 保存到 Redis
            await self.redis_client.setex(
                key,
                self.ttl,
                json.dumps(history, ensure_ascii=False)
            )
            
            return True
            
        except Exception as e:
            print(f"保存消息失败: {str(e)}")
            return False
    
    async def get_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """
        获取会话历史
        
        Args:
            session_id: 会话ID
            limit: 限制返回的消息数量，None 表示返回所有
            
        Returns:
            消息历史列表
        """
        try:
            key = f"chat:{session_id}"
            data = await self.redis_client.get(key)
            
            if not data:
                return []
            
            history = json.loads(data)
            
            # 如果指定了限制，返回最近的 N 条消息
            if limit:
                return history[-limit:]
            
            return history
            
        except Exception as e:
            print(f"获取历史消息失败: {str(e)}")
            return []
    
    async def clear_history(self, session_id: str) -> bool:
        """
        清空会话历史
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否清空成功
        """
        try:
            key = f"chat:{session_id}"
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"清空历史失败: {str(e)}")
            return False
    
    async def get_session_exists(self, session_id: str) -> bool:
        """
        检查会话是否存在
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否存在
        """
        try:
            key = f"chat:{session_id}"
            exists = await self.redis_client.exists(key)
            return exists > 0
        except Exception as e:
            print(f"检查会话存在性失败: {str(e)}")
            return False
    
    async def get_session_ttl(self, session_id: str) -> int:
        """
        获取会话剩余过期时间
        
        Args:
            session_id: 会话ID
            
        Returns:
            剩余秒数，-1 表示永不过期，-2 表示不存在
        """
        try:
            key = f"chat:{session_id}"
            ttl = await self.redis_client.ttl(key)
            return ttl
        except Exception as e:
            print(f"获取会话 TTL 失败: {str(e)}")
            return -2
    
    async def refresh_session_ttl(self, session_id: str) -> bool:
        """
        刷新会话过期时间
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否刷新成功
        """
        try:
            key = f"chat:{session_id}"
            await self.redis_client.expire(key, self.ttl)
            return True
        except Exception as e:
            print(f"刷新会话 TTL 失败: {str(e)}")
            return False
    
    async def get_active_sessions_count(self) -> int:
        """
        获取活跃会话数量
        
        Returns:
            会话数量
        """
        try:
            keys = await self.redis_client.keys("chat:*")
            return len(keys)
        except Exception as e:
            print(f"获取活跃会话数失败: {str(e)}")
            return 0


# 创建全局单例
memory_service = MemoryService()
