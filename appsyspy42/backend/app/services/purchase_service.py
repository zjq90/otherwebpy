"""
采购申请服务
处理采购申请的提交、审批等业务逻辑
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
import uuid

from app.models.models import (
    PurchaseRequest, Material, User
)
from app.schemas.schemas import (
    PurchaseRequestCreate, PurchaseRequestUpdate, 
    PurchaseApproval, PurchaseRequestDetailResponse
)


class PurchaseService:
    """采购申请服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _generate_request_no(self) -> str:
        """生成采购申请单号"""
        date_str = datetime.now().strftime("%Y%m%d")
        uuid_part = str(uuid.uuid4().hex)[:8].upper()
        return f"PO-{date_str}-{uuid_part}"
    
    def get_purchase_list(
        self,
        status: Optional[str] = None,
        material_type: Optional[str] = None,
        requested_by: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """
        获取采购申请列表
        :param status: 状态筛选
        :param material_type: 原材料类型筛选
        :param requested_by: 申请人筛选
        :param page: 页码
        :param page_size: 每页数量
        """
        from sqlalchemy.orm import aliased
        Approver = aliased(User)
        
        query = self.db.query(
            PurchaseRequest,
            Material.material_name,
            Material.material_type,
            User.real_name.label("requester_name"),
            Approver.real_name.label("approver_name")
        ).join(
            Material, PurchaseRequest.material_id == Material.id
        ).join(
            User, PurchaseRequest.requested_by == User.id
        ).outerjoin(
            Approver, PurchaseRequest.approved_by == Approver.id
        )
        
        if status:
            query = query.filter(PurchaseRequest.status == status)
        if material_type:
            query = query.filter(Material.material_type == material_type)
        if requested_by:
            query = query.filter(PurchaseRequest.requested_by == requested_by)
        
        total = query.count()
        
        results = query.order_by(PurchaseRequest.created_at.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        purchase_list = []
        for pr, material_name, material_type, requester_name, approver_name in results:
            purchase_list.append(PurchaseRequestDetailResponse(
                id=pr.id,
                request_no=pr.request_no,
                material_id=pr.material_id,
                material_name=material_name,
                material_type=material_type,
                requested_by=pr.requested_by,
                requester_name=requester_name,
                quantity=pr.quantity,
                unit=pr.unit,
                expected_delivery_date=pr.expected_delivery_date,
                status=pr.status,
                reason=pr.reason,
                approved_by=pr.approved_by,
                approver_name=approver_name,
                approval_time=pr.approval_time,
                approval_comment=pr.approval_comment,
                created_at=pr.created_at,
                updated_at=pr.updated_at
            ))
        
        return {
            "list": purchase_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    def get_purchase_by_id(self, purchase_id: int) -> Optional[PurchaseRequestDetailResponse]:
        """根据ID获取采购申请详情"""
        from sqlalchemy.orm import aliased
        Approver = aliased(User)
        
        result = self.db.query(
            PurchaseRequest,
            Material.material_name,
            Material.material_type,
            User.real_name.label("requester_name"),
            Approver.real_name.label("approver_name")
        ).join(
            Material, PurchaseRequest.material_id == Material.id
        ).join(
            User, PurchaseRequest.requested_by == User.id
        ).outerjoin(
            Approver, PurchaseRequest.approved_by == Approver.id
        ).filter(PurchaseRequest.id == purchase_id).first()
        
        if not result:
            return None
        
        pr, material_name, material_type, requester_name, approver_name = result
        
        return PurchaseRequestDetailResponse(
            id=pr.id,
            request_no=pr.request_no,
            material_id=pr.material_id,
            material_name=material_name,
            material_type=material_type,
            requested_by=pr.requested_by,
            requester_name=requester_name,
            quantity=pr.quantity,
            unit=pr.unit,
            expected_delivery_date=pr.expected_delivery_date,
            status=pr.status,
            reason=pr.reason,
            approved_by=pr.approved_by,
            approver_name=approver_name,
            approval_time=pr.approval_time,
            approval_comment=pr.approval_comment,
            created_at=pr.created_at,
            updated_at=pr.updated_at
        )
    
    def create_purchase_request(
        self, 
        purchase_data: PurchaseRequestCreate, 
        user_id: int
    ) -> PurchaseRequest:
        """创建采购申请"""
        db_purchase = PurchaseRequest(
            **purchase_data.model_dump(),
            request_no=self._generate_request_no(),
            requested_by=user_id,
            status="待审批"
        )
        
        self.db.add(db_purchase)
        self.db.commit()
        self.db.refresh(db_purchase)
        
        return db_purchase
    
    def update_purchase_request(
        self, 
        purchase_id: int, 
        purchase_data: PurchaseRequestUpdate,
        user_id: int
    ) -> Optional[PurchaseRequest]:
        """更新采购申请（只能更新待审批的申请）"""
        db_purchase = self.db.query(PurchaseRequest).filter(
            PurchaseRequest.id == purchase_id
        ).first()
        
        if not db_purchase:
            return None
        
        if db_purchase.status != "待审批":
            return None
        
        if db_purchase.requested_by != user_id:
            return None
        
        for key, value in purchase_data.model_dump(exclude_unset=True).items():
            setattr(db_purchase, key, value)
        
        self.db.commit()
        self.db.refresh(db_purchase)
        
        return db_purchase
    
    def cancel_purchase_request(
        self, 
        purchase_id: int, 
        user_id: int
    ) -> Optional[PurchaseRequest]:
        """取消采购申请"""
        db_purchase = self.db.query(PurchaseRequest).filter(
            PurchaseRequest.id == purchase_id
        ).first()
        
        if not db_purchase:
            return None
        
        if db_purchase.status != "待审批":
            return None
        
        if db_purchase.requested_by != user_id:
            return None
        
        db_purchase.status = "已取消"
        
        self.db.commit()
        self.db.refresh(db_purchase)
        
        return db_purchase
    
    def approve_purchase_request(
        self, 
        purchase_id: int, 
        approval_data: PurchaseApproval,
        admin_id: int
    ) -> Optional[PurchaseRequest]:
        """审批采购申请"""
        db_purchase = self.db.query(PurchaseRequest).filter(
            PurchaseRequest.id == purchase_id
        ).first()
        
        if not db_purchase:
            return None
        
        if db_purchase.status != "待审批":
            return None
        
        db_purchase.status = approval_data.status
        db_purchase.approved_by = admin_id
        db_purchase.approval_time = datetime.now()
        db_purchase.approval_comment = approval_data.approval_comment
        
        self.db.commit()
        self.db.refresh(db_purchase)
        
        return db_purchase
    
    def complete_purchase_request(self, purchase_id: int) -> Optional[PurchaseRequest]:
        """完成采购申请"""
        db_purchase = self.db.query(PurchaseRequest).filter(
            PurchaseRequest.id == purchase_id
        ).first()
        
        if not db_purchase:
            return None
        
        if db_purchase.status != "已批准":
            return None
        
        db_purchase.status = "已完成"
        
        self.db.commit()
        self.db.refresh(db_purchase)
        
        return db_purchase
    
    def get_pending_count(self) -> int:
        """获取待审批的采购申请数量"""
        return self.db.query(func.count(PurchaseRequest.id)).filter(
            PurchaseRequest.status == "待审批"
        ).scalar() or 0
    
    def get_my_purchases(
        self,
        user_id: int,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """获取我提交的采购申请"""
        return self.get_purchase_list(
            status=status,
            requested_by=user_id,
            page=page,
            page_size=page_size
        )
