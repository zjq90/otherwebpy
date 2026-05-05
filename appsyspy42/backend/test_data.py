"""
测试数据生成脚本
功能：初始化数据库并生成测试数据，用于系统功能测试
包括：用户、供应商、原材料、料仓、库存、采购申请、供货记录、供应商评价等
"""
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models.models import (
    User, Supplier, Material, Warehouse, Inventory,
    PurchaseRequest, SupplyRecord, SupplierEvaluation, StockAlert
)
from app.services.auth_service import get_password_hash


def init_database():
    """
    初始化数据库
    删除所有表并重新创建（用于测试环境）
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("数据库初始化完成")


def create_test_users(db: Session):
    """
    创建测试用户
    包括管理员和采购员
    """
    admin = User(
        username="admin",
        password=get_password_hash("admin123"),
        real_name="系统管理员",
        role="管理员",
        phone="13800138000",
        email="admin@example.com",
        is_active=1
    )
    
    purchaser1 = User(
        username="purchaser",
        password=get_password_hash("purchaser123"),
        real_name="张三",
        role="采购员",
        phone="13800138001",
        email="zhangsan@example.com",
        is_active=1
    )
    
    purchaser2 = User(
        username="purchaser2",
        password=get_password_hash("purchaser2123"),
        real_name="李四",
        role="采购员",
        phone="13800138002",
        email="lisi@example.com",
        is_active=1
    )
    
    db.add_all([admin, purchaser1, purchaser2])
    db.commit()
    db.refresh(admin)
    db.refresh(purchaser1)
    db.refresh(purchaser2)
    
    print(f"创建测试用户：管理员(admin/admin123)、采购员(purchaser/purchaser123)、采购员(purchaser2/purchaser2123)")
    return admin, purchaser1, purchaser2


def create_test_suppliers(db: Session):
    """
    创建测试供应商
    """
    suppliers = [
        Supplier(
            supplier_name="华新水泥股份有限公司",
            contact_person="王经理",
            phone="13900139001",
            address="湖北省黄石市大棋大道298号",
            business_license="91420000178413138W",
            quality_rating=4.8,
            total_orders=156,
            total_amount=1256800.0,
            description="华新水泥是中国水泥行业的龙头企业，产品质量稳定可靠",
            is_active=1
        ),
        Supplier(
            supplier_name="中国建筑材料集团有限公司",
            contact_person="李总",
            phone="13900139002",
            address="北京市海淀区复兴路17号国海广场",
            business_license="91110000101830898X",
            quality_rating=4.9,
            total_orders=234,
            total_amount=2568000.0,
            description="中国建材集团是大型央企，产品种类齐全，服务完善",
            is_active=1
        ),
        Supplier(
            supplier_name="江苏沙钢集团有限公司",
            contact_person="张经理",
            phone="13900139003",
            address="江苏省苏州市张家港市锦丰镇",
            business_license="91320500711556571D",
            quality_rating=4.6,
            total_orders=89,
            total_amount=896500.0,
            description="沙钢集团是国内最大的民营钢铁企业，也是重要的建材供应商",
            is_active=1
        ),
        Supplier(
            supplier_name="海螺水泥股份有限公司",
            contact_person="赵总",
            phone="13900139004",
            address="安徽省芜湖市文化路39号",
            business_license="91340000149490386T",
            quality_rating=4.7,
            total_orders=178,
            total_amount=1456000.0,
            description="海螺水泥是亚太地区最大的水泥供应商，技术先进",
            is_active=1
        ),
        Supplier(
            supplier_name="东方雨虹防水技术股份有限公司",
            contact_person="陈经理",
            phone="13900139005",
            address="北京市顺义区顺平路沙岭段甲2号",
            business_license="911100007177421943",
            quality_rating=4.9,
            total_orders=45,
            total_amount=568000.0,
            description="东方雨虹专注于防水材料和外加剂，行业领先",
            is_active=1
        )
    ]
    
    db.add_all(suppliers)
    db.commit()
    
    for supplier in suppliers:
        db.refresh(supplier)
    
    print(f"创建测试供应商 {len(suppliers)} 家")
    return suppliers


def create_test_materials(db: Session):
    """
    创建测试原材料
    包括水泥、砂石、粉煤灰、外加剂四大类
    """
    materials = [
        Material(
            material_name="P.O 42.5普通硅酸盐水泥",
            material_type="水泥",
            specification="P.O 42.5",
            unit="吨",
            description="普通硅酸盐水泥，强度等级42.5，适用于一般建筑工程"
        ),
        Material(
            material_name="P.O 52.5普通硅酸盐水泥",
            material_type="水泥",
            specification="P.O 52.5",
            unit="吨",
            description="普通硅酸盐水泥，强度等级52.5，适用于高强度混凝土"
        ),
        Material(
            material_name="P.C 32.5复合硅酸盐水泥",
            material_type="水泥",
            specification="P.C 32.5",
            unit="吨",
            description="复合硅酸盐水泥，强度等级32.5，适用于一般建筑工程"
        ),
        Material(
            material_name="天然河砂（中砂）",
            material_type="砂石",
            specification="细度模数2.3-3.0",
            unit="立方米",
            description="天然河砂，中砂规格，适用于混凝土搅拌"
        ),
        Material(
            material_name="碎石（5-25mm）",
            material_type="砂石",
            specification="粒径5-25mm",
            unit="立方米",
            description="花岗岩碎石，连续级配，适用于混凝土搅拌"
        ),
        Material(
            material_name="碎石（16-31.5mm）",
            material_type="砂石",
            specification="粒径16-31.5mm",
            unit="立方米",
            description="花岗岩碎石，大粒径，适用于大体积混凝土"
        ),
        Material(
            material_name="Ⅰ级粉煤灰",
            material_type="粉煤灰",
            specification="Ⅰ级",
            unit="吨",
            description="Ⅰ级粉煤灰，细度高，活性好，适用于高性能混凝土"
        ),
        Material(
            material_name="Ⅱ级粉煤灰",
            material_type="粉煤灰",
            specification="Ⅱ级",
            unit="吨",
            description="Ⅱ级粉煤灰，适用于普通混凝土"
        ),
        Material(
            material_name="聚羧酸高效减水剂",
            material_type="外加剂",
            specification="PC-100",
            unit="吨",
            description="聚羧酸系高效减水剂，减水率高，适用于高强混凝土"
        ),
        Material(
            material_name="萘系高效减水剂",
            material_type="外加剂",
            specification="FDN",
            unit="吨",
            description="萘系高效减水剂，性价比高，适用于普通混凝土"
        ),
        Material(
            material_name="早强剂",
            material_type="外加剂",
            specification="早强型",
            unit="吨",
            description="混凝土早强剂，加快混凝土早期强度发展"
        ),
        Material(
            material_name="缓凝剂",
            material_type="外加剂",
            specification="缓凝型",
            unit="吨",
            description="混凝土缓凝剂，延长混凝土凝结时间"
        )
    ]
    
    db.add_all(materials)
    db.commit()
    
    for material in materials:
        db.refresh(material)
    
    print(f"创建测试原材料 {len(materials)} 种")
    return materials


def create_test_warehouses(db: Session):
    """
    创建测试料仓
    """
    warehouses = [
        Warehouse(
            warehouse_name="1号水泥料仓",
            location="厂区东侧",
            max_capacity=5000.0,
            current_usage=0,
            description="专门用于存储水泥的立式料仓，容量5000吨",
            is_active=1
        ),
        Warehouse(
            warehouse_name="2号水泥料仓",
            location="厂区东侧",
            max_capacity=5000.0,
            current_usage=0,
            description="专门用于存储水泥的立式料仓，容量5000吨",
            is_active=1
        ),
        Warehouse(
            warehouse_name="1号砂石料场",
            location="厂区南侧",
            max_capacity=20000.0,
            current_usage=0,
            description="露天砂石堆场，容量20000立方米",
            is_active=1
        ),
        Warehouse(
            warehouse_name="2号砂石料场",
            location="厂区南侧",
            max_capacity=15000.0,
            current_usage=0,
            description="露天砂石堆场，容量15000立方米",
            is_active=1
        ),
        Warehouse(
            warehouse_name="粉煤灰料仓",
            location="厂区北侧",
            max_capacity=3000.0,
            current_usage=0,
            description="粉煤灰专用立式料仓，容量3000吨",
            is_active=1
        ),
        Warehouse(
            warehouse_name="外加剂仓库",
            location="厂区西侧",
            max_capacity=1000.0,
            current_usage=0,
            description="外加剂专用室内仓库，容量1000吨",
            is_active=1
        )
    ]
    
    db.add_all(warehouses)
    db.commit()
    
    for warehouse in warehouses:
        db.refresh(warehouse)
    
    print(f"创建测试料仓 {len(warehouses)} 个")
    return warehouses


def create_test_inventory(db: Session, materials, warehouses):
    """
    创建测试库存数据
    """
    inventories = []
    
    now = datetime.now()
    
    # 水泥库存
    inventories.append(Inventory(
        material_id=materials[0].id,
        warehouse_id=warehouses[0].id,
        quantity=1500.0,
        safety_threshold=1000.0,
        unit_price=480.0,
        production_date=now - timedelta(days=5),
        expiry_date=now + timedelta(days=90),
        batch_number="CEM-20240101-001",
        is_low_stock=0
    ))
    
    inventories.append(Inventory(
        material_id=materials[1].id,
        warehouse_id=warehouses[1].id,
        quantity=800.0,
        safety_threshold=500.0,
        unit_price=520.0,
        production_date=now - timedelta(days=3),
        expiry_date=now + timedelta(days=90),
        batch_number="CEM-20240102-002",
        is_low_stock=0
    ))
    
    inventories.append(Inventory(
        material_id=materials[2].id,
        warehouse_id=warehouses[0].id,
        quantity=500.0,
        safety_threshold=800.0,
        unit_price=420.0,
        production_date=now - timedelta(days=15),
        expiry_date=now + timedelta(days=80),
        batch_number="CEM-20240103-003",
        is_low_stock=1
    ))
    
    # 砂石库存
    inventories.append(Inventory(
        material_id=materials[3].id,
        warehouse_id=warehouses[2].id,
        quantity=8000.0,
        safety_threshold=5000.0,
        unit_price=120.0,
        batch_number="SAND-20240101-001",
        is_low_stock=0
    ))
    
    inventories.append(Inventory(
        material_id=materials[4].id,
        warehouse_id=warehouses[2].id,
        quantity=6000.0,
        safety_threshold=4000.0,
        unit_price=130.0,
        batch_number="STONE-20240101-001",
        is_low_stock=0
    ))
    
    inventories.append(Inventory(
        material_id=materials[5].id,
        warehouse_id=warehouses[3].id,
        quantity=2000.0,
        safety_threshold=3000.0,
        unit_price=125.0,
        batch_number="STONE-20240102-002",
        is_low_stock=1
    ))
    
    # 粉煤灰库存
    inventories.append(Inventory(
        material_id=materials[6].id,
        warehouse_id=warehouses[4].id,
        quantity=1200.0,
        safety_threshold=800.0,
        unit_price=80.0,
        production_date=now - timedelta(days=20),
        expiry_date=now + timedelta(days=180),
        batch_number="FLY-20240101-001",
        is_low_stock=0
    ))
    
    inventories.append(Inventory(
        material_id=materials[7].id,
        warehouse_id=warehouses[4].id,
        quantity=400.0,
        safety_threshold=600.0,
        unit_price=65.0,
        production_date=now - timedelta(days=30),
        expiry_date=now + timedelta(days=170),
        batch_number="FLY-20240102-002",
        is_low_stock=1
    ))
    
    # 外加剂库存
    inventories.append(Inventory(
        material_id=materials[8].id,
        warehouse_id=warehouses[5].id,
        quantity=80.0,
        safety_threshold=100.0,
        unit_price=3500.0,
        production_date=now - timedelta(days=45),
        expiry_date=now + timedelta(days=365),
        batch_number="ADM-20240101-001",
        is_low_stock=1
    ))
    
    inventories.append(Inventory(
        material_id=materials[9].id,
        warehouse_id=warehouses[5].id,
        quantity=150.0,
        safety_threshold=80.0,
        unit_price=2800.0,
        production_date=now - timedelta(days=30),
        expiry_date=now + timedelta(days=365),
        batch_number="ADM-20240102-002",
        is_low_stock=0
    ))
    
    db.add_all(inventories)
    db.commit()
    
    for inv in inventories:
        db.refresh(inv)
    
    print(f"创建测试库存数据 {len(inventories)} 条")
    return inventories


def create_test_alerts(db: Session, inventories):
    """
    创建测试库存预警
    """
    now = datetime.now()
    
    alerts = []
    
    for inv in inventories:
        if inv.is_low_stock == 1:
            alerts.append(StockAlert(
                inventory_id=inv.id,
                alert_type="低库存",
                threshold_value=inv.safety_threshold,
                current_value=inv.quantity,
                message=f"库存预警：当前库存 {inv.quantity} 低于安全阈值 {inv.safety_threshold}",
                is_read=0,
                is_handled=0,
                created_at=now
            ))
    
    db.add_all(alerts)
    db.commit()
    
    print(f"创建测试库存预警 {len(alerts)} 条")
    return alerts


def create_test_purchase_requests(db: Session, users, materials):
    """
    创建测试采购申请
    """
    now = datetime.now()
    
    purchase_requests = [
        PurchaseRequest(
            request_no=f"PO{now.strftime('%Y%m%d')}001",
            material_id=materials[2].id,
            requested_by=users[1].id,
            quantity=2000.0,
            unit="吨",
            expected_delivery_date=now + timedelta(days=7),
            status="待审批",
            reason="库存预警：P.C 32.5水泥库存低于安全阈值，需要补充"
        ),
        PurchaseRequest(
            request_no=f"PO{now.strftime('%Y%m%d')}002",
            material_id=materials[5].id,
            requested_by=users[1].id,
            quantity=5000.0,
            unit="立方米",
            expected_delivery_date=now + timedelta(days=3),
            status="待审批",
            reason="生产计划需求：下月有大型项目需要大粒径碎石"
        ),
        PurchaseRequest(
            request_no=f"PO{now.strftime('%Y%m%d')}003",
            material_id=materials[7].id,
            requested_by=users[2].id,
            quantity=1500.0,
            unit="吨",
            expected_delivery_date=now + timedelta(days=5),
            status="已批准",
            reason="库存预警：Ⅱ级粉煤灰库存不足",
            approved_by=users[0].id,
            approval_time=now - timedelta(hours=2),
            approval_comment="同意采购，请尽快安排"
        ),
        PurchaseRequest(
            request_no=f"PO{now.strftime('%Y%m%d')}004",
            material_id=materials[8].id,
            requested_by=users[1].id,
            quantity=200.0,
            unit="吨",
            expected_delivery_date=now + timedelta(days=10),
            status="已拒绝",
            reason="库存预警：聚羧酸减水剂库存低",
            approved_by=users[0].id,
            approval_time=now - timedelta(days=1),
            approval_comment="库存还够用，请确认是否真的需要采购"
        ),
        PurchaseRequest(
            request_no=f"PO{now.strftime('%Y%m%d')}005",
            material_id=materials[0].id,
            requested_by=users[2].id,
            quantity=3000.0,
            unit="吨",
            expected_delivery_date=now - timedelta(days=2),
            status="已完成",
            reason="常规补充库存",
            approved_by=users[0].id,
            approval_time=now - timedelta(days=5),
            approval_comment="同意"
        )
    ]
    
    db.add_all(purchase_requests)
    db.commit()
    
    for pr in purchase_requests:
        db.refresh(pr)
    
    print(f"创建测试采购申请 {len(purchase_requests)} 条")
    return purchase_requests


def create_test_supply_records(db: Session, suppliers, materials, users):
    """
    创建测试供货记录
    """
    now = datetime.now()
    
    supply_records = [
        SupplyRecord(
            supplier_id=suppliers[0].id,
            material_id=materials[0].id,
            quantity=1000.0,
            unit_price=480.0,
            total_amount=480000.0,
            delivery_date=now - timedelta(days=30),
            quality_status="合格",
            batch_number="HX-20240101-001",
            remark="华新水泥供货，质量稳定"
        ),
        SupplyRecord(
            supplier_id=suppliers[0].id,
            material_id=materials[1].id,
            quantity=500.0,
            unit_price=520.0,
            total_amount=260000.0,
            delivery_date=now - timedelta(days=15),
            quality_status="合格",
            batch_number="HX-20240115-002",
            remark="华新水泥供货"
        ),
        SupplyRecord(
            supplier_id=suppliers[1].id,
            material_id=materials[3].id,
            quantity=3000.0,
            unit_price=120.0,
            total_amount=360000.0,
            delivery_date=now - timedelta(days=20),
            quality_status="合格",
            batch_number="CBMC-20240110-001",
            remark="中建材河砂供应"
        ),
        SupplyRecord(
            supplier_id=suppliers[1].id,
            material_id=materials[4].id,
            quantity=2500.0,
            unit_price=130.0,
            total_amount=325000.0,
            delivery_date=now - timedelta(days=10),
            quality_status="合格",
            batch_number="CBMC-20240120-002",
            remark="中建材碎石供应"
        ),
        SupplyRecord(
            supplier_id=suppliers[3].id,
            material_id=materials[6].id,
            quantity=800.0,
            unit_price=80.0,
            total_amount=64000.0,
            delivery_date=now - timedelta(days=25),
            quality_status="合格",
            batch_number="HL-20240105-001",
            remark="海螺粉煤灰供应"
        ),
        SupplyRecord(
            supplier_id=suppliers[4].id,
            material_id=materials[8].id,
            quantity=100.0,
            unit_price=3500.0,
            total_amount=350000.0,
            delivery_date=now - timedelta(days=40),
            quality_status="合格",
            batch_number="DFYH-20240101-001",
            remark="东方雨虹聚羧酸减水剂供应"
        )
    ]
    
    db.add_all(supply_records)
    db.commit()
    
    print(f"创建测试供货记录 {len(supply_records)} 条")
    return supply_records


def create_test_evaluations(db: Session, suppliers, users):
    """
    创建测试供应商评价
    """
    now = datetime.now()
    
    evaluations = [
        SupplierEvaluation(
            supplier_id=suppliers[0].id,
            evaluated_by=users[1].id,
            quality_score=5.0,
            delivery_score=4.5,
            price_score=4.0,
            service_score=4.5,
            total_score=4.5,
            comment="华新水泥质量稳定可靠，交货及时，价格合理，是长期合作的优质供应商。",
            evaluation_date=now - timedelta(days=10)
        ),
        SupplierEvaluation(
            supplier_id=suppliers[0].id,
            evaluated_by=users[2].id,
            quality_score=4.5,
            delivery_score=5.0,
            price_score=4.5,
            service_score=5.0,
            total_score=4.75,
            comment="服务态度很好，有问题能及时响应。",
            evaluation_date=now - timedelta(days=5)
        ),
        SupplierEvaluation(
            supplier_id=suppliers[1].id,
            evaluated_by=users[1].id,
            quality_score=4.8,
            delivery_score=4.2,
            price_score=4.5,
            service_score=4.0,
            total_score=4.375,
            comment="中建材作为央企，质量有保障，但是服务响应速度一般。",
            evaluation_date=now - timedelta(days=15)
        ),
        SupplierEvaluation(
            supplier_id=suppliers[3].id,
            evaluated_by=users[2].id,
            quality_score=4.5,
            delivery_score=4.0,
            price_score=4.8,
            service_score=4.2,
            total_score=4.375,
            comment="价格有竞争力，粉煤灰质量稳定。",
            evaluation_date=now - timedelta(days=20)
        ),
        SupplierEvaluation(
            supplier_id=suppliers[4].id,
            evaluated_by=users[1].id,
            quality_score=5.0,
            delivery_score=5.0,
            price_score=4.0,
            service_score=5.0,
            total_score=4.75,
            comment="东方雨虹的外加剂质量一流，专业服务好，就是价格稍高。",
            evaluation_date=now - timedelta(days=25)
        )
    ]
    
    db.add_all(evaluations)
    db.commit()
    
    print(f"创建测试供应商评价 {len(evaluations)} 条")
    return evaluations


def main():
    """
    主函数：执行测试数据生成
    """
    print("=" * 60)
    print("库存管理系统 - 测试数据生成")
    print("=" * 60)
    
    # 初始化数据库
    init_database()
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 创建测试数据
        print("\n开始创建测试数据...\n")
        
        # 用户
        users = create_test_users(db)
        
        # 供应商
        suppliers = create_test_suppliers(db)
        
        # 原材料
        materials = create_test_materials(db)
        
        # 料仓
        warehouses = create_test_warehouses(db)
        
        # 库存
        inventories = create_test_inventory(db, materials, warehouses)
        
        # 库存预警
        alerts = create_test_alerts(db, inventories)
        
        # 采购申请
        purchase_requests = create_test_purchase_requests(db, users, materials)
        
        # 供货记录
        supply_records = create_test_supply_records(db, suppliers, materials, users)
        
        # 供应商评价
        evaluations = create_test_evaluations(db, suppliers, users)
        
        print("\n" + "=" * 60)
        print("测试数据生成完成！")
        print("=" * 60)
        print("\n测试账号信息：")
        print(f"  管理员账号：admin / admin123")
        print(f"  采购员账号：purchaser / purchaser123")
        print(f"  采购员账号：purchaser2 / purchaser2123")
        print("\n数据统计：")
        print(f"  - 用户数：{db.query(User).count()}")
        print(f"  - 供应商数：{db.query(Supplier).count()}")
        print(f"  - 原材料数：{db.query(Material).count()}")
        print(f"  - 料仓数：{db.query(Warehouse).count()}")
        print(f"  - 库存记录数：{db.query(Inventory).count()}")
        print(f"  - 库存预警数：{db.query(StockAlert).count()}")
        print(f"  - 采购申请数：{db.query(PurchaseRequest).count()}")
        print(f"  - 供货记录数：{db.query(SupplyRecord).count()}")
        print(f"  - 供应商评价数：{db.query(SupplierEvaluation).count()}")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
