# app/schemas.py

from pydantic import BaseModel, EmailStr
from typing import List


class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool

class UserPreferencesBase(BaseModel):
    job_title: str
    location: str
    skills: str

class UserPreferencesCreate(UserPreferencesBase):
    pass

class UserPreferencesResponse(UserPreferencesBase):
    id: int
    user_id : int

class Job(BaseModel):
    title: str
    company: str
    location: str
    url: str

class JobListingResponse(BaseModel):
    jobs: List[Job]

    class Config:
        from_attributes = True

