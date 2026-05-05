"""
物资采购相关API路由
包含原材料库存、采购申请、供应商管理等功能
"""

from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..database import get_db
from ..models.user_models import User
from ..models.business_models import (
    MaterialInventory, PurchaseRequest, Supplier
)
from ..schemas.business_schemas import (
    MaterialInventoryCreate, MaterialInventoryUpdate, MaterialInventoryResponse,
    PurchaseRequestCreate, PurchaseRequestUpdate, PurchaseRequestResponse,
    SupplierCreate, SupplierResponse
)
from ..schemas.user_schemas import ApiResponse, PaginatedResponse
from ..utils.security import (
    get_current_user, require_role, is_admin
)

router = APIRouter(prefix="/material", tags=["物资采购管理"])


def generate_request_no() -> str:
    """生成采购申请编号"""
    import time
    timestamp = int(time.time())
    return f"PR{timestamp}"


@router.get("/inventory", response_model=PaginatedResponse)
async def get_material_inventory(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    material_type: Optional[str] = Query(None, description="材料类型"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    only_warning: bool = Query(False, description="仅显示预警库存"),
    current_user: User = Depends(require_role("material_purchaser")),
    db: AsyncSession = Depends(get_db)
):
    """
    获取原材料库存列表（物资采购员权限）
    """
    # 构建查询条件
    query = select(MaterialInventory)
    
    if material_type:
        query = query.where(MaterialInventory.material_type == material_type)
    
    if keyword:
        query = query.where(
            (MaterialInventory.material_name.contains(keyword)) |
            (MaterialInventory.material_code.contains(keyword))
        )
    
    if only_warning:
        query = query.where(MaterialInventory.quantity <= MaterialInventory.min_warning)
    
    # 查询总数
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar_one()
    
    # 分页查询
    query = query.order_by(MaterialInventory.updated_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    inventories = result.scalars().all()
    
    inventory_responses = [MaterialInventoryResponse.model_validate(i) for i in inventories]
    
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=inventory_responses
    )


@router.get("/inventory/{inventory_id}", response_model=MaterialInventoryResponse)
async def get_material_inventory_detail(
    inventory_id: int,
    current_user: User = Depends(require_role("material_purchaser")),
    db: AsyncSession = Depends(get_db)
):
    """
    获取原材料库存详情（物资采购员权限）
    """
    result = await db.execute(
        select(MaterialInventory).where(MaterialInventory.id == inventory_id)
    )
    inventory = result.scalar_one_or_none()
    
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="库存记录不存在"
        )
    
    return MaterialInventoryResponse.model_validate(inventory)


@router.post("/inventory", response_model=MaterialInventoryResponse)
async def create_material_inventory(
    inventory_data: MaterialInventoryCreate,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    创建原材料库存（管理员权限）
    """
    # 检查材料编码是否已存在
    result = await db.execute(
        select(MaterialInventory).where(MaterialInventory.material_code == inventory_data.material_code)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="材料编码已存在"
        )
    
    inventory = MaterialInventory(**inventory_data.model_dump())
    db.add(inventory)
    await db.commit()
    await db.refresh(inventory)
    
    return MaterialInventoryResponse.model_validate(inventory)


@router.put("/inventory/{inventory_id}", response_model=MaterialInventoryResponse)
async def update_material_inventory(
    inventory_id: int,
    inventory_data: MaterialInventoryUpdate,
    current_user: User = Depends(require_role("material_purchaser")),
    db: AsyncSession = Depends(get_db)
):
    """
    更新原材料库存（物资采购员权限）
    """
    result = await db.execute(
        select(MaterialInventory).where(MaterialInventory.id == inventory_id)
    )
    inventory = result.scalar_one_or_none()
    
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="库存记录不存在"
        )
    
    # 更新字段
    update_data = inventory_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(inventory, key, value)
    
    inventory.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(inventory)
    
    return MaterialInventoryResponse.model_validate(inventory)


@router.post("/purchase-requests", response_model=PurchaseRequestResponse)
async def create_purchase_request(
    request_data: PurchaseRequestCreate,
    current_user: User = Depends(require_role("material_purchaser")),
    db: AsyncSession = Depends(get_db)
):
    """
    提交采购申请（物资采购员权限）
    """
    request = PurchaseRequest(
        **request_data.model_dump(),
        request_no=generate_request_no(),
        applicant_id=current_user.id,
        status="pending"
    )
    db.add(request)
    await db.commit()
    await db.refresh(request)
    
    return PurchaseRequestResponse.model_validate(request)


@router.get("/purchase-requests", response_model=PaginatedResponse)
async def get_purchase_requests(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="状态"),
    urgency: Optional[str] = Query(None, description="紧急程度"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取采购申请列表
    - 管理员：可以查看所有申请
    - 物资采购员：可以查看自己提交的申请
    """
    # 构建查询条件
    query = select(PurchaseRequest)
    
    # 非管理员只能看到自己的申请
    if not is_admin(current_user):
        query = query.where(PurchaseRequest.applicant_id == current_user.id)
    
    if status:
        query = query.where(PurchaseRequest.status == status)
    
    if urgency:
        query = query.where(PurchaseRequest.urgency == urgency)
    
    # 查询总数
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar_one()
    
    # 分页查询
    query = query.order_by(PurchaseRequest.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    requests = result.scalars().all()
    
    request_responses = [PurchaseRequestResponse.model_validate(r) for r in requests]
    
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=request_responses
    )


@router.get("/purchase-requests/{request_id}", response_model=PurchaseRequestResponse)
async def get_purchase_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取采购申请详情
    """
    result = await db.execute(
        select(PurchaseRequest).where(PurchaseRequest.id == request_id)
    )
    request = result.scalar_one_or_none()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="采购申请不存在"
        )
    
    # 权限检查
    if not is_admin(current_user) and request.applicant_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此申请"
        )
    
    return PurchaseRequestResponse.model_validate(request)


@router.put("/purchase-requests/{request_id}/approve", response_model=PurchaseRequestResponse)
async def approve_purchase_request(
    request_id: int,
    approval_data: PurchaseRequestUpdate,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    审批采购申请（管理员权限）
    """
    result = await db.execute(
        select(PurchaseRequest).where(PurchaseRequest.id == request_id)
    )
    request = result.scalar_one_or_none()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="采购申请不存在"
        )
    
    if request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能审批待处理的申请"
        )
    
    # 更新审批状态
    if approval_data.status in ["approved", "rejected"]:
        request.status = approval_data.status
        request.approver_id = current_user.id
        request.approval_opinion = approval_data.approval_opinion
        request.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(request)
    
    return PurchaseRequestResponse.model_validate(request)


