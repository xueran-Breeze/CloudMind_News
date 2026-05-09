from typing import List, Optional

from pydantic import Field, BaseModel
from schemas.news import NewsBaseResponse


class AddFavoriteRequest(BaseModel):
    news_id: int = Field(..., alias="newsId", description="新闻ID")
    
    model_config = {
        "populate_by_name": True
    }


class FavoriteNewsResponse(NewsBaseResponse):
    """收藏新闻响应模型 - 继承基础模型并添加收藏时间"""
    favorite_time: Optional[str] = Field(None, alias="favoriteTime", description="收藏时间")


class ListFavoriteResponse(BaseModel):
    list: List[FavoriteNewsResponse] = Field(..., description="收藏列表")
    total: int = Field(..., description="总数")
    has_more: bool = Field(..., alias="hasMore", description="是否有更多")
    
    model_config = {
        "populate_by_name": True
    }
