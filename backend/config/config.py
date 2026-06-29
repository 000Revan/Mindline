import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

FILE_PATH=Path(__file__).resolve()
BASE_PATH=FILE_PATH.parent.parent.parent
ENV_PATH=BASE_PATH.joinpath('.env')

load_dotenv(dotenv_path=ENV_PATH)

@dataclass(frozen=True)
class CONFIG:


    # JWT
    secret_key:str
    algorithm:str
    access_token_expire_minutes:int

config=CONFIG(
    secret_key=os.getenv('SECRET_KEY'),
    algorithm=os.getenv('ALGORITHM','HS256'),
    access_token_expire_minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES','30'))
)