from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, ForeignKey


class Base(DeclarativeBase):
    pass
