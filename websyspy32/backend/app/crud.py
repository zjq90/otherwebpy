from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from app.models import (
    Silo, InventoryRecord, ProductionPlan, MaterialDemand,
    Supplier, SupplierRating, PurchaseOrder, Settlement
)
from app.schemas import (
    SiloCreate, SiloUpdate, InventoryRecordCreate,
    ProductionPlanCreate, ProductionPlanUpdate,
    MaterialDemandCreate, SupplierCreate, SupplierUpdate,
    SupplierRatingCreate, PurchaseOrderCreate, PurchaseOrderUpdate,
    SettlementCreate, SettlementUpdate
)

class CRUDBase:
    def __init__(self, model):
        self.model = model

    def get(self, db: Session, id: Any):
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in):
        db_obj = self.model(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj, obj_in):
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: Any):
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

class CRUDSilo(CRUDBase):
    def __init__(self):
        super().__init__(Silo)

    def get_low_inventory(self, db: Session) -> List[Silo]:
        return db.query(Silo).filter(
            Silo.current_level <= Silo.min_threshold
        ).all()

    def update_current_level(self, db: Session, silo_id: int, quantity: float, 
                              change_type: str, reason: str = None, operator: str = None):
        silo = self.get(db, silo_id)
        if not silo:
            return None

        balance_before = silo.current_level

        if change_type == "入库":
            silo.current_level = min(silo.current_level + quantity, silo.capacity)
        elif change_type == "出库":
            silo.current_level = max(silo.current_level - quantity, 0)
        elif change_type == "调整":
            silo.current_level = quantity

        balance_after = silo.current_level

        if balance_after <= silo.min_threshold:
            silo.status = "低库存"
        elif balance_after == 0:
            silo.status = "空仓"
        else:
            silo.status = "正常"

        inventory_record = InventoryRecord(
            silo_id=silo_id,
            change_type=change_type,
            quantity=quantity,
            balance_before=balance_before,
            balance_after=balance_after,
            reason=reason,
            operator=operator
        )
        db.add(inventory_record)
        db.commit()
        db.refresh(silo)
        return silo

    def get_by_material_type(self, db: Session, material_type: str) -> List[Silo]:
        return db.query(Silo).filter(Silo.material_type == material_type).all()

class CRUDInventoryRecord(CRUDBase):
    def __init__(self):
        super().__init__(InventoryRecord)

    def get_by_silo(self, db: Session, silo_id: int, skip: int = 0, limit: int = 50):
        return db.query(InventoryRecord).filter(
            InventoryRecord.silo_id == silo_id
        ).order_by(desc(InventoryRecord.record_time)).offset(skip).limit(limit).all()

    def get_by_date_range(self, db: Session, start_date: date, end_date: date):
        return db.query(InventoryRecord).filter(
            InventoryRecord.record_time >= start_date,
            InventoryRecord.record_time <= end_date + timedelta(days=1)
        ).all()

class CRUDProductionPlan(CRUDBase):
    def __init__(self):
        super().__init__(ProductionPlan)

    def get_by_date(self, db: Session, plan_date: date):
        return db.query(ProductionPlan).filter(
            ProductionPlan.plan_date == plan_date
        ).all()

    def get_pending_plans(self, db: Session):
        return db.query(ProductionPlan).filter(
            ProductionPlan.status.in_(["待执行", "执行中"])
        ).all()

    def generate_material_demands(self, db: Session, plan_id: int):
        plan = self.get(db, plan_id)
        if not plan:
            return None

        consumption_rates = {
            "水泥": 0.35,
            "砂石": 1.8,
            "粉煤灰": 0.08,
            "外加剂": 0.012,
            "水": 0.18
        }

        if plan.material_demands:
            for demand in plan.material_demands:
                db.delete(demand)
            db.commit()

        demands = []
        for material_type, rate in consumption_rates.items():
            silos = db.query(Silo).filter(Silo.material_type == material_type).all()
            total_stock = sum(silo.current_level for silo in silos)

            required_quantity = plan.concrete_volume * rate
            shortage = max(0, required_quantity - total_stock)

            priority = 1
            if shortage > 0:
                if shortage > required_quantity * 0.5:
                    priority = 1
                elif shortage > required_quantity * 0.3:
                    priority = 2
                else:
                    priority = 3
            else:
                priority = 4

            demand = MaterialDemand(
                production_plan_id=plan.id,
                material_type=material_type,
                required_quantity=required_quantity,
                unit_consumption=rate,
                current_stock=total_stock,
                shortage=shortage,
                priority=priority,
                status="待处理" if shortage > 0 else "已满足"
            )
            db.add(demand)
            demands.append(demand)

        db.commit()
        return demands

