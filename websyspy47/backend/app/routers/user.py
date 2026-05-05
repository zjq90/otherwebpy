from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.user import User, Feedback
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserListResponse,
    FeedbackCreate, FeedbackUpdate, FeedbackResponse
)
from app.schemas.common import ApiResponse, PageParams, PageResult

router = APIRouter(prefix="/users", tags=["用户管理"])

@router.post("/", response_model=ApiResponse[UserResponse])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    创建用户
    """
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    if user.phone:
        existing_phone = db.query(User).filter(User.phone == user.phone).first()
        if existing_phone:
            raise HTTPException(status_code=400, detail="手机号已被注册")
    
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return ApiResponse(data=db_user)

@router.get("/{user_id}", response_model=ApiResponse[UserResponse])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    获取用户详情
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return ApiResponse(data=user)

@router.get("/", response_model=ApiResponse[PageResult[UserListResponse]])
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    username: Optional[str] = None,
    phone: Optional[str] = None,
    user_type: Optional[int] = None,
    status: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取用户列表（分页）
    """
    query = db.query(User)
    
    if username:
        query = query.filter(User.username.like(f"%{username}%"))
    if phone:
        query = query.filter(User.phone.like(f"%{phone}%"))
    if user_type is not None:
        query = query.filter(User.user_type == user_type)
    if status is not None:
        query = query.filter(User.status == status)
    
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    users = query.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    result = PageResult[UserListResponse](
        list=users,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
    return ApiResponse(data=result)

@router.put("/{user_id}", response_model=ApiResponse[UserResponse])
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """
    更新用户信息
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return ApiResponse(data=user)

@router.delete("/{user_id}", response_model=ApiResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    删除用户（软删除，实际修改状态）
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    user.status = 0
    db.commit()
    return ApiResponse(message="用户已禁用")

@router.post("/batch-delete", response_model=ApiResponse)
def batch_delete_users(ids: List[int], db: Session = Depends(get_db)):
    """
    批量删除用户
    """
    for user_id in ids:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.status = 0
    db.commit()
    return ApiResponse(message="批量操作成功")

@router.post("/feedbacks/", response_model=ApiResponse[FeedbackResponse])
def create_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    """
    创建反馈/投诉
    """
    db_feedback = Feedback(**feedback.model_dump())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return ApiResponse(data=db_feedback)

@router.get("/feedbacks/", response_model=ApiResponse[PageResult[FeedbackResponse]])
def list_feedbacks(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user_id: Optional[int] = None,
    feedback_type: Optional[int] = None,
    status: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取反馈列表（分页）
    """
    query = db.query(Feedback)
    
    if user_id:
        query = query.filter(Feedback.user_id == user_id)
    if feedback_type is not None:
        query = query.filter(Feedback.feedback_type == feedback_type)
    if status is not None:
        query = query.filter(Feedback.status == status)
    
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    feedbacks = query.order_by(Feedback.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    result = PageResult[FeedbackResponse](
        list=feedbacks,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
    return ApiResponse(data=result)

@router.get("/feedbacks/{feedback_id}", response_model=ApiResponse[FeedbackResponse])
def get_feedback(feedback_id: int, db: Session = Depends(get_db)):
    """
    获取反馈详情
    """
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈不存在")
    return ApiResponse(data=feedback)

@router.put("/feedbacks/{feedback_id}", response_model=ApiResponse[FeedbackResponse])
def update_feedback(feedback_id: int, feedback_update: FeedbackUpdate, db: Session = Depends(get_db)):
    """
    更新反馈（回复）
    """
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈不存在")
    
    update_data = feedback_update.model_dump(exclude_unset=True)
    if 'reply' in update_data and update_data['reply']:
        update_data['reply_time'] = datetime.now()
    
    for key, value in update_data.items():
        setattr(feedback, key, value)
    
    db.commit()
    db.refresh(feedback)
    return ApiResponse(data=feedback)
