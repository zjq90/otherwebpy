"""
角色数据访问�?
封装角色相关的数据库增删改查操作
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.role import Role
from app.models.permission import Permission
from app.schemas.role import RoleCreate, RoleUpdate


class CRUDRole:
    """
    角色数据访问�?
    封装角色相关的所有数据库操作
    """
    
    def get_by_id(self, db: Session, role_id: int) -> Optional[Role]:
        """
        根据ID获取角色
        
        参数:
            db: 数据库会�?
            role_id: 角色ID
        
        返回:
            角色对象，如果不存在则返回None
        """
        return db.query(Role).filter(Role.id == role_id).first()
    
    def get_by_code(self, db: Session, code: str) -> Optional[Role]:
        """
        根据角色代码获取角色
        
        参数:
            db: 数据库会�?
            code: 角色代码
        
        返回:
            角色对象，如果不存在则返回None
        """
        return db.query(Role).filter(Role.code == code).first()
    
    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        keyword: Optional[str] = None
    ) -> tuple:
        """
        分页获取角色列表
        
        参数:
            db: 数据库会�?
            skip: 跳过的记录数（用于分页）
            limit: 每页显示的记录数
            keyword: 搜索关键词（角色名称、代码、描述）
        
        返回:
            (角色列表, 总记录数)
        """
        query = db.query(Role)
        
        # 关键词搜�?
        if keyword:
            query = query.filter(
                or_(
                    Role.name.contains(keyword),
                    Role.code.contains(keyword),
                    Role.description.contains(keyword)
                )
            )
        
        # 获取总记录数
        total = query.count()
        
        # 分页查询
        roles = query.offset(skip).limit(limit).all()
        
        return roles, total
    
    def create(self, db: Session, obj_in: RoleCreate) -> Role:
        """
        创建新角�?
        
        参数:
            db: 数据库会�?
            obj_in: 角色创建数据
        
        返回:
            创建的角色对�?
        """
        # 创建角色对象
        db_obj = Role(
            name=obj_in.name,
            code=obj_in.code,
            description=obj_in.description,
            is_active=obj_in.is_active
        )
        
        # 添加到数据库
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # 如果指定了权限，关联权限
        if obj_in.permission_ids:
            permissions = db.query(Permission).filter(Permission.id.in_(obj_in.permission_ids)).all()
            db_obj.permissions = permissions
            db.commit()
            db.refresh(db_obj)
        
        return db_obj
    
    def update(self, db: Session, db_obj: Role, obj_in: RoleUpdate) -> Role:
        """
        更新角色信息
        
        参数:
            db: 数据库会�?
            db_obj: 数据库中的角色对�?
            obj_in: 角色更新数据
        
        返回:
            更新后的角色对象
        """
        # 获取更新数据的字�?
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # 更新权限关联
        permission_ids = update_data.pop("permission_ids", None)
        
        # 更新角色基本信息
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        # 更新权限关联
        if permission_ids is not None:
            permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
            db_obj.permissions = permissions
        
        # 提交到数据库
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def remove(self, db: Session, role_id: int) -> Optional[Role]:
        """
        删除角色
        
        参数:
            db: 数据库会�?
            role_id: 角色ID
        
        返回:
            删除的角色对象，如果不存在则返回None
        """
        obj = db.query(Role).filter(Role.id == role_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj
    
    def get_role_with_permissions(self, db: Session, role_id: int) -> Optional[Role]:
        """
        获取角色及其关联的权�?
        
        参数:
            db: 数据库会�?
            role_id: 角色ID
        
        返回:
            角色对象（包含权限信息）
        """
        return db.query(Role).filter(Role.id == role_id).first()
    
    def get_roles_by_user_id(self, db: Session, user_id: int) -> List[Role]:
        """
        根据用户ID获取该用户的所有角�?
        
        参数:
            db: 数据库会�?
            user_id: 用户ID
        
        返回:
            角色列表
        """
        from app.models.user import User
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            return user.roles
        return []


# 创建角色CRUD实例
role_crud = CRUDRole()
