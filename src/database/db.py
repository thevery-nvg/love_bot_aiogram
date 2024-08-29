from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import and_
from src.database.models import User, Gender
from random import shuffle, sample
from aiogram.types import Location
from shapely.geometry import Point
from geoalchemy2.shape import from_shape


async def get_or_create_user(session: AsyncSession, user_id: int, username: str):
    async with session.begin():
        stmt = insert(User).values(id=user_id, username=username)
        stmt = stmt.on_conflict_do_nothing(index_elements=['user_id'])
        await session.execute(stmt)
        user = await session.scalar(select(User).where(User.id == user_id))
        return user


async def get_nearby_users(session: AsyncSession,
                           location: Location,
                           radius_km: float,
                           gender: Gender):
    target_location = Point(location.longitude, location.latitude)
    target_location = from_shape(target_location, srid=4326)
    radius_meters = radius_km * 1000
    async with session.begin():
        result = await session.execute(
            select(User).where(
                and_(
                    User.frozen is False,
                    User.gender == gender,
                    func.ST_DWithin(
                        User.location,
                        target_location,
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
                    User.frozen is False,
                    User.gender == gender,
                    User.city == city
                )
            )
        )
        same_city_users = result.scalars().all()

    return same_city_users


async def get_nearby_and_same_city_users(session: AsyncSession,
                                         location: Location,
                                         radius_km: float,
                                         city: str,
                                         gender: Gender):
    nearby_users = await get_nearby_users(session, location, radius_km, gender)
    same_city_users = await get_same_city_users(session, city, gender)

    combined_users = {user.id: user for user in nearby_users}
    for user in same_city_users:
        if user.id not in combined_users:
            combined_users[user.id] = user

    ordered_users = list(combined_users.values())[:100]
    shuffle(ordered_users)
    return ordered_users


async def get_user(session: AsyncSession, user_id: int):
    async with session.begin():
        try:
            user = await session.get(User, user_id)
        except NoResultFound:
            return None
    return user


async def freeze_user(session: AsyncSession, user: User):
    async with session.begin():
        user.frozen = True
        await session.commit()
    return user


async def unfreeze_user(session: AsyncSession, user: User):
    async with session.begin():
        user.frozen = False
        await session.commit()
    return user


async def calculate_distance(session: AsyncSession, user1: User, user2: User) -> float:
    if not user1.location or not user2.location:
        raise ValueError("Один из пользователей не имеет координат.")

    distance_query = select([
        func.ST_Distance(user1.location, user2.location)
    ])

    distance = await session.execute(distance_query)
    return distance.scalar()


async def get_random_photos(session: AsyncSession):
    async with session.begin():
        count = await session.execute(select(User.id))
        total_count = count.scalar()
        random_indices = sample(range(total_count), 200)
        result = await session.execute(
            select(User.photos).where(User.id.in_(random_indices))
        )
        photos = result.scalars().all()
    return photos


async def update_user(session: AsyncSession, user: User, **kwargs) -> User:
    async with session.begin():
        for key, value in kwargs.items():
            match key:
                case "username":
                    user.username = value
                case "age":
                    user.age = value
                case "gender":
                    user.gender = value
                case "looking_for":
                    user.looking_for = value
                case "name":
                    user.name = value
                case "description":
                    user.description = value
                case "photos":
                    user.photos = value
                case "location":
                    if value:
                        point = Point(value.longitude, value.latitude)
                        user.location = from_shape(point, srid=4326)
                    else:
                        user.location = None
                case "city":
                    user.city = value
                case "is_registered":
                    user.is_registered = value
                case "frozen":
                    user.frozen = value
                case "liker":
                    user.liker = value
                case "liked_by":
                    user.liked_by = value
                case "matched_with":
                    user.matched_with = value
                case _:
                    raise ValueError(f"Неизвестное поле {key}")
        await session.commit()
        await session.refresh(user)
        return user
