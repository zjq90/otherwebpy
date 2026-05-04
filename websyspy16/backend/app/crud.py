"""
CRUD操作模块
封装数据库的增删改查操作
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Type, Any, Dict
from datetime import datetime

from app import models, schemas
from app.models import PropertyStatus


# ==================== 物业项目CRUD操作 ====================


def get_property_project(db: Session, project_id: int) -> Optional[models.PropertyProject]:
    """
    根据ID获取单个物业项目
    """
    return db.query(models.PropertyProject).filter(models.PropertyProject.id == project_id).first()


def get_property_projects(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None
) -> tuple[List[models.PropertyProject], int]:
    """
    获取物业项目列表，支持分页和名称搜索
    """
    query = db.query(models.PropertyProject)
    if name:
        query = query.filter(models.PropertyProject.name.contains(name))
    total = query.count()
    items = query.order_by(models.PropertyProject.created_at.desc()).offset(skip).limit(limit).all()
    return items, total


def create_property_project(
    db: Session,
    project: schemas.PropertyProjectCreate
) -> models.PropertyProject:
    """
    创建新的物业项目
    """
    db_project = models.PropertyProject(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def update_property_project(
    db: Session,
    project_id: int,
    project: schemas.PropertyProjectUpdate
) -> Optional[models.PropertyProject]:
    """
    更新物业项目信息
    """
    db_project = get_property_project(db, project_id)
    if db_project:
        update_data = project.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_project, key, value)
        db_project.updated_at = datetime.now()
        db.commit()
        db.refresh(db_project)
    return db_project


def delete_property_project(db: Session, project_id: int) -> bool:
    """
    删除物业项目
    """
    db_project = get_property_project(db, project_id)
    if db_project:
        db.delete(db_project)
        db.commit()
        return True
    return False


# ==================== 房产信息CRUD操作 ====================


def get_property(db: Session, property_id: int) -> Optional[models.Property]:
    """
    根据ID获取单个房产信息
    """
    return db.query(models.Property).filter(models.Property.id == property_id).first()


def get_properties(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    building_number: Optional[str] = None,
    room_number: Optional[str] = None
) -> tuple[List[models.Property], int]:
    """
    获取房产信息列表，支持多条件筛选和分页
    """
    query = db.query(models.Property)
    if project_id:
        query = query.filter(models.Property.project_id == project_id)
    if status:
        query = query.filter(models.Property.status == status)
    if building_number:
        query = query.filter(models.Property.building_number.contains(building_number))
    if room_number:
        query = query.filter(models.Property.room_number.contains(room_number))
    total = query.count()
    items = query.order_by(models.Property.created_at.desc()).offset(skip).limit(limit).all()
    return items, total


def create_property(
    db: Session,
    property: schemas.PropertyCreate
) -> models.Property:
    """
    创建新的房产信息
    """
    db_property = models.Property(**property.model_dump())
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property


def update_property(
    db: Session,
    property_id: int,
    property: schemas.PropertyUpdate
) -> Optional[models.Property]:
    """
    更新房产信息
    """
    db_property = get_property(db, property_id)
    if db_property:
        update_data = property.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_property, key, value)
        db_property.updated_at = datetime.now()
        db.commit()
        db.refresh(db_property)
    return db_property


def delete_property(db: Session, property_id: int) -> bool:
    """
    删除房产信息
    """
    db_property = get_property(db, property_id)
    if db_property:
        db.delete(db_property)
        db.commit()
        return True
    return False


# ==================== 业主/住户CRUD操作 ====================


def get_owner(db: Session, owner_id: int) -> Optional[models.Owner]:
    """
    根据ID获取单个业主/住户信息
    """
    return db.query(models.Owner).filter(models.Owner.id == owner_id).first()


def get_owners(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    is_owner: Optional[bool] = None
) -> tuple[List[models.Owner], int]:
    """
    获取业主/住户列表，支持多条件筛选和分页
    """
    query = db.query(models.Owner)
    if name:
        query = query.filter(models.Owner.name.contains(name))
    if phone:
        query = query.filter(models.Owner.phone.contains(phone))
    if is_owner is not None:
        query = query.filter(models.Owner.is_owner == is_owner)
    total = query.count()
    items = query.order_by(models.Owner.created_at.desc()).offset(skip).limit(limit).all()
    return items, total


def create_owner(
    db: Session,
    owner: schemas.OwnerCreate
) -> models.Owner:
    """
    创建新的业主/住户信息
    """
    db_owner = models.Owner(**owner.model_dump())
    db.add(db_owner)
    db.commit()
    db.refresh(db_owner)
    return db_owner


def update_owner(
    db: Session,
    owner_id: int,
    owner: schemas.OwnerUpdate
) -> Optional[models.Owner]:
    """
    更新业主/住户信息
    """
    db_owner = get_owner(db, owner_id)
    if db_owner:
        update_data = owner.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_owner, key, value)
        db_owner.updated_at = datetime.now()
        db.commit()
        db.refresh(db_owner)
    return db_owner


def delete_owner(db: Session, owner_id: int) -> bool:
    """
    删除业主/住户信息
    """
    db_owner = get_owner(db, owner_id)
    if db_owner:
        db.delete(db_owner)
        db.commit()
        return True
    return False


# ==================== 家庭成员CRUD操作 ====================


def create_family_member(
    db: Session,
    owner_id: int,
    member: schemas.FamilyMemberCreate
) -> models.FamilyMember:
    """
    为业主添加家庭成员
    """
    db_member = models.FamilyMember(owner_id=owner_id, **member.model_dump())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


def delete_family_member(db: Session, member_id: int) -> bool:
    """
    删除家庭成员
    """
    db_member = db.query(models.FamilyMember).filter(models.FamilyMember.id == member_id).first()
    if db_member:
        db.delete(db_member)
        db.commit()
        return True
    return False


# ==================== 车辆信息CRUD操作 ====================


def create_vehicle(
    db: Session,
    owner_id: int,
    vehicle: schemas.VehicleCreate
) -> models.Vehicle:
    """
    为业主添加车辆信息
    """
    db_vehicle = models.Vehicle(owner_id=owner_id, **vehicle.model_dump())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


def delete_vehicle(db: Session, vehicle_id: int) -> bool:
    """
    删除车辆信息
    """
    db_vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if db_vehicle:
        db.delete(db_vehicle)
        db.commit()
        return True
    return False


# ==================== 业主-房产关联CRUD操作 ====================


def create_owner_property(
    db: Session,
    relation: schemas.OwnerPropertyCreate
) -> models.OwnerProperty:
    """
    创建业主与房产的关联
    """
    db_relation = models.OwnerProperty(**relation.model_dump())
    db.add(db_relation)
    db.commit()
    db.refresh(db_relation)
    return db_relation


def get_owner_properties_by_owner(db: Session, owner_id: int) -> List[models.OwnerProperty]:
    """
    获取业主的所有房产关联
    """
    return db.query(models.OwnerProperty).filter(models.OwnerProperty.owner_id == owner_id).all()


# ==================== 统计数据操作 ====================


def get_dashboard_stats(db: Session) -> Dict[str, Any]:
    """
    获取首页统计数据
    """
    # 项目总数
    total_projects = db.query(func.count(models.PropertyProject.id)).scalar() or 0
    
    # 房产总数
    total_properties = db.query(func.count(models.Property.id)).scalar() or 0
    
    # 业主总数
    total_owners = db.query(func.count(models.Owner.id)).scalar() or 0
    
    # 各状态房产数量
    vacant_properties = db.query(func.count(models.Property.id)).filter(
        models.Property.status == PropertyStatus.VACANT.value
    ).scalar() or 0
    
    rented_properties = db.query(func.count(models.Property.id)).filter(
        models.Property.status == PropertyStatus.RENTED.value
    ).scalar() or 0
    
    occupied_properties = db.query(func.count(models.Property.id)).filter(
        models.Property.status == PropertyStatus.OCCUPIED.value
    ).scalar() or 0
    
    return {
        "total_projects": total_projects,
        "total_properties": total_properties,
        "total_owners": total_owners,
        "vacant_properties": vacant_properties,
        "rented_properties": rented_properties,
        "occupied_properties": occupied_properties
    }
