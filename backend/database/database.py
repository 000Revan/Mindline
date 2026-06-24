from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config.db_config import DB_URL

print(DB_URL)
engine=create_async_engine(
    DB_URL,
    echo=True,
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600
)

AsyncSessionFactory=async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionFactory() as session:
        yield session
