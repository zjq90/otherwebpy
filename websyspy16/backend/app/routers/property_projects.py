"""
物业项目档案API路由
提供物业项目的增删改查接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.config import get_db
from app import crud, schemas

router = APIRouter(
    prefix="/api/property-projects",
    tags=["物业项目档案管理"]
)


@router.get("/", response_model=schemas.PropertyProjectList, summary="获取物业项目列表")
def read_property_projects(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="每页记录数"),
    name: Optional[str] = Query(None, description="项目名称搜索关键词"),
    db: Session = Depends(get_db)
):
    """
    获取物业项目列表，支持分页和名称搜索
    """
    items, total = crud.get_property_projects(db, skip=skip, limit=limit, name=name)
    return {"items": items, "total": total}


@router.get("/{project_id}", response_model=schemas.PropertyProject, summary="获取单个物业项目详情")
def read_property_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取单个物业项目的详细信息
    """
    db_project = crud.get_property_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="物业项目不存在")
    return db_project


@router.post("/", response_model=schemas.PropertyProject, summary="创建新的物业项目")
def create_property_project(
    project: schemas.PropertyProjectCreate,
    db: Session = Depends(get_db)
):
    """
    创建新的物业项目档案
    """
    return crud.create_property_project(db=db, project=project)


@router.put("/{project_id}", response_model=schemas.PropertyProject, summary="更新物业项目信息")
def update_property_project(
    project_id: int,
    project: schemas.PropertyProjectUpdate,
    db: Session = Depends(get_db)
):
    """
    更新指定ID的物业项目信息
    """
    db_project = crud.update_property_project(db, project_id=project_id, project=project)
    if db_project is None:
        raise HTTPException(status_code=404, detail="物业项目不存在")
    return db_project


@router.delete("/{project_id}", summary="删除物业项目")
def delete_property_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    删除指定ID的物业项目
    """
    success = crud.delete_property_project(db, project_id=project_id)
    if not success:
        raise HTTPException(status_code=404, detail="物业项目不存在")
    return {"message": "删除成功", "success": True}
