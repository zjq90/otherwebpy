"""
CRUD操作模块
包含所有数据的增删改查操作
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from typing import List, Optional, Tuple, Any
from datetime import date, datetime
import models
import schemas
from config import settings


def get_count_from_query(query) -> int:
    """从查询获取总数"""
    return query.count()


def get_supplier_by_name(db: Session, name: str, exclude_id: Optional[int] = None) -> Optional[models.Supplier]:
    """根据名称获取供应商（用于唯一性检查）"""
    query = db.query(models.Supplier).filter(models.Supplier.name == name)
    if exclude_id:
        query = query.filter(models.Supplier.id != exclude_id)
    return query.first()


def generate_purchase_no(db: Session) -> str:
    """
    生成采购单号
    格式: CG + 年月日 + 6位序号
    """
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"CG{today}"
    
    count = db.query(func.count(models.Purchase.id)).filter(
        models.Purchase.purchase_no.like(f"{prefix}%")
    ).scalar() or 0
    
    sequence = str(count + 1).zfill(6)
    return f"{prefix}{sequence}"


def get_supplier_by_id(db: Session, supplier_id: int) -> Optional[models.Supplier]:
    """根据ID获取供应商"""
    return db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()


def get_suppliers(db: Session, skip: int = 0, limit: int = 100) -> List[models.Supplier]:
    """获取供应商列表"""
    return db.query(models.Supplier).offset(skip).limit(limit).all()


def create_supplier(db: Session, supplier: schemas.SupplierCreate) -> models.Supplier:
    """创建供应商"""
    db_supplier = models.Supplier(**supplier.model_dump())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier


def update_supplier(db: Session, supplier_id: int, supplier: schemas.SupplierUpdate) -> Optional[models.Supplier]:
    """更新供应商"""
    db_supplier = get_supplier_by_id(db, supplier_id)
    if db_supplier:
        for key, value in supplier.model_dump().items():
            setattr(db_supplier, key, value)
        db.commit()
        db.refresh(db_supplier)
    return db_supplier


def delete_supplier(db: Session, supplier_id: int) -> bool:
    """删除供应商"""
    db_supplier = get_supplier_by_id(db, supplier_id)
    if db_supplier:
        db.delete(db_supplier)
        db.commit()
        return True
    return False


def get_category_by_id(db: Session, category_id: int) -> Optional[models.Category]:
    """根据ID获取分类"""
    return db.query(models.Category).filter(models.Category.id == category_id).first()


def get_category_by_code(db: Session, code: str) -> Optional[models.Category]:
    """根据编码获取分类"""
    return db.query(models.Category).filter(models.Category.code == code).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[models.Category]:
    """获取分类列表"""
    return db.query(models.Category).offset(skip).limit(limit).all()


def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
    """创建分类"""
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(db: Session, category_id: int, category: schemas.CategoryUpdate) -> Optional[models.Category]:
    """更新分类"""
    db_category = get_category_by_id(db, category_id)
    if db_category:
        for key, value in category.model_dump().items():
            setattr(db_category, key, value)
        db.commit()
        db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> bool:
    """删除分类"""
    db_category = get_category_by_id(db, category_id)
    if db_category:
        db.delete(db_category)
        db.commit()
        return True
    return False


def get_supply_by_id(db: Session, supply_id: int) -> Optional[models.Supply]:
    """根据ID获取农资"""
    return db.query(models.Supply).filter(models.Supply.id == supply_id).first()


def get_supplies(db: Session, skip: int = 0, limit: int = 100, category_id: Optional[int] = None) -> List[models.Supply]:
    """获取农资列表"""
    query = db.query(models.Supply)
    if category_id:
        query = query.filter(models.Supply.category_id == category_id)
    return query.offset(skip).limit(limit).all()


def create_supply(db: Session, supply: schemas.SupplyCreate) -> models.Supply:
    """创建农资"""
    db_supply = models.Supply(**supply.model_dump())
    db.add(db_supply)
    db.commit()
    db.refresh(db_supply)
    return db_supply


def update_supply(db: Session, supply_id: int, supply: schemas.SupplyUpdate) -> Optional[models.Supply]:
    """更新农资"""
    db_supply = get_supply_by_id(db, supply_id)
    if db_supply:
        for key, value in supply.model_dump().items():
            setattr(db_supply, key, value)
        db.commit()
        db.refresh(db_supply)
    return db_supply


def delete_supply(db: Session, supply_id: int) -> bool:
    """删除农资"""
    db_supply = get_supply_by_id(db, supply_id)
    if db_supply:
        db.delete(db_supply)
        db.commit()
        return True
    return False


def get_plot_by_id(db: Session, plot_id: int) -> Optional[models.Plot]:
    """根据ID获取地块"""
    return db.query(models.Plot).filter(models.Plot.id == plot_id).first()


def get_plots(db: Session, skip: int = 0, limit: int = 100) -> List[models.Plot]:
    """获取地块列表"""
    return db.query(models.Plot).offset(skip).limit(limit).all()


def create_plot(db: Session, plot: schemas.PlotCreate) -> models.Plot:
    """创建地块"""
    db_plot = models.Plot(**plot.model_dump())
    db.add(db_plot)
    db.commit()
    db.refresh(db_plot)
    return db_plot


def update_plot(db: Session, plot_id: int, plot: schemas.PlotUpdate) -> Optional[models.Plot]:
    """更新地块"""
    db_plot = get_plot_by_id(db, plot_id)
    if db_plot:
        for key, value in plot.model_dump().items():
            setattr(db_plot, key, value)
        db.commit()
        db.refresh(db_plot)
    return db_plot


def delete_plot(db: Session, plot_id: int) -> bool:
    """删除地块"""
    db_plot = get_plot_by_id(db, plot_id)
    if db_plot:
        db.delete(db_plot)
        db.commit()
        return True
    return False


def get_crop_by_id(db: Session, crop_id: int) -> Optional[models.Crop]:
    """根据ID获取作物"""
    return db.query(models.Crop).filter(models.Crop.id == crop_id).first()


def get_crops(db: Session, skip: int = 0, limit: int = 100) -> List[models.Crop]:
    """获取作物列表"""
    return db.query(models.Crop).offset(skip).limit(limit).all()


def create_crop(db: Session, crop: schemas.CropCreate) -> models.Crop:
    """创建作物"""
    db_crop = models.Crop(**crop.model_dump())
    db.add(db_crop)
    db.commit()
    db.refresh(db_crop)
    return db_crop


def update_crop(db: Session, crop_id: int, crop: schemas.CropUpdate) -> Optional[models.Crop]:
    """更新作物"""
    db_crop = get_crop_by_id(db, crop_id)
    if db_crop:
        for key, value in crop.model_dump().items():
            setattr(db_crop, key, value)
        db.commit()
        db.refresh(db_crop)
    return db_crop


def delete_crop(db: Session, crop_id: int) -> bool:
    """删除作物"""
    db_crop = get_crop_by_id(db, crop_id)
    if db_crop:
        db.delete(db_crop)
        db.commit()
        return True
    return False


def get_purchase_by_id(db: Session, purchase_id: int) -> Optional[models.Purchase]:
    """根据ID获取采购记录"""
    return db.query(models.Purchase).filter(models.Purchase.id == purchase_id).first()


def get_purchases(db: Session, skip: int = 0, limit: int = 100, supply_id: Optional[int] = None) -> List[models.Purchase]:
    """获取采购记录列表"""
    query = db.query(models.Purchase).order_by(desc(models.Purchase.purchase_date))
    if supply_id:
        query = query.filter(models.Purchase.supply_id == supply_id)
    return query.offset(skip).limit(limit).all()


def create_purchase(db: Session, purchase: schemas.PurchaseCreate) -> models.Purchase:
    """
    创建采购记录
    同时创建库存记录，支持批次管理
    """
    purchase_data = purchase.model_dump()
    purchase_data["purchase_no"] = generate_purchase_no(db)
    purchase_data["total_price"] = purchase_data["quantity"] * purchase_data["unit_price"]
    
    db_purchase = models.Purchase(**purchase_data)
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    
    db_inventory = models.Inventory(
        supply_id=purchase.supply_id,
        purchase_id=db_purchase.id,
        batch_no=purchase.batch_no,
        quantity=purchase.quantity,
        expiry_date=purchase.expiry_date
    )
    db.add(db_inventory)
    db.commit()
    
    db.refresh(db_purchase)
    return db_purchase


def update_purchase(db: Session, purchase_id: int, purchase: schemas.PurchaseUpdate) -> Optional[models.Purchase]:
    """更新采购记录"""
    db_purchase = get_purchase_by_id(db, purchase_id)
    if db_purchase:
        purchase_data = purchase.model_dump()
        purchase_data["total_price"] = purchase_data["quantity"] * purchase_data["unit_price"]
        
        old_quantity = db_purchase.quantity
        for key, value in purchase_data.items():
            setattr(db_purchase, key, value)
        
        inventory = db.query(models.Inventory).filter(
            models.Inventory.purchase_id == purchase_id
        ).first()
        if inventory:
            inventory.batch_no = purchase.batch_no
            inventory.expiry_date = purchase.expiry_date
        
        db.commit()
        db.refresh(db_purchase)
    return db_purchase


def delete_purchase(db: Session, purchase_id: int) -> bool:
    """删除采购记录（同时删除关联的库存，库存必须为空）"""
    db_purchase = get_purchase_by_id(db, purchase_id)
    if db_purchase:
        inventory = db.query(models.Inventory).filter(
            models.Inventory.purchase_id == purchase_id
        ).first()
        
        if inventory and inventory.quantity > 0:
            return False
        
        if inventory:
            db.delete(inventory)
        
        db.delete(db_purchase)
        db.commit()
        return True
    return False


def get_inventory_by_id(db: Session, inventory_id: int) -> Optional[models.Inventory]:
    """根据ID获取库存"""
    return db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()


def get_inventory_by_supply(db: Session, supply_id: int) -> List[models.Inventory]:
    """
    获取指定农资的所有库存批次
    按保质期先后排序（先进先出）
    """
    return db.query(models.Inventory).filter(
        models.Inventory.supply_id == supply_id,
        models.Inventory.quantity > 0
    ).order_by(
        models.Inventory.expiry_date.asc(),
        models.Inventory.created_at.asc()
    ).all()


def get_inventories(db: Session, skip: int = 0, limit: int = 100, supply_id: Optional[int] = None) -> List[models.Inventory]:
    """获取库存列表"""
    query = db.query(models.Inventory)
    if supply_id:
        query = query.filter(models.Inventory.supply_id == supply_id)
    return query.offset(skip).limit(limit).all()


def get_inventory_summary(db: Session) -> List[dict]:
    """获取库存汇总信息"""
    results = db.query(
        models.Supply.id.label("supply_id"),
        models.Supply.name.label("supply_name"),
        models.Category.name.label("category_name"),
        func.sum(models.Inventory.quantity).label("total_quantity"),
        models.Supply.unit,
        models.Supply.warning_threshold
    ).join(
        models.Inventory, models.Supply.id == models.Inventory.supply_id
    ).join(
        models.Category, models.Supply.category_id == models.Category.id
    ).group_by(
        models.Supply.id
    ).all()
    
    summary_list = []
    for result in results:
        total_quantity = result.total_quantity or 0
        warning_threshold = result.warning_threshold or 0
        summary_list.append({
            "supply_id": result.supply_id,
            "supply_name": result.supply_name,
            "category_name": result.category_name,
            "total_quantity": total_quantity,
            "unit": result.unit or "",
            "warning_threshold": warning_threshold,
            "is_below_threshold": total_quantity <= warning_threshold
        })
    
    return summary_list


def get_low_inventory_alerts(db: Session) -> List[dict]:
    """
    获取库存预警列表
    检查库存是否低于预警阈值
    """
    summary = get_inventory_summary(db)
    alerts = []
    
    for item in summary:
        if item["is_below_threshold"]:
            alerts.append({
                "supply_id": item["supply_id"],
                "supply_name": item["supply_name"],
                "category_name": item["category_name"],
                "current_quantity": item["total_quantity"],
                "warning_threshold": item["warning_threshold"],
                "alert_type": "库存不足"
            })
    
    return alerts


def get_usage_record_by_id(db: Session, usage_id: int) -> Optional[models.UsageRecord]:
    """根据ID获取使用记录"""
    return db.query(models.UsageRecord).filter(models.UsageRecord.id == usage_id).first()


def get_usage_records(db: Session, skip: int = 0, limit: int = 100, 
                       supply_id: Optional[int] = None,
                       plot_id: Optional[int] = None,
                       crop_id: Optional[int] = None) -> List[models.UsageRecord]:
    """获取使用记录列表"""
    query = db.query(models.UsageRecord).order_by(desc(models.UsageRecord.usage_date))
    if supply_id:
        query = query.filter(models.UsageRecord.supply_id == supply_id)
    if plot_id:
        query = query.filter(models.UsageRecord.plot_id == plot_id)
    if crop_id:
        query = query.filter(models.UsageRecord.crop_id == crop_id)
    return query.offset(skip).limit(limit).all()


def create_usage_record(db: Session, usage: schemas.UsageRecordCreate) -> Optional[models.UsageRecord]:
    """
    创建使用记录
    实现先进先出（FIFO）策略：
    1. 检查指定库存是否有足够数量
    2. 扣减库存
    3. 创建使用记录
    """
    inventory = get_inventory_by_id(db, usage.inventory_id)
    if not inventory:
        return None
    
    if inventory.quantity < usage.quantity:
        return None
    
    inventory.quantity -= usage.quantity
    
    db_usage = models.UsageRecord(**usage.model_dump())
    db.add(db_usage)
    db.commit()
    db.refresh(db_usage)
    
    return db_usage


def create_usage_record_fifo(db: Session, usage_data: dict) -> Optional[models.UsageRecord]:
    """
    使用先进先出策略创建使用记录
    自动选择最早过期/最早入库的批次
    
    参数:
        usage_data: 包含以下字段的字典
            - supply_id: 农资ID
            - plot_id: 地块ID
            - crop_id: 作物ID
            - quantity: 使用数量
            - usage_date: 使用日期
            - usage_method: 使用方法（可选）
            - operator: 操作人（可选）
            - remark: 备注（可选）
    """
    supply_id = usage_data.get("supply_id")
    required_quantity = usage_data.get("quantity")
    
    if not supply_id or not required_quantity:
        return None
    
    inventory_list = get_inventory_by_supply(db, supply_id)
    
    if not inventory_list:
        return None
    
    total_available = sum(inv.quantity for inv in inventory_list)
    if total_available < required_quantity:
        return None
    
    remaining_quantity = required_quantity
    selected_inventory = None
    used_quantity = 0
    
    for inventory in inventory_list:
        if remaining_quantity <= 0:
            break
        
        if inventory.quantity >= remaining_quantity:
            selected_inventory = inventory
            used_quantity = remaining_quantity
            inventory.quantity -= remaining_quantity
            remaining_quantity = 0
        else:
            selected_inventory = inventory
            used_quantity = inventory.quantity
            remaining_quantity -= inventory.quantity
            inventory.quantity = 0
    
    if selected_inventory is None:
        return None
    
    db_usage = models.UsageRecord(
        usage_date=usage_data.get("usage_date"),
        supply_id=supply_id,
        inventory_id=selected_inventory.id,
        plot_id=usage_data.get("plot_id"),
        crop_id=usage_data.get("crop_id"),
        quantity=used_quantity,
        usage_method=usage_data.get("usage_method"),
        operator=usage_data.get("operator"),
        remark=usage_data.get("remark")
    )
    db.add(db_usage)
    db.commit()
    db.refresh(db_usage)
    
    return db_usage


def update_usage_record(db: Session, usage_id: int, usage: schemas.UsageRecordUpdate) -> Optional[models.UsageRecord]:
    """更新使用记录"""
    db_usage = get_usage_record_by_id(db, usage_id)
    if db_usage:
        old_inventory = db.query(models.Inventory).filter(
            models.Inventory.id == db_usage.inventory_id
        ).first()
        old_quantity = db_usage.quantity
        
        if old_inventory and old_inventory.id != usage.inventory_id:
            old_inventory.quantity += old_quantity
            
            new_inventory = db.query(models.Inventory).filter(
                models.Inventory.id == usage.inventory_id
            ).first()
            if new_inventory:
                if new_inventory.quantity < usage.quantity:
                    return None
                new_inventory.quantity -= usage.quantity
        elif old_inventory and old_inventory.id == usage.inventory_id:
            quantity_diff = usage.quantity - old_quantity
            if quantity_diff > 0:
                if old_inventory.quantity < quantity_diff:
                    return None
                old_inventory.quantity -= quantity_diff
            elif quantity_diff < 0:
                old_inventory.quantity += abs(quantity_diff)
        
        for key, value in usage.model_dump().items():
            setattr(db_usage, key, value)
        
        db.commit()
        db.refresh(db_usage)
    return db_usage


def delete_usage_record(db: Session, usage_id: int) -> bool:
    """删除使用记录（归还库存）"""
    db_usage = get_usage_record_by_id(db, usage_id)
    if db_usage:
        inventory = db.query(models.Inventory).filter(
            models.Inventory.id == db_usage.inventory_id
        ).first()
        
        if inventory:
            inventory.quantity += db_usage.quantity
        
        db.delete(db_usage)
        db.commit()
        return True
    return False


def get_statistics(db: Session) -> dict:
    """获取系统统计数据"""
    supplier_count = db.query(func.count(models.Supplier.id)).scalar() or 0
    supply_count = db.query(func.count(models.Supply.id)).scalar() or 0
    plot_count = db.query(func.count(models.Plot.id)).scalar() or 0
    crop_count = db.query(func.count(models.Crop.id)).scalar() or 0
    
    purchase_count = db.query(func.count(models.Purchase.id)).scalar() or 0
    total_purchase_amount = db.query(func.sum(models.Purchase.total_price)).scalar() or 0
    
    usage_count = db.query(func.count(models.UsageRecord.id)).scalar() or 0
    
    low_inventory_count = len(get_low_inventory_alerts(db))
    
    return {
        "supplier_count": supplier_count,
        "supply_count": supply_count,
        "plot_count": plot_count,
        "crop_count": crop_count,
        "purchase_count": purchase_count,
        "total_purchase_amount": float(total_purchase_amount),
        "usage_count": usage_count,
        "low_inventory_count": low_inventory_count
    }


def get_supplier_count(db: Session) -> int:
    """获取供应商总数"""
    return db.query(func.count(models.Supplier.id)).scalar() or 0


def get_supply_count(db: Session, category_id: Optional[int] = None) -> int:
    """获取农资总数"""
    query = db.query(func.count(models.Supply.id))
    if category_id:
        query = query.filter(models.Supply.category_id == category_id)
    return query.scalar() or 0


def get_plot_count(db: Session) -> int:
    """获取地块总数"""
    return db.query(func.count(models.Plot.id)).scalar() or 0


def get_crop_count(db: Session) -> int:
    """获取作物总数"""
    return db.query(func.count(models.Crop.id)).scalar() or 0


def get_purchase_count(db: Session, supply_id: Optional[int] = None) -> int:
    """获取采购记录总数"""
    query = db.query(func.count(models.Purchase.id))
    if supply_id:
        query = query.filter(models.Purchase.supply_id == supply_id)
    return query.scalar() or 0


def get_inventory_count(db: Session, supply_id: Optional[int] = None) -> int:
    """获取库存记录总数"""
    query = db.query(func.count(models.Inventory.id))
    if supply_id:
        query = query.filter(models.Inventory.supply_id == supply_id)
    return query.scalar() or 0


def get_usage_record_count(db: Session, 
                            supply_id: Optional[int] = None,
                            plot_id: Optional[int] = None,
                            crop_id: Optional[int] = None) -> int:
    """获取使用记录总数"""
    query = db.query(func.count(models.UsageRecord.id))
    if supply_id:
        query = query.filter(models.UsageRecord.supply_id == supply_id)
    if plot_id:
        query = query.filter(models.UsageRecord.plot_id == plot_id)
    if crop_id:
        query = query.filter(models.UsageRecord.crop_id == crop_id)
    return query.scalar() or 0


def get_supply_by_name(db: Session, name: str, exclude_id: Optional[int] = None) -> Optional[models.Supply]:
    """根据名称获取农资（用于唯一性检查）"""
    query = db.query(models.Supply).filter(models.Supply.name == name)
    if exclude_id:
        query = query.filter(models.Supply.id != exclude_id)
    return query.first()


def get_plot_by_name(db: Session, name: str, exclude_id: Optional[int] = None) -> Optional[models.Plot]:
    """根据名称获取地块（用于唯一性检查）"""
    query = db.query(models.Plot).filter(models.Plot.name == name)
    if exclude_id:
        query = query.filter(models.Plot.id != exclude_id)
    return query.first()


def get_crop_by_name(db: Session, name: str, exclude_id: Optional[int] = None) -> Optional[models.Crop]:
    """根据名称获取作物（用于唯一性检查）"""
    query = db.query(models.Crop).filter(models.Crop.name == name)
    if exclude_id:
        query = query.filter(models.Crop.id != exclude_id)
    return query.first()


def get_purchase_by_batch_no(db: Session, batch_no: str, exclude_id: Optional[int] = None) -> Optional[models.Purchase]:
    """根据批次号获取采购记录（用于唯一性检查）"""
    query = db.query(models.Purchase).filter(models.Purchase.batch_no == batch_no)
    if exclude_id:
        query = query.filter(models.Purchase.id != exclude_id)
    return query.first()
