from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from ..models import Staff
from ..schemas import StaffCreate, StaffUpdate
from ..models.role import Role
from ..permissions import parse_permissions, has_permission


class StaffCRUD:
    """
    人员管理CRUD操作类
    提供员工信息的增删改查功能
    """
    
    def get_by_id(self, db: Session, staff_id: int) -> Optional[Staff]:
        """
        根据ID获取员工信息
        :param db: 数据库会话
        :param staff_id: 员工ID
        :return: 员工对象或None
        """
        return db.query(Staff).filter(Staff.id == staff_id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Staff]:
        """
        获取所有员工信息（分页）
        :param db: 数据库会话
        :param skip: 跳过的记录数
        :param limit: 返回的最大记录数
        :return: 员工列表
        """
        return db.query(Staff).offset(skip).limit(limit).all()
    
    def get_by_staff_number(self, db: Session, staff_number: str) -> Optional[Staff]:
        """
        根据员工工号获取员工信息
        :param db: 数据库会话
        :param staff_number: 员工工号
        :return: 员工对象或None
        """
        return db.query(Staff).filter(Staff.staff_number == staff_number).first()
    
    def get_by_name(self, db: Session, name: str) -> List[Staff]:
        """
        根据姓名获取员工信息
        :param db: 数据库会话
        :param name: 员工姓名
        :return: 员工列表
        """
        return db.query(Staff).filter(Staff.name == name).all()
    
    def get_by_position(self, db: Session, position: str) -> List[Staff]:
        """
        根据岗位获取员工信息
        :param db: 数据库会话
        :param position: 岗位职责
        :return: 员工列表
        """
        return db.query(Staff).filter(Staff.position == position).all()
    
    def get_by_role(self, db: Session, role_id: int) -> List[Staff]:
        """
        根据角色获取员工列表
        :param db: 数据库会话
        :param role_id: 角色ID
        :return: 员工列表
        """
        return db.query(Staff).filter(Staff.role_id == role_id).all()
    
    def create(self, db: Session, staff: StaffCreate) -> Staff:
        """
        创建新员工
        如果员工没有指定角色，且存在默认角色，则自动分配默认角色
        :param db: 数据库会话
        :param staff: 员工创建数据
        :return: 创建的员工对象
        """
        staff_data = staff.model_dump()
        
        # 如果没有指定角色，检查是否有默认角色
        if not staff_data.get("role_id"):
            default_role = db.query(Role).filter(Role.is_default == True).first()
            if default_role:
                staff_data["role_id"] = default_role.id
        
        db_staff = Staff(**staff_data)
        db.add(db_staff)
        db.commit()
        db.refresh(db_staff)
        return db_staff
    
    def update(self, db: Session, staff_id: int, staff: StaffUpdate) -> Optional[Staff]:
        """
        更新员工信息
        :param db: 数据库会话
        :param staff_id: 员工ID
        :param staff: 员工更新数据
        :return: 更新后的员工对象或None
        """
        db_staff = self.get_by_id(db, staff_id)
        if db_staff:
            # 只更新提供的字段
            for key, value in staff.model_dump(exclude_unset=True).items():
                setattr(db_staff, key, value)
            db.commit()
            db.refresh(db_staff)
        return db_staff
    
    def delete(self, db: Session, staff_id: int) -> bool:
        """
        删除员工
        :param db: 数据库会话
        :param staff_id: 员工ID
        :return: 是否成功删除
        """
        db_staff = self.get_by_id(db, staff_id)
        if db_staff:
            db.delete(db_staff)
            db.commit()
            return True
        return False
    
    def count(self, db: Session) -> int:
        """
        统计员工数量
        :param db: 数据库会话
        :return: 员工总数
        """
        return db.query(Staff).count()
    
    def get_staff_role(self, db: Session, staff_id: int) -> Optional[Role]:
        """
        获取员工的角色信息
        :param db: 数据库会话
        :param staff_id: 员工ID
        :return: 角色对象或None
        """
        staff = self.get_by_id(db, staff_id)
        if staff and staff.role_id:
            return db.query(Role).filter(Role.id == staff.role_id).first()
        return None
    
    def get_effective_permissions(self, db: Session, staff_id: int) -> List[str]:
        """
        获取员工实际生效的权限
        优先级：自定义权限 > 角色权限 > 无权限
        :param db: 数据库会话
        :param staff_id: 员工ID
        :return: 权限列表
        """
        staff = self.get_by_id(db, staff_id)
        if not staff:
            return []
        
        # 检查是否有自定义权限
        if staff.permissions:
            return parse_permissions(staff.permissions)
        
        # 检查是否有角色
        if staff.role_id:
            role = db.query(Role).filter(Role.id == staff.role_id).first()
            if role and role.permissions:
                # 超级管理员角色，返回所有权限
                if role.code == "super_admin":
                    return ["*"]
                return parse_permissions(role.permissions)
        
        return []
    
    def has_permission(self, db: Session, staff_id: int, required_permission: str) -> bool:
        """
        检查员工是否拥有指定权限
        :param db: 数据库会话
        :param staff_id: 员工ID
        :param required_permission: 需要检查的权限代码
        :return: 是否拥有权限
        """
        effective_permissions = self.get_effective_permissions(db, staff_id)
        return has_permission(effective_permissions, required_permission)
    
    def assign_role(self, db: Session, staff_id: int, role_id: int) -> Optional[Staff]:
        """
        为员工分配角色
        :param db: 数据库会话
        :param staff_id: 员工ID
        :param role_id: 角色ID
        :return: 更新后的员工对象或None
        """
        staff = self.get_by_id(db, staff_id)
        if staff:
            # 验证角色是否存在
            role = db.query(Role).filter(Role.id == role_id).first()
            if role:
                staff.role_id = role_id
                db.commit()
                db.refresh(staff)
                return staff
        return None
    
    def remove_role(self, db: Session, staff_id: int) -> Optional[Staff]:
        """
        移除员工的角色
        :param db: 数据库会话
        :param staff_id: 员工ID
        :return: 更新后的员工对象或None
        """
        staff = self.get_by_id(db, staff_id)
        if staff:
            staff.role_id = None
            db.commit()
            db.refresh(staff)
            return staff
        return None


# 全局实例
staff_crud = StaffCRUD()
