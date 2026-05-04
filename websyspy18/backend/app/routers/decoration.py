"""
装修管理模块 - API路由
包含装修申请、押金管理、巡检记录等API接口
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.decoration import (
    DecorationApplicationCreate, DecorationApplicationUpdate, DecorationApplicationResponse,
    DecorationDepositCreate, DecorationDepositUpdate, DecorationDepositResponse,
    DecorationInspectionCreate, DecorationInspectionUpdate, DecorationInspectionResponse
)
from app.crud import decoration as crud_decoration

router = APIRouter()

# ==================== 装修申请 API ====================

@router.post("/applications/", response_model=DecorationApplicationResponse, tags=["装修申请"])
def create_application(application: DecorationApplicationCreate, db: Session = Depends(get_db)):
    """
    创建装修申请
    """
    if application.application_no:
        db_application = crud_decoration.decoration_application.get_by_application_no(db, application_no=application.application_no)
        if db_application:
            raise HTTPException(status_code=400, detail="申请编号已存在")
    return crud_decoration.decoration_application.create(db=db, obj_in=application)

@router.get("/applications/", response_model=List[DecorationApplicationResponse], tags=["装修申请"])
def read_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    room_number: Optional[str] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取装修申请列表
    """
    if keyword:
        return crud_decoration.decoration_application.search(db, keyword=keyword, skip=skip, limit=limit)
    if room_number:
        return crud_decoration.decoration_application.get_by_room(db, room_number=room_number, skip=skip, limit=limit)
    if status:
        return crud_decoration.decoration_application.get_by_status(db, status=status, skip=skip, limit=limit)
    return crud_decoration.decoration_application.get_multi(db, skip=skip, limit=limit)

@router.get("/applications/{application_id}", response_model=DecorationApplicationResponse, tags=["装修申请"])
def read_application(application_id: int, db: Session = Depends(get_db)):
    """
    获取单个装修申请
    """
    db_application = crud_decoration.decoration_application.get(db, id=application_id)
    if db_application is None:
        raise HTTPException(status_code=404, detail="装修申请不存在")
    return db_application

@router.put("/applications/{application_id}", response_model=DecorationApplicationResponse, tags=["装修申请"])
def update_application(application_id: int, application: DecorationApplicationUpdate, db: Session = Depends(get_db)):
    """
    更新装修申请
    """
    db_application = crud_decoration.decoration_application.get(db, id=application_id)
    if db_application is None:
        raise HTTPException(status_code=404, detail="装修申请不存在")
    return crud_decoration.decoration_application.update(db, db_obj=db_application, obj_in=application)

@router.delete("/applications/{application_id}", response_model=DecorationApplicationResponse, tags=["装修申请"])
def delete_application(application_id: int, db: Session = Depends(get_db)):
    """
    删除装修申请
    """
    db_application = crud_decoration.decoration_application.get(db, id=application_id)
    if db_application is None:
        raise HTTPException(status_code=404, detail="装修申请不存在")
    return crud_decoration.decoration_application.remove(db, id=application_id)

# ==================== 装修押金 API ====================

@router.post("/deposits/", response_model=DecorationDepositResponse, tags=["装修押金"])
def create_deposit(deposit: DecorationDepositCreate, db: Session = Depends(get_db)):
    """
    创建装修押金记录
    """
    return crud_decoration.decoration_deposit.create(db=db, obj_in=deposit)

