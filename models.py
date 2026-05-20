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