from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app import schemas
from app.crud import order_crud

router = APIRouter(prefix="/api/orders", tags=["订单管理"])

@router.get("/", response_model=schemas.OrderList)
def read_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    customer_name: Optional[str] = None,
    shipping_status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    
    if customer_name or shipping_status or start_date or end_date:
        orders = order_crud.search(
            db,
            customer_name=customer_name,
            shipping_status=shipping_status,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )
    elif keyword:
        from app.models import Order
        orders = db.query(Order).filter(
            Order.customer_name.contains(keyword)
        ).order_by(Order.order_date.desc()).offset(skip).limit(limit).all()
    else:
        orders = order_crud.get_multi(db, skip=skip, limit=limit)
    
    total = order_crud.get_count(db)
    return {"orders": orders, "total": total}

@router.get("/{order_id}", response_model=schemas.Order)
def read_order(order_id: int, db: Session = Depends(get_db)):
    order = order_crud.get(db, id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order

@router.post("/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    order_data = order.model_dump(exclude={"items"})
    items_data = [item.model_dump() for item in order.items]
    
    for item in items_data:
        item.pop("id", None)
        item.pop("order_id", None)
    
    return order_crud.create_with_items(db, order_data=order_data, items=items_data)

@router.put("/{order_id}", response_model=schemas.Order)
def update_order(
    order_id: int,
    order: schemas.OrderUpdate,
    db: Session = Depends(get_db)
):
    db_order = order_crud.get(db, id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    update_data = order.model_dump(exclude_unset=True)
    return order_crud.update(db, db_obj=db_order, obj_in=update_data)

@router.delete("/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = order_crud.get(db, id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    order_crud.remove(db, id=order_id)
    return {"message": "删除成功"}

@router.get("/customer/{customer_id}", response_model=List[schemas.Order])
def get_customer_orders(
    customer_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    return order_crud.get_by_customer(db, customer_id=customer_id, skip=skip, limit=limit)
