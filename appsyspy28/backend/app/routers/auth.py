from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User, UserRole
from app.schemas.schemas import (
    UserCreate, UserResponse, UserLogin, Token
)
from app.crud.crud import user_crud
from app.core.security import (
    authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user, get_password_hash
)

router = APIRouter(prefix="/api/auth", tags=["认证"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if user_crud.get_by_username(db, username=user_in.username):
        raise HTTPException(
            status_code=400,
            detail="用户名已存在"
        )
    if user_crud.get_by_phone(db, phone=user_in.phone):
        raise HTTPException(
            status_code=400,
            detail="手机号已被注册"
        )
    return user_crud.create(db, user_in=user_in)

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="用户已被禁用"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "role": user.role.value
        },
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login-password", response_model=Token)
def login_with_password(login_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, username=login_data.username, password=login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="用户已被禁用"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "role": user.role.value
        },
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
def update_user_me(
    name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    update_data = {}
    if name:
        update_data["name"] = name
    if phone:
        if user_crud.get_by_phone(db, phone=phone) and phone != current_user.phone:
            raise HTTPException(status_code=400, detail="手机号已被使用")
        update_data["phone"] = phone
    if email:
        update_data["email"] = email
    
    from app.schemas.schemas import UserUpdate
    user_update = UserUpdate(**update_data)
    return user_crud.update(db, db_user=current_user, user_in=user_update)
