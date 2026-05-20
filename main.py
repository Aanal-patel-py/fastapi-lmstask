from fastapi import FastAPI, Depends, HTTPException, status
from database import TaskStorage, get_task_store
from models import TaskCreate, TaskUpdate, TaskResponse

app = FastAPI(title="Task Management API", version="1.0")

@app.get("/", tags=["Home"])
def home():
    return {"message": "Task Management API Running"}


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Tasks"], summary="Create new task")
def create_task(task: TaskCreate, store: TaskStorage = Depends(get_task_store)):

    new_task = {
        "id": store.current_id,
        "title": task.title,
        "description": task.description,
        "due_date": task.due_date
    }

    store.tasks.append(new_task)
    store.current_id += 1

    return new_task

