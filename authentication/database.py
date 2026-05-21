from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
class TaskStorage:
    def __init__(self):
        self.tasks = []
        self.current_id = 1
task_store = TaskStorage()

def get_task_store():
    
    return task_store

Base=declarative_base()
URL="postgresql://postgres:123456@localhost:5432/todolist"

engine=create_engine(URL)

SessionLocal=sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()