from typing import Optional

from geoalchemy2 import WKTElement
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import and_
from src.database.models import User, Gender, Like


async def get_or_create_user(session: AsyncSession, user_id: int, username: str):
    async with session.begin():
        stmt = insert(User).values(id=user_id, username=username)
        stmt = stmt.on_conflict_do_nothing(index_elements=['user_id'])
        await session.execute(stmt)
        user = await session.get(User, user_id)
        stmt = insert(Like).values(user_id=user_id)
        await session.execute(stmt)
        return user


async def get_nearby_users(session: AsyncSession,
                           lat: float, lon: float,
                           radius_km: float,
                           gender: Gender):
    target_location = f'SRID=4326;POINT({lon} {lat})'
    radius_meters = radius_km * 1000

    async with session.begin():
        result = await session.execute(
            select(User).where(
                and_(
                    User.frozen == False,
                    User.gender == gender,
                    func.ST_DWithin(
                        User.location,
                        func.ST_GeogFromText(target_location),
                        radius_meters
                    )
                )
            )
        )
        nearby_users = result.scalars().all()

    return nearby_users


async def get_same_city_users(session: AsyncSession,
                              city: str,
                              gender: Gender):
    async with session.begin():
        result = await session.execute(
            select(User).where(
                and_(
                    User.frozen == False,
                    User.gender == gender,
                    User.city == city
                )
            )
        )
        same_city_users = result.scalars().all()

    return same_city_users


async def update_location(session: AsyncSession,
                          user_id: int,
                          latitude: Optional[float] = None,
                          longitude: Optional[float] = None,
                          city: Optional[str] = None, ):
    async with session.begin():
        user = await session.get(User, user_id)
    if latitude is not None and longitude is not None:
        user.location = WKTElement(f'POINT({longitude} {latitude})', srid=4326)
    if city is not None:
        user.city = city
    await session.commit()


async def get_nearby_and_same_city_users(session: AsyncSession,
                                         lat: float, lon: float,
                                         radius_km: float,
                                         city: str,
                                         gender: Gender):
    nearby_users = await get_nearby_users(session, lat, lon, radius_km, gender)
    same_city_users = await get_same_city_users(session, city, gender)

    combined_users = {user.id: user for user in nearby_users}
    for user in same_city_users:
        if user.id not in combined_users:
            combined_users[user.id] = user

    ordered_users = list(combined_users.values())[:100]

    return ordered_users


async def get_user(session: AsyncSession, user_id: int):
    async with session.begin():
        try:
            user = await session.get(User, user_id)
        except NoResultFound:
            return None
    return user


async def freeze_user(session: AsyncSession, user_id: int):
    async with session.begin():
        user = await session.get(User, user_id)
        user.frozen = True
        await session.commit()


async def unfreeze_user(session: AsyncSession, user_id: int):
    async with session.begin():
        user = await session.get(User, user_id)
        user.frozen = False
        await session.commit()


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
        user = session.get(User, user_id)
        user.age = age
        user.gender = gender
        user.looking_for = looking_for
        user.name = name
        user.description = description
        user.photos = photos
        if latitude is not None and longitude is not None:
            user.location = WKTElement(f'POINT({longitude} {latitude})', srid=4326)
        if city is not None:
            user.city = city
        user.is_registered = True
        await session.commit()
        await session.refresh(user)
        return user


async def calculate_distance(session: AsyncSession, user1: User, user2: User) -> float:
    if not user1.location or not user2.location:
        raise ValueError("Один из пользователей не имеет координат.")

    distance_query = select([
        func.ST_Distance(user1.location, user2.location)
    ])

    distance = await session.execute(distance_query)
    return distance.scalar()
