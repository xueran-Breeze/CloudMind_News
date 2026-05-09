from typing import Optional

from pydantic import Field, BaseModel


class NewsBaseResponse(BaseModel):
    """新闻基础响应模型 - 可被收藏和历史记录复用"""
    id: int = Field(..., description="新闻ID")
    title: str = Field(..., description="标题")
    description: str = Field(..., description="描述")
    image: str = Field(..., description="封面图")
    author: str = Field(..., description="作者")
    category_id: int = Field(..., alias="categoryId", description="分类ID")
    views: int = Field(..., description="浏览量")
    publish_time: Optional[str] = Field(None, alias="publishTime", description="发布时间")
    
    model_config = {
        "populate_by_name": True
    }
