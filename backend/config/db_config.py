import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

FILE_PATH=Path(__file__).resolve()
BASE_PATH=FILE_PATH.parent.parent.parent
ENV_PATH=BASE_PATH.joinpath('.env')

load_dotenv(dotenv_path=ENV_PATH)

@dataclass(frozen=True)
class DBCONFIG:
    select_db: str
    driver: str
    host: str
    port: int
    user: str
    password: str
    database: str
    charset: str = "utf8mb4"

    def db_url(self):
        return f"{self.select_db}+{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?charset={self.charset}"

DB_CONFIG=DBCONFIG(
    select_db=os.getenv('DB_SELECT'),
    driver=os.getenv('DB_DRIVER'),
    host=os.getenv('DB_HOST'),
    port=int(os.getenv('DB_PORT')),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME'),
    charset=os.getenv('DB_CHARSET')
)

DB_URL=DB_CONFIG.db_url()


if __name__ == '__main__':
    # print(FILE_PATH)
    # print(BASE_PATH)
    # print(ENV_PATH)
    print(DB_URL)