from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from database.models import User
from schemas.users import UserRequest, UserUpdateRequest, UserChangePasswordRequest
from services import user_service
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/user", tags=['用户相关'])


# 用户注册
@router.post("/register")
async def register(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 用户注册接口
    data = await user_service.register(db, user_data)
    return success_response(msg="注册成功",data=data)



# 用户登录
@router.post("/login")
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    data = await user_service.login(db, user_data)
    return success_response(msg="登录成功",data=data)

# 获取用户信息(ID查询)
@router.get("/info")
async def get_user_info(user_data:User= Depends(get_current_user)):
    return success_response(msg="获取用户信息成功",data=user_data)

#修改用户信息
@router.put("/update")
async def update_user_info(
        user_data:UserUpdateRequest,
        user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_db)
):
    data=await user_service.update_user_info(db,user.id,user_data)
    return success_response(msg="修改用户信息成功",data=data)

#修改密码
@router.put("/password")
async def update_password(
        password_data:UserChangePasswordRequest,
        user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_db)
):
    await user_service.update_password(db,user.id,password_data)
    return success_response(msg="修改密码成功",data=None)