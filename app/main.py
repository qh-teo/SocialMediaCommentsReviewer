from __future__ import annotations

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from pwdlib import PasswordHash

from .db import engine, get_db
from .models import Base, Todo, User
from .schemas import (
    TodoCreate, TodoUpdate, TodoOut,
    UserCreate, UserOut,
    LoginRequest, LoginResponse
)

# Create tables (quick-project approach)
Base.metadata.create_all(bind=engine)

pwd_hasher = PasswordHash.recommended()
# Dummy hash to equalize timing for non-existent users
DUMMY_HASH = pwd_hasher.hash("dummypassword")

app = FastAPI(title="Todo API", version="1.0.0")

allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

# -----------------------
# Todo endpoints (existing)
# -----------------------
@app.post("/api/v1/todos", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate, db: Session = Depends(get_db)):
    todo = Todo(title=payload.title, completed=False)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo

@app.get("/api/v1/todos", response_model=list[TodoOut])
def list_todos(db: Session = Depends(get_db)):
    todos = db.scalars(select(Todo).order_by(Todo.id.desc())).all()
    return todos

@app.get("/api/v1/todos/{todo_id}", response_model=TodoOut)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.patch("/api/v1/todos/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: int, payload: TodoUpdate, db: Session = Depends(get_db)):
    todo = db.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    if payload.title is not None:
        todo.title = payload.title
    if payload.completed is not None:
        todo.completed = payload.completed

    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo

@app.delete("/api/v1/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return None

# -----------------------
# User endpoints (new)
# -----------------------
@app.post("/api/v1/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    # Check uniqueness (backend must enforce this)
    existing = db.scalar(
        select(User).where(or_(User.username == payload.username, User.email == payload.email))
    )
    if existing:
        # Don’t leak which one exists if you don’t want to; keeping it simple here:
        raise HTTPException(status_code=409, detail="Username or email already in use")

    user = User(
        username=payload.username,
        firstname=payload.firstname,
        lastname=payload.lastname,
        dateOfBirth=payload.dateOfBirth,
        email=str(payload.email),
        password_hash=pwd_hasher.hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.get("/api/v1/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/api/v1/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(
        select(User).where(or_(User.username == payload.username_or_email, User.email == payload.username_or_email))
    )
    if not user:
        # run a dummy verify to reduce timing differences
        try:
            pwd_hasher.verify(payload.password, DUMMY_HASH)
        except Exception:
            pass
        raise HTTPException(status_code=401, detail="Invalid credentials")

    try:
        verified = pwd_hasher.verify(payload.password, user.password_hash)
    except Exception:
        verified = False
    if not verified:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"ok": True, "user": user}
