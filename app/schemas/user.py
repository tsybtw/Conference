from typing import Optional
from datetime import date
from pydantic import BaseModel, EmailStr, validator, Field
from app.models.user import GenderEnum

class UserBase(BaseModel):
    first_name: str
    last_name: str
    gender: GenderEnum
    nationality: str
    organization: str
    position: str
    birth_date: date
    email: EmailStr
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    password_confirm: str
    
    @validator('password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[GenderEnum] = None
    nationality: Optional[str] = None
    organization: Optional[str] = None
    position: Optional[str] = None
    birth_date: Optional[date] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    password_confirm: Optional[str] = None
    
    @validator('password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and values['password'] is not None and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class UserInDB(UserBase):
    id: int
    
    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    pass