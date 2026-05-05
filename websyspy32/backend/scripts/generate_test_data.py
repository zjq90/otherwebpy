import sys
import os
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base, SessionLocal
from app.models import (
    Silo, InventoryRecord, ProductionPlan, MaterialDemand,
    Supplier, SupplierRating, PurchaseOrder, Settlement
)

def generate_test_data():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    
    try:
        print("开始生成测试数据...")
        
        silos_data = [
            {"name": "水泥仓1号", "material_type": "水泥", "capacity": 500.0, "current_level": 150.0, "min_threshold": 50.0, "unit": "吨"},
            {"name": "水泥仓2号", "material_type": "水泥", "capacity": 500.0, "current_level": 80.0, "min_threshold": 50.0, "unit": "吨"},
            {"name": "砂石仓1号", "material_type": "砂石", "capacity": 800.0, "current_level": 200.0, "min_threshold": 80.0, "unit": "吨"},
            {"name": "砂石仓2号", "material_type": "砂石", "capacity": 800.0, "current_level": 60.0, "min_threshold": 80.0, "unit": "吨"},
            {"name": "粉煤灰仓", "material_type": "粉煤灰", "capacity": 200.0, "current_level": 30.0, "min_threshold": 20.0, "unit": "吨"},
            {"name": "外加剂罐", "material_type": "外加剂", "capacity": 50.0, "current_level": 15.0, "min_threshold": 5.0, "unit": "吨"},
        ]
        
        for silo_data in silos_data:
            silo = Silo(**silo_data)
            if silo.current_level <= silo.min_threshold:
                silo.status = "低库存"
            else:
                silo.status = "正常"
            db.add(silo)
        
        db.commit()
        print("已创建料仓数据: 6个料仓")
        
        suppliers_data = [
            {"name": "华强建材有限公司", "contact_person": "张经理", "contact_phone": "13800138001", 
             "address": "华强市工业园区", "material_types": "水泥,砂石", "overall_rating": 8.5, "status": "合作中"},
            {"name": "鑫源材料公司", "contact_person": "李总", "contact_phone": "13800138002",
             "address": "鑫源市建材路88号", "material_types": "粉煤灰,水泥", "overall_rating": 7.2, "status": "合作中"},
            {"name": "高科外加剂厂", "contact_person": "王工", "contact_phone": "13800138003",
             "address": "高开区科技大道", "material_types": "外加剂", "overall_rating": 9.1, "status": "合作中"},
            {"name": "顺达砂石场", "contact_person": "赵场长", "contact_phone": "13800138004",
             "address": "顺达县矿区", "material_types": "砂石", "overall_rating": 6.8, "status": "暂停合作"},
        ]
        
        for supplier_data in suppliers_data:
            supplier = Supplier(**supplier_data)
            db.add(supplier)
        
        db.commit()
        print("已创建供应商数据: 4个供应商")
        
        suppliers = db.query(Supplier).all()
        today = date.today()
        
        for i, supplier in enumerate(suppliers):
            rating_date = today - timedelta(days=(i + 1) * 7)
            ratings_data = [
                {
                    "supplier_id": supplier.id,
                    "rating_date": rating_date,
                    "delivery_score": 8.0 + i,
                    "quality_score": 7.5 + i * 0.5,
                    "price_score": 7.0,
                    "service_score": 7.5,
                    "total_score": 0.0,
                    "comment": f"{supplier.name} 综合评价良好",
                    "evaluator": "系统管理员"
                }
            ]
            
            for rating_data in ratings_data:
                total_score = (rating_data["delivery_score"] * 0.35 + 
                              rating_data["quality_score"] * 0.35 + 
                              rating_data["price_score"] * 0.15 + 
                              rating_data["service_score"] * 0.15)
                rating_data["total_score"] = round(total_score, 2)
                rating = SupplierRating(**rating_data)
                db.add(rating)
        
        db.commit()
        print("已创建供应商评级数据")
        
        plans_data = [
            {
                "plan_name": "5月市政工程批次1",
                "plan_date": today,
                "concrete_volume": 500.0,
                "concrete_grade": "C30",
                "status": "执行中",
                "description": "市政道路建设项目，需C30混凝土500方"
            },
            {
                "plan_name": "5月商业楼项目",
                "plan_date": today + timedelta(days=2),
                "concrete_volume": 800.0,
                "concrete_grade": "C50",
                "status": "待执行",
                "description": "商业综合楼建设，需高强度C50混凝土"
            },
            {
                "plan_name": "小区配套工程",
                "plan_date": today - timedelta(days=1),
                "concrete_volume": 300.0,
                "concrete_grade": "C25",
                "status": "已完成",
                "description": "小区配套设施建设，已完成"
            }
        ]
        
        for plan_data in plans_data:
            plan = ProductionPlan(**plan_data)
            db.add(plan)
        
        db.commit()
        print("已创建生产计划数据: 3个生产计划")
        
        consumption_rates = {
            "水泥": 0.35,
            "砂石": 1.8,
            "粉煤灰": 0.08,
            "外加剂": 0.012,
            "水": 0.18
        }
        
        plans = db.query(ProductionPlan).all()
        silos = db.query(Silo).all()
        
        for plan in plans:
            for material_type, rate in consumption_rates.items():
                material_silos = [s for s in silos if s.material_type == material_type]
                total_stock = sum(s.current_level for s in material_silos)
                
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
                    status="待处理" if (shortage > 0 and plan.status != "已完成") else "已满足"
                )
                db.add(demand)
        
        db.commit()
        print("已创建物料需求预测数据")
        
        active_suppliers = db.query(Supplier).filter(Supplier.status == "合作中").all()
        
        order_date_1 = today - timedelta(days=5)
        order1 = PurchaseOrder(
            order_no=f"PO{order_date_1.strftime('%Y%m%d')}001",
            supplier_id=active_suppliers[0].id,
            material_type="水泥",
            quantity=200.0,
            unit_price=450.0,
            total_amount=90000.0,
            order_date=order_date_1,
            delivery_date=order_date_1 + timedelta(days=3),
            actual_delivery_date=order_date_1 + timedelta(days=2),
            status="已完成",
            remark="市政工程补充采购"
        )
        db.add(order1)
        
        order2 = PurchaseOrder(
            order_no=f"PO{today.strftime('%Y%m%d')}001",
            supplier_id=active_suppliers[0].id,
            material_type="砂石",
            quantity=300.0,
            unit_price=80.0,
            total_amount=24000.0,
            order_date=today,
            delivery_date=today + timedelta(days=2),
            status="待发货",
            remark="商业楼项目备货"
        )
        db.add(order2)
        
        order3 = PurchaseOrder(
            order_no=f"PO{today.strftime('%Y%m%d')}002",
            supplier_id=active_suppliers[2].id,
            material_type="外加剂",
            quantity=10.0,
            unit_price=2500.0,
            total_amount=25000.0,
            order_date=today - timedelta(days=1),
            delivery_date=today + timedelta(days=1),
            status="已发货",
            remark="紧急补货"
        )
        db.add(order3)
        
        db.commit()
        print("已创建采购订单数据: 3个采购订单")
        
        orders = db.query(PurchaseOrder).all()
        for order in orders:
            if order.status == "已完成":
                settlement = Settlement(
                    settlement_no=f"SET{order.order_date.strftime('%Y%m%d')}001",
                    purchase_order_id=order.id,
                    settlement_date=order.actual_delivery_date or order.delivery_date,
                    material_type=order.material_type,
                    quantity=order.quantity,
                    unit_price=order.unit_price,
                    total_amount=order.total_amount,
                    tax_rate=0.13,
                    tax_amount=order.total_amount * 0.13,
                    total_payable=order.total_amount * 1.13,
                    payment_status="部分付款",
                    paid_amount=order.total_amount * 0.5 * 1.13,
                    remark="已支付50%预付款"
                )
                db.add(settlement)
        
        db.commit()
        print("已创建结算单数据")
        
        for silo in silos:
            if silo.material_type == "水泥" and silo.current_level > 100:
                record = InventoryRecord(
                    silo_id=silo.id,
                    change_type="出库",
                    quantity=50.0,
                    balance_before=silo.current_level + 50.0,
                    balance_after=silo.current_level,
                    reason="生产消耗",
                    operator="系统",
                    record_time=datetime.now() - timedelta(hours=8)
                )
                db.add(record)
                
                record2 = InventoryRecord(
                    silo_id=silo.id,
                    change_type="入库",
                    quantity=100.0,
                    balance_before=silo.current_level,
                    balance_after=silo.current_level + 100.0,
                    reason="采购到货",
                    operator="张仓管",
                    record_time=datetime.now() - timedelta(days=2)
                )
                db.add(record2)
        
        db.commit()
        print("已创建库存变更记录")
        
        print("\n" + "="*50)
        print("测试数据生成完成!")
        print("="*50)
        print("\n生成的数据概览:")
        print(f"  - 料仓: {db.query(Silo).count()} 个")
        print(f"  - 供应商: {db.query(Supplier).count()} 个")
        print(f"  - 生产计划: {db.query(ProductionPlan).count()} 个")
        print(f"  - 物料需求: {db.query(MaterialDemand).count()} 条")
        print(f"  - 采购订单: {db.query(PurchaseOrder).count()} 个")
        print(f"  - 结算单: {db.query(Settlement).count()} 个")
        
    except Exception as e:
        db.rollback()
        print(f"生成测试数据失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def clear_all_data():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    
    try:
        print("正在清除所有数据...")
        
        db.query(InventoryRecord).delete()
        db.query(MaterialDemand).delete()
        db.query(Settlement).delete()
        db.query(PurchaseOrder).delete()
        db.query(SupplierRating).delete()
        db.query(Supplier).delete()
        db.query(ProductionPlan).delete()
        db.query(Silo).delete()
        
        db.commit()
        print("所有数据已清除")
    except Exception as e:
        db.rollback()
        print(f"清除数据失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="测试数据管理工具")
    parser.add_argument("--action", choices=["generate", "clear", "reset"], default="generate",
                        help="操作类型: generate(生成数据), clear(清除数据), reset(重置数据)")
    
    args = parser.parse_args()
    
    if args.action == "generate":
        generate_test_data()
    elif args.action == "clear":
        clear_all_data()
    elif args.action == "reset":
        clear_all_data()
        generate_test_data()
