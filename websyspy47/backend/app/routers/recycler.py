from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.recycler import Recycler, RecyclerPerformance
from app.schemas.recycler import (
    RecyclerCreate, RecyclerUpdate, RecyclerResponse,
    RecyclerPerformanceCreate, RecyclerPerformanceResponse
)
from app.schemas.common import ApiResponse, PageResult

router = APIRouter(prefix="/recyclers", tags=["回收人员管理"])

@router.post("/", response_model=ApiResponse[RecyclerResponse])
def create_recycler(recycler: RecyclerCreate, db: Session = Depends(get_db)):
    """
    创建回收人员
    """
    existing = db.query(Recycler).filter(Recycler.username == recycler.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    if recycler.phone:
        existing_phone = db.query(Recycler).filter(Recycler.phone == recycler.phone).first()
        if existing_phone:
            raise HTTPException(status_code=400, detail="手机号已被使用")
    
    db_recycler = Recycler(**recycler.model_dump())
    db.add(db_recycler)
    db.commit()
    db.refresh(db_recycler)
    return ApiResponse(data=db_recycler)

@router.get("/{recycler_id}", response_model=ApiResponse[RecyclerResponse])
def get_recycler(recycler_id: int, db: Session = Depends(get_db)):
    """
    获取回收人员详情
    """
    recycler = db.query(Recycler).filter(Recycler.id == recycler_id).first()
    if not recycler:
        raise HTTPException(status_code=404, detail="回收人员不存在")
    return ApiResponse(data=recycler)

@router.get("/", response_model=ApiResponse[PageResult[RecyclerResponse]])
def list_recyclers(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    username: Optional[str] = None,
    real_name: Optional[str] = None,
    phone: Optional[str] = None,
    status: Optional[int] = None,
    area: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取回收人员列表（分页）
    """
    query = db.query(Recycler)
    
    if username:
        query = query.filter(Recycler.username.like(f"%{username}%"))
    if real_name:
        query = query.filter(Recycler.real_name.like(f"%{real_name}%"))
    if phone:
        query = query.filter(Recycler.phone.like(f"%{phone}%"))
    if status is not None:
        query = query.filter(Recycler.status == status)
    if area:
        query = query.filter(Recycler.area.like(f"%{area}%"))
    
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    recyclers = query.order_by(Recycler.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    result = PageResult[RecyclerResponse](
        list=recyclers,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
    return ApiResponse(data=result)

@router.put("/{recycler_id}", response_model=ApiResponse[RecyclerResponse])
def update_recycler(recycler_id: int, recycler_update: RecyclerUpdate, db: Session = Depends(get_db)):
    """
    更新回收人员信息
    """
    recycler = db.query(Recycler).filter(Recycler.id == recycler_id).first()
    if not recycler:
        raise HTTPException(status_code=404, detail="回收人员不存在")
    
    update_data = recycler_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(recycler, key, value)
    
    db.commit()
    db.refresh(recycler)
    return ApiResponse(data=recycler)

@router.delete("/{recycler_id}", response_model=ApiResponse)
def delete_recycler(recycler_id: int, db: Session = Depends(get_db)):
    """
    删除回收人员（软删除）
    """
    recycler = db.query(Recycler).filter(Recycler.id == recycler_id).first()
    if not recycler:
        raise HTTPException(status_code=404, detail="回收人员不存在")
    
    recycler.status = 0
    db.commit()
    return ApiResponse(message="回收人员已禁用")

@router.post("/performances/", response_model=ApiResponse[RecyclerPerformanceResponse])
def create_performance(performance: RecyclerPerformanceCreate, db: Session = Depends(get_db)):
    """
    创建绩效考核记录
    """
    db_performance = RecyclerPerformance(**performance.model_dump())
    db.add(db_performance)
    db.commit()
    db.refresh(db_performance)
    return ApiResponse(data=db_performance)

@router.get("/performances/", response_model=ApiResponse[PageResult[RecyclerPerformanceResponse]])
def list_performances(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    recycler_id: Optional[int] = Query(None),
    period_type: Optional[int] = Query(None),
    period_year: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取绩效考核记录列表
    """
    query = db.query(RecyclerPerformance)
    
    if recycler_id:
        query = query.filter(RecyclerPerformance.recycler_id == recycler_id)
    if period_type is not None:
        query = query.filter(RecyclerPerformance.period_type == str(period_type))
    target_year = period_year if period_year is not None else year
    if target_year:
        query = query.filter(RecyclerPerformance.period_year == target_year)
    
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    performances = query.order_by(RecyclerPerformance.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    result = PageResult[RecyclerPerformanceResponse](
        list=performances,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
    return ApiResponse(data=result)
