from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
import hashlib


def get_password_hash(password: str) -> str:
    """
    生成密码哈希值
    使用 SHA256 算法进行简单加密
    
    Args:
        password: 原始密码
        
    Returns:
        加密后的密码哈希值
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否正确
    
    Args:
        plain_password: 原始密码
        hashed_password: 存储的哈希密码
        
    Returns:
        密码是否匹配
    """
    return get_password_hash(plain_password) == hashed_password


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    根据 ID 获取用户
    
    Args:
        db: 数据库会话
        user_id: 用户 ID
        
    Returns:
        用户对象，不存在返回 None
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    根据用户名获取用户
    
    Args:
        db: 数据库会话
        username: 用户名
        
    Returns:
        用户对象，不存在返回 None
    """
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    获取用户列表
    
    Args:
        db: 数据库会话
        skip: 跳过的记录数
        limit: 返回的最大记录数
        
    Returns:
        用户列表
    """
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    """
    创建新用户
    
    Args:
        db: 数据库会话
        user: 用户创建数据
        
    Returns:
        创建的用户对象
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        password=hashed_password,
        real_name=user.real_name,
        phone=user.phone,
        email=user.email,
        room_number=user.room_number,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: UserUpdate) -> Optional[User]:
    """
    更新用户信息
    
    Args:
        db: 数据库会话
        user_id: 用户 ID
        user: 用户更新数据
        
    Returns:
        更新后的用户对象，不存在返回 None
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    update_data = user.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """
    删除用户
    
    Args:
        db: 数据库会话
        user_id: 用户 ID
        
    Returns:
        是否删除成功
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    用户认证
    
    Args:
        db: 数据库会话
        username: 用户名
        password: 密码
        
    Returns:
        认证成功返回用户对象，失败返回 None
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user
