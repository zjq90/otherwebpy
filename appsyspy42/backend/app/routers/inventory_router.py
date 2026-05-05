"""
库存管理路由
处理库存查询、料仓管理、原材料管理等接口
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.models import User, Material, Warehouse
from app.schemas.schemas import (
    MaterialCreate, MaterialUpdate, MaterialResponse,
    WarehouseCreate, WarehouseUpdate, WarehouseResponse,
    InventoryCreate, InventoryUpdate, InventoryDetailResponse
)
from app.services.inventory_service import InventoryService
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/inventory", tags=["库存管理"])


@router.get("/materials", summary="获取原材料列表")
def get_materials(
    material_type: Optional[str] = Query(None, description="原材料类型"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取原材料列表，支持按类型筛选和关键词搜索"""
    query = db.query(Material)
    
    if material_type:
        query = query.filter(Material.material_type == material_type)
    if keyword:
        query = query.filter(Material.material_name.like(f"%{keyword}%"))
    
    total = query.count()
    materials = query.order_by(Material.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return {
        "list": [MaterialResponse.model_validate(m) for m in materials],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/materials/{material_id}", response_model=MaterialResponse, summary="获取原材料详情")
def get_material(
    material_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定原材料的详细信息"""
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="原材料不存在"
        )
    return MaterialResponse.model_validate(material)


@router.post("/materials", response_model=MaterialResponse, summary="创建原材料")
def create_material(
    material_data: MaterialCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新的原材料"""
    existing = db.query(Material).filter(
        Material.material_name == material_data.material_name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原材料名称已存在"
        )
    
    db_material = Material(**material_data.model_dump())
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    
    return MaterialResponse.model_validate(db_material)


@router.put("/materials/{material_id}", response_model=MaterialResponse, summary="更新原材料")
def update_material(
    material_id: int,
    material_data: MaterialUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新原材料信息"""
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="原材料不存在"
        )
    
    for key, value in material_data.model_dump(exclude_unset=True).items():
        setattr(material, key, value)
    
    db.commit()
    db.refresh(material)
    
    return MaterialResponse.model_validate(material)


@router.get("/warehouses", summary="获取料仓列表")
def get_warehouses(
    is_active: Optional[int] = Query(None, description="是否启用"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取料仓列表"""
    query = db.query(Warehouse)
    
    if is_active is not None:
        query = query.filter(Warehouse.is_active == is_active)
    
    total = query.count()
    warehouses = query.order_by(Warehouse.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return {
        "list": [WarehouseResponse.model_validate(w) for w in warehouses],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/warehouses/{warehouse_id}", response_model=WarehouseResponse, summary="获取料仓详情")
def get_warehouse(
    warehouse_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定料仓的详细信息"""
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="料仓不存在"
        )
    return WarehouseResponse.model_validate(warehouse)


@router.post("/warehouses", response_model=WarehouseResponse, summary="创建料仓")
def create_warehouse(
    warehouse_data: WarehouseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新的料仓"""
    db_warehouse = Warehouse(**warehouse_data.model_dump())
    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)
    
    return WarehouseResponse.model_validate(db_warehouse)


@router.put("/warehouses/{warehouse_id}", response_model=WarehouseResponse, summary="更新料仓")
def update_warehouse(
    warehouse_id: int,
    warehouse_data: WarehouseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新料仓信息"""
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="料仓不存在"
        )
    
    for key, value in warehouse_data.model_dump(exclude_unset=True).items():
        setattr(warehouse, key, value)
    
    db.commit()
    db.refresh(warehouse)
    
    return WarehouseResponse.model_validate(warehouse)


@router.get("/list", summary="获取库存列表")
def get_inventory_list(
    material_type: Optional[str] = Query(None, description="原材料类型"),
    material_name: Optional[str] = Query(None, description="原材料名称"),
    warehouse_id: Optional[int] = Query(None, description="料仓ID"),
    is_low_stock: Optional[int] = Query(None, description="是否低库存"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取库存列表，支持多种筛选条件"""
    service = InventoryService(db)
    result = service.get_inventory_list(
        material_type=material_type,
        material_name=material_name,
        warehouse_id=warehouse_id,
        is_low_stock=is_low_stock,
        page=page,
        page_size=page_size
    )
    return result


@router.get("/list/{inventory_id}", response_model=InventoryDetailResponse, summary="获取库存详情")
def get_inventory_detail(
    inventory_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定库存的详细信息"""
    service = InventoryService(db)
    inventory = service.get_inventory_by_id(inventory_id)
    
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="库存记录不存在"
        )
    
    return inventory


@router.post("/list", summary="创建库存记录")
def create_inventory(
    inventory_data: InventoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新的库存记录"""
    material = db.query(Material).filter(
        Material.id == inventory_data.material_id
    ).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原材料不存在"
        )
    
    warehouse = db.query(Warehouse).filter(
        Warehouse.id == inventory_data.warehouse_id
    ).first()
    
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="料仓不存在"
        )
    
    existing = db.query(Material).filter(
        Material.material_name == material.material_name
    ).first()
    
    service = InventoryService(db)
    inventory = service.create_inventory(inventory_data)
    
    return {"success": True, "message": "库存创建成功", "data": {"id": inventory.id}}


@router.put("/list/{inventory_id}", summary="更新库存记录")
def update_inventory(
    inventory_id: int,
    inventory_data: InventoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新库存记录"""
    service = InventoryService(db)
    inventory = service.update_inventory(inventory_id, inventory_data)
    
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="库存记录不存在"
        )
    
    return {"success": True, "message": "库存更新成功"}


@router.get("/alerts", summary="获取低库存预警列表")
def get_low_stock_alerts(
    is_read: Optional[int] = Query(None, description="是否已读"),
    is_handled: Optional[int] = Query(None, description="是否已处理"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取低库存预警列表"""
    service = InventoryService(db)
    alerts = service.get_low_stock_alerts(is_read=is_read, is_handled=is_handled)
    
    return {"list": alerts, "total": len(alerts)}


@router.get("/statistics", summary="获取库存统计数据")
def get_inventory_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取库存相关的统计数据"""
    service = InventoryService(db)
    stats = service.get_statistics()
    
    return stats
