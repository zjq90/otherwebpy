from app.database import SessionLocal, engine, Base
from app.models import (
    Product, Customer, Order, OrderItem, Contract,
    Logistics, LogisticsTrack, PurchaseHistory, Feedback
)
from datetime import date, datetime, timedelta
from decimal import Decimal
import random

def generate_products(db):
    products_data = [
        {
            "name": "有机大米",
            "specification": "5kg/袋",
            "grade": "特级",
            "production_date": date.today() - timedelta(days=30),
            "shelf_life": 180,
            "suggested_retail_price": Decimal("88.00")
        },
        {
            "name": "新鲜苹果",
            "specification": "10斤/箱",
            "grade": "一级",
            "production_date": date.today() - timedelta(days=5),
            "shelf_life": 30,
            "suggested_retail_price": Decimal("68.00")
        },
        {
            "name": "土鸡蛋",
            "specification": "30枚/盒",
            "grade": "特级",
            "production_date": date.today() - timedelta(days=3),
            "shelf_life": 45,
            "suggested_retail_price": Decimal("45.00")
        },
        {
            "name": "有机蔬菜套餐",
            "specification": "5kg/箱",
            "grade": "一级",
            "production_date": date.today() - timedelta(days=2),
            "shelf_life": 15,
            "suggested_retail_price": Decimal("128.00")
        },
        {
            "name": "散养土鸡",
            "specification": "2-3斤/只",
            "grade": "特级",
            "production_date": date.today() - timedelta(days=1),
            "shelf_life": 7,
            "suggested_retail_price": Decimal("158.00")
        },
        {
            "name": "绿色白菜",
            "specification": "2棵/份",
            "grade": "二级",
            "production_date": date.today() - timedelta(days=1),
            "shelf_life": 10,
            "suggested_retail_price": Decimal("15.00")
        },
        {
            "name": "有机西红柿",
            "specification": "2kg/盒",
            "grade": "一级",
            "production_date": date.today() - timedelta(days=2),
            "shelf_life": 14,
            "suggested_retail_price": Decimal("35.00")
        },
        {
            "name": "农家蜂蜜",
            "specification": "500g/瓶",
            "grade": "特级",
            "production_date": date.today() - timedelta(days=60),
            "shelf_life": 365,
            "suggested_retail_price": Decimal("98.00")
        }
    ]
    
    for product_data in products_data:
        product = Product(**product_data)
        db.add(product)
    
    db.commit()
    print(f"已生成 {len(products_data)} 个产品测试数据")

def generate_customers(db):
    customers_data = [
        {
            "name": "北京华联超市",
            "phone": "010-88888888",
            "email": "contact@hualian.com",
            "address": "北京市朝阳区建国路88号",
            "contact_person": "张经理",
            "preferences": "偏好有机产品，经常采购大米、鸡蛋、蔬菜",
            "status": "active"
        },
        {
            "name": "上海物美超市",
            "phone": "021-66666666",
            "email": "shanghai@wumei.com",
            "address": "上海市浦东新区张江高科技园区",
            "contact_person": "李总",
            "preferences": "偏好新鲜水果和蔬菜",
            "status": "active"
        },
        {
            "name": "广州百佳超市",
            "phone": "020-55555555",
            "email": "guangzhou@baijia.com",
            "address": "广州市天河区体育西路",
            "contact_person": "王经理",
            "preferences": "偏好土鸡、土鸡蛋等农家产品",
            "status": "active"
        },
        {
            "name": "深圳天虹商场",
            "phone": "0755-77777777",
            "email": "shenzhen@tianhong.com",
            "address": "深圳市南山区科技园",
            "contact_person": "陈主管",
            "preferences": "偏好有机蔬菜和蜂蜜",
            "status": "active"
        },
        {
            "name": "杭州世纪联华",
            "phone": "0571-99999999",
            "email": "hangzhou@lianhu.com",
            "address": "杭州市西湖区文三路",
            "contact_person": "刘经理",
            "preferences": "偏好新鲜水果和大米",
            "status": "inactive"
        }
    ]
    
    for customer_data in customers_data:
        customer = Customer(**customer_data)
        db.add(customer)
    
    db.commit()
    print(f"已生成 {len(customers_data)} 个客户测试数据")

