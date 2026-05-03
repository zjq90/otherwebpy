"""
用户管理路由
包含用户注册、登录、信息管理等API接口
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate
from app.utils.security import get_password_hash, verify_password, create_access_token, decode_access_token

router = APIRouter()

# OAuth2密码模式
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户（依赖函数）
    
    Args:
        token: JWT令牌
        db: 数据库会话
        
    Returns:
        User: 用户对象
        
    Raises:
        HTTPException: 令牌无效或用户不存在
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前管理员用户（依赖函数）
    
    Args:
        current_user: 当前用户
        
    Returns:
        User: 管理员用户对象
        
    Raises:
        HTTPException: 用户不是管理员
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册
    
    Args:
        user_data: 用户注册数据
        db: 数据库会话
        
    Returns:
        UserResponse: 创建的用户信息
        
    Raises:
        HTTPException: 手机号已被注册
    """
    existing_user = db.query(User).filter(User.phone == user_data.phone).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号已被注册"
        )
    
    new_user = User(
        phone=user_data.phone,
        name=user_data.name,
        password_hash=get_password_hash(user_data.password),
        role=UserRole.USER
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    用户登录（OAuth2密码模式）
    
    Args:
        form_data: 登录表单数据（username为手机号，password为密码）
        db: 数据库会话
        
    Returns:
        dict: 包含访问令牌和用户信息
    """
    user = db.query(User).filter(
        User.phone == form_data.username,
        User.is_deleted == False
    ).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="手机号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }


@router.post("/login-phone")
def login_by_phone(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录（手机号密码方式）
    
    Args:
        login_data: 登录数据（手机号和密码）
        db: 数据库会话
        
    Returns:
        dict: 包含访问令牌和用户信息
    """
    user = db.query(User).filter(
        User.phone == login_data.phone,
        User.is_deleted == False
    ).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="手机号或密码错误"
        )
    
    access_token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户信息
    
    Args:
        current_user: 当前登录用户
        
    Returns:
        UserResponse: 用户信息
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新当前用户信息
    
    Args:
        user_data: 更新的数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        UserResponse: 更新后的用户信息
    """
    if user_data.name is not None:
        current_user.name = user_data.name
    if user_data.password is not None:
        current_user.password_hash = get_password_hash(user_data.password)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取用户列表（管理员权限）
    
    Args:
        skip: 跳过的数量
        limit: 返回的最大数量
        current_admin: 当前管理员
        db: 数据库会话
        
    Returns:
        List[UserResponse]: 用户列表
    """
    users = db.query(User).filter(
        User.is_deleted == False
    ).offset(skip).limit(limit).all()
    
    return [user.to_dict() for user in users]


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    根据ID获取用户信息（管理员权限）
    
    Args:
        user_id: 用户ID
        current_admin: 当前管理员
        db: 数据库会话
        
    Returns:
        UserResponse: 用户信息
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return user.to_dict()


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    删除用户（软删除，管理员权限）
    
    Args:
        user_id: 用户ID
        current_admin: 当前管理员
        db: 数据库会话
        
    Returns:
        dict: 删除成功提示
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user.is_deleted = True
    db.commit()
    
    return {"message": "用户删除成功"}
