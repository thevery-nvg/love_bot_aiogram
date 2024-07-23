from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from src.database.models import User, Base


async def first_access(user_id, username, session: AsyncSession):
    async with session.begin():
        stmt = insert(User).values(id=user_id, username=username)
        stmt = stmt.on_conflict_do_nothing(index_elements=['id'])
        await session.execute(stmt)
        await session.commit()


async def find_nearby_users(lat, lon, radius_km, session: AsyncSession):
    target_location = f'SRID=4326;POINT({lon} {lat})'
    radius_meters = radius_km * 1000
    async with session.begin():
        result = await session.execute(select(User).where(
            func.ST_DWithin(
                User.location,
                func.ST_GeogFromText(target_location),
                radius_meters
            )
        ))
        nearby_users = result.scalars().all()
    return nearby_users


async def get_user(user_id: int, session: AsyncSession):
    async with session.begin():
        result = await session.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_all_users(session: AsyncSession):
    async with session.begin():
        query = select(User)
        result = await session.execute(query)
    return result.scalars().all()


async def get_all_users_raw(session: AsyncSession):
    async with session.begin():
        query = text("select * from users")
        result = await session.execute(query)
    return result.all()


async def init_db(session: AsyncSession):
    async with session.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
