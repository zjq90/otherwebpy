"""
业主/住户信息API路由
提供业主/住户信息的增删改查接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.config import get_db
from app import crud, schemas

router = APIRouter(
    prefix="/api/owners",
    tags=["业主/住户信息管理"]
)


@router.get("/", response_model=schemas.OwnerList, summary="获取业主/住户列表")
def read_owners(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="每页记录数"),
    name: Optional[str] = Query(None, description="姓名搜索关键词"),
    phone: Optional[str] = Query(None, description="电话搜索关键词"),
    is_owner: Optional[bool] = Query(None, description="是否为业主"),
    db: Session = Depends(get_db)
):
    """
    获取业主/住户列表，支持多条件筛选和分页
    """
    items, total = crud.get_owners(
        db, 
        skip=skip, 
        limit=limit,
        name=name,
        phone=phone,
        is_owner=is_owner
    )
    return {"items": items, "total": total}


@router.get("/{owner_id}", response_model=schemas.Owner, summary="获取单个业主/住户详情")
def read_owner(
    owner_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取单个业主/住户的详细信息
    """
    db_owner = crud.get_owner(db, owner_id=owner_id)
    if db_owner is None:
        raise HTTPException(status_code=404, detail="业主/住户信息不存在")
    return db_owner


@router.post("/", response_model=schemas.Owner, summary="创建新的业主/住户信息")
def create_owner(
    owner: schemas.OwnerCreate,
    db: Session = Depends(get_db)
):
    """
    创建新的业主/住户信息记录
    """
    return crud.create_owner(db=db, owner=owner)


@router.put("/{owner_id}", response_model=schemas.Owner, summary="更新业主/住户信息")
def update_owner(
    owner_id: int,
    owner: schemas.OwnerUpdate,
    db: Session = Depends(get_db)
):
    """
    更新指定ID的业主/住户信息
    """
    db_owner = crud.update_owner(db, owner_id=owner_id, owner=owner)
    if db_owner is None:
        raise HTTPException(status_code=404, detail="业主/住户信息不存在")
    return db_owner


@router.delete("/{owner_id}", summary="删除业主/住户信息")
def delete_owner(
    owner_id: int,
    db: Session = Depends(get_db)
):
    """
    删除指定ID的业主/住户信息
    """
    success = crud.delete_owner(db, owner_id=owner_id)
    if not success:
        raise HTTPException(status_code=404, detail="业主/住户信息不存在")
    return {"message": "删除成功", "success": True}


# ==================== 家庭成员相关接口 ====================


@router.post("/{owner_id}/family-members", response_model=schemas.FamilyMember, summary="添加家庭成员")
def add_family_member(
    owner_id: int,
    member: schemas.FamilyMemberCreate,
    db: Session = Depends(get_db)
):
    """
    为指定业主添加家庭成员
    """
    db_owner = crud.get_owner(db, owner_id=owner_id)
    if db_owner is None:
        raise HTTPException(status_code=404, detail="业主/住户信息不存在")
    return crud.create_family_member(db=db, owner_id=owner_id, member=member)


@router.delete("/family-members/{member_id}", summary="删除家庭成员")
def remove_family_member(
    member_id: int,
    db: Session = Depends(get_db)
):
    """
    删除指定的家庭成员
    """
    success = crud.delete_family_member(db, member_id=member_id)
    if not success:
        raise HTTPException(status_code=404, detail="家庭成员不存在")
    return {"message": "删除成功", "success": True}


# ==================== 车辆信息相关接口 ====================


@router.post("/{owner_id}/vehicles", response_model=schemas.Vehicle, summary="添加车辆信息")
def add_vehicle(
    owner_id: int,
    vehicle: schemas.VehicleCreate,
    db: Session = Depends(get_db)
):
    """
    为指定业主添加车辆信息
    """
    db_owner = crud.get_owner(db, owner_id=owner_id)
    if db_owner is None:
        raise HTTPException(status_code=404, detail="业主/住户信息不存在")
    return crud.create_vehicle(db=db, owner_id=owner_id, vehicle=vehicle)


@router.delete("/vehicles/{vehicle_id}", summary="删除车辆信息")
def remove_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    """
    删除指定的车辆信息
    """
    success = crud.delete_vehicle(db, vehicle_id=vehicle_id)
    if not success:
        raise HTTPException(status_code=404, detail="车辆信息不存在")
    return {"message": "删除成功", "success": True}


# ==================== 业主-房产关联接口 ====================


@router.post("/relations", response_model=schemas.OwnerProperty, summary="创建业主-房产关联")
def create_owner_property_relation(
    relation: schemas.OwnerPropertyCreate,
    db: Session = Depends(get_db)
):
    """
    创建业主与房产的关联关系
    """
    db_owner = crud.get_owner(db, owner_id=relation.owner_id)
    if db_owner is None:
        raise HTTPException(status_code=404, detail="业主/住户信息不存在")
    db_property = crud.get_property(db, property_id=relation.property_id)
    if db_property is None:
        raise HTTPException(status_code=404, detail="房产信息不存在")
    return crud.create_owner_property(db=db, relation=relation)
