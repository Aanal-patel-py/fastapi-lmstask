from fastapi import FastAPI, Depends, HTTPException, status
from database import TaskStorage, get_task_store,get_db
from models import TaskCreate, TaskUpdate, TaskResponse,UserCreate,UserInDB,UserUpdate,UserPublic
from sqlalchemy.orm import Session
from schema import User
from auth import hash_password,verify_password
from database import Base, engine
app = FastAPI(title="Task Management API", version="1.0")
Base.metadata.create_all(bind=engine)

@app.get("/", tags=["Home"])
def home():
    return {"message": "Task Management API Running"}


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Tasks"], summary="Create new task")
def create_task(task: TaskCreate, store: TaskStorage = Depends(get_task_store)):

    new_task = {
        "id": store.current_id,
        "title": task.title,
        "description": task.description,
        "due_date": task.due_date,
        "completed":task.completed
    }

    store.tasks.append(new_task)
    store.current_id += 1

    return new_task


@app.get("/tasks", response_model=list[TaskResponse], tags=["Tasks"], summary="Get all tasks")
def get_tasks(store: TaskStorage = Depends(get_task_store)):
    return store.tasks



@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"], summary="Get task by ID")
def get_single_task(task_id: int, store: TaskStorage = Depends(get_task_store)):
    for task in store.tasks:
        if task["id"] == task_id:
            return task

    raise HTTPException(status_code=404, detail="Task not found")



@app.put("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"], summary="Update task")
def update_task(task_id: int, updated_task: TaskCreate, store: TaskStorage = Depends(get_task_store)):

    for task in store.tasks:
        if task["id"] == task_id:
            task["title"] = updated_task.title
            task["due_date"] = updated_task.due_date
            task["completed"]=updated_task.completed
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.patch("/tasks/{task_id}",response_model=TaskResponse,tags=["Tasks"],summary="Partially update task")

def patch_task(task_id: int,updated_task: TaskUpdate,store: TaskStorage = Depends(get_task_store)):

    for task in store.tasks:
        if task["id"] == task_id:
            update_data = updated_task.model_dump(exclude_unset=True)
            task.update(update_data)
            return task

    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}", tags=["Tasks"], summary="Delete task")
def delete_task(task_id: int, store: TaskStorage = Depends(get_task_store)):

    for index, task in enumerate(store.tasks):
        if task["id"] == task_id:
            store.tasks.pop(index)
            return {"message": "Task deleted successfully"}

    raise HTTPException(status_code=404, detail="Task not found")


@app.post("/register", tags=["authentication"],status_code=status.HTTP_201_CREATED,response_model=UserPublic,summary="registration")
def register(user: UserCreate,db:Session=Depends(get_db)):

    hashed_pwd=hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        age=user.age,
        hashed_password=hashed_pwd
    )
    print(user.password)
    print(type(user.password))
    print(len(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/users", tags=["authentication"], response_model=list[UserPublic], summary="Get all users")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users