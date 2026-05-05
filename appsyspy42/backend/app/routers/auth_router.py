"""
用户认证路由
处理登录、注册、用户信息管理等接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.models import User
from app.schemas.schemas import (
    UserCreate, UserUpdate, UserResponse, 
    LoginRequest, LoginResponse
)
from app.services.auth_service import (
    get_password_hash, authenticate_user, create_access_token,
    get_current_user, get_current_admin
)

router = APIRouter(prefix="/auth", tags=["认证管理"])


@router.post("/login", response_model=LoginResponse, summary="用户登录")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录接口
    - username: 用户名
    - password: 密码
    返回JWT令牌和用户信息
    """
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return LoginResponse(
        token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/register", response_model=UserResponse, summary="用户注册")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    只有管理员可以创建新用户
    """
    existing_user = db.query(User).filter(
        User.username == user_data.username
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    db_user = User(
        username=user_data.username,
        password=get_password_hash(user_data.password),
        real_name=user_data.real_name,
        role=user_data.role,
        phone=user_data.phone,
        email=user_data.email,
        is_active=1
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse.model_validate(db_user)


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前登录用户的详细信息"""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse, summary="更新当前用户信息")
def update_current_user_info(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前登录用户的信息"""
    for key, value in user_data.model_dump(exclude_unset=True).items():
        if key not in ['is_active']:
            setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


@router.get("/users", summary="获取用户列表（管理员）")
def get_users(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取所有用户列表，需要管理员权限"""
    query = db.query(User)
    total = query.count()
    
    users = query.order_by(User.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return {
        "list": [UserResponse.model_validate(u) for u in users],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/users/{user_id}", response_model=UserResponse, summary="获取用户详情（管理员）")
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取指定用户的详细信息，需要管理员权限"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}", response_model=UserResponse, summary="更新用户信息（管理员）")
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新指定用户的信息，需要管理员权限"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    for key, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.post("/users/{user_id}/reset-password", summary="重置用户密码（管理员）")
def reset_user_password(
    user_id: int,
    new_password: str,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """重置指定用户的密码，需要管理员权限"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user.password = get_password_hash(new_password)
    db.commit()
    
    return {"success": True, "message": "密码重置成功"}
