"""
权限数据访问�?
封装权限相关的数据库增删改查操作
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.permission import Permission
from app.schemas.permission import PermissionCreate, PermissionUpdate


class CRUDPermission:
    """
    权限数据访问�?
    封装权限相关的所有数据库操作
    """
    
    def get_by_id(self, db: Session, permission_id: int) -> Optional[Permission]:
        """
        根据ID获取权限
        
        参数:
            db: 数据库会�?
            permission_id: 权限ID
        
        返回:
            权限对象，如果不存在则返回None
        """
        return db.query(Permission).filter(Permission.id == permission_id).first()
    
    def get_by_code(self, db: Session, code: str) -> Optional[Permission]:
        """
        根据权限代码获取权限
        
        参数:
            db: 数据库会�?
            code: 权限代码
        
        返回:
            权限对象，如果不存在则返回None
        """
        return db.query(Permission).filter(Permission.code == code).first()
    
    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        keyword: Optional[str] = None,
        module: Optional[str] = None
    ) -> tuple:
        """
        分页获取权限列表
        
        参数:
            db: 数据库会�?
            skip: 跳过的记录数（用于分页）
            limit: 每页显示的记录数
            keyword: 搜索关键词（权限名称、代码、描述）
            module: 模块筛�?
        
        返回:
            (权限列表, 总记录数)
        """
        query = db.query(Permission)
        
        # 关键词搜�?
        if keyword:
            query = query.filter(
                or_(
                    Permission.name.contains(keyword),
                    Permission.code.contains(keyword),
                    Permission.description.contains(keyword)
                )
            )
        
        # 模块筛�?
        if module:
            query = query.filter(Permission.module == module)
        
        # 获取总记录数
        total = query.count()
        
        # 分页查询
        permissions = query.offset(skip).limit(limit).all()
        
        return permissions, total
    
    def create(self, db: Session, obj_in: PermissionCreate) -> Permission:
        """
        创建新权�?
        
        参数:
            db: 数据库会�?
            obj_in: 权限创建数据
        
        返回:
            创建的权限对�?
        """
        # 创建权限对象
        db_obj = Permission(
            name=obj_in.name,
            code=obj_in.code,
            description=obj_in.description,
            module=obj_in.module,
            action=obj_in.action,
            is_active=obj_in.is_active
        )
        
        # 添加到数据库
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def update(self, db: Session, db_obj: Permission, obj_in: PermissionUpdate) -> Permission:
        """
        更新权限信息
        
        参数:
            db: 数据库会�?
            db_obj: 数据库中的权限对�?
            obj_in: 权限更新数据
        
        返回:
            更新后的权限对象
        """
        # 获取更新数据的字�?
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # 更新权限基本信息
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        # 提交到数据库
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def remove(self, db: Session, permission_id: int) -> Optional[Permission]:
        """
        删除权限
        
        参数:
            db: 数据库会�?
            permission_id: 权限ID
        
        返回:
            删除的权限对象，如果不存在则返回None
        """
        obj = db.query(Permission).filter(Permission.id == permission_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj
    
    def get_permissions_by_role_id(self, db: Session, role_id: int) -> List[Permission]:
        """
        根据角色ID获取该角色的所有权�?
        
        参数:
            db: 数据库会�?
            role_id: 角色ID
        
        返回:
            权限列表
        """
        from app.models.role import Role
        role = db.query(Role).filter(Role.id == role_id).first()
        if role:
            return role.permissions
        return []
    
    def get_all_modules(self, db: Session) -> List[str]:
        """
        获取所有权限模�?
        
        参数:
            db: 数据库会�?
        
        返回:
            模块名称列表
        """
        modules = db.query(Permission.module).filter(Permission.module.isnot(None)).distinct().all()
        return [m[0] for m in modules]
    
    def get_permissions_by_user_id(self, db: Session, user_id: int) -> List[Permission]:
        """
        根据用户ID获取该用户的所有权�?
        
        参数:
            db: 数据库会�?
            user_id: 用户ID
        
        返回:
            权限列表
        """
        from app.models.user import User
        from app.models.role import Role
        
        # 查询用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        # 超级管理员拥有所有权�?
        if user.is_superuser:
            return db.query(Permission).all()
        
        # 获取用户的所有角�?
        roles = user.roles
        if not roles:
            return []
        
        # 获取所有角色的权限ID
        permission_ids = set()
        for role in roles:
            for permission in role.permissions:
                permission_ids.add(permission.id)
        
        # 获取权限列表
        if permission_ids:
            return db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
        
        return []


# 创建权限CRUD实例
permission_crud = CRUDPermission()