@router.get("/deposits/", response_model=List[DecorationDepositResponse], tags=["装修押金"])
def read_deposits(
    skip: int = 0,
    limit: int = 100,
    application_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取装修押金列表
    """
    if application_id:
        return crud_decoration.decoration_deposit.get_by_application(db, application_id=application_id, skip=skip, limit=limit)
    if status:
        return crud_decoration.decoration_deposit.get_by_status(db, status=status, skip=skip, limit=limit)
    return crud_decoration.decoration_deposit.get_multi(db, skip=skip, limit=limit)

@router.get("/deposits/{deposit_id}", response_model=DecorationDepositResponse, tags=["装修押金"])
def read_deposit(deposit_id: int, db: Session = Depends(get_db)):
    """
    获取单个装修押金记录
    """
    db_deposit = crud_decoration.decoration_deposit.get(db, id=deposit_id)
    if db_deposit is None:
        raise HTTPException(status_code=404, detail="押金记录不存在")
    return db_deposit

@router.put("/deposits/{deposit_id}", response_model=DecorationDepositResponse, tags=["装修押金"])
def update_deposit(deposit_id: int, deposit: DecorationDepositUpdate, db: Session = Depends(get_db)):
    """
    更新装修押金记录
    """
    db_deposit = crud_decoration.decoration_deposit.get(db, id=deposit_id)
    if db_deposit is None:
        raise HTTPException(status_code=404, detail="押金记录不存在")
    return crud_decoration.decoration_deposit.update(db, db_obj=db_deposit, obj_in=deposit)

@router.delete("/deposits/{deposit_id}", response_model=DecorationDepositResponse, tags=["装修押金"])
def delete_deposit(deposit_id: int, db: Session = Depends(get_db)):
    """
    删除装修押金记录
    """
    db_deposit = crud_decoration.decoration_deposit.get(db, id=deposit_id)
    if db_deposit is None:
        raise HTTPException(status_code=404, detail="押金记录不存在")
    return crud_decoration.decoration_deposit.remove(db, id=deposit_id)

# ==================== 装修巡检 API ====================

@router.post("/inspections/", response_model=DecorationInspectionResponse, tags=["装修巡检"])
def create_inspection(inspection: DecorationInspectionCreate, db: Session = Depends(get_db)):
    """
    创建装修巡检记录
    """
    return crud_decoration.decoration_inspection.create(db=db, obj_in=inspection)

@router.get("/inspections/", response_model=List[DecorationInspectionResponse], tags=["装修巡检"])
def read_inspections(
    skip: int = 0,
    limit: int = 100,
    application_id: Optional[int] = None,
    unrectified: bool = False,
    db: Session = Depends(get_db)
):
    """
    获取装修巡检列表
    """
    if unrectified:
        return crud_decoration.decoration_inspection.get_unrectified(db, skip=skip, limit=limit)
    if application_id:
        return crud_decoration.decoration_inspection.get_by_application(db, application_id=application_id, skip=skip, limit=limit)
    return crud_decoration.decoration_inspection.get_multi(db, skip=skip, limit=limit)

@router.get("/inspections/{inspection_id}", response_model=DecorationInspectionResponse, tags=["装修巡检"])
def read_inspection(inspection_id: int, db: Session = Depends(get_db)):
    """
    获取单个装修巡检记录
    """
    db_inspection = crud_decoration.decoration_inspection.get(db, id=inspection_id)
    if db_inspection is None:
        raise HTTPException(status_code=404, detail="巡检记录不存在")
    return db_inspection

@router.put("/inspections/{inspection_id}", response_model=DecorationInspectionResponse, tags=["装修巡检"])
def update_inspection(inspection_id: int, inspection: DecorationInspectionUpdate, db: Session = Depends(get_db)):
    """
    更新装修巡检记录
    """
    db_inspection = crud_decoration.decoration_inspection.get(db, id=inspection_id)
    if db_inspection is None:
        raise HTTPException(status_code=404, detail="巡检记录不存在")
    return crud_decoration.decoration_inspection.update(db, db_obj=db_inspection, obj_in=inspection)

@router.delete("/inspections/{inspection_id}", response_model=DecorationInspectionResponse, tags=["装修巡检"])
def delete_inspection(inspection_id: int, db: Session = Depends(get_db)):
    """
    删除装修巡检记录
    """
    db_inspection = crud_decoration.decoration_inspection.get(db, id=inspection_id)
    if db_inspection is None:
        raise HTTPException(status_code=404, detail="巡检记录不存在")
    return crud_decoration.decoration_inspection.remove(db, id=inspection_id)
