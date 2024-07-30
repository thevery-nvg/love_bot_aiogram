from typing import Optional

from geoalchemy2 import WKTElement
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func, select
from sqlalchemy.dialects.postgresql import insert

from src.database.models import User, Gender


async def add_user_if_not_exists(session: AsyncSession,user_id: int, username: str):
    async with session.begin():
        stmt = insert(User).values(id=user_id, username=username)
        stmt = stmt.on_conflict_do_nothing(index_elements=['user_id'])
        await session.execute(stmt)


async def find_nearby_users(session: AsyncSession,lat: float, lon: float, radius_km: float):
    target_location = f'SRID=4326;POINT({lon} {lat})'
    radius_meters = radius_km * 1000

    async with session.begin():
        result = await session.execute(
            select(User).where(
                func.ST_DWithin(
                    User.location,
                    func.ST_GeogFromText(target_location),
                    radius_meters
                )
            )
        )
        nearby_users = result.scalars().all()

    return nearby_users


async def update_location(session: AsyncSession,user_id: int, lat_str: str, lon_str: str):
    # Unfinished
    try:
        lat = float(lat_str)
        lon = float(lon_str)
    except ValueError:
        raise ValueError("Latitude and longitude must be valid numbers")

    location_wkt = f'POINT({lon} {lat})'

    async with session.begin():
        query = select(User).filter(User.id == user_id)
        result = await session.execute(query)

        try:
            user = result.scalar_one()
            user.location = WKTElement(location_wkt, srid=4326)
        except NoResultFound:
            raise ValueError(f"User with id {user_id} does not exist")

        await session.commit()


async def get_userdata_by_id(session: AsyncSession, user_id: int):
    async with session.begin():
        result = await session.execute(
            select(User).where(
                User.id == user_id)
        )
    return result.scalars().first()


async def get_all_users(session: AsyncSession):
    async with session.begin():
        result = await session.execute(select(User))
    return result.scalars().all()


async def get_all_users_raw(session: AsyncSession):
    async with session.begin():
        result = await session.execute(text("select * from users"))
    return result.all()


async def update_user(session: AsyncSession,
                      user_id: int,
                      age: Optional[int] = None,
                      gender: Optional[Gender] = None,
                      looking_for: Optional[Gender] = None,
                      name: Optional[str] = None,
                      description: Optional[str] = None,
                      photos: Optional[list[str]] = None,
                      latitude: Optional[str] = None,
                      longitude: Optional[str] = None,
                      city: Optional[str] = None, ):
    async with session.begin():
        result = await session.execute(select(User).filter_by(id=user_id))
        user = result.scalar_one_or_none()

        if user is None:
            raise ValueError(f"User with id {user_id} does not exist")

        if age is not None:
            user.age = age
        if gender is not None:
            user.gender = gender
        if looking_for is not None:
            user.looking_for = looking_for
        if name is not None:
            user.name = name
        if description is not None:
            user.description = description
        if photos is not None:
            user.photos = photos
        if latitude is not None and longitude is not None:
            user.location = WKTElement(f'POINT({longitude} {latitude})', srid=4326)
        if city is not None:
            user.city = city
        user.is_registered = True

        await session.commit()
        await session.refresh(user)
        return user
