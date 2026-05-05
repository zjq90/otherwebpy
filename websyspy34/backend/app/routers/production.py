from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.models import (
    ProductionPlan, ProductionOrder, Resource, ResourceAllocation,
    ProductionStatus, ResourceStatus, ResourceType, ProductionStage,
    ProductionStatusHistory
)
from app.schemas.schemas import (
    ProductionPlan as ProductionPlanSchema,
    ProductionPlanCreate,
    ProductionPlanUpdate,
    ProductionOrder as ProductionOrderSchema,
    ProductionOrderCreate,
    ProductionOrderUpdate,
    Resource as ResourceSchema,
    ResourceCreate,
    ResourceUpdate,
    ResourceAllocation as ResourceAllocationSchema,
    ResourceAllocationCreate
)

router = APIRouter(prefix="/api/production", tags=["生产计划与调度"])


@router.get("/plans/", response_model=List[ProductionPlanSchema], summary="获取生产计划列表")
def get_production_plans(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[ProductionStatus] = Query(None, description="状态"),
    priority: Optional[int] = Query(None, ge=1, le=5, description="优先级"),
    db: Session = Depends(get_db)
):
    """
    获取生产计划列表，支持分页和筛选
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    - **keyword**: 搜索关键词，匹配计划编码、名称、项目名称
    - **status**: 按状态筛选
    - **priority**: 按优先级筛选
    """
    query = db.query(ProductionPlan)
    
    if keyword:
        query = query.filter(
            or_(
                ProductionPlan.plan_code.contains(keyword),
                ProductionPlan.plan_name.contains(keyword),
                ProductionPlan.project_name.contains(keyword)
            )
        )
    if status:
        query = query.filter(ProductionPlan.status == status)
    if priority:
        query = query.filter(ProductionPlan.priority == priority)
    
    plans = query.order_by(ProductionPlan.priority.desc(), ProductionPlan.created_at.desc()).offset(skip).limit(limit).all()
    return plans


@router.get("/plans/{plan_id}", response_model=ProductionPlanSchema, summary="获取生产计划详情")
def get_production_plan(plan_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取生产计划详情
    
    - **plan_id**: 计划ID
    """
    plan = db.query(ProductionPlan).filter(ProductionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="生产计划不存在")
    return plan


@router.post("/plans/", response_model=ProductionPlanSchema, summary="创建生产计划")
def create_production_plan(plan: ProductionPlanCreate, db: Session = Depends(get_db)):
    """
    创建新的生产计划
    
    - **plan**: 生产计划数据
    """
    existing = db.query(ProductionPlan).filter(ProductionPlan.plan_code == plan.plan_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="计划编码已存在")
    
    db_plan = ProductionPlan(**plan.dict())
    db_plan.created_at = datetime.utcnow()
    db_plan.updated_at = datetime.utcnow()
    db_plan.completed_volume = 0.0
    
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


@router.put("/plans/{plan_id}", response_model=ProductionPlanSchema, summary="更新生产计划")
def update_production_plan(plan_id: int, plan: ProductionPlanUpdate, db: Session = Depends(get_db)):
    """
    更新生产计划信息
    
    - **plan_id**: 计划ID
    - **plan**: 更新的计划数据
    """
    db_plan = db.query(ProductionPlan).filter(ProductionPlan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="生产计划不存在")
    
    update_data = plan.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_plan, key, value)
    
    db_plan.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_plan)
    return db_plan


@router.delete("/plans/{plan_id}", summary="删除生产计划")
def delete_production_plan(plan_id: int, db: Session = Depends(get_db)):
    """
    删除生产计划（软删除，将状态设为CANCELLED）
    
    - **plan_id**: 计划ID
    """
    db_plan = db.query(ProductionPlan).filter(ProductionPlan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="生产计划不存在")
    
    db_plan.status = ProductionStatus.CANCELLED
    db_plan.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "生产计划已取消", "plan_id": plan_id}


@router.get("/orders/", response_model=List[ProductionOrderSchema], summary="获取生产任务单列表")
def get_production_orders(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量"),
    plan_id: Optional[int] = Query(None, description="所属计划ID"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[ProductionStatus] = Query(None, description="状态"),
    current_stage: Optional[ProductionStage] = Query(None, description="当前阶段"),
    db: Session = Depends(get_db)
):
    """
    获取生产任务单列表
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    - **plan_id**: 按计划ID筛选
    - **keyword**: 搜索关键词
    - **status**: 按状态筛选
    - **current_stage**: 按当前阶段筛选
    """
    query = db.query(ProductionOrder)
    
    if plan_id:
        query = query.filter(ProductionOrder.plan_id == plan_id)
    if keyword:
        query = query.filter(
            or_(
                ProductionOrder.order_code.contains(keyword),
                ProductionOrder.batch_number.contains(keyword)
            )
        )
    if status:
        query = query.filter(ProductionOrder.status == status)
    if current_stage:
        query = query.filter(ProductionOrder.current_stage == current_stage)
    
    orders = query.order_by(ProductionOrder.created_at.desc()).offset(skip).limit(limit).all()
    return orders


@router.get("/orders/{order_id}", response_model=ProductionOrderSchema, summary="获取生产任务单详情")
def get_production_order(order_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取生产任务单详情
    
    - **order_id**: 任务单ID
    """
    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="生产任务单不存在")
    return order


