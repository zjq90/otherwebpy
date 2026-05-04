from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.activity import ActivityStatus
from app.schemas.activity import (
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse,
    ActivityRegistrationCreate,
    ActivityRegistrationResponse
)
from app.crud import activity as activity_crud
from app.routers.auth import get_current_active_user, get_admin_user

router = APIRouter(prefix="/api/activities", tags=["社区活动"])


@router.post("/", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    activity: ActivityCreate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    创建活动
    
    仅管理员和物业人员可以创建活动
    
    - **title**: 活动标题
    - **description**: 活动描述
    - **activity_type**: 活动类型
    - **start_time**: 开始时间
    - **end_time**: 结束时间
    - **registration_deadline**: 报名截止时间
    - **location**: 活动地点
    - **max_participants**: 最大参与人数
    - **image_url**: 活动图片URL
    - **contact_name**: 联系人姓名
    - **contact_phone**: 联系电话
    - **is_featured**: 是否为推荐活动
    """
    return activity_crud.create_activity(db=db, activity=activity, organizer_id=current_user.id)


@router.get("/", response_model=List[ActivityResponse])
def read_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    activity_type: Optional[str] = Query(None, description="活动类型过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
    is_featured: Optional[bool] = Query(None, description="是否推荐过滤"),
    db: Session = Depends(get_db)
):
    """
    获取活动列表
    
    所有人都可以查看已发布的活动列表
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    - **activity_type**: 活动类型过滤
    - **status**: 状态过滤
    - **is_featured**: 是否推荐过滤
    """
    activities = activity_crud.get_activities(
        db=db,
        skip=skip,
        limit=limit,
        activity_type=activity_type,
        status=status,
        is_featured=is_featured
    )
    return activities


@router.get("/published", response_model=List[ActivityResponse])
def read_published_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    activity_type: Optional[str] = Query(None, description="活动类型过滤"),
    is_featured: Optional[bool] = Query(None, description="是否推荐过滤"),
    db: Session = Depends(get_db)
):
    """
    获取已发布的活动列表
    
    获取所有已发布、可报名或进行中的活动
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    - **activity_type**: 活动类型过滤
    - **is_featured**: 是否推荐过滤
    """
    activities = activity_crud.get_activities(
        db=db,
        skip=skip,
        limit=limit,
        activity_type=activity_type,
        is_featured=is_featured
    )
    published_statuses = [
        ActivityStatus.PUBLISHED.value,
        ActivityStatus.REGISTRATION_OPEN.value,
        ActivityStatus.ONGOING.value
    ]
    return [a for a in activities if a.status in published_statuses]


@router.get("/{activity_id}", response_model=ActivityResponse)
def read_activity(
    activity_id: int,
    db: Session = Depends(get_db)
):
    """
    获取活动详情
    
    浏览活动详情时会增加浏览次数
    
    - **activity_id**: 活动 ID
    """
    db_activity = activity_crud.get_activity_by_id(db, activity_id=activity_id)
    if db_activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    activity_crud.increment_views(db, activity_id=activity_id)
    return db_activity


@router.put("/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: int,
    activity: ActivityUpdate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    更新活动
    
    仅管理员和物业人员可以更新活动
    
    - **activity_id**: 活动 ID
    - **activity**: 更新数据
    """
    db_activity = activity_crud.get_activity_by_id(db, activity_id=activity_id)
    if db_activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    updated_activity = activity_crud.update_activity(
        db=db,
        activity_id=activity_id,
        activity=activity
    )
    return updated_activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    activity_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    删除活动
    
    仅管理员可以删除
    
    - **activity_id**: 活动 ID
    """
    success = activity_crud.delete_activity(db, activity_id=activity_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )


@router.post("/{activity_id}/register", response_model=ActivityRegistrationResponse, status_code=status.HTTP_201_CREATED)
def register_activity(
    activity_id: int,
    registration: ActivityRegistrationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    报名活动
    
    业主可以报名参与活动
    
    - **activity_id**: 活动 ID
    - **registration**: 报名信息
    """
    db_activity = activity_crud.get_activity_by_id(db, activity_id=activity_id)
    if db_activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    if db_activity.status not in [ActivityStatus.REGISTRATION_OPEN.value, ActivityStatus.PUBLISHED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="活动不接受报名"
        )
    
    db_registration = activity_crud.create_activity_registration(
        db=db,
        activity_id=activity_id,
        registration=registration,
        user_id=current_user.id
    )
    
    if db_registration is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="报名失败，可能是人数已满或已报名"
        )
    
    return db_registration


@router.delete("/{activity_id}/register", status_code=status.HTTP_204_NO_CONTENT)
def cancel_registration(
    activity_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    取消活动报名
    
    - **activity_id**: 活动 ID
    """
    registrations = activity_crud.get_activity_registrations(
        db=db,
        activity_id=activity_id,
        user_id=current_user.id
    )
    
    if not registrations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到该活动的报名记录"
        )
    
    for reg in registrations:
        activity_crud.cancel_activity_registration(db, registration_id=reg.id, user_id=current_user.id)


@router.get("/{activity_id}/registrations", response_model=List[ActivityRegistrationResponse])
def read_activity_registrations(
    activity_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取活动的报名列表
    
    仅管理员和物业人员可以查看
    
    - **activity_id**: 活动 ID
    """
    db_activity = activity_crud.get_activity_by_id(db, activity_id=activity_id)
    if db_activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    registrations = activity_crud.get_activity_registrations(db, activity_id=activity_id)
    return registrations


@router.get("/my/registrations", response_model=List[ActivityRegistrationResponse])
def read_my_registrations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的活动报名列表
    """
    registrations = activity_crud.get_activity_registrations(db, user_id=current_user.id)
    return registrations


@router.post("/{activity_id}/publish", response_model=ActivityResponse)
def publish_activity(
    activity_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    发布活动
    
    将活动状态改为已发布并开放报名
    
    - **activity_id**: 活动 ID
    """
    db_activity = activity_crud.get_activity_by_id(db, activity_id=activity_id)
    if db_activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    update_data = ActivityUpdate(status=ActivityStatus.REGISTRATION_OPEN.value)
    updated_activity = activity_crud.update_activity(
        db=db,
        activity_id=activity_id,
        activity=update_data
    )
    return updated_activity


@router.post("/{activity_id}/close-registration", response_model=ActivityResponse)
def close_activity_registration(
    activity_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    关闭活动报名
    
    - **activity_id**: 活动 ID
    """
    db_activity = activity_crud.get_activity_by_id(db, activity_id=activity_id)
    if db_activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    update_data = ActivityUpdate(status=ActivityStatus.REGISTRATION_CLOSED.value)
    updated_activity = activity_crud.update_activity(
        db=db,
        activity_id=activity_id,
        activity=update_data
    )
    return updated_activity
