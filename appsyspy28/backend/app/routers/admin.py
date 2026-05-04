from typing import List, Optional
from datetime import date, timedelta, time
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import (
    User, UserRole, Class, ClassCategory, Room,
    CoachSchedule, CardType
)
from app.schemas.schemas import (
    ClassCreate, ClassUpdate, ClassResponse,
    ClassCategoryCreate, ClassCategoryUpdate, ClassCategoryResponse,
    RoomCreate, RoomUpdate, RoomResponse, UserResponse,
    CoachScheduleCreate, CoachScheduleResponse
)
from app.crud.crud import (
    class_crud, category_crud, room_crud, coach_schedule_crud, user_crud
)
from app.core.security import get_current_active_admin

router = APIRouter(prefix="/api/admin", tags=["管理后台"])

@router.post("/categories", response_model=ClassCategoryResponse, status_code=201)
def create_category(
    category_in: ClassCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    return category_crud.create(
        db, 
        name=category_in.name, 
        description=category_in.description
    )

@router.get("/categories", response_model=List[ClassCategoryResponse])
def get_categories(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    return category_crud.get_all(db, is_active=is_active)

@router.put("/categories/{category_id}", response_model=ClassCategoryResponse)
def update_category(
    category_id: int,
    category_in: ClassCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    category = category_crud.get_by_id(db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="类别不存在")
    
    update_data = category_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    
    return category

@router.post("/rooms", response_model=RoomResponse, status_code=201)
def create_room(
    room_in: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    return room_crud.create(
        db,
        name=room_in.name,
        capacity=room_in.capacity,
        location=room_in.location
    )

@router.get("/rooms", response_model=List[RoomResponse])
def get_rooms(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    return room_crud.get_all(db, is_active=is_active)

@router.put("/rooms/{room_id}", response_model=RoomResponse)
def update_room(
    room_id: int,
    room_in: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    room = room_crud.get_by_id(db, room_id=room_id)
    if not room:
        raise HTTPException(status_code=404, detail="教室不存在")
    
    update_data = room_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(room, key, value)
    db.commit()
    db.refresh(room)
    
    return room

@router.post("/classes", response_model=ClassResponse, status_code=201)
def create_class(
    class_in: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    coach = user_crud.get_by_id(db, user_id=class_in.coach_id)
    if not coach or coach.role != UserRole.COACH:
        raise HTTPException(status_code=400, detail="无效的教练ID")
    
    room = room_crud.get_by_id(db, room_id=class_in.room_id)
    if not room:
        raise HTTPException(status_code=400, detail="无效的教室ID")
    
    category = category_crud.get_by_id(db, category_id=class_in.category_id)
    if not category:
        raise HTTPException(status_code=400, detail="无效的课程类别ID")
    
    if class_in.end_time <= class_in.start_time:
        raise HTTPException(status_code=400, detail="结束时间必须晚于开始时间")
    
    cls = class_crud.create(db, class_in=class_in)
    return class_crud.get_by_id_with_details(db, class_id=cls.id)

@router.put("/classes/{class_id}", response_model=ClassResponse)
def update_class(
    class_id: int,
    class_in: ClassUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    cls = class_crud.get_by_id(db, class_id=class_id)
    if not cls:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    class_crud.update(db, db_class=cls, class_in=class_in)
    return class_crud.get_by_id_with_details(db, class_id=cls.id)

@router.delete("/classes/{class_id}", response_model=dict)
def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    cls = class_crud.get_by_id(db, class_id=class_id)
    if not cls:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    cls.is_active = False
    db.commit()
    
    return {"success": True, "message": "课程已下架"}

@router.post("/coach-schedules", response_model=CoachScheduleResponse, status_code=201)
def create_coach_schedule(
    schedule_in: CoachScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    coach = user_crud.get_by_id(db, user_id=schedule_in.coach_id)
    if not coach or coach.role != UserRole.COACH:
        raise HTTPException(status_code=400, detail="无效的教练ID")
    
    if schedule_in.end_time <= schedule_in.start_time:
        raise HTTPException(status_code=400, detail="结束时间必须晚于开始时间")
    
    schedule = coach_schedule_crud.create(db, schedule_in=schedule_in)
    return coach_schedule_crud.get_by_id(db, schedule_id=schedule.id)

@router.post("/coach-schedules/batch", response_model=List[CoachScheduleResponse])
def create_coach_schedules_batch(
    coach_id: int = Body(..., embed=True),
    start_date: date = Body(..., embed=True),
    end_date: date = Body(..., embed=True),
    time_slots: List[dict] = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    coach = user_crud.get_by_id(db, user_id=coach_id)
    if not coach or coach.role != UserRole.COACH:
        raise HTTPException(status_code=400, detail="无效的教练ID")
    
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="结束日期不能早于开始日期")
    
    if not time_slots:
        raise HTTPException(status_code=400, detail="请指定时段")
    
    created_schedules = []
    
    current_date = start_date
    while current_date <= end_date:
        for slot in time_slots:
            start_time = time.fromisoformat(slot["start_time"])
            end_time = time.fromisoformat(slot["end_time"])
            
            schedule = coach_schedule_crud.create(
                db,
                schedule_in=CoachScheduleCreate(
                    coach_id=coach_id,
                    schedule_date=current_date,
                    start_time=start_time,
                    end_time=end_time,
                    is_available=True
                )
            )
            created_schedules.append(schedule)
        
        current_date += timedelta(days=1)
    
    result = []
    for schedule in created_schedules:
        result.append(coach_schedule_crud.get_by_id(db, schedule_id=schedule.id))
    
    return result

@router.get("/users", response_model=List[UserResponse])
def get_users(
    role: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    query = db.query(User)
    
    if role:
        try:
            user_role = UserRole(role)
            query = query.filter(User.role == user_role)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的角色")
    
    users = query.offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    user = user_crud.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

@router.put("/users/{user_id}/status", response_model=UserResponse)
def update_user_status(
    user_id: int,
    is_active: bool = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    user = user_crud.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    
    return user
