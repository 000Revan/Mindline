from datetime import datetime, timezone, timedelta
from typing import Any

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

import jwt
from jwt import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from database.crud import users
from database.database import get_db
from schemas.users import  UserInfoResponse

# 密钥
SECRET_KEY = "65c748a670a40a228bce5efe6c29d199d046aa1793e8fe6147ac4aca490cdebd"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# 生成Token
def create_access_token(data: dict[str, Any]) -> str:
    """
    创建访问令牌
    :param data:内容
    :return: TOKEN
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # 设置过期时间

    payload = data.copy()

    payload.update(
        {
            "type": "access",  # 设置令牌类型
            "iat": now,  # 设置签发时间
            "exp": expire,  # 设置过期时间
        }
    )  # 设置过期时间
    encode_jwt = jwt.encode(
        payload,  # 要通过TOKEN传输的内容
        SECRET_KEY,  # JWT签名的密钥
        algorithm=ALGORITHM  # JWT的加密算法
    )
    return encode_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "access":
            return None
        return payload
    except PyJWTError:
        return None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")


# 获取验证Token
async def get_current_user(
        db: AsyncSession=Depends(get_db),
        token: str = Depends(oauth2_scheme)
):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录状态无效或已过期",
        )
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录状态无效或已过期",
        )

    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录状态无效或已过期",
        )

    user = await users.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )
    return UserInfoResponse.model_validate(user)