class CRUDMaterialDemand(CRUDBase):
    def __init__(self):
        super().__init__(MaterialDemand)

    def get_pending_demands(self, db: Session):
        return db.query(MaterialDemand).filter(
            MaterialDemand.status.in_(["待处理", "部分补货"])
        ).order_by(MaterialDemand.priority).all()

    def get_by_material_type(self, db: Session, material_type: str):
        return db.query(MaterialDemand).filter(
            MaterialDemand.material_type == material_type
        ).all()

class CRUDSupplier(CRUDBase):
    def __init__(self):
        super().__init__(Supplier)

    def update_overall_rating(self, db: Session, supplier_id: int):
        supplier = self.get(db, supplier_id)
        if not supplier:
            return None

        recent_ratings = db.query(SupplierRating).filter(
            SupplierRating.supplier_id == supplier_id
        ).order_by(desc(SupplierRating.rating_date)).limit(10).all()

        if recent_ratings:
            total_score = sum(r.total_score for r in recent_ratings)
            supplier.overall_rating = total_score / len(recent_ratings)
            db.commit()
            db.refresh(supplier)
        return supplier

    def get_by_material_type(self, db: Session, material_type: str):
        return db.query(Supplier).filter(
            Supplier.material_types.like(f"%{material_type}%"),
            Supplier.status == "合作中"
        ).all()

class CRUDSupplierRating(CRUDBase):
    def __init__(self):
        super().__init__(SupplierRating)

    def create(self, db: Session, obj_in: SupplierRatingCreate):
        total_score = (obj_in.delivery_score * 0.35 + 
                      obj_in.quality_score * 0.35 + 
                      obj_in.price_score * 0.15 + 
                      obj_in.service_score * 0.15)
        
        rating_data = obj_in.dict()
        rating_data["total_score"] = round(total_score, 2)
        
        db_obj = SupplierRating(**rating_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_supplier(self, db: Session, supplier_id: int, skip: int = 0, limit: int = 20):
        return db.query(SupplierRating).filter(
            SupplierRating.supplier_id == supplier_id
        ).order_by(desc(SupplierRating.rating_date)).offset(skip).limit(limit).all()

class CRUDPurchaseOrder(CRUDBase):
    def __init__(self):
        super().__init__(PurchaseOrder)

    def create(self, db: Session, obj_in: PurchaseOrderCreate):
        order_no = f"PO{datetime.now().strftime('%Y%m%d%H%M%S')}"
        total_amount = obj_in.quantity * obj_in.unit_price
        
        order_data = obj_in.dict()
        order_data["order_no"] = order_no
        order_data["total_amount"] = total_amount
        
        db_obj = PurchaseOrder(**order_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_pending_orders(self, db: Session):
        return db.query(PurchaseOrder).filter(
            PurchaseOrder.status.in_(["待发货", "已发货", "部分收货"])
        ).all()

    def get_by_supplier(self, db: Session, supplier_id: int):
        return db.query(PurchaseOrder).filter(
            PurchaseOrder.supplier_id == supplier_id
        ).all()

    def get_by_status(self, db: Session, status: str):
        return db.query(PurchaseOrder).filter(
            PurchaseOrder.status == status
        ).all()

class CRUDSettlement(CRUDBase):
    def __init__(self):
        super().__init__(Settlement)

    def create(self, db: Session, obj_in: SettlementCreate):
        purchase_order = db.query(PurchaseOrder).get(obj_in.purchase_order_id)
        if not purchase_order:
            return None

        settlement_no = f"SET{datetime.now().strftime('%Y%m%d%H%M%S')}"
        total_amount = obj_in.quantity * obj_in.unit_price
        tax_amount = total_amount * obj_in.tax_rate
        total_payable = total_amount + tax_amount

        settlement_data = obj_in.dict()
        settlement_data.update({
            "settlement_no": settlement_no,
            "material_type": purchase_order.material_type,
            "total_amount": total_amount,
            "tax_amount": tax_amount,
            "total_payable": total_payable
        })

        db_obj = Settlement(**settlement_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_pending_payments(self, db: Session):
        return db.query(Settlement).filter(
            Settlement.payment_status.in_(["待付款", "部分付款"])
        ).all()

    def get_by_purchase_order(self, db: Session, purchase_order_id: int):
        return db.query(Settlement).filter(
            Settlement.purchase_order_id == purchase_order_id
        ).first()

silo_crud = CRUDSilo()
inventory_record_crud = CRUDInventoryRecord()
production_plan_crud = CRUDProductionPlan()
material_demand_crud = CRUDMaterialDemand()
supplier_crud = CRUDSupplier()
supplier_rating_crud = CRUDSupplierRating()
purchase_order_crud = CRUDPurchaseOrder()
settlement_crud = CRUDSettlement()
