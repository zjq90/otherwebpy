import random
from datetime import datetime, timedelta
from decimal import Decimal
from app.database import SessionLocal, init_db
from app.models.user import User, Feedback
from app.models.recycler import Recycler, RecyclerPerformance
from app.models.order import Order, OrderItem
from app.models.category import ClothingCategory, PricingRule
from app.models.product import Product, PointsRule, PointsExchange
from app.models.announcement import Announcement
from app.models.customer_service import CustomerServiceStaff, Consultation, ConsultationMessage

def generate_order_no():
    """生成订单号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = str(random.randint(1000, 9999))
    return f"ORD{timestamp}{random_suffix}"

def generate_exchange_no():
    """生成兑换单号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = str(random.randint(1000, 9999))
    return f"EXC{timestamp}{random_suffix}"

def generate_consultation_no():
    """生成咨询编号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = str(random.randint(1000, 9999))
    return f"CON{timestamp}{random_suffix}"

def init_test_data():
    """初始化测试数据"""
    db = SessionLocal()
    
    try:
        init_db()
        
        print("正在创建测试数据...")
        
        categories = [
            {"name": "羽绒服", "code": "YRF", "level": 1, "sort": 1, "status": 1, "description": "羽绒类衣物"},
            {"name": "棉衣", "code": "MY", "level": 1, "sort": 2, "status": 1, "description": "棉服类"},
            {"name": "毛衣", "code": "MAOY", "level": 1, "sort": 3, "status": 1, "description": "针织毛衣类"},
            {"name": "外套", "code": "WT", "level": 1, "sort": 4, "status": 1, "description": "外套类"},
            {"name": "裤子", "code": "KZ", "level": 1, "sort": 5, "status": 1, "description": "裤装类"},
            {"name": "T恤", "code": "TX", "level": 1, "sort": 6, "status": 1, "description": "T恤类"},
            {"name": "鞋子", "code": "XZ", "level": 1, "sort": 7, "status": 1, "description": "鞋类"},
            {"name": "箱包", "code": "XB", "level": 1, "sort": 8, "status": 1, "description": "箱包类"},
            {"name": "床上用品", "code": "CSYP", "level": 1, "sort": 9, "status": 1, "description": "床上用品"},
            {"name": "其他", "code": "QT", "level": 1, "sort": 10, "status": 1, "description": "其他物品"},
        ]
        
        for cat in categories:
            db_cat = ClothingCategory(**cat)
            db.add(db_cat)
        db.flush()
        
        db_categories = db.query(ClothingCategory).all()
        
        pricing_rules = [
            {"category_id": 1, "category_name": "羽绒服", "pricing_type": 0, "unit_price": Decimal('30.00'), "weight_price": Decimal('15.00'), "has_min_price": 1, "min_price_per_item": Decimal('25.00'), "points_per_unit": 300, "status": 1},
            {"category_id": 2, "category_name": "棉衣", "pricing_type": 0, "unit_price": Decimal('15.00'), "weight_price": Decimal('12.00'), "has_min_price": 1, "min_price_per_item": Decimal('10.00'), "points_per_unit": 150, "status": 1},
            {"category_id": 3, "category_name": "毛衣", "pricing_type": 1, "unit_price": Decimal('8.00'), "weight_price": Decimal('10.00'), "has_min_price": 0, "min_price_per_item": Decimal('0.00'), "points_per_unit": 100, "status": 1},
            {"category_id": 4, "category_name": "外套", "pricing_type": 1, "unit_price": Decimal('5.00'), "weight_price": Decimal('8.00'), "has_min_price": 0, "min_price_per_item": Decimal('0.00'), "points_per_unit": 80, "status": 1},
            {"category_id": 5, "category_name": "裤子", "pricing_type": 1, "unit_price": Decimal('3.00'), "weight_price": Decimal('6.00'), "has_min_price": 0, "min_price_per_item": Decimal('0.00'), "points_per_unit": 60, "status": 1},
            {"category_id": 6, "category_name": "T恤", "pricing_type": 1, "unit_price": Decimal('2.00'), "weight_price": Decimal('5.00'), "has_min_price": 0, "min_price_per_item": Decimal('0.00'), "points_per_unit": 50, "status": 1},
            {"category_id": 7, "category_name": "鞋子", "pricing_type": 0, "unit_price": Decimal('10.00'), "weight_price": Decimal('8.00'), "has_min_price": 1, "min_price_per_item": Decimal('5.00'), "points_per_unit": 100, "status": 1},
            {"category_id": 8, "category_name": "箱包", "pricing_type": 0, "unit_price": Decimal('8.00'), "weight_price": Decimal('6.00'), "has_min_price": 1, "min_price_per_item": Decimal('5.00'), "points_per_unit": 80, "status": 1},
            {"category_id": 9, "category_name": "床上用品", "pricing_type": 1, "unit_price": Decimal('10.00'), "weight_price": Decimal('12.00'), "has_min_price": 0, "min_price_per_item": Decimal('0.00'), "points_per_unit": 120, "status": 1},
            {"category_id": 10, "category_name": "其他", "pricing_type": 1, "unit_price": Decimal('2.00'), "weight_price": Decimal('3.00'), "has_min_price": 0, "min_price_per_item": Decimal('0.00'), "points_per_unit": 30, "status": 1},
        ]
        
        for rule in pricing_rules:
            db_rule = PricingRule(**rule)
            db.add(db_rule)
        
        users = []
        for i in range(1, 51):
            user = User(
                username=f"user{i:03d}",
                password=f"password{i}",
                phone=f"138{random.randint(10000000, 99999999)}",
                email=f"user{i}@example.com",
                nickname=f"用户{i}号",
                address=f"北京市朝阳区某某街道{i}号",
                user_type=1 if i == 1 else 0,
                status=1,
                points=random.randint(0, 5000),
                total_points=random.randint(0, 10000)
            )
            users.append(user)
            db.add(user)
        db.flush()
        
        recyclers = []
        recycler_names = ["张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十", "郑十一", "王十二"]
        for i in range(1, 11):
            recycler = Recycler(
                username=f"recycler{i:02d}",
                password=f"recycler{i}",
                real_name=recycler_names[i-1],
                phone=f"139{random.randint(10000000, 99999999)}",
                id_card=f"110101{random.randint(19800101, 20001231)}1234",
                area=f"朝阳区区域{i}",
                status=1,
                total_orders=random.randint(50, 500),
                completed_orders=random.randint(40, 480),
                total_weight=Decimal(random.uniform(100, 2000)),
                total_amount=Decimal(random.uniform(1000, 20000)),
                performance_score=Decimal(random.uniform(80, 100))
            )
            recyclers.append(recycler)
            db.add(recycler)
        db.flush()
        
        products = [
            {"product_name": "小米手环8", "product_code": "PRD001", "points_price": 5000, "original_price": Decimal('249.00'), "stock": 100, "sold_count": 45, "status": 1, "sort": 1, "description": "智能手环，健康监测"},
            {"product_name": "京东E卡50元", "product_code": "PRD002", "points_price": 500, "original_price": Decimal('50.00'), "stock": 500, "sold_count": 320, "status": 1, "sort": 2, "description": "京东购物卡"},
            {"product_name": "星巴克中杯券", "product_code": "PRD003", "points_price": 300, "original_price": Decimal('33.00'), "stock": 200, "sold_count": 150, "status": 1, "sort": 3, "description": "星巴克中杯饮品兑换券"},
            {"product_name": "环保布袋", "product_code": "PRD004", "points_price": 100, "original_price": Decimal('29.90'), "stock": 1000, "sold_count": 680, "status": 1, "sort": 4, "description": "环保帆布购物袋"},
            {"product_name": "手机话费10元", "product_code": "PRD005", "points_price": 120, "original_price": Decimal('10.00'), "stock": 999, "sold_count": 850, "status": 1, "sort": 5, "description": "中国移动/联通/电信话费充值"},
            {"product_name": "洗衣液2kg", "product_code": "PRD006", "points_price": 800, "original_price": Decimal('35.00'), "stock": 300, "sold_count": 120, "status": 1, "sort": 6, "description": "洗衣液家庭装"},
            {"product_name": "抽纸10包", "product_code": "PRD007", "points_price": 500, "original_price": Decimal('25.00'), "stock": 500, "sold_count": 230, "status": 1, "sort": 7, "description": "原生木浆抽纸"},
            {"product_name": "雨伞", "product_code": "PRD008", "points_price": 600, "original_price": Decimal('45.00'), "stock": 200, "sold_count": 85, "status": 1, "sort": 8, "description": "晴雨两用折叠伞"},
        ]
        
        for prod in products:
            db_prod = Product(**prod)
            db.add(db_prod)
        
        points_rules = [
            {"name": "羽绒服积分规则", "category_id": 1, "category_name": "羽绒服", "pricing_type": 0, "points_per_unit": 300, "has_bonus": 1, "bonus_condition": "一次回收5件以上", "bonus_points": 200, "status": 1},
            {"name": "普通衣物积分规则", "category_id": 4, "category_name": "外套", "pricing_type": 1, "points_per_unit": 80, "has_bonus": 0, "status": 1},
            {"name": "裤子积分规则", "category_id": 5, "category_name": "裤子", "pricing_type": 1, "points_per_unit": 60, "has_bonus": 0, "status": 1},
        ]
        
        for rule in points_rules:
            db.add(PointsRule(**rule))
        
        announcements = [
            {"title": "环保回收新活动开始啦！", "summary": "参与旧衣物回收，赢取双倍积分", "content": "亲爱的用户：\n\n为了感谢大家对环保事业的支持，我们推出了新的环保回收活动。活动期间，参与旧衣物回收的用户将获得双倍积分奖励！\n\n活动时间：2024年1月1日至2024年2月28日\n\n快来参与吧！", "announcement_type": 1, "status": 1, "is_top": 1, "view_count": 1520},
            {"title": "春节放假通知", "summary": "春节期间回收服务安排", "content": "尊敬的用户：\n\n2024年春节假期（2月9日-2月17日）期间，回收服务安排如下：\n\n1. 2月9日-2月11日：暂停回收服务\n2. 2月12日起：逐步恢复回收服务\n\n给您带来的不便，敬请谅解。\n\n祝您春节快乐！", "announcement_type": 0, "status": 1, "is_top": 0, "view_count": 890},
            {"title": "价格调整公告", "summary": "部分衣物回收价格调整", "content": "根据市场行情变化，我们对部分衣物的回收价格进行了调整：\n\n- 羽绒服：30元/件（原28元/件）\n- 棉衣：15元/件（原12元/件）\n- 床上用品：12元/公斤（原10元/公斤）\n\n新价格自2024年1月15日起生效。感谢您的支持！", "announcement_type": 0, "status": 1, "is_top": 0, "view_count": 756},
            {"title": "新功能上线：积分兑换", "summary": "积分商城正式上线", "content": "好消息！积分兑换功能正式上线了！\n\n您现在可以使用回收获得的积分兑换：\n\n1. 京东E卡\n2. 星巴克饮品券\n3. 手机话费\n4. 各种实物商品\n\n快来积分商城看看吧！", "announcement_type": 0, "status": 1, "is_top": 0, "view_count": 2100},
        ]
        
        for ann in announcements:
            db_ann = Announcement(**ann)
            db_ann.publish_time = datetime.now() - timedelta(days=random.randint(1, 60))
            db.add(db_ann)
        
        cs_staffs = []
        cs_names = ["客服小王", "客服小李", "客服小张", "客服小刘", "客服小陈"]
        for i in range(1, 6):
            staff = CustomerServiceStaff(
                username=f"cs{i:02d}",
                password=f"cs{i}pass",
                real_name=cs_names[i-1],
                phone=f"137{random.randint(10000000, 99999999)}",
                group_type=random.randint(0, 2),
                status=1,
                total_consultations=random.randint(50, 200),
                resolved_count=random.randint(40, 180)
            )
            cs_staffs.append(staff)
            db.add(staff)
        db.flush()
        
        for i in range(1, 201):
            order_date = datetime.now() - timedelta(days=random.randint(0, 180))
            status = random.choices([0, 1, 3, 4, 5], weights=[5, 10, 75, 8, 2])[0]
            
            user_idx = random.randint(0, 49)
            recycler_idx = random.randint(0, 9) if status >= 1 else -1
            
            order = Order(
                order_no=generate_order_no(),
                user_id=users[user_idx].id,
                user_name=users[user_idx].nickname,
                user_phone=users[user_idx].phone,
                address=users[user_idx].address,
                area=f"朝阳区区域{recycler_idx + 1}" if recycler_idx >= 0 else None,
                appointment_date=order_date + timedelta(hours=random.randint(24, 72)),
                appointment_time=random.choice(["上午9:00-12:00", "下午14:00-18:00", "全天"]),
                recycler_id=recyclers[recycler_idx].id if recycler_idx >= 0 else None,
                recycler_name=recyclers[recycler_idx].real_name if recycler_idx >= 0 else None,
                status=status,
                created_at=order_date
            )
            
            if status == 1:
                order.accept_time = order_date + timedelta(hours=random.randint(1, 24))
            elif status == 3:
                order.accept_time = order_date + timedelta(hours=random.randint(1, 12))
                order.complete_time = order_date + timedelta(days=random.randint(1, 3), hours=random.randint(1, 12))
            elif status == 4:
                order.cancel_time = order_date + timedelta(hours=random.randint(1, 48))
                order.cancel_reason = random.choice(["用户临时有事", "预约时间不合适", "改变主意了"])
            elif status == 5:
                order.exception_reason = random.choice(["地址错误", "用户不在家", "物品不符合要求"])
            
            db.add(order)
            db.flush()
            
            item_count = random.randint(1, 10)
            total_weight = Decimal(0)
            total_amount = Decimal(0)
            total_points = 0
            
            for _ in range(item_count):
                cat_idx = random.randint(0, len(categories) - 1)
                cat = categories[cat_idx]
                rule = pricing_rules[cat_idx]
                
                pricing_type = rule["pricing_type"]
                
                if pricing_type == 0:
                    quantity = random.randint(1, 5)
                    weight = None
                    amount = Decimal(quantity) * rule["unit_price"]
                    points = quantity * rule["points_per_unit"]
                else:
                    quantity = None
                    weight = Decimal(f"{random.uniform(0.5, 5):.2f}")
                    amount = weight * rule["weight_price"]
                    points = int(float(weight) * rule["points_per_unit"])
                
                total_weight += weight if weight else Decimal(0)
                total_amount += amount
                total_points += points
                
                item = OrderItem(
                    order_id=order.id,
                    category_id=cat_idx + 1,
                    category_name=cat["name"],
                    pricing_type=pricing_type,
                    quantity=quantity,
                    weight=weight,
                    unit_price=rule["unit_price"] if pricing_type == 0 else rule["weight_price"],
                    amount=amount,
                    points=points
                )
                db.add(item)
            
            if status == 3:
                order.total_weight = total_weight
                order.total_amount = total_amount
                order.total_points = total_points
        
        for i in range(1, 31):
            user_idx = random.randint(0, 49)
            prod_idx = random.randint(0, len(products) - 1)
            prod = products[prod_idx]
            
            quantity = random.randint(1, 3)
            total_points = prod["points_price"] * quantity
            
            exchange = PointsExchange(
                exchange_no=generate_exchange_no(),
                user_id=users[user_idx].id,
                user_name=users[user_idx].nickname,
                user_phone=users[user_idx].phone,
                product_id=prod_idx + 1,
                product_name=prod["product_name"],
                quantity=quantity,
                points_price=prod["points_price"],
                total_points=total_points,
                receive_name=users[user_idx].nickname,
                receive_phone=users[user_idx].phone,
                receive_address=users[user_idx].address,
                status=random.choice([0, 1, 2, 3]),
                created_at=datetime.now() - timedelta(days=random.randint(0, 90))
            )
            db.add(exchange)
        
        feedback_types = ["回收速度慢", "价格不满意", "服务态度好", "建议增加品类", "系统使用问题"]
        for i in range(1, 21):
            user_idx = random.randint(0, 49)
            feedback_type = random.randint(0, 2)
            status = random.randint(0, 3)
            
            feedback = Feedback(
                user_id=users[user_idx].id,
                feedback_type=feedback_type,
                title=feedback_types[random.randint(0, 4)],
                content=f"这是一条测试反馈内容。用户{users[user_idx].nickname}对系统的{random.choice(['回收服务', '积分系统', '客服服务', '价格体系'])}提出了一些意见。",
                contact=users[user_idx].phone,
                status=status,
                created_at=datetime.now() - timedelta(days=random.randint(1, 60))
            )
            
            if status >= 2:
                feedback.reply = "感谢您的反馈，我们会认真处理并持续改进服务。"
                feedback.reply_user_id = cs_staffs[random.randint(0, 4)].id
                feedback.reply_time = feedback.created_at + timedelta(hours=random.randint(1, 24))
            
            db.add(feedback)
        
        for i in range(1, 16):
            user_idx = random.randint(0, 49)
            cs_idx = random.randint(0, 4)
            con_type = random.randint(0, 3)
            status = random.randint(0, 3)
            
            con = Consultation(
                consultation_no=generate_consultation_no(),
                user_id=users[user_idx].id,
                user_name=users[user_idx].nickname,
                user_phone=users[user_idx].phone,
                cs_staff_id=cs_staffs[cs_idx].id if status >= 1 else None,
                cs_staff_name=cs_staffs[cs_idx].real_name if status >= 1 else None,
                consultation_type=con_type,
                title=f"咨询类型：{['订单问题', '积分问题', '回收问题', '其他'][con_type]}",
                question=f"这是一条测试咨询内容。用户{users[user_idx].nickname}咨询关于{['订单', '积分', '回收服务', '其他'][con_type]}的问题。",
                status=status,
                rating=random.randint(1, 5) if status == 3 else None,
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            
            if status >= 1:
                con.assign_time = con.created_at + timedelta(hours=random.randint(1, 12))
            if status >= 2:
                con.resolve_time = con.created_at + timedelta(hours=random.randint(12, 72))
            if status == 3:
                con.close_time = con.resolve_time + timedelta(hours=random.randint(1, 24))
            
            db.add(con)
        
        db.commit()
        print("测试数据创建完成！")
        print(f"创建了 {len(users)} 个用户")
        print(f"创建了 {len(recyclers)} 个回收人员")
        print(f"创建了 {len(categories)} 个衣物分类")
        print(f"创建了 {len(products)} 个积分商品")
        
    except Exception as e:
        print(f"创建测试数据时出错: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_test_data()
