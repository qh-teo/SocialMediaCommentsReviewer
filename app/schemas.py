from __future__ import annotations

from pydantic import BaseModel, Field, EmailStr
from datetime import date

class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)

class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    completed: bool | None = None

class TodoOut(BaseModel):
    id: int
    title: str
    completed: bool

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    firstname: str = Field(min_length=1, max_length=50)
    lastname: str = Field(min_length=1, max_length=50)
    dateOfBirth: date
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

class UserOut(BaseModel):
    user_id: int
    username: str
    firstname: str
    lastname: str
    dateOfBirth: date
    email: EmailStr

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username_or_email: str
    password: str = Field(min_length=8, max_length=72)


class LoginResponse(BaseModel):
    ok: bool
    user: UserOut
