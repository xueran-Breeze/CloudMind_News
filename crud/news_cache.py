from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from cache.news_cache import get_cached_categories, set_cache_categories, get_cached_news_list, set_cache_news_list, get_cached_news_detail, set_cache_news_detail
from models.news import Category, News


async def get_categories(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
):
    # 先尝试从缓存中获取数据
    cached_categories = await get_cached_categories()
    if cached_categories:
        return cached_categories

    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()

    # 将 SQLAlchemy 模型对象转换为字典列表
    if categories:
        # 使用列表推导式手动转换为字典
        cached_categories = [
            {
                "id": category.id,
                "name": category.name,
                "sort_order": category.sort_order
            }
            for category in categories
        ]
        # 写入缓存
        await set_cache_categories(cached_categories)

    # 返回数据
    return cached_categories

async def get_news_list(
        db: AsyncSession,
        category_id: int,
        skip: int = 0,
        limit: int = 10
):
    # 计算页码
    page = (skip // limit) + 1 if limit > 0 else 1
    
    # 先尝试从缓存中获取数据
    cached_news_list = await get_cached_news_list(category_id, page, limit)
    if cached_news_list:
        return cached_news_list

    # 查询指定分类下的所有新闻
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()

    # 将 SQLAlchemy 模型对象转换为字典列表
    if news_list:
        news_list_dict = [
            {
                "id": news.id,
                "title": news.title,
                "description": news.description,
                "image": news.image,
                "author": news.author,
                "publishTime": news.publish_time.isoformat() if news.publish_time else None,
                "categoryId": news.category_id,
                "views": news.views
            }
            for news in news_list
        ]
        # 写入缓存
        await set_cache_news_list(category_id, page, limit, news_list_dict)
        return news_list_dict

    return []


async def get_news_count(
        db: AsyncSession,
        category_id: int
):
    # 查询指定分类下的新闻总数
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)

    return result.scalar_one()  # 只能有一个结果


async def get_news_detail(
        db: AsyncSession,
        news_id: int
):
    # 先尝试从缓存中获取数据
    cached_news_detail = await get_cached_news_detail(news_id)
    if cached_news_detail:
        return cached_news_detail

    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    news = result.scalar_one_or_none()
    
    if news:
        # 将 SQLAlchemy 模型对象转换为字典
        news_detail_dict = {
            "id": news.id,
            "title": news.title,
            "content": news.content,
            "image": news.image,
            "author": news.author,
            "publishTime": news.publish_time.isoformat() if news.publish_time else None,
            "categoryId": news.category_id,
            "views": news.views
        }
        # 写入缓存
        await set_cache_news_detail(news_id, news_detail_dict)
        return news_detail_dict
    
    return None
