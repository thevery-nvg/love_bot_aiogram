from typing import Optional
import enum
from geoalchemy2 import Geography
from sqlalchemy import (Column, Integer, String, ForeignKey, Boolean, BigInteger, func,
                        DateTime, Enum as SQLAEnum, JSON)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Sex(str, enum.Enum):
    male = "male"
    female = "female"


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now())


class User(Base):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(String, unique=True)

    def __repr__(self):
        return f"User(id={self.id}, username={self.username!r})"


class Questionary(Base):
    __tablename__ = "questionaries"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    sex: Mapped[Sex] = mapped_column(SQLAEnum(Sex), nullable=False)
    find: Mapped[Sex] = mapped_column(SQLAEnum(Sex), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    about: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    photo: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class Location(Base):
    __tablename__ = "locations"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    location: Mapped[Geography] = mapped_column(Geography(geometry_type='POINT', srid=4326))


class City(Base):
    __tablename__ = "cities"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    city: Mapped[str] = mapped_column(String, nullable=False)
