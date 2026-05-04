"""
房产信息API路由
提供房产信息的增删改查接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.config import get_db
from app import crud, schemas

router = APIRouter(
    prefix="/api/properties",
    tags=["房产信息管理"]
)


@router.get("/", response_model=schemas.PropertyList, summary="获取房产信息列表")
def read_properties(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="每页记录数"),
    project_id: Optional[int] = Query(None, description="所属项目ID"),
    status: Optional[str] = Query(None, description="房产状态"),
    building_number: Optional[str] = Query(None, description="楼栋号"),
    room_number: Optional[str] = Query(None, description="房间号"),
    db: Session = Depends(get_db)
):
    """
    获取房产信息列表，支持多条件筛选和分页
    """
    items, total = crud.get_properties(
        db, 
        skip=skip, 
        limit=limit,
        project_id=project_id,
        status=status,
        building_number=building_number,
        room_number=room_number
    )
    return {"items": items, "total": total}


@router.get("/{property_id}", response_model=schemas.Property, summary="获取单个房产详情")
def read_property(
    property_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取单个房产的详细信息
    """
    db_property = crud.get_property(db, property_id=property_id)
    if db_property is None:
        raise HTTPException(status_code=404, detail="房产信息不存在")
    return db_property


@router.post("/", response_model=schemas.Property, summary="创建新的房产信息")
def create_property(
    property: schemas.PropertyCreate,
    db: Session = Depends(get_db)
):
    """
    创建新的房产信息记录
    """
    return crud.create_property(db=db, property=property)


@router.put("/{property_id}", response_model=schemas.Property, summary="更新房产信息")
def update_property(
    property_id: int,
    property: schemas.PropertyUpdate,
    db: Session = Depends(get_db)
):
    """
    更新指定ID的房产信息
    """
    db_property = crud.update_property(db, property_id=property_id, property=property)
    if db_property is None:
        raise HTTPException(status_code=404, detail="房产信息不存在")
    return db_property


@router.delete("/{property_id}", summary="删除房产信息")
def delete_property(
    property_id: int,
    db: Session = Depends(get_db)
):
    """
    删除指定ID的房产信息
    """
    success = crud.delete_property(db, property_id=property_id)
    if not success:
        raise HTTPException(status_code=404, detail="房产信息不存在")
    return {"message": "删除成功", "success": True}
