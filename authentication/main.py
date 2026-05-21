from fastapi import FastAPI, Depends, HTTPException, status
from database import TaskStorage, get_task_store,get_db
from models import TaskCreate, TaskUpdate, TaskResponse,UserCreate,UserInDB,UserUpdate,UserPublic,RoleCreate,RoleResponse,ChangeRoleRequest
from sqlalchemy.orm import Session
from schema import User,Role
from auth import hash_password,verify_password,authenticate_user,create_access_token,ACCESS_TOKEN_EXPIRE_MINUTES,get_current_active_user,get_current_user,require_admin
from datetime import datetime, timedelta, timezone
from database import Base, engine
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI(title="Task Management API", version="1.0")
Base.metadata.create_all(bind=engine)

@app.get("/", tags=["Home"])
def home():
    return {"message":"Task Management API Running"}


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
    user_role = db.query(Role).filter(Role.name == "user").first()
    if user_role:
        new_user.roles.append(user_role)

    print(user.password)
    print(type(user.password))
    print(len(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/users", tags=["authentication"], response_model=list[UserPublic], summary="Get all users")
def get_all_users(db: Session = Depends(get_db),admin_user: User=Depends(require_admin)):
    users = db.query(User).all()
    return users


@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),db: Session=Depends(get_db)):

    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Incorrect username or password",headers={"WWW-Authenticate": "Bearer"})
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", tags=["profile"],response_model=UserPublic)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.patch("/users/update/{user_id}",tags=["profile"], response_model=UserPublic)
async def update_profile(user_id: int,user_update: UserUpdate,current_user: User = Depends(get_current_active_user),db: Session = Depends(get_db)):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404,detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user
    

@app.post("/roles",tags=["roles"],response_model=RoleResponse)
async def create_roles(role:RoleCreate, db: Session=Depends(get_db)):
    existing_role = db.query(Role).filter(Role.name == role.name).first()

    if existing_role:
        raise HTTPException(status_code=400,detail="Role already exists")

    new_role = Role(name=role.name,description=role.description)

    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    return new_role

@app.patch("/users/{user_id}/role",response_model=UserPublic,tags=["roles"],summary="Change user role")
def change_user_role(user_id: int,role_data: ChangeRoleRequest,admin_user: User = Depends(require_admin),db: Session = Depends(get_db)):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404,detail="User not found")

    role = db.get(Role, role_data.role_id)

    if not role:
        raise HTTPException(status_code=404,detail="Role not found")

    user.roles.clear()
    user.roles.append(role)
    db.commit()
    db.refresh(user)

    return user