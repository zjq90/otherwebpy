"""
促销活动相关CRUD操作
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime
import json
from models.promotion import Promotion, Coupon, MemberCoupon, PromotionStatus, CouponStatus, TargetType
from schemas.promotion import PromotionCreate, PromotionUpdate, CouponCreate


class PromotionCRUD:
    """促销活动CRUD操作类"""

    def get_by_id(self, db: Session, promotion_id: int) -> Optional[Promotion]:
        """根据ID获取活动"""
        return db.query(Promotion).filter(Promotion.id == promotion_id, Promotion.is_deleted == 0).first()

    def get_list(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 10,
        keyword: Optional[str] = None,
        type: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple[List[Promotion], int]:
        """
        获取活动列表
        返回：(活动列表, 总数)
        """
        query = db.query(Promotion).filter(Promotion.is_deleted == 0)
        
        if keyword:
            query = query.filter(Promotion.name.contains(keyword))
        
        if type:
            query = query.filter(Promotion.type == type)
        
        if status:
            query = query.filter(Promotion.status == status)
        
        total = query.count()
        promotions = query.order_by(Promotion.created_at.desc()).offset(skip).limit(limit).all()
        
        return promotions, total

    def get_active_promotions(self, db: Session) -> List[Promotion]:
        """获取所有进行中的活动"""
        now = datetime.now()
        return db.query(Promotion).filter(
            Promotion.is_deleted == 0,
            Promotion.status == PromotionStatus.ACTIVE.value,
            Promotion.valid_from <= now,
            Promotion.valid_to >= now
        ).all()

    def create(self, db: Session, promotion_in: PromotionCreate) -> Promotion:
        """创建活动"""
        db_promotion = Promotion(**promotion_in.model_dump())
        db.add(db_promotion)
        db.commit()
        db.refresh(db_promotion)
        return db_promotion

    def update(self, db: Session, db_promotion: Promotion, promotion_in: PromotionUpdate) -> Promotion:
        """更新活动"""
        update_data = promotion_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_promotion, key, value)
        db.commit()
        db.refresh(db_promotion)
        return db_promotion

    def start(self, db: Session, db_promotion: Promotion) -> Promotion:
        """开始活动"""
        db_promotion.status = PromotionStatus.ACTIVE.value
        db.commit()
        db.refresh(db_promotion)
        return db_promotion

    def end(self, db: Session, db_promotion: Promotion) -> Promotion:
        """结束活动"""
        db_promotion.status = PromotionStatus.ENDED.value
        db.commit()
        db.refresh(db_promotion)
        return db_promotion

    def delete(self, db: Session, db_promotion: Promotion) -> Promotion:
        """逻辑删除活动"""
        db_promotion.is_deleted = 1
        db.commit()
        return db_promotion

    def get_target_members(self, db: Session, db_promotion: Promotion) -> List[int]:
        """
        获取活动的目标会员ID列表
        """
        if db_promotion.target_type == TargetType.ALL.value:
            # 全部会员
            from models.member import Member
            members = db.query(Member.id).filter(Member.is_deleted == 0).all()
            return [m[0] for m in members]
        
        elif db_promotion.target_type == TargetType.SLEEPING.value:
            # 沉睡会员
            from models.member import Member, MemberStatus
            members = db.query(Member.id).filter(
                Member.is_deleted == 0,
                Member.status == MemberStatus.SLEEPING.value
            ).all()
            return [m[0] for m in members]
        
        elif db_promotion.target_type == TargetType.HIGH_VALUE.value:
            # 高价值会员（累计消费>=10000）
            from models.member import Member
            members = db.query(Member.id).filter(
                Member.is_deleted == 0,
                Member.total_consumption >= 10000.0
            ).all()
            return [m[0] for m in members]
        
        elif db_promotion.target_type == TargetType.SPECIFIC.value:
            # 指定会员
            if db_promotion.target_member_ids:
                try:
                    return json.loads(db_promotion.target_member_ids)
                except:
                    return []
            return []
        
        return []


class CouponCRUD:
    """优惠券CRUD操作类"""

    def get_by_id(self, db: Session, coupon_id: int) -> Optional[Coupon]:
        """根据ID获取优惠券"""
        return db.query(Coupon).filter(Coupon.id == coupon_id).first()

    def get_by_coupon_no(self, db: Session, coupon_no: str) -> Optional[Coupon]:
        """根据券号获取优惠券"""
        return db.query(Coupon).filter(Coupon.coupon_no == coupon_no).first()

    def get_by_promotion_id(self, db: Session, promotion_id: int) -> List[Coupon]:
        """获取活动下的所有优惠券"""
        return db.query(Coupon).filter(Coupon.promotion_id == promotion_id).all()

    def get_available_by_promotion(self, db: Session, promotion_id: int) -> List[Coupon]:
        """获取活动下可用的优惠券"""
        return db.query(Coupon).filter(
            Coupon.promotion_id == promotion_id,
            Coupon.status == CouponStatus.AVAILABLE.value
        ).all()

    def create(self, db: Session, coupon_in: CouponCreate) -> Coupon:
        """创建优惠券"""
        db_coupon = Coupon(**coupon_in.model_dump())
        db.add(db_coupon)
        db.commit()
        db.refresh(db_coupon)
        return db_coupon

    def claim(self, db: Session, db_coupon: Coupon) -> Coupon:
        """领取优惠券"""
        db_coupon.status = CouponStatus.CLAIMED.value
        db_coupon.claimed_at = datetime.now()
        db.commit()
        db.refresh(db_coupon)
        return db_coupon

    def use(self, db: Session, db_coupon: Coupon) -> Coupon:
        """使用优惠券"""
        db_coupon.status = CouponStatus.USED.value
        db_coupon.used_at = datetime.now()
        db.commit()
        db.refresh(db_coupon)
        return db_coupon

    def expire(self, db: Session, db_coupon: Coupon) -> Coupon:
        """过期优惠券"""
        db_coupon.status = CouponStatus.EXPIRED.value
        db.commit()
        db.refresh(db_coupon)
        return db_coupon


class MemberCouponCRUD:
    """会员优惠券关联CRUD操作类"""

    def get_by_member_and_coupon(self, db: Session, member_id: int, coupon_id: int) -> Optional[MemberCoupon]:
        """根据会员ID和优惠券ID获取关联"""
        return db.query(MemberCoupon).filter(
            MemberCoupon.member_id == member_id,
            MemberCoupon.coupon_id == coupon_id
        ).first()

    def get_by_member_id(self, db: Session, member_id: int, status: Optional[str] = None) -> List[MemberCoupon]:
        """获取会员的优惠券"""
        query = db.query(MemberCoupon).filter(MemberCoupon.member_id == member_id)
        if status:
            query = query.filter(MemberCoupon.status == status)
        return query.order_by(MemberCoupon.created_at.desc()).all()

    def count_by_member_and_promotion(self, db: Session, member_id: int, promotion_id: int) -> int:
        """统计会员在某个活动中已领取的优惠券数量"""
        return db.query(MemberCoupon).filter(
            MemberCoupon.member_id == member_id,
            Coupon.promotion_id == promotion_id,
            MemberCoupon.coupon_id == Coupon.id
        ).count()

    def create(self, db: Session, member_id: int, coupon_id: int) -> MemberCoupon:
        """创建会员优惠券关联"""
        db_member_coupon = MemberCoupon(
            member_id=member_id,
            coupon_id=coupon_id,
            status="claimed"
        )
        db.add(db_member_coupon)
        db.commit()
        db.refresh(db_member_coupon)
        return db_member_coupon

    def use(self, db: Session, db_member_coupon: MemberCoupon) -> MemberCoupon:
        """使用会员优惠券"""
        db_member_coupon.status = "used"
        db_member_coupon.used_at = datetime.now()
        db.commit()
        db.refresh(db_member_coupon)
        return db_member_coupon


# 创建全局CRUD实例
promotion_crud = PromotionCRUD()
coupon_crud = CouponCRUD()
member_coupon_crud = MemberCouponCRUD()
