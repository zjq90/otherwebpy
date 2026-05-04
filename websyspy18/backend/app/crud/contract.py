"""
合同与供应商管理模块 - CRUD操作
包含供应商管理、合同管理、付款记录、服务质量评估等CRUD操作
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.crud.base import CRUDBase
from app.models.contract import (
    Supplier, Contract, ContractPayment, ServiceEvaluation
)
from app.schemas.contract import (
    SupplierCreate, SupplierUpdate,
    ContractCreate, ContractUpdate,
    ContractPaymentCreate, ContractPaymentUpdate,
    ServiceEvaluationCreate, ServiceEvaluationUpdate
)

# ==================== 供应商 CRUD ====================

class CRUDSupplier(CRUDBase[Supplier, SupplierCreate, SupplierUpdate]):
    """
    供应商CRUD类
    """

    def get_by_code(self, db: Session, code: str) -> Optional[Supplier]:
        """
        根据供应商编号获取供应商
        """
        return db.query(self.model).filter(self.model.code == code).first()

    def get_by_category(self, db: Session, category: str, skip: int = 0, limit: int = 100) -> List[Supplier]:
        """
        根据类别获取供应商列表
        """
        return db.query(self.model).filter(self.model.category == category).offset(skip).limit(limit).all()

    def get_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[Supplier]:
        """
        根据状态获取供应商列表
        """
        return db.query(self.model).filter(self.model.status == status).offset(skip).limit(limit).all()

    def search(self, db: Session, keyword: str, skip: int = 0, limit: int = 100) -> List[Supplier]:
        """
        搜索供应商（按名称、编号、联系人）
        """
        return db.query(self.model).filter(
            (self.model.name.like(f"%{keyword}%")) |
            (self.model.code.like(f"%{keyword}%")) |
            (self.model.contact_person.like(f"%{keyword}%"))
        ).offset(skip).limit(limit).all()

# ==================== 合同 CRUD ====================

class CRUDContract(CRUDBase[Contract, ContractCreate, ContractUpdate]):
    """
    合同CRUD类
    """

    def get_by_contract_no(self, db: Session, contract_no: str) -> Optional[Contract]:
        """
        根据合同编号获取合同
        """
        return db.query(self.model).filter(self.model.contract_no == contract_no).first()

    def get_by_supplier(self, db: Session, supplier_id: int, skip: int = 0, limit: int = 100) -> List[Contract]:
        """
        根据供应商ID获取合同列表
        """
        return db.query(self.model).filter(self.model.supplier_id == supplier_id).offset(skip).limit(limit).all()

    def get_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[Contract]:
        """
        根据状态获取合同列表
        """
        return db.query(self.model).filter(self.model.status == status).offset(skip).limit(limit).all()

    def search(self, db: Session, keyword: str, skip: int = 0, limit: int = 100) -> List[Contract]:
        """
        搜索合同（按合同名称、合同编号）
        """
        return db.query(self.model).filter(
            (self.model.contract_name.like(f"%{keyword}%")) |
            (self.model.contract_no.like(f"%{keyword}%"))
        ).offset(skip).limit(limit).all()

# ==================== 合同付款 CRUD ====================

class CRUDContractPayment(CRUDBase[ContractPayment, ContractPaymentCreate, ContractPaymentUpdate]):
    """
    合同付款CRUD类
    """

    def get_by_contract(self, db: Session, contract_id: int, skip: int = 0, limit: int = 100) -> List[ContractPayment]:
        """
        根据合同ID获取付款记录列表
        """
        return db.query(self.model).filter(self.model.contract_id == contract_id).offset(skip).limit(limit).all()

    def get_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[ContractPayment]:
        """
        根据状态获取付款记录列表
        """
        return db.query(self.model).filter(self.model.status == status).offset(skip).limit(limit).all()

# ==================== 服务质量评估 CRUD ====================

class CRUDServiceEvaluation(CRUDBase[ServiceEvaluation, ServiceEvaluationCreate, ServiceEvaluationUpdate]):
    """
    服务质量评估CRUD类
    """

    def get_by_supplier(self, db: Session, supplier_id: int, skip: int = 0, limit: int = 100) -> List[ServiceEvaluation]:
        """
        根据供应商ID获取评估记录列表
        """
        return db.query(self.model).filter(self.model.supplier_id == supplier_id).offset(skip).limit(limit).all()

    def get_by_period(self, db: Session, period: str, skip: int = 0, limit: int = 100) -> List[ServiceEvaluation]:
        """
        根据评估周期获取评估记录列表
        """
        return db.query(self.model).filter(self.model.evaluation_period == period).offset(skip).limit(limit).all()

    def get_supplier_statistics(self, db: Session, supplier_id: int):
        """
        获取供应商评估统计
        """
        evaluations = db.query(self.model).filter(self.model.supplier_id == supplier_id).all()
        
        if not evaluations:
            return {
                "total_evaluations": 0,
                "avg_total_score": 0,
                "avg_service_quality": 0,
                "avg_response_speed": 0,
                "avg_personnel_quality": 0,
                "avg_compliance": 0,
                "avg_cost_effectiveness": 0
            }
        
        total_evaluations = len(evaluations)
        avg_total_score = sum(e.total_score or 0 for e in evaluations) / total_evaluations
        avg_service_quality = sum(e.service_quality_score or 0 for e in evaluations) / total_evaluations
        avg_response_speed = sum(e.response_speed_score or 0 for e in evaluations) / total_evaluations
        avg_personnel_quality = sum(e.personnel_quality_score or 0 for e in evaluations) / total_evaluations
        avg_compliance = sum(e.compliance_score or 0 for e in evaluations) / total_evaluations
        avg_cost_effectiveness = sum(e.cost_effectiveness_score or 0 for e in evaluations) / total_evaluations
        
        return {
            "total_evaluations": total_evaluations,
            "avg_total_score": round(avg_total_score, 2),
            "avg_service_quality": round(avg_service_quality, 2),
            "avg_response_speed": round(avg_response_speed, 2),
            "avg_personnel_quality": round(avg_personnel_quality, 2),
            "avg_compliance": round(avg_compliance, 2),
            "avg_cost_effectiveness": round(avg_cost_effectiveness, 2)
        }

# 实例化CRUD对象
supplier = CRUDSupplier(Supplier)
contract = CRUDContract(Contract)
contract_payment = CRUDContractPayment(ContractPayment)
service_evaluation = CRUDServiceEvaluation(ServiceEvaluation)
