from typing import List, Optional
from datetime import date, timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User, Class
from app.schemas.schemas import (
    ClassResponse, ClassSimpleResponse, ClassListResponse
)
from app.crud.crud import class_crud, category_crud
from app.core.security import get_current_active_member

router = APIRouter(prefix="/api/classes", tags=["课程日历"])

def get_week_start_end(target_date: date) -> tuple:
    weekday = target_date.weekday()
    week_start = target_date - timedelta(days=weekday)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end

@router.get("/calendar/week", response_model=ClassListResponse)
def get_week_calendar(
    target_date: Optional[date] = Query(None, description="目标日期，不传则为今天"),
    category_id: Optional[int] = Query(None, description="课程类别ID过滤"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    if target_date is None:
        target_date = date.today()
    
    week_start, week_end = get_week_start_end(target_date)
    
    classes = class_crud.get_by_date_range(
        db, 
        start_date=week_start, 
        end_date=week_end,
        category_id=category_id
    )
    
    return ClassListResponse(
        total=len(classes),
        items=[ClassResponse.model_validate(cls) for cls in classes]
    )

@router.get("/calendar/day", response_model=ClassListResponse)
def get_day_calendar(
    target_date: Optional[date] = Query(None, description="目标日期，不传则为今天"),
    category_id: Optional[int] = Query(None, description="课程类别ID过滤"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    if target_date is None:
        target_date = date.today()
    
    classes = class_crud.get_by_day(db, class_date=target_date)
    
    if category_id:
        classes = [c for c in classes if c.category_id == category_id]
    
    return ClassListResponse(
        total=len(classes),
        items=[ClassResponse.model_validate(cls) for cls in classes]
    )

@router.get("/calendar/range", response_model=ClassListResponse)
def get_classes_by_range(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    category_id: Optional[int] = Query(None, description="课程类别ID过滤"),
    coach_id: Optional[int] = Query(None, description="教练ID过滤"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="结束日期不能早于开始日期")
    
    classes = class_crud.get_by_date_range(
        db,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id,
        coach_id=coach_id
    )
    
    return ClassListResponse(
        total=len(classes),
        items=[ClassResponse.model_validate(cls) for cls in classes]
    )

@router.get("/{class_id}", response_model=ClassResponse)
def get_class_detail(
    class_id: int = Path(..., gt=0, description="课程ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    cls = class_crud.get_by_id_with_details(db, class_id=class_id)
    if not cls:
        raise HTTPException(status_code=404, detail="课程不存在")
    return ClassResponse.model_validate(cls)

@router.get("/", response_model=ClassListResponse)
def get_classes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    today = date.today()
    end_date = today + timedelta(days=30)
    
    classes = class_crud.get_by_date_range(
        db,
        start_date=today,
        end_date=end_date,
        category_id=category_id
    )
    
    return ClassListResponse(
        total=len(classes),
        items=[ClassResponse.model_validate(cls) for cls in classes]
    )
