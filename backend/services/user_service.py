from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.concurrency import run_in_threadpool

from database.crud import users
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserChangePasswordRequest, UserUpdateRequest
from utils.auth import create_access_token
from utils.security import get_hash_password,verify_password
from sqlalchemy.exc import IntegrityError



AVATAR_DIR = Path(__file__).resolve().parents[1] / "static" / "avatars"

ALLOWED_AVATAR_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

MAX_AVATAR_SIZE = 2 * 1024 * 1024





#用户注册
async def register(db: AsyncSession, user_data:UserRequest):
    try:
        # 验证用户是否存在
        existing_user = await users.get_user_by_username(db, user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户已存在"
            )

        # 密码加密
        password_hash = get_hash_password(user_data.password)
        # 创建用户
        user=await users.create_user(
            db=db,
            username=user_data.username,
            password_hash=password_hash
        )
        await db.commit()
        await db.refresh(user)

        access_token = create_access_token(
            {
                "sub": str(user.id),
                "username": user.username
            }
        )

        return UserAuthResponse(
            token=access_token,
            user=UserInfoResponse.model_validate(user)
        )

    except HTTPException:
        raise
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已存在",
        )
    except Exception:
        await db.rollback()
        raise

#用户登录
async def login(db:AsyncSession, user_data:UserRequest):
    user = await users.get_user_by_username(db, user_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或密码错误"
        )
    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或密码错误"
        )
    access_token=create_access_token(
        {
            "sub":str(user.id),
            "username":user.username
        }
    )

    return UserAuthResponse(
        token=access_token,
        user=UserInfoResponse.model_validate(user)
    )

#修改用户信息
async def update_user_info(
        db:AsyncSession,
        user_id: int,
        user_data: UserUpdateRequest
):
    try:
        update_data=user_data.model_dump(
            exclude_unset=True,
            exclude_none=True
        )
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有需要修改的字段"
            )

        user=await users.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        await users.update_user(db, user_id,update_data)

        await db.refresh(user)
        result=UserInfoResponse.model_validate(user)
        await db.commit()
        return result

    except Exception:
        await db.rollback()
        raise


#修改用户头像
async def upload_user_avatar(
    db: AsyncSession,
    user_id: int,
    file: UploadFile,
) -> UserInfoResponse:
    """校验并保存用户头像，同时更新数据库头像地址。"""

    suffix = ALLOWED_AVATAR_TYPES.get(file.content_type or "")
    if suffix is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持 jpg、png、webp、gif 格式头像",
        )

    # 多读取一个字节，用于判断文件是否超过限制。
    content = await file.read(MAX_AVATAR_SIZE + 1)
    await file.close()

    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="头像文件不能超过 2MB",
        )

    user = await users.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    old_avatar_url = user.avatar_url
    filename = f"user_{user_id}_{uuid4().hex}{suffix}"
    target_path = AVATAR_DIR / filename
    avatar_url = f"/static/avatars/{filename}"

    try:
        AVATAR_DIR.mkdir(parents=True, exist_ok=True)
        await run_in_threadpool(target_path.write_bytes, content)

        await users.update_user_avatar(
            db=db,
            user_id=user_id,
            avatar_url=avatar_url,
        )

        await db.refresh(user)
        result = UserInfoResponse.model_validate(user)
        await db.commit()

    except Exception:
        await db.rollback()

        if target_path.exists():
            await run_in_threadpool(target_path.unlink)

        raise

    # 新头像和数据库均更新成功后，再清理旧头像。
    if old_avatar_url and old_avatar_url.startswith("/static/avatars/"):
        old_path = AVATAR_DIR / Path(old_avatar_url).name

        if old_path.exists() and old_path != target_path:
            try:
                await run_in_threadpool(old_path.unlink)
            except OSError:
                # 清理旧文件失败不能影响已经成功的头像更新。
                pass

    return result



#修改用户密码
async def update_password(db: AsyncSession, user_id: int, password_data: UserChangePasswordRequest):
    try:
        user=await users.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        if not verify_password(password_data.old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码错误"
            )

        if verify_password(password_data.new_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密码不能和旧密码相同",
            )
        new_password_hash=get_hash_password(password_data.new_password)
        result=await users.update_password(db=db, user_id=user_id, password_hash=new_password_hash)
        if result.rowcount==0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        await db.commit()
    except HTTPException:
        raise
    except Exception:
        await db.rollback()
        raise