@router.post("/orders/", response_model=ProductionOrderSchema, summary="创建生产任务单")
def create_production_order(order: ProductionOrderCreate, db: Session = Depends(get_db)):
    """
    创建新的生产任务单
    
    - **order**: 任务单数据
    """
    existing = db.query(ProductionOrder).filter(ProductionOrder.order_code == order.order_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="任务单编码已存在")
    
    db_order = ProductionOrder(**order.dict())
    db_order.created_at = datetime.utcnow()
    db_order.updated_at = datetime.utcnow()
    db_order.progress = 0.0
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@router.put("/orders/{order_id}", response_model=ProductionOrderSchema, summary="更新生产任务单")
def update_production_order(order_id: int, order: ProductionOrderUpdate, db: Session = Depends(get_db)):
    """
    更新生产任务单信息，同时记录状态变更历史
    
    - **order_id**: 任务单ID
    - **order**: 更新的任务单数据
    """
    db_order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="生产任务单不存在")
    
    old_status = db_order.status
    old_stage = db_order.current_stage
    
    update_data = order.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)
    
    db_order.updated_at = datetime.utcnow()
    
    if 'status' in update_data or 'current_stage' in update_data:
        status_history = ProductionStatusHistory(
            order_id=order_id,
            previous_status=old_status,
            new_status=db_order.status if 'status' in update_data else old_status,
            previous_stage=old_stage,
            new_stage=db_order.current_stage if 'current_stage' in update_data else old_stage,
            change_reason="状态更新"
        )
        db.add(status_history)
    
    db.commit()
    db.refresh(db_order)
    return db_order


@router.post("/orders/{order_id}/start", response_model=ProductionOrderSchema, summary="开始生产任务")
def start_production_order(order_id: int, db: Session = Depends(get_db)):
    """
    开始生产任务，更新状态为IN_PROGRESS
    
    - **order_id**: 任务单ID
    """
    db_order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="生产任务单不存在")
    
    if db_order.status not in [ProductionStatus.PENDING, ProductionStatus.DELAYED]:
        raise HTTPException(status_code=400, detail="该任务单无法开始生产")
    
    old_status = db_order.status
    
    db_order.status = ProductionStatus.IN_PROGRESS
    db_order.actual_start_time = datetime.utcnow()
    db_order.current_stage = ProductionStage.BATCHING
    db_order.updated_at = datetime.utcnow()
    
    status_history = ProductionStatusHistory(
        order_id=order_id,
        previous_status=old_status,
        new_status=ProductionStatus.IN_PROGRESS,
        previous_stage=None,
        new_stage=ProductionStage.BATCHING,
        change_reason="开始生产"
    )
    db.add(status_history)
    
    db.commit()
    db.refresh(db_order)
    return db_order


@router.post("/orders/{order_id}/complete", response_model=ProductionOrderSchema, summary="完成生产任务")
def complete_production_order(order_id: int, db: Session = Depends(get_db)):
    """
    完成生产任务，更新状态为COMPLETED
    
    - **order_id**: 任务单ID
    """
    db_order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="生产任务单不存在")
    
    if db_order.status != ProductionStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="该任务单不在进行中")
    
    old_status = db_order.status
    old_stage = db_order.current_stage
    
    db_order.status = ProductionStatus.COMPLETED
    db_order.actual_end_time = datetime.utcnow()
    db_order.current_stage = ProductionStage.COMPLETED
    db_order.progress = 100.0
    db_order.updated_at = datetime.utcnow()
    
    status_history = ProductionStatusHistory(
        order_id=order_id,
        previous_status=old_status,
        new_status=ProductionStatus.COMPLETED,
        previous_stage=old_stage,
        new_stage=ProductionStage.COMPLETED,
        change_reason="生产完成"
    )
    db.add(status_history)
    
    if db_order.plan_id:
        plan = db.query(ProductionPlan).filter(ProductionPlan.id == db_order.plan_id).first()
        if plan:
            plan.completed_volume += db_order.volume
            plan.updated_at = datetime.utcnow()
            
            all_orders = db.query(ProductionOrder).filter(
                ProductionOrder.plan_id == db_order.plan_id
            ).all()
            completed_count = sum(1 for o in all_orders if o.status == ProductionStatus.COMPLETED)
            if completed_count == len(all_orders):
                plan.status = ProductionStatus.COMPLETED
                plan.actual_end_date = datetime.utcnow()
    
    db.commit()
    db.refresh(db_order)
    return db_order


