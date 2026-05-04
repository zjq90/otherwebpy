"""
测试数据生成工具
用于生成物业管理系统的测试数据
"""

import random
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List

from faker import Faker
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import (
    Base,
    FeeItem,
    Property,
    Bill,
    PaymentRecord,
    Reminder,
    Invoice,
)
from app.schemas import BillStatus, PaymentMethod, ReminderMethod, InvoiceStatus, InvoiceType

fake = Faker("zh_CN")


def generate_fee_items(db: Session) -> List[FeeItem]:
    """
    生成默认的费用项目
    
    包括：物业费、停车费、水电公摊、维修基金等
    """
    fee_items_data = [
        {
            "name": "物业管理费",
            "code": "PROPERTY_FEE",
            "description": "按照房屋建筑面积计算的物业管理服务费",
            "billing_cycle": "monthly",
            "billing_type": "area",
            "unit_price": Decimal("2.5"),
        },
        {
            "name": "停车费",
            "code": "PARKING_FEE",
            "description": "小区停车位月租费用",
            "billing_cycle": "monthly",
            "billing_type": "fixed",
            "unit_price": Decimal("300.00"),
        },
        {
            "name": "水电公摊费",
            "code": "UTILITY_FEE",
            "description": "公共区域水电费用公摊",
            "billing_cycle": "monthly",
            "billing_type": "area",
            "unit_price": Decimal("0.5"),
        },
        {
            "name": "维修基金",
            "code": "MAINTENANCE_FUND",
            "description": "住宅专项维修资金",
            "billing_cycle": "yearly",
            "billing_type": "area",
            "unit_price": Decimal("10.00"),
        },
        {
            "name": "电梯使用费",
            "code": "ELEVATOR_FEE",
            "description": "电梯日常运行和维护费用",
            "billing_cycle": "monthly",
            "billing_type": "fixed",
            "unit_price": Decimal("50.00"),
        },
        {
            "name": "垃圾清运费",
            "code": "GARBAGE_FEE",
            "description": "生活垃圾清运处理费用",
            "billing_cycle": "monthly",
            "billing_type": "fixed",
            "unit_price": Decimal("20.00"),
        },
    ]
    
    fee_items = []
    for data in fee_items_data:
        existing = db.query(FeeItem).filter(FeeItem.code == data["code"]).first()
        if not existing:
            fee_item = FeeItem(**data)
            db.add(fee_item)
            fee_items.append(fee_item)
    
    db.commit()
    
    # 重新查询获取所有费用项目
    all_fee_items = db.query(FeeItem).filter(FeeItem.is_active == True).all()
    return all_fee_items


def generate_properties(db: Session, count: int = 50) -> List[Property]:
    """
    生成房产测试数据
    
    参数:
        count: 生成的房产数量
    """
    buildings = ["1号楼", "2号楼", "3号楼", "4号楼", "5号楼", "6号楼", "7号楼", "8号楼"]
    units = ["1单元", "2单元", "3单元"]
    
    properties = []
    for i in range(count):
        building = random.choice(buildings)
        unit = random.choice(units)
        floor = random.randint(1, 30)
        room = random.randint(1, 4)
        room_number = f"{floor:02d}{room:02d}"
        
        # 生成房产编号
        property_number = f"{building[:-2]}-{unit[:-2]}-{room_number}"
        
        # 面积 50-200 平方米
        area = Decimal(str(round(random.uniform(50, 200), 2)))
        
        # 房产类型
        property_types = ["住宅", "商铺", "车位", "写字楼"]
        property_type = random.choice(property_types)
        
        # 业主信息
        owner_name = fake.name()
        owner_phone = fake.phone_number()
        owner_id_card = fake.ssn()
        
        # 入住日期（过去1-5年内随机）
        move_in_days = random.randint(30, 1825)
        move_in_date = date.today() - timedelta(days=move_in_days)
        
        property_data = Property(
            property_number=property_number,
            building=building,
            unit=unit,
            room_number=room_number,
            area=area,
            property_type=property_type,
            owner_name=owner_name,
            owner_phone=owner_phone,
            owner_id_card=owner_id_card,
            is_occupied=random.choice([True, True, True, False]),
            move_in_date=move_in_date,
            is_active=True,
            remark=fake.text(max_nb_chars=50) if random.random() > 0.7 else None,
        )
        
        db.add(property_data)
        properties.append(property_data)
    
    db.commit()
    return properties


