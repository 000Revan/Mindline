from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from database.database import get_db
from database.models import User
from schemas.users import UserRequest, UserUpdateRequest, UserChangePasswordRequest
from services import user_service
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/user", tags=['用户相关'])

AVATAR_DIR = Path(__file__).resolve().parents[1] / "static" / "avatars"
ALLOWED_AVATAR_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
MAX_AVATAR_SIZE = 2 * 1024 * 1024

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

#上传头像
@router.post("/avatar")
async def upload_avatar(
        file: UploadFile = File(...),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    suffix = ALLOWED_AVATAR_TYPES.get(file.content_type or "")
    if not suffix:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持 jpg、png、webp、gif 格式头像",
        )

    content = await file.read()
    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="头像文件不能超过 2MB",
        )

    AVATAR_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"user_{user.id}_{uuid4().hex}{suffix}"
    target_path = AVATAR_DIR / filename
    target_path.write_bytes(content)

    avatar_url = f"/static/avatars/{filename}"
    data = await user_service.update_user_info(
        db,
        user.id,
        UserUpdateRequest(avatar_url=avatar_url),
    )
    return success_response(msg="头像上传成功", data=data)