@router.get("/resources/", response_model=List[ResourceSchema], summary="获取资源列表")
def get_resources(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量"),
    resource_type: Optional[ResourceType] = Query(None, description="资源类型"),
    status: Optional[ResourceStatus] = Query(None, description="状态"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """
    获取资源列表（搅拌车、铲车等）
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    - **resource_type**: 按资源类型筛选
    - **status**: 按状态筛选
    - **keyword**: 搜索关键词
    """
    query = db.query(Resource)
    
    if resource_type:
        query = query.filter(Resource.resource_type == resource_type)
    if status:
        query = query.filter(Resource.status == status)
    if keyword:
        query = query.filter(
            or_(
                Resource.resource_code.contains(keyword),
                Resource.resource_name.contains(keyword),
                Resource.license_plate.contains(keyword)
            )
        )
    
    resources = query.order_by(Resource.created_at.desc()).offset(skip).limit(limit).all()
    return resources


@router.get("/resources/{resource_id}", response_model=ResourceSchema, summary="获取资源详情")
def get_resource(resource_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取资源详情
    
    - **resource_id**: 资源ID
    """
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    return resource


@router.post("/resources/", response_model=ResourceSchema, summary="创建资源")
def create_resource(resource: ResourceCreate, db: Session = Depends(get_db)):
    """
    创建新资源
    
    - **resource**: 资源数据
    """
    existing = db.query(Resource).filter(Resource.resource_code == resource.resource_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="资源编码已存在")
    
    db_resource = Resource(**resource.dict())
    db_resource.created_at = datetime.utcnow()
    db_resource.updated_at = datetime.utcnow()
    
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource


@router.put("/resources/{resource_id}", response_model=ResourceSchema, summary="更新资源")
def update_resource(resource_id: int, resource: ResourceUpdate, db: Session = Depends(get_db)):
    """
    更新资源信息
    
    - **resource_id**: 资源ID
    - **resource**: 更新的资源数据
    """
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    
    update_data = resource.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_resource, key, value)
    
    db_resource.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_resource)
    return db_resource


@router.post("/resources/allocate/", response_model=ResourceAllocationSchema, summary="分配资源")
def allocate_resource(allocation: ResourceAllocationCreate, db: Session = Depends(get_db)):
    """
    分配资源给生产计划或任务单
    
    - **allocation**: 分配数据
    """
    resource = db.query(Resource).filter(Resource.id == allocation.resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    
    if resource.status != ResourceStatus.AVAILABLE:
        raise HTTPException(status_code=400, detail="资源不可用")
    
    active_allocations = db.query(ResourceAllocation).filter(
        ResourceAllocation.resource_id == allocation.resource_id,
        ResourceAllocation.is_active == True
    ).all()
    
    for active in active_allocations:
        active.is_active = False
    
    db_allocation = ResourceAllocation(**allocation.dict())
    db_allocation.is_active = True
    db_allocation.created_at = datetime.utcnow()
    
    resource.status = ResourceStatus.IN_USE
    if allocation.order_id:
        resource.current_order_id = allocation.order_id
    resource.updated_at = datetime.utcnow()
    
    db.add(db_allocation)
    db.commit()
    db.refresh(db_allocation)
    return db_allocation


@router.post("/resources/{resource_id}/release", summary="释放资源")
def release_resource(resource_id: int, db: Session = Depends(get_db)):
    """
    释放资源，将状态设为AVAILABLE
    
    - **resource_id**: 资源ID
    """
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    
    active_allocations = db.query(ResourceAllocation).filter(
        ResourceAllocation.resource_id == resource_id,
        ResourceAllocation.is_active == True
    ).all()
    
    for allocation in active_allocations:
        allocation.is_active = False
        allocation.allocation_end_time = datetime.utcnow()
    
    resource.status = ResourceStatus.AVAILABLE
    resource.current_order_id = None
    resource.updated_at = datetime.utcnow()
    
    db.commit()
    return {"message": "资源已释放", "resource_id": resource_id}