def calculate_bill_amount(property_obj: Property, fee_item: FeeItem) -> Decimal:
    """计算账单金额"""
    if fee_item.billing_type == "area":
        return property_obj.area * fee_item.unit_price
    elif fee_item.billing_type == "unit":
        return fee_item.unit_price
    elif fee_item.billing_type == "fixed":
        return fee_item.unit_price
    return Decimal(0)


def generate_bills(
    db: Session,
    properties: List[Property],
    fee_items: List[FeeItem],
    months_count: int = 6
) -> List[Bill]:
    """
    生成账单测试数据
    
    参数:
        properties: 房产列表
        fee_items: 费用项目列表
        months_count: 生成过去多少个月的账单
    """
    today = date.today()
    bills = []
    
    for month_offset in range(months_count):
        # 计算账单月份
        months_ago = months_count - 1 - month_offset
        bill_date = today - timedelta(days=months_ago * 30)
        billing_year = bill_date.year
        billing_month = bill_date.month
        
        for property_obj in properties:
            # 只对已入住的房产生成账单
            if not property_obj.is_occupied:
                continue
            
            for fee_item in fee_items:
                # 检查是否已存在该账单
                existing = db.query(Bill).filter(
                    Bill.property_id == property_obj.id,
                    Bill.fee_item_id == fee_item.id,
                    Bill.billing_year == billing_year,
                    Bill.billing_month == billing_month
                ).first()
                
                if existing:
                    continue
                
                # 计算金额
                amount = calculate_bill_amount(property_obj, fee_item)
                
                # 生成账单编号
                bill_number = f"B{billing_year:04d}{billing_month:02d}{property_obj.id:06d}{fee_item.id:04d}{datetime.now().strftime('%H%M%S')}"
                
                # 缴费截止日期（当月25号）
                try:
                    due_date = date(billing_year, billing_month, 25)
                except ValueError:
                    due_date = date(billing_year, billing_month, 28)
                
                # 随机决定账单状态
                status_choices = [
                    BillStatus.PAID.value,
                    BillStatus.PAID.value,
                    BillStatus.PAID.value,
                    BillStatus.PENDING.value,
                    BillStatus.OVERDUE.value,
                ]
                status = random.choice(status_choices)
                
                # 对于已支付的账单，设置支付时间和金额
                paid_amount = amount if status == BillStatus.PAID.value else Decimal(0)
                paid_at = None
                
                if status == BillStatus.PAID.value:
                    # 支付时间在截止日期前后随机
                    paid_days = random.randint(-10, 30)
                    paid_at = datetime.combine(due_date, datetime.min.time()) + timedelta(days=paid_days)
                
                bill = Bill(
                    bill_number=bill_number,
                    property_id=property_obj.id,
                    fee_item_id=fee_item.id,
                    billing_year=billing_year,
                    billing_month=billing_month,
                    amount=amount,
                    paid_amount=paid_amount,
                    status=status,
                    due_date=due_date,
                    generated_at=datetime.now() - timedelta(days=random.randint(0, 10)),
                    paid_at=paid_at,
                    payment_method=random.choice([m.value for m in PaymentMethod]) if status == BillStatus.PAID.value else None,
                )
                
                db.add(bill)
                bills.append(bill)
    
    db.commit()
    return bills


def generate_payment_records(db: Session, bills: List[Bill]) -> List[PaymentRecord]:
    """
    生成缴费记录测试数据
    """
    payment_records = []
    
    for bill in bills:
        if bill.status != BillStatus.PAID.value:
            continue
        
        # 生成缴费记录编号
        record_number = f"R{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
        
        record = PaymentRecord(
            record_number=record_number,
            bill_id=bill.id,
            amount=bill.amount,
            payment_method=bill.payment_method or PaymentMethod.CASH.value,
            transaction_id=fake.uuid4() if bill.payment_method != PaymentMethod.CASH.value else None,
            paid_at=bill.paid_at or datetime.now(),
            collector=fake.name() if random.random() > 0.5 else None,
        )
        
        db.add(record)
        payment_records.append(record)
    
    db.commit()
    return payment_records


