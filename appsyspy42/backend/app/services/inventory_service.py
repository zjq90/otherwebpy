"""
库存服务
处理库存相关的业务逻辑，包括库存查询、预警检查等
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime

from app.models.models import (
    Inventory, Material, Warehouse, StockAlert
)
from app.schemas.schemas import InventoryCreate, InventoryUpdate, InventoryDetailResponse


class InventoryService:
    """库存服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_inventory_list(
        self,
        material_type: Optional[str] = None,
        material_name: Optional[str] = None,
        warehouse_id: Optional[int] = None,
        is_low_stock: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """
        获取库存列表
        :param material_type: 原材料类型筛选
        :param material_name: 原材料名称模糊搜索
        :param warehouse_id: 料仓ID筛选
        :param is_low_stock: 是否低库存筛选
        :param page: 页码
        :param page_size: 每页数量
        """
        query = self.db.query(
            Inventory,
            Material.material_name,
            Material.material_type,
            Material.specification,
            Material.unit,
            Warehouse.warehouse_name,
            Warehouse.location.label("warehouse_location")
        ).join(
            Material, Inventory.material_id == Material.id
        ).join(
            Warehouse, Inventory.warehouse_id == Warehouse.id
        )
        
        if material_type:
            query = query.filter(Material.material_type == material_type)
        if material_name:
            query = query.filter(Material.material_name.like(f"%{material_name}%"))
        if warehouse_id:
            query = query.filter(Inventory.warehouse_id == warehouse_id)
        if is_low_stock is not None:
            query = query.filter(Inventory.is_low_stock == is_low_stock)
        
        total = query.count()
        
        results = query.offset((page - 1) * page_size).limit(page_size).all()
        
        inventory_list = []
        for inventory, material_name, material_type, spec, unit, warehouse_name, location in results:
            inventory_list.append(InventoryDetailResponse(
                id=inventory.id,
                material_id=inventory.material_id,
                warehouse_id=inventory.warehouse_id,
                material_name=material_name,
                material_type=material_type,
                specification=spec,
                warehouse_name=warehouse_name,
                warehouse_location=location,
                quantity=inventory.quantity,
                unit=unit,
                safety_threshold=inventory.safety_threshold,
                unit_price=inventory.unit_price,
                production_date=inventory.production_date,
                expiry_date=inventory.expiry_date,
                batch_number=inventory.batch_number,
                is_low_stock=inventory.is_low_stock,
                last_check_time=inventory.last_check_time,
                created_at=inventory.created_at,
                updated_at=inventory.updated_at
            ))
        
        return {
            "list": inventory_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    def get_inventory_by_id(self, inventory_id: int) -> Optional[InventoryDetailResponse]:
        """根据ID获取库存详情"""
        result = self.db.query(
            Inventory,
            Material.material_name,
            Material.material_type,
            Material.specification,
            Material.unit,
            Warehouse.warehouse_name,
            Warehouse.location.label("warehouse_location")
        ).join(
            Material, Inventory.material_id == Material.id
        ).join(
            Warehouse, Inventory.warehouse_id == Warehouse.id
        ).filter(Inventory.id == inventory_id).first()
        
        if not result:
            return None
        
        inventory, material_name, material_type, spec, unit, warehouse_name, location = result
        
        return InventoryDetailResponse(
            id=inventory.id,
            material_id=inventory.material_id,
            warehouse_id=inventory.warehouse_id,
            material_name=material_name,
            material_type=material_type,
            specification=spec,
            warehouse_name=warehouse_name,
            warehouse_location=location,
            quantity=inventory.quantity,
            unit=unit,
            safety_threshold=inventory.safety_threshold,
            unit_price=inventory.unit_price,
            production_date=inventory.production_date,
            expiry_date=inventory.expiry_date,
            batch_number=inventory.batch_number,
            is_low_stock=inventory.is_low_stock,
            last_check_time=inventory.last_check_time,
            created_at=inventory.created_at,
            updated_at=inventory.updated_at
        )
    
    def create_inventory(self, inventory_data: InventoryCreate) -> Inventory:
        """创建库存记录"""
        db_inventory = Inventory(**inventory_data.model_dump())
        
        is_low_stock = 1 if db_inventory.quantity < db_inventory.safety_threshold else 0
        db_inventory.is_low_stock = is_low_stock
        
        self.db.add(db_inventory)
        self.db.commit()
        self.db.refresh(db_inventory)
        
        self.check_and_create_alert(db_inventory)
        
        return db_inventory
    
    def update_inventory(self, inventory_id: int, inventory_data: InventoryUpdate) -> Optional[Inventory]:
        """更新库存记录"""
        db_inventory = self.db.query(Inventory).filter(Inventory.id == inventory_id).first()
        if not db_inventory:
            return None
        
        for key, value in inventory_data.model_dump(exclude_unset=True).items():
            setattr(db_inventory, key, value)
        
        if hasattr(inventory_data, 'quantity') and hasattr(inventory_data, 'safety_threshold'):
            is_low_stock = 1 if db_inventory.quantity < db_inventory.safety_threshold else 0
            db_inventory.is_low_stock = is_low_stock
        
        self.db.commit()
        self.db.refresh(db_inventory)
        
        self.check_and_create_alert(db_inventory)
        
        return db_inventory
    
    def delete_inventory(self, inventory_id: int) -> bool:
        """删除库存记录"""
        db_inventory = self.db.query(Inventory).filter(Inventory.id == inventory_id).first()
        if not db_inventory:
            return False
        
        self.db.query(StockAlert).filter(StockAlert.inventory_id == inventory_id).delete()
        
        self.db.delete(db_inventory)
        self.db.commit()
        return True
    
    def check_and_create_alert(self, inventory: Inventory):
        """
        检查库存状态并创建预警
        如果库存低于安全阈值，创建低库存预警
        """
        material = self.db.query(Material).filter(Material.id == inventory.material_id).first()
        warehouse = self.db.query(Warehouse).filter(Warehouse.id == inventory.warehouse_id).first()
        
        if inventory.quantity < inventory.safety_threshold:
            existing_alert = self.db.query(StockAlert).filter(
                StockAlert.inventory_id == inventory.id,
                StockAlert.alert_type == "低库存",
                StockAlert.is_handled == 0
            ).first()
            
            if not existing_alert:
                alert = StockAlert(
                    inventory_id=inventory.id,
                    alert_type="低库存",
                    threshold_value=inventory.safety_threshold,
                    current_value=inventory.quantity,
                    message=f"{material.material_name if material else '原材料'} 库存不足！当前库存: {inventory.quantity}, 安全阈值: {inventory.safety_threshold}",
                    is_read=0,
                    is_handled=0
                )
                self.db.add(alert)
                self.db.commit()
    
    def get_statistics(self) -> dict:
        """获取库存统计数据"""
        total_materials = self.db.query(func.count(Material.id)).scalar() or 0
        
        total_value = self.db.query(
            func.sum(Inventory.quantity * Inventory.unit_price)
        ).filter(Inventory.unit_price != None).scalar() or 0
        
        low_stock_count = self.db.query(func.count(Inventory.id)).filter(
            Inventory.is_low_stock == 1
        ).scalar() or 0
        
        return {
            "total_materials": total_materials,
            "total_inventory_value": float(total_value),
            "low_stock_count": low_stock_count
        }
    
    def get_low_stock_alerts(self, is_read: Optional[int] = None, is_handled: Optional[int] = None) -> List[dict]:
        """获取低库存预警列表"""
        query = self.db.query(
            StockAlert,
            Material.material_name,
            Material.material_type,
            Warehouse.warehouse_name
        ).join(
            Inventory, StockAlert.inventory_id == Inventory.id
        ).join(
            Material, Inventory.material_id == Material.id
        ).join(
            Warehouse, Inventory.warehouse_id == Warehouse.id
        )
        
        if is_read is not None:
            query = query.filter(StockAlert.is_read == is_read)
        if is_handled is not None:
            query = query.filter(StockAlert.is_handled == is_handled)
        
        results = query.order_by(StockAlert.created_at.desc()).all()
        
        alerts = []
        for alert, material_name, material_type, warehouse_name in results:
            alerts.append({
                "id": alert.id,
                "inventory_id": alert.inventory_id,
                "material_name": material_name,
                "material_type": material_type,
                "warehouse_name": warehouse_name,
                "alert_type": alert.alert_type,
                "threshold_value": alert.threshold_value,
                "current_value": alert.current_value,
                "message": alert.message,
                "is_read": alert.is_read,
                "is_handled": alert.is_handled,
                "created_at": alert.created_at
            })
        
        return alerts
