from typing import Annotated

from geoalchemy2 import Geography
from sqlalchemy import (Column, Integer, String, TIMESTAMP, ForeignKey, Boolean, BigInteger, func,
                        text, DateTime)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

intpk = Annotated[int, mapped_column(Integer, primary_key=True)]


class Base(DeclarativeBase):
    id: Mapped[intpk]
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = Column(String, unique=True)
    age: str
    sex: str
    find: str

    location: Mapped[Geography(geometry_type='POINT', srid=4326)]
    city: str

    name: str
    about: str
    photo: list[str]

    def __repr__(self):
        return f"User(id={self.id}, username={self.username!r}, location={self.location})"
