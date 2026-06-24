from passlib.context import CryptContext

# 创建密码上下文
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

#密码加密
def get_hash_password(password: str):
    """
    密码加密
    :param password:明文密码
    :return:加密后的密码
    """
    return pwd_context.hash(password)

#验证密码
def verify_password(plain_password, hashed_password):
    """
    验证密码
    :param plain_password:明文密码
    :param hashed_password:密文密码
    :return:如果验证成功，返回True，否则返回False
    """
    return pwd_context.verify(plain_password, hashed_password)
