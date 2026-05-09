

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud.favorite import is_favourite, favorite_add, favorite_delete, favorite_list, favorite_clear
from models.users import User
from schemas.favorite import AddFavoriteRequest, ListFavoriteResponse
from utils.auth import get_current_user
from utils.response import success_response

router=APIRouter(prefix="/api/favorite",tags=["favourite"])



@router.get("/check")
async def check_favorite(
    news_id:int = Query(...,alias="newsId"),
    db:AsyncSession=Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = await is_favourite(news_id,db,user.id)

    if result["isFavorite"]:
        return success_response("已收藏该新闻",data=result)
    return success_response("未收藏该新闻",data=result)


@router.post("/add")
async def add_favorite(
    news: AddFavoriteRequest,
    user:User = Depends(get_current_user),
    db:AsyncSession = Depends(get_db),
):
    result = await favorite_add(news.news_id, db, user.id)
    return success_response("收藏成功", data={
        "id": result.id,
        "userId": result.user_id,
        "newsId": result.news_id,
        "createTime": result.created_at.strftime("%Y-%m-%d %H:%M:%S") if result.created_at else ""
    })

@router.delete("/remove")
async def remove_favorite(
    news_id:int = Query(...,alias="newsId"),
    user:User = Depends(get_current_user),
    db:AsyncSession = Depends(get_db)
):
    if await favorite_delete(news_id,db,user.id):
        return success_response("取消收藏成功")
    return success_response("取消收藏失败")


@router.get("/list")
async def get_favorite_list(
    page:int = Query(1,ge=1),
    page_size:int = Query(10,alias="pageSize",le=100),
    user:User = Depends(get_current_user),
    db:AsyncSession = Depends(get_db)
):
    data = await favorite_list(db,user.id,page,page_size)
    return success_response("获取收藏列表成功",data=data)

@router.delete("/clear")
async def clear_favorite(
    user:User = Depends(get_current_user),
    db:AsyncSession = Depends(get_db)
):
    count = await favorite_clear(db, user.id)
    if count > 0:
        return success_response(f"成功删除{count}条收藏记录")
    else:
        return success_response("没有收藏记录可删除")