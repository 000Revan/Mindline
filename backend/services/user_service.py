from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from database.crud import users
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserChangePasswordRequest
from utils.auth import create_access_token
from utils.security import get_hash_password,verify_password
from sqlalchemy.exc import IntegrityError


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


async def update_user_info(db:AsyncSession, user_id, user_data):
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

        result = await users.update_user(db, user_id,update_data)

        #检查更新
        if result.rowcount==0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        await db.commit()

        #获取一下更新后的用户
        updated_user=await users.get_user_by_id(db, user_id)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return UserInfoResponse.model_validate(updated_user)
    except HTTPException:
        raise
    except Exception:
        await db.rollback()
        raise


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
