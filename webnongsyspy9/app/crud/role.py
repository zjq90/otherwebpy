from sqlalchemy.orm import Session
from typing import List, Optional, Type
from ..models.role import Role
from ..schemas.role import RoleCreate, RoleUpdate
from ..permissions import parse_permissions


class CRUDRole:
    """
    角色管理CRUD操作类
    封装角色的增删改查操作
    """
    
    def __init__(self, model: Type[Role]):
        self.model = model
    
    def get_by_id(self, db: Session, role_id: int) -> Optional[Role]:
        """
        根据ID获取角色
        """
        return db.query(self.model).filter(self.model.id == role_id).first()
    
    def get_by_code(self, db: Session, code: str) -> Optional[Role]:
        """
        根据代码获取角色
        """
        return db.query(self.model).filter(self.model.code == code).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
        """
        获取所有角色列表
        """
        return db.query(self.model).order_by(self.model.sort_order.asc(), self.model.id.asc()).offset(skip).limit(limit).all()
    
    def get_default(self, db: Session) -> Optional[Role]:
        """
        获取默认角色
        """
        return db.query(self.model).filter(self.model.is_default == True).first()
    
    def get_by_ids(self, db: Session, role_ids: List[int]) -> List[Role]:
        """
        根据ID列表获取角色
        """
        if not role_ids:
            return []
        return db.query(self.model).filter(self.model.id.in_(role_ids)).all()
    
    def count(self, db: Session) -> int:
        """
        统计角色数量
        """
        return db.query(self.model).count()
    
    def create(self, db: Session, obj_in: RoleCreate) -> Role:
        """
        创建新角色
        """
        db_obj = Role(
            name=obj_in.name,
            code=obj_in.code,
            description=obj_in.description,
            permissions=obj_in.permissions,
            is_system=False,
            is_default=obj_in.is_default,
            sort_order=obj_in.sort_order
        )
        
        # 如果设置为默认角色，先取消其他角色的默认设置
        if obj_in.is_default:
            db.query(self.model).filter(self.model.is_default == True).update({"is_default": False})
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, db_obj: Role, obj_in: RoleUpdate) -> Role:
        """
        更新角色信息
        """
        update_data = obj_in.dict(exclude_unset=True)
        
        # 如果设置为默认角色，先取消其他角色的默认设置
        if "is_default" in update_data and update_data["is_default"]:
            db.query(self.model).filter(self.model.is_default == True, self.model.id != db_obj.id).update({"is_default": False})
        
        for field, value in update_data.items():
            if value is not None:
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, role_id: int) -> bool:
        """
        删除角色
        注意：系统预设角色不可删除
        """
        db_obj = self.get_by_id(db, role_id)
        if db_obj and not db_obj.is_system:
            db.delete(db_obj)
            db.commit()
            return True
        return False
    
    def init_default_roles(self, db: Session) -> List[Role]:
        """
        初始化默认角色
        从预设角色配置中创建系统角色
        """
        from ..permissions import PREDEFINED_ROLES
        
        created_roles = []
        
        for role_data in PREDEFINED_ROLES:
            # 检查角色是否已存在
            existing_role = self.get_by_code(db, role_data["code"])
            
            if existing_role:
                # 更新已存在的系统角色
                existing_role.name = role_data["name"]
                existing_role.description = role_data["description"]
                existing_role.permissions = ",".join(role_data["permissions"]) if role_data["permissions"] else None
                existing_role.is_system = role_data["is_system"]
                existing_role.is_default = role_data["is_default"]
                db.commit()
                db.refresh(existing_role)
                created_roles.append(existing_role)
            else:
                # 创建新角色
                db_obj = Role(
                    name=role_data["name"],
                    code=role_data["code"],
                    description=role_data["description"],
                    permissions=",".join(role_data["permissions"]) if role_data["permissions"] else None,
                    is_system=role_data["is_system"],
                    is_default=role_data["is_default"],
                    sort_order=PREDEFINED_ROLES.index(role_data)
                )
                db.add(db_obj)
                db.commit()
                db.refresh(db_obj)
                created_roles.append(db_obj)
        
        return created_roles


# 实例化CRUDRole
role_crud = CRUDRole(Role)
