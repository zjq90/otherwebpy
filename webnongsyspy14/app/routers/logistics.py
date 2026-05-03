from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app import schemas
from app.crud import logistics_crud

router = APIRouter(prefix="/api/logistics", tags=["物流管理"])

@router.get("/", response_model=schemas.LogisticsList)
def read_logistics(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    current_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    from app.models import Logistics, Order
    from sqlalchemy import or_
    
    skip = (page - 1) * limit
    query = db.query(Logistics)
    
    if keyword:
        query = query.filter(
            or_(
                Logistics.tracking_number.contains(keyword),
                Logistics.logistics_company.contains(keyword),
                Logistics.current_location.contains(keyword)
            )
        )
    
    if current_status:
        query = query.filter(Logistics.current_status == current_status)
    
    total = query.count()
    logistics_list = query.order_by(Logistics.created_at.desc()).offset(skip).limit(limit).all()
    
    return {"logistics": logistics_list, "total": total}

@router.get("/{logistics_id}", response_model=schemas.Logistics)
def read_logistics(logistics_id: int, db: Session = Depends(get_db)):
    logistics = logistics_crud.get(db, id=logistics_id)
    if logistics is None:
        raise HTTPException(status_code=404, detail="物流记录不存在")
    return logistics

@router.get("/order/{order_id}", response_model=schemas.Logistics)
def get_logistics_by_order(order_id: int, db: Session = Depends(get_db)):
    logistics = logistics_crud.get_by_order(db, order_id=order_id)
    if logistics is None:
        raise HTTPException(status_code=404, detail="该订单暂无物流信息")
    return logistics

@router.get("/tracking/{tracking_number}", response_model=schemas.Logistics)
def get_logistics_by_tracking(tracking_number: str, db: Session = Depends(get_db)):
    logistics = logistics_crud.get_by_tracking_number(db, tracking_number=tracking_number)
    if logistics is None:
        raise HTTPException(status_code=404, detail="物流单号不存在")
    return logistics

@router.post("/", response_model=schemas.Logistics)
def create_logistics(logistics: schemas.LogisticsCreate, db: Session = Depends(get_db)):
    existing = logistics_crud.get_by_order(db, order_id=logistics.order_id)
    if existing:
        raise HTTPException(status_code=400, detail="该订单已存在物流信息")
    logistics_data = logistics.model_dump()
    return logistics_crud.create(db, obj_in=logistics_data)

@router.put("/{logistics_id}", response_model=schemas.Logistics)
def update_logistics(
    logistics_id: int,
    logistics: schemas.LogisticsUpdate,
    db: Session = Depends(get_db)
):
    db_logistics = logistics_crud.get(db, id=logistics_id)
    if db_logistics is None:
        raise HTTPException(status_code=404, detail="物流记录不存在")
    update_data = logistics.model_dump(exclude_unset=True)
    return logistics_crud.update(db, db_obj=db_logistics, obj_in=update_data)

@router.delete("/{logistics_id}")
def delete_logistics(logistics_id: int, db: Session = Depends(get_db)):
    db_logistics = logistics_crud.get(db, id=logistics_id)
    if db_logistics is None:
        raise HTTPException(status_code=404, detail="物流记录不存在")
    logistics_crud.remove(db, id=logistics_id)
    return {"message": "删除成功"}

@router.get("/{logistics_id}/tracks", response_model=List[schemas.LogisticsTrack])
def get_logistics_tracks(
    logistics_id: int,
    db: Session = Depends(get_db)
):
    db_logistics = logistics_crud.get(db, id=logistics_id)
    if db_logistics is None:
        raise HTTPException(status_code=404, detail="物流记录不存在")
    return logistics_crud.get_tracks(db, logistics_id=logistics_id)

@router.post("/{logistics_id}/tracks", response_model=schemas.LogisticsTrack)
def add_logistics_track(
    logistics_id: int,
    track: schemas.LogisticsTrackCreate,
    db: Session = Depends(get_db)
):
    from app.models import Logistics
    
    db_logistics = logistics_crud.get(db, id=logistics_id)
    if db_logistics is None:
        raise HTTPException(status_code=404, detail="物流记录不存在")
    
    track_data = track.model_dump()
    track_data.pop("logistics_id", None)
    
    new_track = logistics_crud.add_track(db, logistics_id=logistics_id, track_data=track_data)
    
    db.refresh(db_logistics)
    if new_track.status:
        db_logistics.current_status = new_track.status
    if new_track.location:
        db_logistics.current_location = new_track.location
    db.commit()
    db.refresh(db_logistics)
    
    return new_track
