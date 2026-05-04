"""
用户相关API路由模块
包含用户注册、登录、信息管理等接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..config import get_db
from ..schemas import (
    UserCreate, UserUpdate, UserLogin, UserResponse, TokenResponse, ApiResponse
)
from ..crud import (
    get_user_by_id, get_user_by_username, get_users, create_user, update_user, delete_user, authenticate_user
)

router = APIRouter(prefix="/api/users", tags=["用户管理"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def user_register(user: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    
    检查用户名是否已存在，若不存在则创建新用户
    """
    # 检查用户名是否已存在
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 创建新用户
    return create_user(db=db, user=user)


@router.post("/login", response_model=TokenResponse)
def user_login(user: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录接口
    
    验证用户名和密码，返回访问令牌和用户信息
    """
    # 验证用户
    db_user = authenticate_user(db, username=user.username, password=user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 生成简单的令牌（实际项目中应该使用JWT）
    token = f"token_{db_user.id}_{db_user.username}"
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.from_orm(db_user)
    )


@router.get("/", response_model=List[UserResponse])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取用户列表接口
    
    支持分页查询
    """
    users = get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取用户信息接口
    """
    db_user = get_user_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return db_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user_info(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """
    更新用户信息接口
    """
    db_user = update_user(db, user_id=user_id, user=user)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return db_user


@router.delete("/{user_id}", response_model=ApiResponse)
def delete_user_info(user_id: int, db: Session = Depends(get_db)):
    """
    删除用户接口
    """
    success = delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return ApiResponse(
        code=status.HTTP_200_OK,
        message="用户删除成功"
    )


@router.get("/username/{username}", response_model=UserResponse)
def get_user_by_name(username: str, db: Session = Depends(get_db)):
    """
    根据用户名获取用户信息接口
    """
    db_user = get_user_by_username(db, username=username)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return db_user
