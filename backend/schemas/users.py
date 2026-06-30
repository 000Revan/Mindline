from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class UserRequest(BaseModel):
    username:str=Field(...,title="用户名")
    password:str=Field(...,title="密码")


class UserUpdateRequest(BaseModel):
    nickname:Optional[str]=Field(None,title="昵称")
    gender:Optional[str]=Field(default="unknown",title="性别")
    bio:Optional[str]=Field(None,title="个人简介")

class UserChangePasswordRequest(BaseModel):
    old_password:str=Field(...,title="旧密码")
    new_password:str=Field(...,title="新密码")


class UserInfoBase(BaseModel):
    nickname:Optional[str]=Field(None,title="昵称")
    avatar_url:Optional[str]=Field(None,title="头像URL")
    gender:str=Field(default="unknown",title="性别")
    bio:Optional[str]=Field(None,title="个人简介")

class UserInfoResponse(UserInfoBase):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class UserAuthResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    user: UserInfoResponse=Field(...)

    model_config = ConfigDict(from_attributes=True)
