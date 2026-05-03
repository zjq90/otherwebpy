from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Type
from datetime import date, datetime
from decimal import Decimal

from app.models import (
    Product, Customer, Order, OrderItem, Contract,
    Logistics, LogisticsTrack, PurchaseHistory, Feedback
)

class CRUDBase:
    def __init__(self, model: Type):
        self.model = model

    def get(self, db: Session, id: int):
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(self.model).offset(skip).limit(limit).all()

    def get_count(self, db: Session):
        return db.query(self.model).count()

    def create(self, db: Session, obj_in: dict):
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj, obj_in: dict):
        for key, value in obj_in.items():
            if value is not None:
                setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: int):
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

class CRUDProduct(CRUDBase):
    def search(self, db: Session, name: Optional[str] = None, grade: Optional[str] = None, skip: int = 0, limit: int = 100):
        query = db.query(self.model)
        if name:
            query = query.filter(self.model.name.contains(name))
        if grade:
            query = query.filter(self.model.grade == grade)
        return query.offset(skip).limit(limit).all()

class CRUDCustomer(CRUDBase):
    def search(self, db: Session, name: Optional[str] = None, phone: Optional[str] = None, status: Optional[str] = None, skip: int = 0, limit: int = 100):
        query = db.query(self.model)
        if name:
            query = query.filter(self.model.name.contains(name))
        if phone:
            query = query.filter(self.model.phone.contains(phone))
        if status:
            query = query.filter(self.model.status == status)
        return query.offset(skip).limit(limit).all()

    def get_purchase_history(self, db: Session, customer_id: int, skip: int = 0, limit: int = 100):
        return db.query(PurchaseHistory).filter(
            PurchaseHistory.customer_id == customer_id
        ).order_by(desc(PurchaseHistory.purchase_date)).offset(skip).limit(limit).all()

    def get_feedbacks(self, db: Session, customer_id: int, skip: int = 0, limit: int = 100):
        return db.query(Feedback).filter(
            Feedback.customer_id == customer_id
        ).order_by(desc(Feedback.feedback_date)).offset(skip).limit(limit).all()

class CRUDOrder(CRUDBase):
    def search(self, db: Session, customer_name: Optional[str] = None, shipping_status: Optional[str] = None, start_date: Optional[date] = None, end_date: Optional[date] = None, skip: int = 0, limit: int = 100):
        query = db.query(self.model)
        if customer_name:
            query = query.filter(self.model.customer_name.contains(customer_name))
        if shipping_status:
            query = query.filter(self.model.shipping_status == shipping_status)
        if start_date:
            query = query.filter(self.model.order_date >= start_date)
        if end_date:
            query = query.filter(self.model.order_date <= end_date)
        return query.order_by(desc(self.model.order_date)).offset(skip).limit(limit).all()

    def create_with_items(self, db: Session, order_data: dict, items: List[dict]):
        db_order = self.model(**order_data)
        db.add(db_order)
        db.flush()
        
        for item_data in items:
            db_item = OrderItem(**item_data, order_id=db_order.id)
            db.add(db_item)
        
        db.commit()
        db.refresh(db_order)
        return db_order

    def get_by_customer(self, db: Session, customer_id: int, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(
            self.model.customer_id == customer_id
        ).order_by(desc(self.model.order_date)).offset(skip).limit(limit).all()

class CRUDContract(CRUDBase):
    def get_by_order(self, db: Session, order_id: int):
        return db.query(self.model).filter(self.model.order_id == order_id).first()

    def get_by_number(self, db: Session, contract_number: str):
        return db.query(self.model).filter(self.model.contract_number == contract_number).first()

class CRUDLogistics(CRUDBase):
    def get_by_order(self, db: Session, order_id: int):
        return db.query(self.model).filter(self.model.order_id == order_id).first()

    def get_by_tracking_number(self, db: Session, tracking_number: str):
        return db.query(self.model).filter(self.model.tracking_number == tracking_number).first()

    def add_track(self, db: Session, logistics_id: int, track_data: dict):
        db_track = LogisticsTrack(**track_data, logistics_id=logistics_id)
        db.add(db_track)
        db.commit()
        db.refresh(db_track)
        return db_track

    def get_tracks(self, db: Session, logistics_id: int):
        return db.query(LogisticsTrack).filter(
            LogisticsTrack.logistics_id == logistics_id
        ).order_by(desc(LogisticsTrack.track_time)).all()

class CRUDPurchaseHistory(CRUDBase):
    def get_by_customer(self, db: Session, customer_id: int, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(
            self.model.customer_id == customer_id
        ).order_by(desc(self.model.purchase_date)).offset(skip).limit(limit).all()

    def get_by_product(self, db: Session, product_id: int, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(
            self.model.product_id == product_id
        ).order_by(desc(self.model.purchase_date)).offset(skip).limit(limit).all()

class CRUDFeedback(CRUDBase):
    def get_by_customer(self, db: Session, customer_id: int, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(
            self.model.customer_id == customer_id
        ).order_by(desc(self.model.feedback_date)).offset(skip).limit(limit).all()

    def get_by_order(self, db: Session, order_id: int):
        return db.query(self.model).filter(self.model.order_id == order_id).all()

    def search(self, db: Session, feedback_type: Optional[str] = None, status: Optional[str] = None, skip: int = 0, limit: int = 100):
        query = db.query(self.model)
        if feedback_type:
            query = query.filter(self.model.feedback_type == feedback_type)
        if status:
            query = query.filter(self.model.status == status)
        return query.order_by(desc(self.model.feedback_date)).offset(skip).limit(limit).all()

product_crud = CRUDProduct(Product)
customer_crud = CRUDCustomer(Customer)
order_crud = CRUDOrder(Order)
contract_crud = CRUDContract(Contract)
logistics_crud = CRUDLogistics(Logistics)
purchase_history_crud = CRUDPurchaseHistory(PurchaseHistory)
feedback_crud = CRUDFeedback(Feedback)
