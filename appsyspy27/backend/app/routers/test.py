"""
测试功能路由模块
提供API测试、数据生成等测试辅助功能
"""

from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal
import random

from app.database import get_db
from app.models.user import User
from app.models.card import CardType, UserCard
from app.models.order import Order, ConsumptionRecord, Promotion
from app.utils.security import get_password_hash, create_access_token
from app.utils.helpers import generate_order_no, generate_card_number

router = APIRouter(prefix="/test", tags=["测试功能"])


@router.post("/generate-test-data", summary="生成测试数据")
def generate_test_data(
    user_count: int = 3,
    db: Session = Depends(get_db)
):
    """
    生成完整的测试数据，包括：
    - 会员卡类型
    - 优惠活动
    - 测试用户
    - 用户卡包
    - 订单和消费记录
    
    - **user_count**: 生成测试用户数量
    """
    # 1. 创建会员卡类型
    card_types_data = [
        {
            "name": "年度VIP会员",
            "code": "YEAR_VIP",
            "description": "全年不限次数使用所有场馆设施和团体课程",
            "category": "YEAR",
            "original_price": Decimal("3680.00"),
            "current_price": Decimal("2980.00"),
            "valid_days": 365,
            "usage_scope": "所有门店通用，含团体课程、器械区、泳池",
            "sort_order": 100
        },
        {
            "name": "半年卡",
            "code": "HALF_YEAR",
            "description": "半年期会员，享受所有会员权益",
            "category": "YEAR",
            "original_price": Decimal("2280.00"),
            "current_price": Decimal("1880.00"),
            "valid_days": 180,
            "usage_scope": "所有门店通用",
            "sort_order": 90
        },
        {
            "name": "30次次卡",
            "code": "COUNT_30",
            "description": "30次入场次卡，有效期一年",
            "category": "COUNT",
            "original_price": Decimal("1580.00"),
            "current_price": Decimal("1280.00"),
            "valid_days": 365,
            "total_count": 30,
            "usage_scope": "单次入场，可使用器械区和淋浴",
            "sort_order": 80
        },
        {
            "name": "10次次卡",
            "code": "COUNT_10",
            "description": "10次入场次卡，有效期半年",
            "category": "COUNT",
            "original_price": Decimal("680.00"),
            "current_price": Decimal("580.00"),
            "valid_days": 180,
            "total_count": 10,
            "usage_scope": "单次入场，可使用器械区和淋浴",
            "sort_order": 70
        },
        {
            "name": "私教课10节套餐",
            "code": "PRIVATE_10",
            "description": "专业教练一对一私教课10节",
            "category": "LESSON",
            "original_price": Decimal("3800.00"),
            "current_price": Decimal("3200.00"),
            "valid_days": 180,
            "total_count": 10,
            "usage_scope": "私教课专用，每节课60分钟",
            "sort_order": 60
        },
        {
            "name": "私教课30节套餐",
            "code": "PRIVATE_30",
            "description": "专业教练一对一私教课30节，送身体评估",
            "category": "LESSON",
            "original_price": Decimal("10800.00"),
            "current_price": Decimal("8800.00"),
            "valid_days": 365,
            "total_count": 30,
            "usage_scope": "私教课专用，每节课60分钟，含一次免费体测",
            "sort_order": 50
        },
        {
            "name": "月卡（时长型）",
            "code": "DURATION_MONTH",
            "description": "按时长计费的月卡，共60小时",
            "category": "DURATION",
            "original_price": Decimal("980.00"),
            "current_price": Decimal("780.00"),
            "valid_days": 30,
            "total_duration": 60 * 60,  # 60小时 = 3600分钟
            "usage_scope": "按时长计费，入场开始计时",
            "sort_order": 40
        }
    ]
    
    created_card_types = []
    for ct_data in card_types_data:
        existing = db.query(CardType).filter(CardType.code == ct_data["code"]).first()
        if not existing:
            ct = CardType(**ct_data, is_on_sale=True)
            db.add(ct)
            db.commit()
            db.refresh(ct)
            created_card_types.append(ct)
        else:
            created_card_types.append(existing)
    
    # 2. 创建优惠活动
    promotions_data = [
        {
            "name": "新会员85折",
            "code": "NEW_MEMBER_85",
            "promotion_type": "DISCOUNT",
            "description": "新用户首次购卡享85折优惠",
            "discount_config": '{"type": "discount", "rate": 0.85}',
            "sort_order": 10
        },
        {
            "name": "满减活动",
            "code": "FULL_REDUCTION",
            "promotion_type": "FULL_REDUCTION",
            "description": "满2000减200，满5000减600",
            "discount_config": '{"type": "full_reduction", "thresholds": [{"full": 5000, "reduction": 600}, {"full": 2000, "reduction": 200}]}',
            "sort_order": 20
        }
    ]
    
    created_promotions = []
    for p_data in promotions_data:
        existing = db.query(Promotion).filter(Promotion.code == p_data["code"]).first()
        if not existing:
            p = Promotion(**p_data, is_active=True)
            db.add(p)
            db.commit()
            db.refresh(p)
            created_promotions.append(p)
        else:
            created_promotions.append(existing)
    
    # 3. 创建测试用户
    test_users = []
    for i in range(1, user_count + 1):
        user_data = {
            "username": f"testuser{i}",
            "password_hash": get_password_hash("123456"),
            "real_name": f"测试用户{i}",
            "phone": f"138{str(10000000 + i).zfill(8)}",
            "email": f"testuser{i}@example.com",
            "is_active": True,
            "is_admin": i == 1  # 第一个用户设为管理员
        }
        
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing:
            user = User(**user_data)
            db.add(user)
            db.commit()
            db.refresh(user)
            test_users.append(user)
        else:
            test_users.append(existing)
    
    # 4. 为每个用户创建卡包、订单和消费记录
    now = datetime.now()
    for user in test_users:
        # 随机为用户选择2-3种卡
        selected_cards = random.sample(created_card_types, k=min(3, len(created_card_types)))
        
        for card_type in selected_cards:
            # 创建订单
            order = Order(
                order_no=generate_order_no(),
                user_id=user.id,
                order_type="PURCHASE",
                card_type_id=card_type.id,
                title=f"{card_type.name}",
                description=card_type.description,
                quantity=1,
                unit_price=card_type.current_price,
                original_amount=card_type.current_price,
                discount_amount=Decimal("0"),
                pay_amount=card_type.current_price,
                pay_method=random.choice(["WECHAT", "ALIPAY"]),
                third_pay_no=f"TP_{generate_order_no()}",
                status="PAID",
                pay_time=now - timedelta(days=random.randint(1, 30))
            )
            db.add(order)
            db.commit()
            db.refresh(order)
            
            # 计算过期时间
            expire_time = None
            if card_type.valid_days:
                expire_time = order.pay_time.date() + timedelta(days=card_type.valid_days)
            
            # 创建用户卡
            # 随机使用一些次数
            used_count = 0
            if card_type.total_count:
                used_count = random.randint(0, card_type.total_count // 2)
            
            used_duration = 0
            if card_type.total_duration:
                used_duration = random.randint(0, card_type.total_duration // 3)
            
            user_card = UserCard(
                user_id=user.id,
                card_type_id=card_type.id,
                card_number=generate_card_number(),
                purchase_time=order.pay_time,
                activate_time=order.pay_time,
                expire_time=expire_time,
                remaining_count=card_type.total_count - used_count if card_type.total_count else None,
                total_count=card_type.total_count,
                remaining_duration=card_type.total_duration - used_duration if card_type.total_duration else None,
                total_duration=card_type.total_duration,
                status="ACTIVE",
                order_id=order.id
            )
            db.add(user_card)
            db.commit()
            db.refresh(user_card)
            
            # 创建购卡消费记录
            purchase_record = ConsumptionRecord(
                user_id=user.id,
                record_type="PURCHASE",
                order_id=order.id,
                user_card_id=user_card.id,
                title=f"购买{card_type.name}",
                description=card_type.description,
                amount=order.pay_amount,
                store_name=random.choice(["旗舰店", "中心店", "社区店"]),
                created_at=order.pay_time
            )
            db.add(purchase_record)
            
            # 如果有使用次数，创建使用记录
            for j in range(used_count):
                use_time = order.pay_time + timedelta(days=random.randint(1, 20))
                lesson_record = ConsumptionRecord(
                    user_id=user.id,
                    record_type="LESSON" if card_type.category == "LESSON" else "GOODS",
                    user_card_id=user_card.id,
                    title=f"{'私教课' if card_type.category == 'LESSON' else '入场'}消费",
                    description=f"第{j+1}次使用",
                    amount=Decimal("0"),
                    count_before=card_type.total_count - j,
                    count_after=card_type.total_count - j - 1,
                    store_name=random.choice(["旗舰店", "中心店", "社区店"]),
                    operator_name=random.choice(["张教练", "李教练", "王教练"]),
                    created_at=use_time
                )
                db.add(lesson_record)
    
    db.commit()
    
    return {
        "message": "测试数据生成成功",
        "data": {
            "card_types_count": len(created_card_types),
            "promotions_count": len(created_promotions),
            "users_count": len(test_users),
            "test_accounts": [
                {
                    "username": u.username,
                    "password": "123456",
                    "is_admin": u.is_admin,
                    "token": create_access_token(subject=u.id)
                } for u in test_users
            ]
        }
    }


@router.get("/health", summary="健康检查")
def health_check():
    """
    检查API服务是否正常运行
    """
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "Membership API"
    }


@router.get("/db-stats", summary="数据库统计")
def get_db_stats(db: Session = Depends(get_db)):
    """
    获取数据库各表的统计信息
    """
    stats = {
        "users": db.query(User).count(),
        "card_types": db.query(CardType).count(),
        "user_cards": db.query(UserCard).count(),
        "orders": db.query(Order).count(),
        "consumption_records": db.query(ConsumptionRecord).count(),
        "promotions": db.query(Promotion).count()
    }
    return stats
