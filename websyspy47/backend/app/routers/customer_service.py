from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.customer_service import CustomerServiceStaff, Consultation, ConsultationMessage
from app.schemas.customer_service import (
    CustomerServiceStaffCreate, CustomerServiceStaffUpdate, CustomerServiceStaffResponse,
    ConsultationCreate, ConsultationUpdate, ConsultationResponse,
    ConsultationMessageCreate, ConsultationMessageResponse
)
from app.schemas.common import ApiResponse, PageResult

router = APIRouter(prefix="/customer-service", tags=["客服管理"])

@router.post("/staffs/", response_model=ApiResponse[CustomerServiceStaffResponse])
def create_cs_staff(staff: CustomerServiceStaffCreate, db: Session = Depends(get_db)):
    """
    创建客服人员
    """
    existing = db.query(CustomerServiceStaff).filter(CustomerServiceStaff.username == staff.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    db_staff = CustomerServiceStaff(**staff.model_dump())
    db.add(db_staff)
    db.commit()
    db.refresh(db_staff)
    return ApiResponse(data=db_staff)

@router.get("/staffs/{staff_id}", response_model=ApiResponse[CustomerServiceStaffResponse])
def get_cs_staff(staff_id: int, db: Session = Depends(get_db)):
    """
    获取客服人员详情
    """
    staff = db.query(CustomerServiceStaff).filter(CustomerServiceStaff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="客服人员不存在")
    return ApiResponse(data=staff)

@router.get("/staffs/", response_model=ApiResponse[PageResult[CustomerServiceStaffResponse]])
def list_cs_staffs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    username: Optional[str] = None,
    real_name: Optional[str] = None,
    group_type: Optional[int] = None,
    status: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取客服人员列表
    """
    query = db.query(CustomerServiceStaff)
    
    if username:
        query = query.filter(CustomerServiceStaff.username.like(f"%{username}%"))
    if real_name:
        query = query.filter(CustomerServiceStaff.real_name.like(f"%{real_name}%"))
    if group_type is not None:
        query = query.filter(CustomerServiceStaff.group_type == group_type)
    if status is not None:
        query = query.filter(CustomerServiceStaff.status == status)
    
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    staffs = query.order_by(CustomerServiceStaff.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    result = PageResult[CustomerServiceStaffResponse](
        list=staffs,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
    return ApiResponse(data=result)

@router.put("/staffs/{staff_id}", response_model=ApiResponse[CustomerServiceStaffResponse])
def update_cs_staff(staff_id: int, staff_update: CustomerServiceStaffUpdate, db: Session = Depends(get_db)):
    """
    更新客服人员信息
    """
    staff = db.query(CustomerServiceStaff).filter(CustomerServiceStaff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="客服人员不存在")
    
    update_data = staff_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(staff, key, value)
    
    db.commit()
    db.refresh(staff)
    return ApiResponse(data=staff)

@router.delete("/staffs/{staff_id}", response_model=ApiResponse)
def delete_cs_staff(staff_id: int, db: Session = Depends(get_db)):
    """
    删除客服人员（软删除）
    """
    staff = db.query(CustomerServiceStaff).filter(CustomerServiceStaff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="客服人员不存在")
    
    staff.status = 0
    db.commit()
    return ApiResponse(message="客服人员已禁用")

@router.get("/consultations/", response_model=ApiResponse[PageResult[ConsultationResponse]])
def list_consultations(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user_id: Optional[int] = Query(None),
    user_name: Optional[str] = Query(None),
    cs_staff_id: Optional[int] = Query(None),
    staff_id: Optional[int] = Query(None),
    consultation_type: Optional[int] = Query(None),
    type: Optional[int] = Query(None),
    status: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取咨询记录列表
    """
    query = db.query(Consultation)
    
    if user_id:
        query = query.filter(Consultation.user_id == user_id)
    if user_name:
        query = query.filter(
            (Consultation.user_name.like(f"%{user_name}%")) |
            (Consultation.user_phone.like(f"%{user_name}%"))
        )
    
    target_staff_id = cs_staff_id if cs_staff_id is not None else staff_id
    if target_staff_id:
        query = query.filter(Consultation.cs_staff_id == target_staff_id)
    
    target_type = consultation_type if consultation_type is not None else type
    if target_type is not None:
        query = query.filter(Consultation.consultation_type == target_type)
    
    if status is not None:
        query = query.filter(Consultation.status == status)
    
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Consultation.created_at >= start_dt)
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(Consultation.created_at <= end_dt)
        except ValueError:
            pass
    
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    consultations = query.order_by(Consultation.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    result = PageResult[ConsultationResponse](
        list=consultations,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
    return ApiResponse(data=result)

@router.get("/consultations/{consultation_id}", response_model=ApiResponse[ConsultationResponse])
def get_consultation(consultation_id: int, db: Session = Depends(get_db)):
    """
    获取咨询详情
    """
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(status_code=404, detail="咨询记录不存在")
    return ApiResponse(data=consultation)

@router.put("/consultations/{consultation_id}", response_model=ApiResponse[ConsultationResponse])
def update_consultation(consultation_id: int, consultation_update: ConsultationUpdate, db: Session = Depends(get_db)):
    """
    更新咨询记录（分配、回复等）
    """
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(status_code=404, detail="咨询记录不存在")
    
    update_data = consultation_update.model_dump(exclude_unset=True)
    
    if 'cs_staff_id' in update_data and update_data['cs_staff_id'] and consultation.status == 0:
        update_data['status'] = 1
        update_data['assign_time'] = datetime.now()
    
    if 'status' in update_data:
        status = update_data['status']
        if status == 2 and consultation.status != 2:
            update_data['resolve_time'] = datetime.now()
        elif status == 3 and consultation.status != 3:
            update_data['close_time'] = datetime.now()
    
    for key, value in update_data.items():
        setattr(consultation, key, value)
    
    db.commit()
    db.refresh(consultation)
    return ApiResponse(data=consultation)

@router.get("/consultations/{consultation_id}/messages", response_model=ApiResponse[List[ConsultationMessageResponse]])
def get_consultation_messages(consultation_id: int, db: Session = Depends(get_db)):
    """
    获取咨询的消息列表
    """
    messages = db.query(ConsultationMessage).filter(
        ConsultationMessage.consultation_id == consultation_id
    ).order_by(ConsultationMessage.id.asc()).all()
    return ApiResponse(data=messages)

@router.post("/consultations/{consultation_id}/messages", response_model=ApiResponse[ConsultationMessageResponse])
def create_consultation_message(consultation_id: int, message: ConsultationMessageCreate, db: Session = Depends(get_db)):
    """
    发送咨询消息
    """
    db_message = ConsultationMessage(**message.model_dump())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return ApiResponse(data=db_message)
