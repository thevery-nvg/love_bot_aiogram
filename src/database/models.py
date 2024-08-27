from typing import Optional
import enum
from geoalchemy2 import Geography
from sqlalchemy import (Integer, String, BigInteger, func,
                        DateTime, Enum as SQLAEnum, JSON, Boolean, ForeignKey)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Gender(str, enum.Enum):
    male = "male"
    female = "female"
    anything = "anything"


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now())


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True)

    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender: Mapped[Optional[Gender]] = mapped_column(SQLAEnum(Gender), nullable=True)
    looking_for: Mapped[Optional[Gender]] = mapped_column(SQLAEnum(Gender), nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    photos: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)

    location: Mapped[Optional[Geography]] = mapped_column(
        Geography(geometry_type='POINT', srid=4326), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_registered: Mapped[bool] = mapped_column(Boolean, default=False)
    frozen: Mapped[bool] = mapped_column(Boolean, default=False)

    liker: Mapped[list[int]] = mapped_column(JSON, defalut=list())
    liked_by: Mapped[list[int]] = mapped_column(JSON, defalut=list())
    matched_with: Mapped[list[int]] = mapped_column(JSON, defalut=list())

    def __repr__(self):
        return f"User(id={self.id}, username={self.username!r})"