@router.post("/suppliers", response_model=SupplierResponse)
async def create_supplier(
    supplier_data: SupplierCreate,
    current_user: User = Depends(require_role("material_purchaser")),
    db: AsyncSession = Depends(get_db)
):
    """
    创建供应商（物资采购员权限）
    """
    # 检查供应商编码是否已存在
    result = await db.execute(
        select(Supplier).where(Supplier.supplier_code == supplier_data.supplier_code)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="供应商编码已存在"
        )
    
    supplier = Supplier(**supplier_data.model_dump())
    db.add(supplier)
    await db.commit()
    await db.refresh(supplier)
    
    return SupplierResponse.model_validate(supplier)


@router.get("/suppliers", response_model=PaginatedResponse)
async def get_suppliers(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    is_active: Optional[bool] = Query(None, description="是否合作中"),
    current_user: User = Depends(require_role("material_purchaser")),
    db: AsyncSession = Depends(get_db)
):
    """
    获取供应商列表（物资采购员权限）
    """
    # 构建查询条件
    query = select(Supplier)
    
    if keyword:
        query = query.where(
            (Supplier.supplier_name.contains(keyword)) |
            (Supplier.contact_person.contains(keyword)) |
            (Supplier.phone.contains(keyword))
        )
    
    if is_active is not None:
        query = query.where(Supplier.is_active == is_active)
    
    # 查询总数
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar_one()
    
    # 分页查询
    query = query.order_by(Supplier.updated_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    suppliers = result.scalars().all()
    
    supplier_responses = [SupplierResponse.model_validate(s) for s in suppliers]
    
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=supplier_responses
    )


@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: int,
    current_user: User = Depends(require_role("material_purchaser")),
    db: AsyncSession = Depends(get_db)
):
    """
    获取供应商详情（物资采购员权限）
    """
    result = await db.execute(
        select(Supplier).where(Supplier.id == supplier_id)
    )
    supplier = result.scalar_one_or_none()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="供应商不存在"
        )
    
    return SupplierResponse.model_validate(supplier)


@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: int,
    supplier_data: SupplierCreate,
    current_user: User = Depends(require_role("material_purchaser")),
    db: AsyncSession = Depends(get_db)
):
    """
    更新供应商信息（物资采购员权限）
    """
    result = await db.execute(
        select(Supplier).where(Supplier.id == supplier_id)
    )
    supplier = result.scalar_one_or_none()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="供应商不存在"
        )
    
    # 更新字段
    update_data = supplier_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(supplier, key, value)
    
    supplier.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(supplier)
    
    return SupplierResponse.model_validate(supplier)
