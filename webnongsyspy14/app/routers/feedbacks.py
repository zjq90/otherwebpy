from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.database import get_db
from app import schemas
from app.models import Feedback, Customer
from app.crud import feedback_crud

router = APIRouter(prefix="/api/feedbacks", tags=["反馈管理"])

def feedback_with_customer_name(feedback: Feedback, db: Session):
    result = feedback.__dict__.copy()
    if feedback.customer_id:
        customer = db.query(Customer).filter(Customer.id == feedback.customer_id).first()
        if customer:
            result["customer_name"] = customer.name
        else:
            result["customer_name"] = None
    else:
        result["customer_name"] = None
    return result

@router.get("/", response_model=schemas.FeedbackList)
def read_feedbacks(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    feedback_type: Optional[str] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    
    query = db.query(Feedback).outerjoin(Customer, Feedback.customer_id == Customer.id)
    
    if feedback_type:
        query = query.filter(Feedback.feedback_type == feedback_type)
    if status:
        query = query.filter(Feedback.status == status)
    if keyword:
        query = query.filter(
            Feedback.content.contains(keyword) | Customer.name.contains(keyword)
        )
    
    total = query.count()
    feedbacks = query.order_by(Feedback.feedback_date.desc()).offset(skip).limit(limit).all()
    
    feedbacks_with_name = []
    for feedback in feedbacks:
        item = feedback.__dict__.copy()
        if feedback.customer:
            item["customer_name"] = feedback.customer.name
        else:
            item["customer_name"] = None
        feedbacks_with_name.append(item)
    
    return {"feedbacks": feedbacks_with_name, "total": total}

@router.get("/{feedback_id}", response_model=schemas.Feedback)
def read_feedback(feedback_id: int, db: Session = Depends(get_db)):
    feedback = feedback_crud.get(db, id=feedback_id)
    if feedback is None:
        raise HTTPException(status_code=404, detail="反馈不存在")
    
    result = feedback_with_customer_name(feedback, db)
    return result

@router.get("/customer/{customer_id}", response_model=List[schemas.Feedback])
def get_customer_feedbacks(
    customer_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    feedbacks = feedback_crud.get_by_customer(db, customer_id=customer_id, skip=skip, limit=limit)
    
    feedbacks_with_name = []
    for feedback in feedbacks:
        feedbacks_with_name.append(feedback_with_customer_name(feedback, db))
    return feedbacks_with_name

@router.get("/order/{order_id}", response_model=List[schemas.Feedback])
def get_order_feedbacks(
    order_id: int,
    db: Session = Depends(get_db)
):
    feedbacks = feedback_crud.get_by_order(db, order_id=order_id)
    
    feedbacks_with_name = []
    for feedback in feedbacks:
        feedbacks_with_name.append(feedback_with_customer_name(feedback, db))
    return feedbacks_with_name

@router.post("/", response_model=schemas.Feedback)
def create_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    feedback_data = feedback.model_dump()
    new_feedback = feedback_crud.create(db, obj_in=feedback_data)
    return feedback_with_customer_name(new_feedback, db)

@router.put("/{feedback_id}", response_model=schemas.Feedback)
def update_feedback(
    feedback_id: int,
    feedback: schemas.FeedbackUpdate,
    db: Session = Depends(get_db)
):
    db_feedback = feedback_crud.get(db, id=feedback_id)
    if db_feedback is None:
        raise HTTPException(status_code=404, detail="反馈不存在")
    update_data = feedback.model_dump(exclude_unset=True)
    updated = feedback_crud.update(db, db_obj=db_feedback, obj_in=update_data)
    return feedback_with_customer_name(updated, db)

@router.delete("/{feedback_id}")
def delete_feedback(feedback_id: int, db: Session = Depends(get_db)):
    db_feedback = feedback_crud.get(db, id=feedback_id)
    if db_feedback is None:
        raise HTTPException(status_code=404, detail="反馈不存在")
    feedback_crud.remove(db, id=feedback_id)
    return {"message": "删除成功"}
