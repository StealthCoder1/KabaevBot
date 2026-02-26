from sqlalchemy import select

from db.connect import async_session
from db.models import User, Lead


async def get_all_users() -> list[User]:
    async with async_session() as session:
        result = await session.execute(select(User))
        return list(result.scalars().all())


async def get_latest_leads(limit: int = 10) -> list[Lead]:
    async with async_session() as session:
        result = await session.execute(
            select(Lead).order_by(Lead.created_at.desc(), Lead.id.desc()).limit(limit)
        )
        return list(result.scalars().all())