def generate_reminders(db: Session, bills: List[Bill]) -> List[Reminder]:
    """
    生成催缴记录测试数据
    """
    reminders = []
    
    overdue_bills = [b for b in bills if b.status == BillStatus.OVERDUE.value]
    
    for bill in overdue_bills:
        # 随机生成1-3次催缴记录
        reminder_count = random.randint(1, 3)
        
        for i in range(reminder_count):
            # 催缴内容
            content = (
                f"催缴通知单\n"
                f"业主: {bill.property.owner_name if bill.property else '未知'}\n"
                f"房产: {bill.property.property_number if bill.property else '未知'}\n"
                f"费用项目: {bill.fee_item.name if bill.fee_item else '未知'}\n"
                f"应缴金额: {bill.amount}元\n"
                f"已缴金额: {bill.paid_amount}元\n"
                f"待缴金额: {bill.amount - bill.paid_amount}元\n"
                f"缴费截止日期: {bill.due_date}\n\n"
                f"请尽快缴费，感谢您的配合！\n"
                f"催缴次数: 第{i + 1}次"
            )
            
            reminder = Reminder(
                bill_id=bill.id,
                method=random.choice([m.value for m in ReminderMethod]),
                reminder_count=i + 1,
                content=content,
                operator=fake.name() if random.random() > 0.5 else None,
                reminded_at=datetime.now() - timedelta(days=random.randint(1, 30)),
            )
            
            db.add(reminder)
            reminders.append(reminder)
    
    db.commit()
    return reminders


def generate_invoices(db: Session, bills: List[Bill]) -> List[Invoice]:
    """
    生成票据测试数据
    """
    invoices = []
    
    paid_bills = [b for b in bills if b.status == BillStatus.PAID.value]
    
    for bill in paid_bills:
        # 80%的已支付账单有票据
        if random.random() > 0.8:
            continue
        
        # 生成票据编号
        invoice_number = f"INV{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        # 票据类型
        invoice_type = random.choice([InvoiceStatus.ISSUED.value, InvoiceType.RECEIPT.value])
        if invoice_type == InvoiceType.INVOICE.value:
            invoice_title = fake.company()
            tax_number = fake.ssn()
        else:
            invoice_title = None
            tax_number = None
        
        invoice = Invoice(
            invoice_number=invoice_number,
            bill_id=bill.id,
            invoice_type=invoice_type,
            amount=bill.amount,
            invoice_title=invoice_title,
            tax_number=tax_number,
            issued_at=bill.paid_at or datetime.now(),
            issuer=fake.name() if random.random() > 0.3 else None,
            status=InvoiceStatus.ISSUED.value,
        )
        
        db.add(invoice)
        invoices.append(invoice)
    
    db.commit()
    return invoices


def generate_all_test_data(property_count: int = 50, months_count: int = 6):
    """
    生成所有测试数据
    
    参数:
        property_count: 生成的房产数量
        months_count: 生成过去多少个月的账单
    """
    db = SessionLocal()
    
    try:
        print("正在初始化数据库...")
        Base.metadata.create_all(bind=engine)
        
        print("正在生成费用项目数据...")
        fee_items = generate_fee_items(db)
        print(f"已生成 {len(fee_items)} 个费用项目")
        
        print(f"正在生成房产数据 ({property_count} 个)...")
        properties = generate_properties(db, property_count)
        print(f"已生成 {len(properties)} 个房产")
        
        print(f"正在生成账单数据 (过去 {months_count} 个月)...")
        bills = generate_bills(db, properties, fee_items, months_count)
        print(f"已生成 {len(bills)} 个账单")
        
        print("正在生成缴费记录数据...")
        payment_records = generate_payment_records(db, bills)
        print(f"已生成 {len(payment_records)} 条缴费记录")
        
        print("正在生成催缴记录数据...")
        reminders = generate_reminders(db, bills)
        print(f"已生成 {len(reminders)} 条催缴记录")
        
        print("正在生成票据数据...")
        invoices = generate_invoices(db, bills)
        print(f"已生成 {len(invoices)} 张票据")
        
        print("\n测试数据生成完成！")
        print(f"========================================")
        print(f"费用项目: {len(fee_items)} 个")
        print(f"房产信息: {len(properties)} 个")
        print(f"账单记录: {len(bills)} 个")
        print(f"缴费记录: {len(payment_records)} 条")
        print(f"催缴记录: {len(reminders)} 条")
        print(f"票据记录: {len(invoices)} 张")
        print(f"========================================")
        
    except Exception as e:
        print(f"生成测试数据时发生错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    generate_all_test_data(property_count=50, months_count=6)
