from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.announcement import Announcement
from app.schemas.announcement import (
    AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse
)
from app.schemas.common import ApiResponse, PageResult

router = APIRouter(prefix="/announcements", tags=["公告管理"])

@router.post("/", response_model=ApiResponse[AnnouncementResponse])
def create_announcement(announcement: AnnouncementCreate, db: Session = Depends(get_db)):
    """
    创建公告
    """
    db_announcement = Announcement(**announcement.model_dump())
    db.add(db_announcement)
    db.commit()
    db.refresh(db_announcement)
    return ApiResponse(data=db_announcement)

@router.get("/{announcement_id}", response_model=ApiResponse[AnnouncementResponse])
def get_announcement(announcement_id: int, db: Session = Depends(get_db)):
    """
    获取公告详情
    """
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")
    return ApiResponse(data=announcement)

@router.get("/", response_model=ApiResponse[PageResult[AnnouncementResponse]])
def list_announcements(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    title: Optional[str] = None,
    announcement_type: Optional[int] = None,
    status: Optional[int] = None,
    is_top: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取公告列表（分页）
    """
    query = db.query(Announcement)
    
    if title:
        query = query.filter(Announcement.title.like(f"%{title}%"))
    if announcement_type is not None:
        query = query.filter(Announcement.announcement_type == announcement_type)
    if status is not None:
        query = query.filter(Announcement.status == status)
    if is_top is not None:
        query = query.filter(Announcement.is_top == is_top)
    
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    announcements = query.order_by(Announcement.is_top.desc(), Announcement.sort.asc(), Announcement.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    result = PageResult[AnnouncementResponse](
        list=announcements,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
    return ApiResponse(data=result)

@router.put("/{announcement_id}", response_model=ApiResponse[AnnouncementResponse])
def update_announcement(announcement_id: int, announcement_update: AnnouncementUpdate, db: Session = Depends(get_db)):
    """
    更新公告信息
    """
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")
    
    update_data = announcement_update.model_dump(exclude_unset=True)
    
    if 'status' in update_data and update_data['status'] == 1 and announcement.status != 1:
        update_data['publish_time'] = datetime.now()
    
    for key, value in update_data.items():
        setattr(announcement, key, value)
    
    db.commit()
    db.refresh(announcement)
    return ApiResponse(data=announcement)

@router.delete("/{announcement_id}", response_model=ApiResponse)
def delete_announcement(announcement_id: int, db: Session = Depends(get_db)):
    """
    删除公告（软删除-撤回）
    """
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")
    
    announcement.status = 2
    db.commit()
    return ApiResponse(message="公告已撤回")

@router.post("/{announcement_id}/publish", response_model=ApiResponse[AnnouncementResponse])
def publish_announcement(announcement_id: int, db: Session = Depends(get_db)):
    """
    发布公告
    """
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")
    
    announcement.status = 1
    announcement.publish_time = datetime.now()
    db.commit()
    db.refresh(announcement)
    return ApiResponse(data=announcement)
