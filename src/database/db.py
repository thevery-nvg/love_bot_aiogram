from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func, select
from sqlalchemy.dialects.postgresql import insert

from src.database.models import User, Base, Location, Questionary, City


async def add_user_if_not_exists(user_id: int, username: str, session: AsyncSession):
    async with session.begin():
        stmt = insert(User).values(id=user_id, username=username)
        stmt = stmt.on_conflict_do_nothing(index_elements=['id'])
        await session.execute(stmt)


async def find_nearby_users(lat: float, lon: float, radius_km: float, session: AsyncSession):
    target_location = f'SRID=4326;POINT({lon} {lat})'
    radius_meters = radius_km * 1000
    async with session.begin():
        result = await session.execute(
            select(User).join(Location, User.id == Location.user_id).where(
                func.ST_DWithin(
                    Location.location,
                    func.ST_GeogFromText(target_location),
                    radius_meters
                )
            )
        )
        nearby_users = result.scalars().all()
    return nearby_users


async def get_userdata_by_id(user_id: int, session: AsyncSession):
    async with session.begin():
        result = await session.execute(
            select(User).join(
                Location, User.id == Location.user_id
            ).join(Questionary, User.id == Questionary.user_id).where(
                User.id == user_id
            )
        )
    return result.scalars().first()


async def get_user_by_id(user_id: int, session: AsyncSession):
    async with session.begin():
        result = await session.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_all_users(session: AsyncSession):
    async with session.begin():
        result = await session.execute(select(User))
    return result.scalars().all()


async def get_all_users_raw(session: AsyncSession):
    async with session.begin():
        result = await session.execute(text("select * from users"))
    return result.all()


async def init_db(session: AsyncSession):
    async with session.begin():
        await session.run_sync(Base.metadata.create_all)
