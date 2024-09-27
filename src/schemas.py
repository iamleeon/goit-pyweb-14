from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class ContactBase(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: str = Field(max_length=320)
    phone: str = Field(max_length=15)
    birthday: date
    additional_info: Optional[str] = Field(None, max_length=350)


class ContactCreate(ContactBase):
    pass  # All fields are inherited from ContactBase


class ContactUpdate(BaseModel):
    first_name: Optional[str] = Field(max_length=50)
    last_name: Optional[str] = Field(max_length=50)
    email: Optional[str] = Field(max_length=320)
    phone: Optional[str] = Field(max_length=15)
    birthday: Optional[date]
    additional_info: Optional[str] = Field(None, max_length=350)


class ContactResponse(ContactBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=100)
    email: str
    password: str = Field(min_length=6, max_length=100)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User has been successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
