from typing import Optional
import enum
from geoalchemy2 import Geography
from sqlalchemy import (Integer, String, BigInteger, func,
                        DateTime, Enum as SQLAEnum, JSON)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Sex(str, enum.Enum):
    male = "male"
    female = "female"


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now())


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True)

    age: Mapped[int] = mapped_column(Integer, nullable=True)
    gender: Mapped[Sex] = mapped_column(SQLAEnum(Sex), nullable=True)
    looking_for: Mapped[Sex] = mapped_column(SQLAEnum(Sex), nullable=True)
    name: Mapped[str] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    photos: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    location: Mapped[Geography] = mapped_column(
        Geography(geometry_type='POINT', srid=4326),
        nullable=True
    )
    city: Mapped[str] = mapped_column(String, nullable=True)

    def __repr__(self):
        return f"User(id={self.id}, username={self.username!r})"
