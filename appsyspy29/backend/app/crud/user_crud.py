"""
用户相关CRUD操作模块
负责用户数据的增删改查
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import User
from ..schemas import UserCreate, UserUpdate
from datetime import datetime


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    根据ID获取用户
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    根据用户名获取用户
    """
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    获取用户列表
    """
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    """
    创建新用户
    注意：实际项目中应该对密码进行哈希处理
    """
    db_user = User(
        username=user.username,
        password=user.password,
        nickname=user.nickname,
        avatar=user.avatar,
        gender=user.gender.value if user.gender else None,
        birthday=user.birthday,
        phone=user.phone,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: UserUpdate) -> Optional[User]:
    """
    更新用户信息
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    # 更新非空字段
    update_data = user.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key == "gender" and value:
            value = value.value
        setattr(db_user, key, value)
    
    db_user.updated_at = datetime.now()
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """
    删除用户
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
    验证用户名和密码是否匹配
    """
    db_user = get_user_by_username(db, username)
    if not db_user:
        return None
    # 注意：实际项目中应该使用密码哈希验证
    if db_user.password != password:
        return None
    return db_user
