from fastapi import HTTPException,status
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News
from schemas.favorite import FavoriteNewsResponse


async def is_favourite(
    news_id: int,
    db: AsyncSession,
    user_id: int
):
    query = select(Favorite).where((Favorite.news_id == news_id) & (Favorite.user_id == user_id))
    result = await db.execute(query)
    is_favorite = result.scalar_one_or_none() is not None
    return {"isFavorite": is_favorite}

async def favorite_add(
    news_id: int,
    db: AsyncSession,
    user_id: int
):

    query = select(Favorite).where((Favorite.news_id == news_id) & (Favorite.user_id == user_id))
    result = await db.execute(query)
    is_favorite = result.scalar_one_or_none()
    if is_favorite:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该新闻已收藏")
    favorite=Favorite(news_id=news_id,user_id=user_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

async def favorite_delete(
    news_id: int,
    db: AsyncSession,
    user_id: int
):
    query = select(Favorite).where((Favorite.news_id == news_id) & (Favorite.user_id == user_id))
    result = await db.execute(query)
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该新闻未收藏")

    query = delete(Favorite).where((Favorite.news_id == news_id) & (Favorite.user_id == user_id))
    await db.execute(query)
    await db.commit()
    return True

async def favorite_list(
        db: AsyncSession,
        user_id: int,
        page: int,
        page_size: int
):
    offset = (page - 1) * page_size

    count_stmt = select(func.count()).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    list_stmt = (
        select(News, Favorite.created_at)
        .join(Favorite, News.id == Favorite.news_id)
        .where(Favorite.user_id == user_id)
        .offset(offset)
        .limit(page_size)
        .order_by(Favorite.created_at.desc())
    )
    list_result = await db.execute(list_stmt)
    rows = list_result.all()

    favorite_list = []
    for news, favorite_created_at in rows:
        favorite_list.append({
            "id": news.id,
            "title": news.title,
            "description": news.description,
            "image": news.image,
            "author": news.author,
            "publishTime": news.publish_time.strftime("%Y-%m-%d %H:%M:%S") if news.publish_time else "",
            "categoryId": news.category_id,
            "views": news.views,
            "favoriteTime": favorite_created_at.strftime("%Y-%m-%d %H:%M:%S") if favorite_created_at else ""
        })

    has_more = (offset + len(favorite_list)) < total

    return {"list": favorite_list, "total": total, "hasMore": has_more}

async def favorite_clear(
    db: AsyncSession,
    user_id: int
):
    query = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(query)
    await db.commit()
    if result.rowcount > 0:
        return True
    else:
        return False

