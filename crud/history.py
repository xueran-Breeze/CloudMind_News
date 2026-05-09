from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News


async def history_add(
        news_id: int,
        user_id: int,
        db: AsyncSession
):
    """
    添加浏览历史记录
    :param news_id: 新闻ID
    :param user_id: 用户ID
    :param db: 数据库会话
    :return: 历史记录对象
    """
    history = History(news_id=news_id, user_id=user_id)
    db.add(history)
    
    try:
        await db.commit()
        await db.refresh(history)
        return history
    except Exception as e:
        await db.rollback()
        raise Exception(f"添加历史记录失败: {str(e)}")


async def history_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10
):
    """
    获取用户历史记录列表
    :param db: 数据库会话
    :param user_id: 用户ID
    :param page: 页码
    :param page_size: 每页数量
    :return: 包含列表、总数和是否有更多的字典
    """
    offset = (page - 1) * page_size
    
    # 查询总数
    count_stmt = select(func.count()).where(History.user_id == user_id)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # 查询历史记录列表，关联新闻表获取新闻详情
    list_stmt = (
        select(News, History.view_time)
        .join(History, News.id == History.news_id)
        .where(History.user_id == user_id)
        .offset(offset)
        .limit(page_size)
        .order_by(History.view_time.desc())
    )
    list_result = await db.execute(list_stmt)
    rows = list_result.all()
    
    # 构建响应数据
    history_list_data = []
    for news, view_time in rows:
        history_list_data.append({
            "id": news.id,
            "title": news.title,
            "description": news.description or "",
            "image": news.image or "",
            "author": news.author or "",
            "categoryId": news.category_id,
            "views": news.views,
            "publishTime": news.publish_time.strftime("%Y-%m-%d %H:%M:%S") if news.publish_time else "",
            "viewTime": view_time.strftime("%Y-%m-%d %H:%M:%S") if view_time else ""
        })

    has_more = (offset + len(history_list_data)) < total
    
    return {
        "list": history_list_data,
        "total": total,
        "hasMore": has_more
    }


async def history_delete(
        history_id: int,
        user_id: int,
        db: AsyncSession
):
    """
    删除单条浏览历史记录
    :param history_id: 历史记录ID
    :param user_id: 用户ID（用于权限验证）
    :param db: 数据库会话
    :return: 是否删除成功
    """
    # 先验证该记录属于当前用户
    query = select(History).where(
        (History.id == history_id) & (History.user_id == user_id)
    )
    result = await db.execute(query)
    history = result.scalar_one_or_none()
    
    if not history:
        return False
    
    # 删除记录
    delete_query = delete(History).where(History.id == history_id)
    await db.execute(delete_query)
    await db.commit()
    return True


async def history_clear(
        user_id: int,
        db: AsyncSession
):
    """
    清空用户所有浏览历史记录
    :param user_id: 用户ID
    :param db: 数据库会话
    :return: 删除的记录数
    """
    query = delete(History).where(History.user_id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount
