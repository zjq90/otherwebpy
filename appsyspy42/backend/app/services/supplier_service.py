"""
供应商服务
处理供应商管理、评价等业务逻辑
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.models.models import (
    Supplier, SupplyRecord, SupplierEvaluation, Material, User
)
from app.schemas.schemas import (
    SupplierCreate, SupplierUpdate, SupplierResponse,
    SupplyRecordCreate, SupplyRecordResponse,
    SupplierEvaluationCreate, SupplierEvaluationResponse
)


class SupplierService:
    """供应商服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_supplier_list(
        self,
        keyword: Optional[str] = None,
        is_active: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """
        获取供应商列表
        :param keyword: 关键词搜索（名称、联系人）
        :param is_active: 是否启用筛选
        :param page: 页码
        :param page_size: 每页数量
        """
        query = self.db.query(Supplier)
        
        if keyword:
            query = query.filter(
                (Supplier.supplier_name.like(f"%{keyword}%")) |
                (Supplier.contact_person.like(f"%{keyword}%"))
            )
        if is_active is not None:
            query = query.filter(Supplier.is_active == is_active)
        
        total = query.count()
        
        results = query.order_by(Supplier.created_at.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return {
            "list": [SupplierResponse.model_validate(s) for s in results],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    def get_supplier_by_id(self, supplier_id: int) -> Optional[SupplierResponse]:
        """根据ID获取供应商详情"""
        supplier = self.db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            return None
        return SupplierResponse.model_validate(supplier)
    
    def create_supplier(self, supplier_data: SupplierCreate) -> Supplier:
        """创建供应商"""
        db_supplier = Supplier(**supplier_data.model_dump())
        self.db.add(db_supplier)
        self.db.commit()
        self.db.refresh(db_supplier)
        return db_supplier
    
    def update_supplier(
        self, 
        supplier_id: int, 
        supplier_data: SupplierUpdate
    ) -> Optional[Supplier]:
        """更新供应商"""
        db_supplier = self.db.query(Supplier).filter(
            Supplier.id == supplier_id
        ).first()
        
        if not db_supplier:
            return None
        
        for key, value in supplier_data.model_dump(exclude_unset=True).items():
            setattr(db_supplier, key, value)
        
        self.db.commit()
        self.db.refresh(db_supplier)
        
        return db_supplier
    
    def delete_supplier(self, supplier_id: int) -> bool:
        """删除供应商（软删除，设置为禁用）"""
        db_supplier = self.db.query(Supplier).filter(
            Supplier.id == supplier_id
        ).first()
        
        if not db_supplier:
            return False
        
        db_supplier.is_active = 0
        self.db.commit()
        
        return True
    
    def get_supply_records(
        self,
        supplier_id: Optional[int] = None,
        material_id: Optional[int] = None,
        quality_status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """
        获取供货记录列表
        """
        query = self.db.query(
            SupplyRecord,
            Supplier.supplier_name,
            Material.material_name,
            Material.material_type,
            Material.unit
        ).join(
            Supplier, SupplyRecord.supplier_id == Supplier.id
        ).join(
            Material, SupplyRecord.material_id == Material.id
        )
        
        if supplier_id:
            query = query.filter(SupplyRecord.supplier_id == supplier_id)
        if material_id:
            query = query.filter(SupplyRecord.material_id == material_id)
        if quality_status:
            query = query.filter(SupplyRecord.quality_status == quality_status)
        
        total = query.count()
        
        results = query.order_by(SupplyRecord.created_at.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        record_list = []
        for record, supplier_name, material_name, material_type, unit in results:
            total_amount = record.quantity * record.unit_price if record.unit_price else 0
            record_list.append(SupplyRecordResponse(
                id=record.id,
                supplier_id=record.supplier_id,
                supplier_name=supplier_name,
                material_id=record.material_id,
                material_name=material_name,
                material_type=material_type,
                quantity=record.quantity,
                unit=unit,
                unit_price=record.unit_price,
                total_amount=total_amount,
                delivery_date=record.delivery_date,
                quality_status=record.quality_status,
                batch_number=record.batch_number,
                remark=record.remark,
                created_at=record.created_at
            ))
        
        return {
            "list": record_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    def create_supply_record(self, record_data: SupplyRecordCreate) -> SupplyRecord:
        """创建供货记录"""
        total_amount = record_data.quantity * record_data.unit_price
        
        db_record = SupplyRecord(
            **record_data.model_dump(),
            total_amount=total_amount
        )
        
        self.db.add(db_record)
        
        supplier = self.db.query(Supplier).filter(
            Supplier.id == record_data.supplier_id
        ).first()
        
        if supplier:
            supplier.total_orders += 1
            supplier.total_amount += total_amount
        
        self.db.commit()
        self.db.refresh(db_record)
        
        return db_record
    
    def get_evaluations(
        self,
        supplier_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """
        获取供应商评价列表
        """
        query = self.db.query(
            SupplierEvaluation,
            Supplier.supplier_name,
            User.real_name.label("evaluator_name")
        ).join(
            Supplier, SupplierEvaluation.supplier_id == Supplier.id
        ).join(
            User, SupplierEvaluation.evaluated_by == User.id
        )
        
        if supplier_id:
            query = query.filter(SupplierEvaluation.supplier_id == supplier_id)
        
        total = query.count()
        
        results = query.order_by(SupplierEvaluation.created_at.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        eval_list = []
        for eval_item, supplier_name, evaluator_name in results:
            eval_list.append(SupplierEvaluationResponse(
                id=eval_item.id,
                supplier_id=eval_item.supplier_id,
                supplier_name=supplier_name,
                evaluated_by=eval_item.evaluated_by,
                evaluator_name=evaluator_name,
                quality_score=eval_item.quality_score,
                delivery_score=eval_item.delivery_score,
                price_score=eval_item.price_score,
                service_score=eval_item.service_score,
                total_score=eval_item.total_score,
                comment=eval_item.comment,
                evaluation_date=eval_item.evaluation_date,
                created_at=eval_item.created_at
            ))
        
        return {
            "list": eval_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    def create_evaluation(
        self, 
        eval_data: SupplierEvaluationCreate, 
        user_id: int
    ) -> SupplierEvaluation:
        """创建供应商评价"""
        total_score = (
            eval_data.quality_score + 
            eval_data.delivery_score + 
            eval_data.price_score + 
            eval_data.service_score
        ) / 4
        
        db_eval = SupplierEvaluation(
            **eval_data.model_dump(),
            evaluated_by=user_id,
            total_score=total_score
        )
        
        self.db.add(db_eval)
        
        supplier = self.db.query(Supplier).filter(
            Supplier.id == eval_data.supplier_id
        ).first()
        
        if supplier:
            avg_eval = self.db.query(
                func.avg(SupplierEvaluation.total_score)
            ).filter(
                SupplierEvaluation.supplier_id == eval_data.supplier_id
            ).scalar()
            
            if avg_eval:
                supplier.quality_rating = float(avg_eval)
        
        self.db.commit()
        self.db.refresh(db_eval)
        
        return db_eval
    
    def get_statistics(self) -> dict:
        """获取供应商统计数据"""
        total_suppliers = self.db.query(func.count(Supplier.id)).filter(
            Supplier.is_active == 1
        ).scalar() or 0
        
        avg_rating = self.db.query(func.avg(Supplier.quality_rating)).filter(
            Supplier.is_active == 1
        ).scalar() or 0
        
        return {
            "total_suppliers": total_suppliers,
            "avg_supplier_rating": float(avg_rating)
        }
