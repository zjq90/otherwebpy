"""
测试功能API路由
用于辅助系统功能测试
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta
import random
import string
from config.database import get_db
from crud.member import member_crud, member_card_crud
from crud.promotion import promotion_crud, coupon_crud
from crud.reminder import reminder_crud
from schemas.member import MemberCreate, MemberCardCreate
from schemas.promotion import PromotionCreate
from models.member import MemberLevel, MemberStatus
from models.promotion import PromotionType, PromotionStatus, TargetType
from models.reminder import ReminderType

router = APIRouter(prefix="/api/test", tags=["测试功能"])


def generate_random_string(length: int = 8) -> str:
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def generate_random_phone() -> str:
    """生成随机手机号"""
    prefixes = ['138', '139', '150', '151', '152', '158', '159', '186', '187', '188']
    prefix = random.choice(prefixes)
    suffix = ''.join(random.choices(string.digits, k=8))
    return prefix + suffix


@router.post("/generate-members", summary="生成测试会员数据")
def generate_test_members(
    count: int = Query(10, ge=1, le=100, description="生成数量"),
    db: Session = Depends(get_db)
):
    """
    批量生成测试会员数据
    """
    names = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十',
             '郑伟', '王芳', '李娜', '刘洋', '陈静', '杨帆', '黄磊', '周涛',
             '赵敏', '钱多多', '孙悟空', '猪八戒']
    
    levels = [e.value for e in MemberLevel]
    statuses = [e.value for e in MemberStatus]
    
    created_count = 0
    created_members = []
    
    for i in range(count):
        member_no = f"M{datetime.now().strftime('%Y%m%d')}{str(i+1).zfill(4)}"
        name = random.choice(names)
        phone = generate_random_phone()
        
        # 确保手机号唯一
        while member_crud.get_by_phone(db, phone=phone):
            phone = generate_random_phone()
        
        member_in = MemberCreate(
            member_no=member_no,
            name=name,
            phone=phone,
            email=f"{phone}@example.com",
            gender=random.choice(['男', '女', None]),
            birthday=date(1980 + random.randint(0, 30), random.randint(1, 12), random.randint(1, 28)),
            address=f"北京市朝阳区{random.randint(1, 100)}号",
            level=random.choice(levels),
            status=random.choice(statuses)
        )
        
        try:
            member = member_crud.create(db, member_in=member_in)
            # 随机设置消费金额和积分
            member.total_consumption = round(random.uniform(100, 50000), 2)
            member.points = random.randint(100, 50000)
            # 随机设置最后消费时间
            days_ago = random.randint(0, 90)
            member.last_consumption_time = datetime.now() - timedelta(days=days_ago)
            db.commit()
            db.refresh(member)
            
            created_members.append({"id": member.id, "name": member.name, "member_no": member.member_no})
            created_count += 1
        except Exception as e:
            print(f"创建会员失败: {e}")
            continue
    
    return {
        "message": f"成功生成 {created_count} 个测试会员",
        "created_count": created_count,
        "members": created_members
    }


@router.post("/generate-member-cards", summary="生成测试会员卡数据")
def generate_test_member_cards(
    member_count: int = Query(5, ge=1, description="为多少会员生成会员卡"),
    cards_per_member: int = Query(1, ge=1, le=3, description="每个会员生成多少张卡"),
    db: Session = Depends(get_db)
):
    """
    批量生成测试会员卡数据
    """
    # 获取会员列表
    members, _ = member_crud.get_list(db, skip=0, limit=member_count)
    
    if not members:
        return {"message": "没有可用的会员，请先生成测试会员数据"}
    
    card_types = ['月卡', '季卡', '半年卡', '年卡']
    created_count = 0
    created_cards = []
    
    for member in members:
        for i in range(cards_per_member):
            card_no = f"C{datetime.now().strftime('%Y%m%d')}{generate_random_string(6)}"
            card_type = random.choice(card_types)
            
            # 根据卡类型设置有效期
            if card_type == '月卡':
                valid_days = 30
            elif card_type == '季卡':
                valid_days = 90
            elif card_type == '半年卡':
                valid_days = 180
            else:  # 年卡
                valid_days = 365
            
            # 随机设置开始日期（过去30天到现在）
            start_days_ago = random.randint(0, valid_days - 7)
            valid_from = date.today() - timedelta(days=start_days_ago)
            valid_to = valid_from + timedelta(days=valid_days)
            
            card_in = MemberCardCreate(
                card_no=card_no,
                member_id=member.id,
                card_type=card_type,
                balance=round(random.uniform(0, 5000), 2),
                total_amount=round(random.uniform(100, 10000), 2),
                valid_from=valid_from,
                valid_to=valid_to,
                status="active"
            )
            
            try:
                card = member_card_crud.create(db, card_in=card_in)
                created_cards.append({
                    "id": card.id,
                    "card_no": card.card_no,
                    "member_id": card.member_id,
                    "card_type": card.card_type,
                    "valid_to": str(card.valid_to)
                })
                created_count += 1
            except Exception as e:
                print(f"创建会员卡失败: {e}")
                continue
    
    return {
        "message": f"成功生成 {created_count} 张测试会员卡",
        "created_count": created_count,
        "cards": created_cards
    }


@router.post("/generate-promotions", summary="生成测试促销活动数据")
def generate_test_promotions(
    count: int = Query(3, ge=1, le=10, description="生成数量"),
    db: Session = Depends(get_db)
):
    """
    批量生成测试促销活动数据
    """
    promotion_names = [
        "新春特惠限时折扣",
        "会员专享满减活动",
        "新会员体验券",
        "沉睡会员唤醒计划",
        "高价值客户回馈活动"
    ]
    
    types = [e.value for e in PromotionType]
    target_types = [e.value for e in TargetType]
    
    created_count = 0
    created_promotions = []
    
    for i in range(min(count, len(promotion_names))):
        promo_type = random.choice(types)
        
        # 根据类型设置不同的优惠参数
        discount_rate = None
        full_amount = None
        reduction_amount = None
        experience_amount = None
        
        if promo_type == PromotionType.DISCOUNT.value:
            discount_rate = round(random.uniform(0.5, 0.9), 1)
        elif promo_type == PromotionType.FULL_REDUCTION.value:
            full_amount = random.choice([100, 200, 500, 1000])
            reduction_amount = random.choice([10, 20, 50, 100])
        elif promo_type == PromotionType.EXPERIENCE.value:
            experience_amount = random.choice([50, 100, 200, 500])
        
        # 设置活动时间
        valid_from = datetime.now() - timedelta(days=random.randint(0, 30))
        valid_to = datetime.now() + timedelta(days=random.randint(30, 90))
        
        promotion_in = PromotionCreate(
            name=promotion_names[i],
            type=promo_type,
            description=f"这是一个测试促销活动：{promotion_names[i]}",
            discount_rate=discount_rate,
            full_amount=full_amount,
            reduction_amount=reduction_amount,
            experience_amount=experience_amount,
            valid_from=valid_from,
            valid_to=valid_to,
            total_quantity=random.randint(10, 100),
            per_member_limit=random.randint(1, 3),
            target_type=random.choice(target_types),
            status=PromotionStatus.ACTIVE.value
        )
        
        try:
            promotion = promotion_crud.create(db, promotion_in=promotion_in)
            created_promotions.append({
                "id": promotion.id,
                "name": promotion.name,
                "type": promotion.type,
                "status": promotion.status
            })
            created_count += 1
        except Exception as e:
            print(f"创建活动失败: {e}")
            continue
    
    return {
        "message": f"成功生成 {created_count} 个测试促销活动",
        "created_count": created_count,
        "promotions": created_promotions
    }


@router.post("/generate-coupons", summary="为活动生成优惠券")
def generate_test_coupons(
    promotion_id: int = Query(..., description="活动ID"),
    quantity: int = Query(10, ge=1, le=1000, description="生成数量"),
    db: Session = Depends(get_db)
):
    """
    为指定活动批量生成优惠券
    """
    # 检查活动是否存在
    promotion = promotion_crud.get_by_id(db, promotion_id=promotion_id)
    if promotion is None:
        return {"message": "活动不存在"}
    
    created_count = 0
    created_coupons = []
    
    for i in range(quantity):
        coupon_no = f"CP{datetime.now().strftime('%Y%m%d')}{generate_random_string(8)}"
        
        from schemas.promotion import CouponCreate
        coupon_in = CouponCreate(
            coupon_no=coupon_no,
            promotion_id=promotion_id,
            type=promotion.type,
            name=promotion.name,
            discount_rate=promotion.discount_rate,
            full_amount=promotion.full_amount,
            reduction_amount=promotion.reduction_amount,
            experience_amount=promotion.experience_amount,
            valid_from=promotion.valid_from,
            valid_to=promotion.valid_to
        )
        
        try:
            coupon = coupon_crud.create(db, coupon_in=coupon_in)
            created_coupons.append({
                "id": coupon.id,
                "coupon_no": coupon.coupon_no,
                "status": coupon.status
            })
            created_count += 1
        except Exception as e:
            print(f"创建优惠券失败: {e}")
            continue
    
    return {
        "message": f"成功生成 {created_count} 张优惠券",
        "created_count": created_count,
        "coupons": created_coupons[:10]  # 只返回前10个
    }


@router.post("/generate-expiring-cards", summary="生成即将到期的会员卡（用于测试续费提醒）")
def generate_expiring_cards(
    count: int = Query(5, ge=1, description="生成数量"),
    db: Session = Depends(get_db)
):
    """
    生成即将到期的会员卡，用于测试续费提醒功能
    - 一些卡将在7天后到期
    - 一些卡将在3天后到期
    """
    # 获取会员列表
    members, _ = member_crud.get_list(db, skip=0, limit=count * 2)
    
    if not members:
        return {"message": "没有可用的会员，请先生成测试会员数据"}
    
    created_count = 0
    created_cards = []
    
    for i in range(min(count, len(members))):
        member = members[i]
        card_no = f"CEX{datetime.now().strftime('%Y%m%d')}{generate_random_string(4)}"
        
        # 随机选择7天或3天后到期
        days_until_expiry = random.choice([3, 7])
        valid_to = date.today() + timedelta(days=days_until_expiry)
        valid_from = valid_to - timedelta(days=30)  # 30天前开始
        
        card_in = MemberCardCreate(
            card_no=card_no,
            member_id=member.id,
            card_type='测试月卡',
            balance=round(random.uniform(0, 1000), 2),
            total_amount=500.0,
            valid_from=valid_from,
            valid_to=valid_to,
            status="active"
        )
        
        try:
            card = member_card_crud.create(db, card_in=card_in)
            created_cards.append({
                "id": card.id,
                "card_no": card.card_no,
                "member_name": member.name,
                "days_until_expiry": days_until_expiry,
                "valid_to": str(card.valid_to)
            })
            created_count += 1
        except Exception as e:
            print(f"创建会员卡失败: {e}")
            continue
    
    return {
        "message": f"成功生成 {created_count} 张即将到期的测试会员卡",
        "created_count": created_count,
        "cards": created_cards
    }


@router.post("/generate-all", summary="一键生成所有测试数据")
def generate_all_test_data(
    member_count: int = Query(20, ge=1, description="会员数量"),
    db: Session = Depends(get_db)
):
    """
    一键生成所有测试数据
    """
    results = {}
    
    # 1. 生成会员
    result = generate_test_members(count=member_count, db=db)
    results["members"] = result
    
    # 2. 生成会员卡
    result = generate_test_member_cards(member_count=member_count, cards_per_member=2, db=db)
    results["member_cards"] = result
    
    # 3. 生成即将到期的会员卡
    result = generate_expiring_cards(count=5, db=db)
    results["expiring_cards"] = result
    
    # 4. 生成促销活动
    result = generate_test_promotions(count=3, db=db)
    results["promotions"] = result
    
    # 5. 为活动生成优惠券
    if "promotions" in results and results["promotions"]["created_count"] > 0:
        for promo in results["promotions"]["promotions"]:
            coupon_result = generate_test_coupons(promotion_id=promo["id"], quantity=20, db=db)
            results[f"coupons_{promo['id']}"] = coupon_result
    
    return {
        "message": "所有测试数据生成完成",
        "results": results
    }


@router.get("/stats", summary="获取系统数据统计")
def get_system_stats(db: Session = Depends(get_db)):
    """
    获取系统数据统计信息
    """
    from sqlalchemy import func
    
    # 会员统计
    members, total_members = member_crud.get_list(db, skip=0, limit=1)
    
    # 会员卡统计
    from models.member import MemberCard
    total_cards = db.query(func.count(MemberCard.id)).filter(MemberCard.is_deleted == 0).scalar()
    
    # 活动统计
    from models.promotion import Promotion
    total_promotions = db.query(func.count(Promotion.id)).filter(Promotion.is_deleted == 0).scalar()
    active_promotions = db.query(func.count(Promotion.id)).filter(
        Promotion.is_deleted == 0,
        Promotion.status == PromotionStatus.ACTIVE.value
    ).scalar()
    
    # 优惠券统计
    from models.promotion import Coupon
    total_coupons = db.query(func.count(Coupon.id)).scalar()
    
    # 提醒统计
    from models.reminder import RenewalReminder
    total_reminders = db.query(func.count(RenewalReminder.id)).scalar()
    pending_reminders = db.query(func.count(RenewalReminder.id)).filter(
        RenewalReminder.status == "pending"
    ).scalar()
    
    return {
        "members": {
            "total": total_members
        },
        "member_cards": {
            "total": total_cards
        },
        "promotions": {
            "total": total_promotions,
            "active": active_promotions
        },
        "coupons": {
            "total": total_coupons
        },
        "reminders": {
            "total": total_reminders,
            "pending": pending_reminders
        }
    }
