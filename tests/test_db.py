from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def test_session_reaches_postgres(session: AsyncSession) -> None:
    assert await session.scalar(text("SELECT 1")) == 1
