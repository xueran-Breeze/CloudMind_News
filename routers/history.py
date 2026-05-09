from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud.history import history_add, history_list, history_delete, history_clear
from models.users import User
from schemas.history import UserAddHistory
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/history", tags=["history"])


@router.post("/add")
async def add_history(
    history_request: UserAddHistory,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    添加浏览历史记录
    """
    data = await history_add(history_request.news_id, user.id, db)
    return success_response("添加成功", data={
        "id": data.id,
        "userId": data.user_id,
        "newsId": data.news_id,
        "viewTime": data.view_time.strftime("%Y-%m-%d %H:%M:%S") if data.view_time else ""
    })


@router.get("/list")
async def get_history_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, alias="pageSize", le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户浏览历史记录列表
    """
    data = await history_list(db, user.id, page, page_size)
    return success_response("获取历史记录成功", data=data)


@router.delete("/delete/{history_id}")
async def delete_history(
    history_id: int = Path(..., description="历史记录ID"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除单条浏览历史记录
    """
    result = await history_delete(history_id, user.id, db)
    if result:
        return success_response("删除成功")
    else:
        return success_response("删除失败，记录不存在或无权操作")


@router.delete("/clear")
async def clear_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    清空用户所有浏览历史记录
    """
    count = await history_clear(user.id, db)
    return success_response(f"清空成功，共删除{count}条记录")