def generate_orders(db):
    products = db.query(Product).all()
    customers = db.query(Customer).all()
    
    if not products or not customers:
        print("没有足够的产品或客户数据")
        return
    
    orders_count = 0
    for i in range(5):
        customer = random.choice(customers)
        order_date = date.today() - timedelta(days=random.randint(1, 30))
        
        num_items = random.randint(1, 3)
        selected_products = random.sample(products, min(num_items, len(products)))
        
        total_amount = Decimal("0")
        items_data = []
        
        for product in selected_products:
            quantity = random.randint(10, 100)
            unit_price = product.suggested_retail_price
            subtotal = unit_price * Decimal(quantity)
            total_amount += subtotal
            
            items_data.append({
                "product_id": product.id,
                "product_name": product.name,
                "quantity": quantity,
                "unit_price": unit_price,
                "subtotal": subtotal
            })
        
        shipping_statuses = ["pending", "shipped", "delivered"]
        shipping_status = random.choice(shipping_statuses)
        
        order = Order(
            customer_id=customer.id,
            customer_name=customer.name,
            customer_phone=customer.phone,
            order_date=order_date,
            total_amount=total_amount,
            shipping_status=shipping_status,
            estimated_delivery_date=order_date + timedelta(days=3)
        )
        db.add(order)
        db.flush()
        
        for item_data in items_data:
            item = OrderItem(
                order_id=order.id,
                **item_data
            )
            db.add(item)
            
            purchase_history = PurchaseHistory(
                customer_id=customer.id,
                order_id=order.id,
                product_id=item_data["product_id"],
                product_name=item_data["product_name"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                purchase_date=order_date
            )
            db.add(purchase_history)
        
        orders_count += 1
    
    db.commit()
    print(f"已生成 {orders_count} 个订单测试数据")

def generate_contracts(db):
    orders = db.query(Order).all()
    
    contracts_count = 0
    for i, order in enumerate(orders[:3]):
        contract = Contract(
            order_id=order.id,
            contract_number=f"HT{date.today().strftime('%Y%m%d')}{str(i+1).zfill(3)}",
            contract_date=order.order_date,
            party_a="农产品电商管理系统",
            party_b=order.customer_name,
            contract_content=f"""农产品采购合同

甲方：农产品电商管理系统
乙方：{order.customer_name}

一、产品信息
甲方向乙方供应农产品，具体产品详见订单号：#{order.id}。

二、价格与支付
订单总金额：人民币{order.total_amount}元整。

三、交货方式
甲方负责安排物流配送，预计交货日期：{order.estimated_delivery_date}。

四、质量保证
甲方保证所供农产品质量符合国家标准，新鲜无变质。

五、违约责任
双方应严格履行合同义务，如有违约，应承担相应责任。

六、其他
本合同一式两份，双方各执一份，具有同等法律效力。
""",
            status="signed" if order.shipping_status == "delivered" else "draft",
            signed_date=order.order_date if order.shipping_status == "delivered" else None
        )
        db.add(contract)
        contracts_count += 1
    
    db.commit()
    print(f"已生成 {contracts_count} 个合同测试数据")

def generate_logistics(db):
    orders = db.query(Order).filter(Order.shipping_status != "pending").all()
    
    logistics_companies = ["顺丰速运", "京东物流", "中通快递", "圆通速递", "申通快递"]
    logistics_count = 0
    
    for i, order in enumerate(orders):
        logistics = Logistics(
            order_id=order.id,
            tracking_number=f"SF{datetime.now().strftime('%Y%m%d%H%M%S')}{str(i+1).zfill(4)}",
            logistics_company=random.choice(logistics_companies),
            current_status="已签收" if order.shipping_status == "delivered" else "运输中",
            current_location="北京市朝阳区" if order.shipping_status == "delivered" else "上海市分拨中心",
            estimated_arrival=order.estimated_delivery_date
        )
        db.add(logistics)
        db.flush()
        
        tracks_data = [
            {
                "logistics_id": logistics.id,
                "status": "已揽收",
                "location": "仓储中心",
                "description": "快递员已揽收包裹",
                "track_time": order.order_date
            },
            {
                "logistics_id": logistics.id,
                "status": "运输中",
                "location": "上海市分拨中心",
                "description": "包裹正在运往目的地",
                "track_time": order.order_date + timedelta(days=1)
            }
        ]
        
        if order.shipping_status == "delivered":
            tracks_data.append({
                "logistics_id": logistics.id,
                "status": "已签收",
                "location": "北京市朝阳区",
                "description": "包裹已成功签收",
                "track_time": order.estimated_delivery_date
            })
        
        for track_data in tracks_data:
            track = LogisticsTrack(**track_data)
            db.add(track)
        
        logistics_count += 1
    
    db.commit()
    print(f"已生成 {logistics_count} 个物流测试数据")

def generate_feedbacks(db):
    customers = db.query(Customer).all()
    orders = db.query(Order).all()
    
    feedback_types = ["suggestion", "complaint", "praise"]
    feedback_contents = {
        "suggestion": [
            "希望能增加更多有机蔬菜品种",
            "建议优化配送时间",
            "希望能提供更多优惠活动"
        ],
        "complaint": [
            "上次配送的苹果有部分损坏",
            "配送时间比预期晚了2天",
            "希望改进包装质量"
        ],
        "praise": [
            "产品质量很好，非常新鲜",
            "配送速度很快，服务态度好",
            "价格合理，会继续支持"
        ]
    }
    
    feedback_count = 0
    for i in range(6):
        customer = random.choice(customers)
        feedback_type = random.choice(feedback_types)
        content = random.choice(feedback_contents[feedback_type])
        
        feedback = Feedback(
            customer_id=customer.id,
            order_id=random.choice(orders).id if orders else None,
            feedback_type=feedback_type,
            content=content,
            rating=5 if feedback_type == "praise" else (1 if feedback_type == "complaint" else 3),
            feedback_date=date.today() - timedelta(days=random.randint(1, 10)),
            status="resolved" if i < 3 else "pending",
            response="感谢您的反馈，我们会持续改进。" if i < 3 else None
        )
        db.add(feedback)
        feedback_count += 1
    
    db.commit()
    print(f"已生成 {feedback_count} 个反馈测试数据")

def main():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("开始生成测试数据...")
        print("=" * 50)
        
        generate_products(db)
        generate_customers(db)
        generate_orders(db)
        generate_contracts(db)
        generate_logistics(db)
        generate_feedbacks(db)
        
        print("=" * 50)
        print("测试数据生成完成！")
        
    except Exception as e:
        print(f"生成测试数据时发生错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
