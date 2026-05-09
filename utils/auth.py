from fastapi import Header, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import users


# 整合 根据 Token 查询用户，返回用户
async def get_current_user(
        authorization: str = Header(...,alias="Authorization"),
        db: AsyncSession = Depends(get_db)
):
    #Bearer + token
    #token=authorization.split(" ")[1]
    token=authorization.replace("Bearer ", "")
    user=await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return user


# 获取当前用户ID（便捷函数）
async def get_current_user_id(
        authorization: str = Header(..., alias="Authorization"),
        db: AsyncSession = Depends(get_db)
) -> int:
    """
    获取当前登录用户的ID
    
    Returns:
        用户ID
    """
    token = authorization.replace("Bearer ", "")
    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return user.id