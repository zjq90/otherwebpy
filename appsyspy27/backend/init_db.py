"""
数据库初始化脚本
用于创建数据库表和初始化基础数据
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.card import CardType, UserCard
from app.models.order import Order, ConsumptionRecord, Promotion
from app.utils.security import get_password_hash
from decimal import Decimal


def create_tables():
    """
    创建所有数据库表
    """
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")


def init_basic_data():
    """
    初始化基础数据
    """
    print("正在初始化基础数据...")
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        existing_card_types = db.query(CardType).count()
        if existing_card_types > 0:
            print("基础数据已存在，跳过初始化")
            return
        
        # 创建会员卡类型
        card_types = [
            CardType(
                name="年度VIP会员",
                code="YEAR_VIP",
                description="全年不限次数使用所有场馆设施和团体课程",
                category="YEAR",
                original_price=Decimal("3680.00"),
                current_price=Decimal("2980.00"),
                valid_days=365,
                usage_scope="所有门店通用，含团体课程、器械区、泳池",
                is_on_sale=True,
                sort_order=100
            ),
            CardType(
                name="半年卡",
                code="HALF_YEAR",
                description="半年期会员，享受所有会员权益",
                category="YEAR",
                original_price=Decimal("2280.00"),
                current_price=Decimal("1880.00"),
                valid_days=180,
                usage_scope="所有门店通用",
                is_on_sale=True,
                sort_order=90
            ),
            CardType(
                name="30次次卡",
                code="COUNT_30",
                description="30次入场次卡，有效期一年",
                category="COUNT",
                original_price=Decimal("1580.00"),
                current_price=Decimal("1280.00"),
                valid_days=365,
                total_count=30,
                usage_scope="单次入场，可使用器械区和淋浴",
                is_on_sale=True,
                sort_order=80
            ),
            CardType(
                name="10次次卡",
                code="COUNT_10",
                description="10次入场次卡，有效期半年",
                category="COUNT",
                original_price=Decimal("680.00"),
                current_price=Decimal("580.00"),
                valid_days=180,
                total_count=10,
                usage_scope="单次入场，可使用器械区和淋浴",
                is_on_sale=True,
                sort_order=70
            ),
            CardType(
                name="私教课10节套餐",
                code="PRIVATE_10",
                description="专业教练一对一私教课10节",
                category="LESSON",
                original_price=Decimal("3800.00"),
                current_price=Decimal("3200.00"),
                valid_days=180,
                total_count=10,
                usage_scope="私教课专用，每节课60分钟",
                is_on_sale=True,
                sort_order=60
            ),
            CardType(
                name="私教课30节套餐",
                code="PRIVATE_30",
                description="专业教练一对一私教课30节，送身体评估",
                category="LESSON",
                original_price=Decimal("10800.00"),
                current_price=Decimal("8800.00"),
                valid_days=365,
                total_count=30,
                usage_scope="私教课专用，每节课60分钟，含一次免费体测",
                is_on_sale=True,
                sort_order=50
            )
        ]
        
        for ct in card_types:
            db.add(ct)
        
        # 创建优惠活动
        promotions = [
            Promotion(
                name="新会员85折",
                code="NEW_MEMBER_85",
                promotion_type="DISCOUNT",
                description="新用户首次购卡享85折优惠",
                discount_config='{"type": "discount", "rate": 0.85}',
                is_active=True,
                sort_order=10
            ),
            Promotion(
                name="满减活动",
                code="FULL_REDUCTION",
                promotion_type="FULL_REDUCTION",
                description="满2000减200，满5000减600",
                discount_config='{"type": "full_reduction", "thresholds": [{"full": 5000, "reduction": 600}, {"full": 2000, "reduction": 200}]}',
                is_active=True,
                sort_order=20
            )
        ]
        
        for p in promotions:
            db.add(p)
        
        # 创建默认管理员账户
        admin = User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            real_name="系统管理员",
            phone="13800138000",
            email="admin@example.com",
            is_active=True,
            is_admin=True
        )
        db.add(admin)
        
        db.commit()
        print("基础数据初始化完成！")
        print(f"  - 会员卡类型: {len(card_types)} 种")
        print(f"  - 优惠活动: {len(promotions)} 个")
        print(f"  - 管理员账户: admin / admin123")
        
    except Exception as e:
        db.rollback()
        print(f"初始化数据失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("会员管理系统 - 数据库初始化脚本")
    print("=" * 50)
    
    create_tables()
    init_basic_data()
    
    print("\n" + "=" * 50)
    print("数据库初始化完成！")
    print("=" * 50)
    print("\nAPI文档地址: http://localhost:8000/api/v1/docs")
    print("管理员账户: admin / admin123")
