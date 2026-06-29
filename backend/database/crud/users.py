from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User


# 根据用户名查询数据库
async def get_user_by_username(db: AsyncSession, username: str):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()


# 创建用户
async def create_user(db: AsyncSession, username: str, password_hash: str):
    user = User(username=username, password_hash=password_hash)
    db.add(user)
    await db.flush()
    return user


# 根据用户ID查询数据库
async def get_user_by_id(db: AsyncSession, user_id: int):
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


# 更新用户信息
async def update_user(db: AsyncSession, user_id: int, user_data: dict):
    query = update(User).where(User.id == user_id).values(**user_data)
    result=await db.execute(query)
    return result


# 修改密码
async def update_password(db: AsyncSession,user_id, password_hash: str):
    query=update(User).where(User.id == user_id).values(password_hash=password_hash)
    result=await db.execute(query)
    return result