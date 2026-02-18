from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Boolean, Integer, Date

class Base(DeclarativeBase):
    pass

class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

class User(Base):
    __tablename__ = "tbl_user"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    firstname: Mapped[str] = mapped_column(String(50), nullable=False)
    lastname: Mapped[str] = mapped_column(String(50), nullable=False)
    dateOfBirth: Mapped["Date"] = mapped_column(Date, nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)

    # Store a hash, not plaintext. (Even for quick projects, this is worth it.)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
