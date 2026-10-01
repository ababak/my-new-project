from collections.abc import AsyncIterator

import pytest_asyncio
from sqlalchemy import make_url, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from infrastructure.db.base import Base
from infrastructure.settings import get_settings


@pytest_asyncio.fixture(scope="session")
async def engine() -> AsyncIterator[AsyncEngine]:
    url = make_url(get_settings().database_url)
    test_db = f"{url.database}_test"

    admin = create_async_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    async with admin.connect() as conn:
        exists = await conn.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": test_db}
        )
        if not exists:
            await conn.execute(text(f'CREATE DATABASE "{test_db}"'))
    await admin.dispose()

    test_engine = create_async_engine(url.set(database=test_db))
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    await test_engine.dispose()


@pytest_asyncio.fixture
async def session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    # Everything the test does is rolled back, including its own commits (savepoint mode).
    async with engine.connect() as conn:
        outer = await conn.begin()
        async with AsyncSession(bind=conn, join_transaction_mode="create_savepoint") as s:
            yield s
        await outer.rollback()
