from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app import schemas
from app.crud import customer_crud

router = APIRouter(prefix="/api/customers", tags=["客户管理"])

@router.get("/", response_model=schemas.CustomerList)
def read_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = None,
    phone: Optional[str] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    
    if name or phone or status:
        customers = customer_crud.search(db, name=name, phone=phone, status=status, skip=skip, limit=limit)
    elif keyword:
        from app.models import Customer
        customers = db.query(Customer).filter(
            Customer.name.contains(keyword) | Customer.phone.contains(keyword)
        ).offset(skip).limit(limit).all()
    else:
        customers = customer_crud.get_multi(db, skip=skip, limit=limit)
    
    total = customer_crud.get_count(db)
    return {"customers": customers, "total": total}

@router.get("/{customer_id}", response_model=schemas.Customer)
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = customer_crud.get(db, id=customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="客户不存在")
    return customer

@router.post("/", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    from app.models import Customer
    
    existing_phone = db.query(Customer).filter(Customer.phone == customer.phone).first()
    if existing_phone:
        raise HTTPException(
            status_code=400, 
            detail="该联系电话已存在，请使用其他电话号码"
        )
    
    existing_name = db.query(Customer).filter(Customer.name == customer.name).first()
    if existing_name:
        raise HTTPException(
            status_code=400, 
            detail="该客户名称已存在，请使用其他名称"
        )
    
    customer_data = customer.model_dump()
    return customer_crud.create(db, obj_in=customer_data)

@router.put("/{customer_id}", response_model=schemas.Customer)
def update_customer(
    customer_id: int,
    customer: schemas.CustomerUpdate,
    db: Session = Depends(get_db)
):
    from app.models import Customer
    
    db_customer = customer_crud.get(db, id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="客户不存在")
    
    update_data = customer.model_dump(exclude_unset=True)
    
    if 'phone' in update_data and update_data['phone']:
        existing_phone = db.query(Customer).filter(
            Customer.phone == update_data['phone'],
            Customer.id != customer_id
        ).first()
        if existing_phone:
            raise HTTPException(
                status_code=400, 
                detail="该联系电话已被其他客户使用"
            )
    
    if 'name' in update_data and update_data['name']:
        existing_name = db.query(Customer).filter(
            Customer.name == update_data['name'],
            Customer.id != customer_id
        ).first()
        if existing_name:
            raise HTTPException(
                status_code=400, 
                detail="该客户名称已被其他客户使用"
            )
    
    return customer_crud.update(db, db_obj=db_customer, obj_in=update_data)

@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = customer_crud.get(db, id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="客户不存在")
    customer_crud.remove(db, id=customer_id)
    return {"message": "删除成功"}

@router.get("/{customer_id}/purchase-history", response_model=List[schemas.PurchaseHistory])
def get_customer_purchase_history(
    customer_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    db_customer = customer_crud.get(db, id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="客户不存在")
    
    skip = (page - 1) * limit
    return customer_crud.get_purchase_history(db, customer_id=customer_id, skip=skip, limit=limit)

@router.get("/{customer_id}/feedbacks", response_model=List[schemas.Feedback])
def get_customer_feedbacks(
    customer_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    db_customer = customer_crud.get(db, id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="客户不存在")
    
    skip = (page - 1) * limit
    feedbacks = customer_crud.get_feedbacks(db, customer_id=customer_id, skip=skip, limit=limit)
    
    feedbacks_with_name = []
    for feedback in feedbacks:
        item = feedback.__dict__.copy()
        item["customer_name"] = db_customer.name
        feedbacks_with_name.append(item)
    
    return feedbacks_with_name
