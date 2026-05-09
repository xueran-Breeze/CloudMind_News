from typing import List, Optional

from pydantic import BaseModel, Field
from schemas.news import NewsBaseResponse


class UserAddHistory(BaseModel):
    """添加历史记录请求模型"""
    news_id: int = Field(..., alias="newsId", description="新闻ID")
    
    model_config = {
        "populate_by_name": True
    }


class HistoryNewsResponse(NewsBaseResponse):
    """历史新闻响应模型 - 继承基础模型并添加浏览时间"""
    view_time: Optional[str] = Field(None, alias="viewTime", description="浏览时间")


class ListHistoryResponse(BaseModel):
    """历史记录列表响应模型"""
    list: List[HistoryNewsResponse] = Field(..., description="历史记录列表")
    total: int = Field(..., description="总数")
    has_more: bool = Field(..., alias="hasMore", description="是否有更多")
    
    model_config = {
        "populate_by_name": True
    }
