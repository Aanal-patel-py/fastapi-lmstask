from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class TaskCreate(BaseModel):
    title: str = Field(min_length=3,max_length=100,description="Task title")
    description: Optional[str] = Field(None,max_length=300,description="Task description")
    due_date: Optional[date] = Field(None,description="Task due date")
    completed: Optional[bool]=Field(False,description="wether task completed or not")

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None,min_length=3,max_length=100)
    description: Optional[str] = None
    due_date: Optional[date] = None
    completed: Optional[bool]=None

class TaskResponse(TaskCreate):
    id: int


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=25)
    email: str
    full_name: str
    age: int
    password: str


class RoleCreate(BaseModel):
    name: str
    description: str | None = None

class RoleResponse(BaseModel):
    id: int
    name: str
    description: str | None

    model_config = {"from_attributes":True}
class UserPublic(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    age: int
    roles:list[RoleResponse]
    model_config = {"from_attributes": True}


class UserInDB(UserPublic):
    hashed_password: str


class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None
    email: str | None = None
    full_name: str | None = None
    age: int | None = None

class ChangeRoleRequest(BaseModel):
    role_id: int