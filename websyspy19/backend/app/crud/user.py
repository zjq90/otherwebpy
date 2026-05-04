"""
用户数据访问�?
封装用户相关的数据库增删改查操作
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User, user_role
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class CRUDUser:
    """
    用户数据访问�?
    封装用户相关的所有数据库操作
    """
    
    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """
        根据ID获取用户
        
        参数:
            db: 数据库会�?
            user_id: 用户ID
        
        返回:
            用户对象，如果不存在则返回None
        """
        return db.query(User).filter(User.id == user_id).first()
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        根据用户名获取用�?
        
        参数:
            db: 数据库会�?
            username: 用户�?
        
        返回:
            用户对象，如果不存在则返回None
        """
        return db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        根据邮箱获取用户
        
        参数:
            db: 数据库会�?
            email: 邮箱地址
        
        返回:
            用户对象，如果不存在则返回None
        """
        return db.query(User).filter(User.email == email).first()
    
    def get_by_phone(self, db: Session, phone: str) -> Optional[User]:
        """
        根据手机号获取用�?
        
        参数:
            db: 数据库会�?
            phone: 手机�?
        
        返回:
            用户对象，如果不存在则返回None
        """
        return db.query(User).filter(User.phone == phone).first()
    
    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        keyword: Optional[str] = None
    ) -> tuple:
        """
        分页获取用户列表
        
        参数:
            db: 数据库会�?
            skip: 跳过的记录数（用于分页）
            limit: 每页显示的记录数
            keyword: 搜索关键词（用户名、邮箱、手机号、真实姓名）
        
        返回:
            (用户列表, 总记录数)
        """
        query = db.query(User)
        
        # 关键词搜�?
        if keyword:
            query = query.filter(
                or_(
                    User.username.contains(keyword),
                    User.email.contains(keyword),
                    User.phone.contains(keyword),
                    User.full_name.contains(keyword)
                )
            )
        
        # 获取总记录数
        total = query.count()
        
        # 分页查询
        users = query.offset(skip).limit(limit).all()
        
        return users, total
    
    def create(self, db: Session, obj_in: UserCreate) -> User:
        """
        创建新用�?
        
        参数:
            db: 数据库会�?
            obj_in: 用户创建数据
        
        返回:
            创建的用户对�?
        """
        # 创建用户对象
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            phone=obj_in.phone,
            full_name=obj_in.full_name,
            is_active=obj_in.is_active,
            hashed_password=get_password_hash(obj_in.password)
        )
        
        # 添加到数据库
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # 如果指定了角色，关联角色
        if obj_in.role_ids:
            roles = db.query(Role).filter(Role.id.in_(obj_in.role_ids)).all()
            db_obj.roles = roles
            db.commit()
            db.refresh(db_obj)
        
        return db_obj
    
    def update(self, db: Session, db_obj: User, obj_in: UserUpdate) -> User:
        """
        更新用户信息
        
        参数:
            db: 数据库会�?
            db_obj: 数据库中的用户对�?
            obj_in: 用户更新数据
        
        返回:
            更新后的用户对象
        """
        # 获取更新数据的字�?
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # 如果有密码更�?
        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = get_password_hash(update_data["password"])
            del update_data["password"]
        
        # 更新角色关联
        role_ids = update_data.pop("role_ids", None)
        
        # 更新用户基本信息
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        # 更新角色关联
        if role_ids is not None:
            roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
            db_obj.roles = roles
        
        # 提交到数据库
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def remove(self, db: Session, user_id: int) -> Optional[User]:
        """
        删除用户
        
        参数:
            db: 数据库会�?
            user_id: 用户ID
        
        返回:
            删除的用户对象，如果不存在则返回None
        """
        obj = db.query(User).filter(User.id == user_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj
    
    def authenticate(self, db: Session, username: str, password: str) -> Optional[User]:
        """
        用户认证
        
        参数:
            db: 数据库会�?
            username: 用户�?
            password: 密码
        
        返回:
            认证成功返回用户对象，失败返回None
        """
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def is_active(self, user: User) -> bool:
        """
        检查用户是否激�?
        
        参数:
            user: 用户对象
        
        返回:
            激活返回True，否则返回False
        """
        return user.is_active
    
    def is_superuser(self, user: User) -> bool:
        """
        检查用户是否超级管理员
        
        参数:
            user: 用户对象
        
        返回:
            是超级管理员返回True，否则返回False
        """
        return user.is_superuser
    
    def get_user_with_roles(self, db: Session, user_id: int) -> Optional[User]:
        """
        获取用户及其关联的角�?
        
        参数:
            db: 数据库会�?
            user_id: 用户ID
        
        返回:
            用户对象（包含角色信息）
        """
        return db.query(User).filter(User.id == user_id).first()


# 创建用户CRUD实例
user_crud = CRUDUser()
