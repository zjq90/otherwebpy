"""
采购申请路由
处理采购申请的提交、审批、查询等接口
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.models import User
from app.schemas.schemas import (
    PurchaseRequestCreate, PurchaseRequestUpdate, 
    PurchaseApproval, PurchaseRequestDetailResponse
)
from app.services.purchase_service import PurchaseService
from app.services.auth_service import get_current_user, get_current_admin

router = APIRouter(prefix="/purchase", tags=["采购申请"])


@router.get("/list", summary="获取采购申请列表")
def get_purchase_list(
    status: Optional[str] = Query(None, description="状态筛选"),
    material_type: Optional[str] = Query(None, description="原材料类型"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取采购申请列表，管理员可以看到所有，采购员只能看到自己的"""
    service = PurchaseService(db)
    
    requested_by = None
    if current_user.role != "管理员":
        requested_by = current_user.id
    
    result = service.get_purchase_list(
        status=status,
        material_type=material_type,
        requested_by=requested_by,
        page=page,
        page_size=page_size
    )
    
    return result


@router.get("/list/{purchase_id}", response_model=PurchaseRequestDetailResponse, summary="获取采购申请详情")
def get_purchase_detail(
    purchase_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定采购申请的详细信息"""
    service = PurchaseService(db)
    purchase = service.get_purchase_by_id(purchase_id)
    
    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="采购申请不存在"
        )
    
    if current_user.role != "管理员" and purchase.requested_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此采购申请"
        )
    
    return purchase


@router.post("/list", summary="提交采购申请")
def create_purchase_request(
    purchase_data: PurchaseRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """提交新的采购申请"""
    service = PurchaseService(db)
    purchase = service.create_purchase_request(purchase_data, current_user.id)
    
    return {
        "success": True, 
        "message": "采购申请提交成功", 
        "data": {
            "id": purchase.id,
            "request_no": purchase.request_no
        }
    }


@router.put("/list/{purchase_id}", summary="更新采购申请")
def update_purchase_request(
    purchase_id: int,
    purchase_data: PurchaseRequestUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新待审批的采购申请（只能更新自己提交的）"""
    service = PurchaseService(db)
    purchase = service.update_purchase_request(purchase_id, purchase_data, current_user.id)
    
    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="采购申请不存在或已被审批，无法更新"
        )
    
    return {"success": True, "message": "采购申请更新成功"}


@router.post("/list/{purchase_id}/cancel", summary="取消采购申请")
def cancel_purchase_request(
    purchase_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取消待审批的采购申请"""
    service = PurchaseService(db)
    purchase = service.cancel_purchase_request(purchase_id, current_user.id)
    
    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="采购申请不存在或已被审批，无法取消"
        )
    
    return {"success": True, "message": "采购申请已取消"}


@router.post("/list/{purchase_id}/approve", summary="审批采购申请（管理员）")
def approve_purchase_request(
    purchase_id: int,
    approval_data: PurchaseApproval,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """审批采购申请，需要管理员权限"""
    if approval_data.status not in ["已批准", "已拒绝"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="审批状态必须是'已批准'或'已拒绝'"
        )
    
    service = PurchaseService(db)
    purchase = service.approve_purchase_request(purchase_id, approval_data, current_user.id)
    
    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="采购申请不存在或已被审批"
        )
    
    return {"success": True, "message": f"采购申请已{approval_data.status}"}


@router.post("/list/{purchase_id}/complete", summary="完成采购申请")
def complete_purchase_request(
    purchase_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """标记采购申请为已完成"""
    service = PurchaseService(db)
    purchase = service.complete_purchase_request(purchase_id)
    
    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="采购申请不存在或状态不正确"
        )
    
    return {"success": True, "message": "采购申请已标记为完成"}


@router.get("/pending-count", summary="获取待审批数量")
def get_pending_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取待审批的采购申请数量（管理员专用）"""
    if current_user.role != "管理员":
        return {"count": 0}
    
    service = PurchaseService(db)
    count = service.get_pending_count()
    
    return {"count": count}


@router.get("/my", summary="获取我的采购申请")
def get_my_purchases(
    status: Optional[str] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户提交的采购申请列表"""
    service = PurchaseService(db)
    result = service.get_my_purchases(
        user_id=current_user.id,
        status=status,
        page=page,
        page_size=page_size
    )
    
    return result
