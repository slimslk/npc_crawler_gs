from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config.settings import settings


class DBHelper:
    def __init__(
            self,
            url: str,
            echo: bool = False,
            echo_pool: bool = False,
            pool_size: int = 5,
            max_overflow: int = 10,
            current_schema: str = "public",
    ) -> None:

        print(f"MER: {type(current_schema)}")
        self.engine = create_async_engine(url,
                                          echo=echo,
                                          echo_pool=echo_pool,
                                          pool_size=pool_size,
                                          max_overflow=max_overflow,
                                          connect_args={"server_settings": {
                                              "search_path": current_schema
                                          }
                                          }
                                          )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        await self.engine.dispose()

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session


db_helper = DBHelper(
    url=settings.db.url,
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
    current_schema=settings.db.current_schema,
)
