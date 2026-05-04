from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.activity import Activity, ActivityRegistration, ActivityStatus
from app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityRegistrationCreate


def get_activity_by_id(db: Session, activity_id: int) -> Optional[Activity]:
    """
    根据 ID 获取活动
    
    Args:
        db: 数据库会话
        activity_id: 活动 ID
        
    Returns:
        活动对象，不存在返回 None
    """
    return db.query(Activity).filter(Activity.id == activity_id).first()


def get_activities(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    organizer_id: Optional[int] = None,
    activity_type: Optional[str] = None,
    status: Optional[str] = None,
    is_featured: Optional[bool] = None
) -> List[Activity]:
    """
    获取活动列表
    
    Args:
        db: 数据库会话
        skip: 跳过的记录数
        limit: 返回的最大记录数
        organizer_id: 发布人 ID 过滤
        activity_type: 活动类型过滤
        status: 状态过滤
        is_featured: 是否推荐过滤
        
    Returns:
        活动列表
    """
    query = db.query(Activity)
    
    if organizer_id is not None:
        query = query.filter(Activity.organizer_id == organizer_id)
    if activity_type is not None:
        query = query.filter(Activity.activity_type == activity_type)
    if status is not None:
        query = query.filter(Activity.status == status)
    if is_featured is not None:
        query = query.filter(Activity.is_featured == is_featured)
    
    return query.order_by(Activity.created_at.desc()).offset(skip).limit(limit).all()


def create_activity(db: Session, activity: ActivityCreate, organizer_id: int) -> Activity:
    """
    创建新活动
    
    Args:
        db: 数据库会话
        activity: 活动创建数据
        organizer_id: 发布人 ID
        
    Returns:
        创建的活动对象
    """
    db_activity = Activity(
        title=activity.title,
        description=activity.description,
        activity_type=activity.activity_type,
        status=ActivityStatus.DRAFT.value,
        organizer_id=organizer_id,
        start_time=activity.start_time,
        end_time=activity.end_time,
        registration_deadline=activity.registration_deadline,
        location=activity.location,
        max_participants=activity.max_participants,
        image_url=activity.image_url,
        contact_name=activity.contact_name,
        contact_phone=activity.contact_phone,
        is_featured=activity.is_featured
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


def update_activity(
    db: Session, 
    activity_id: int, 
    activity: ActivityUpdate
) -> Optional[Activity]:
    """
    更新活动信息
    
    Args:
        db: 数据库会话
        activity_id: 活动 ID
        activity: 活动更新数据
        
    Returns:
        更新后的活动对象，不存在返回 None
    """
    db_activity = get_activity_by_id(db, activity_id)
    if not db_activity:
        return None
    
    update_data = activity.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_activity, key, value)
    
    db.commit()
    db.refresh(db_activity)
    return db_activity


def delete_activity(db: Session, activity_id: int) -> bool:
    """
    删除活动
    
    Args:
        db: 数据库会话
        activity_id: 活动 ID
        
    Returns:
        是否删除成功
    """
    db_activity = get_activity_by_id(db, activity_id)
    if not db_activity:
        return False
    
    db.query(ActivityRegistration).filter(ActivityRegistration.activity_id == activity_id).delete()
    db.delete(db_activity)
    db.commit()
    return True


def increment_views(db: Session, activity_id: int) -> Optional[Activity]:
    """
    增加活动浏览次数
    
    Args:
        db: 数据库会话
        activity_id: 活动 ID
        
    Returns:
        更新后的活动对象
    """
    db_activity = get_activity_by_id(db, activity_id)
    if not db_activity:
        return None
    
    db_activity.views_count += 1
    db.commit()
    db.refresh(db_activity)
    return db_activity


def get_activity_registration_by_id(db: Session, registration_id: int) -> Optional[ActivityRegistration]:
    """
    根据 ID 获取活动报名
    
    Args:
        db: 数据库会话
        registration_id: 报名 ID
        
    Returns:
        报名对象，不存在返回 None
    """
    return db.query(ActivityRegistration).filter(ActivityRegistration.id == registration_id).first()


def get_activity_registrations(
    db: Session, 
    activity_id: Optional[int] = None,
    user_id: Optional[int] = None
) -> List[ActivityRegistration]:
    """
    获取活动报名列表
    
    Args:
        db: 数据库会话
        activity_id: 活动 ID 过滤
        user_id: 用户 ID 过滤
        
    Returns:
        报名列表
    """
    query = db.query(ActivityRegistration)
    
    if activity_id is not None:
        query = query.filter(ActivityRegistration.activity_id == activity_id)
    if user_id is not None:
        query = query.filter(ActivityRegistration.user_id == user_id)
    
    return query.order_by(ActivityRegistration.created_at.desc()).all()


def create_activity_registration(
    db: Session, 
    activity_id: int,
    registration: ActivityRegistrationCreate,
    user_id: int
) -> Optional[ActivityRegistration]:
    """
    创建活动报名
    
    Args:
        db: 数据库会话
        activity_id: 活动 ID
        registration: 报名创建数据
        user_id: 报名用户 ID
        
    Returns:
        创建的报名对象，报名失败返回 None
    """
    activity = get_activity_by_id(db, activity_id)
    if not activity:
        return None
    
    if activity.max_participants and activity.current_participants >= activity.max_participants:
        return None
    
    existing = db.query(ActivityRegistration).filter(
        ActivityRegistration.activity_id == activity_id,
        ActivityRegistration.user_id == user_id
    ).first()
    if existing:
        return None
    
    db_registration = ActivityRegistration(
        activity_id=activity_id,
        user_id=user_id,
        participant_name=registration.participant_name,
        participant_phone=registration.participant_phone,
        participant_count=registration.participant_count,
        room_number=registration.room_number,
        remarks=registration.remarks
    )
    db.add(db_registration)
    
    activity.current_participants += 1
    
    db.commit()
    db.refresh(db_registration)
    return db_registration


def cancel_activity_registration(db: Session, registration_id: int, user_id: int) -> bool:
    """
    取消活动报名
    
    Args:
        db: 数据库会话
        registration_id: 报名 ID
        user_id: 用户 ID（用于验证权限）
        
    Returns:
        是否取消成功
    """
    db_registration = get_activity_registration_by_id(db, registration_id)
    if not db_registration or db_registration.user_id != user_id:
        return False
    
    activity = get_activity_by_id(db, db_registration.activity_id)
    if activity:
        activity.current_participants = max(0, activity.current_participants - 1)
    
    db.delete(db_registration)
    db.commit()
    return True
