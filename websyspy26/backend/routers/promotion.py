"""
促销活动相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from config.database import get_db
from schemas.promotion import (
    Promotion, PromotionCreate, PromotionUpdate, PromotionListResponse,
    Coupon, MemberCoupon
)
from crud.promotion import promotion_crud, coupon_crud, member_coupon_crud
from crud.member import member_crud

router = APIRouter(prefix="/api/promotions", tags=["促销活动管理"])


@router.get("/", response_model=PromotionListResponse, summary="获取促销活动列表")
def get_promotions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    type: Optional[str] = Query(None, description="活动类型"),
    status: Optional[str] = Query(None, description="活动状态"),
    db: Session = Depends(get_db)
):
    """
    获取促销活动列表，支持分页和筛选
    """
    skip = (page - 1) * page_size
    promotions, total = promotion_crud.get_list(
        db, skip=skip, limit=page_size,
        keyword=keyword, type=type, status=status
    )
    return PromotionListResponse(
        total=total,
        items=promotions,
        page=page,
        page_size=page_size
    )


@router.get("/active", response_model=List[Promotion], summary="获取进行中的活动")
def get_active_promotions(db: Session = Depends(get_db)):
    """
    获取所有进行中的促销活动
    """
    return promotion_crud.get_active_promotions(db)


@router.get("/{promotion_id}", response_model=Promotion, summary="获取活动详情")
def get_promotion(promotion_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取活动详情
    """
    db_promotion = promotion_crud.get_by_id(db, promotion_id=promotion_id)
    if db_promotion is None:
        raise HTTPException(status_code=404, detail="活动不存在")
    return db_promotion


@router.post("/", response_model=Promotion, summary="创建促销活动")
def create_promotion(promotion_in: PromotionCreate, db: Session = Depends(get_db)):
    """
    创建新的促销活动
    """
    return promotion_crud.create(db, promotion_in=promotion_in)


@router.put("/{promotion_id}", response_model=Promotion, summary="更新活动")
def update_promotion(
    promotion_id: int,
    promotion_in: PromotionUpdate,
    db: Session = Depends(get_db)
):
    """
    更新活动信息
    """
    db_promotion = promotion_crud.get_by_id(db, promotion_id=promotion_id)
    if db_promotion is None:
        raise HTTPException(status_code=404, detail="活动不存在")
    
    return promotion_crud.update(db, db_promotion=db_promotion, promotion_in=promotion_in)


@router.post("/{promotion_id}/start", response_model=Promotion, summary="开始活动")
def start_promotion(promotion_id: int, db: Session = Depends(get_db)):
    """
    开始促销活动
    """
    db_promotion = promotion_crud.get_by_id(db, promotion_id=promotion_id)
    if db_promotion is None:
        raise HTTPException(status_code=404, detail="活动不存在")
    
    return promotion_crud.start(db, db_promotion=db_promotion)


@router.post("/{promotion_id}/end", response_model=Promotion, summary="结束活动")
def end_promotion(promotion_id: int, db: Session = Depends(get_db)):
    """
    结束促销活动
    """
    db_promotion = promotion_crud.get_by_id(db, promotion_id=promotion_id)
    if db_promotion is None:
        raise HTTPException(status_code=404, detail="活动不存在")
    
    return promotion_crud.end(db, db_promotion=db_promotion)


@router.delete("/{promotion_id}", response_model=Promotion, summary="删除活动")
def delete_promotion(promotion_id: int, db: Session = Depends(get_db)):
    """
    逻辑删除活动
    """
    db_promotion = promotion_crud.get_by_id(db, promotion_id=promotion_id)
    if db_promotion is None:
        raise HTTPException(status_code=404, detail="活动不存在")
    
    return promotion_crud.delete(db, db_promotion=db_promotion)


@router.get("/{promotion_id}/coupons", response_model=List[Coupon], summary="获取活动优惠券")
def get_promotion_coupons(promotion_id: int, db: Session = Depends(get_db)):
    """
    获取活动下的所有优惠券
    """
    db_promotion = promotion_crud.get_by_id(db, promotion_id=promotion_id)
    if db_promotion is None:
        raise HTTPException(status_code=404, detail="活动不存在")
    
    return coupon_crud.get_by_promotion_id(db, promotion_id=promotion_id)


@router.post("/{promotion_id}/generate-coupons", response_model=List[Coupon], summary="批量生成优惠券")
def generate_coupons(
    promotion_id: int,
    quantity: int = Query(1, ge=1, le=1000, description="生成数量"),
    db: Session = Depends(get_db)
):
    """
    为活动批量生成优惠券
    """
    from datetime import datetime
    import uuid
    
    db_promotion = promotion_crud.get_by_id(db, promotion_id=promotion_id)
    if db_promotion is None:
        raise HTTPException(status_code=404, detail="活动不存在")
    
    coupons = []
    for i in range(quantity):
        coupon_no = f"CP{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        
        from schemas.promotion import CouponCreate
        coupon_in = CouponCreate(
            coupon_no=coupon_no,
            promotion_id=promotion_id,
            type=db_promotion.type,
            name=db_promotion.name,
            discount_rate=db_promotion.discount_rate,
            full_amount=db_promotion.full_amount,
            reduction_amount=db_promotion.reduction_amount,
            experience_amount=db_promotion.experience_amount,
            valid_from=db_promotion.valid_from,
            valid_to=db_promotion.valid_to
        )
        
        coupon = coupon_crud.create(db, coupon_in=coupon_in)
        coupons.append(coupon)
    
    return coupons


@router.post("/{promotion_id}/distribute", summary="定向发放优惠券")
def distribute_promotion(
    promotion_id: int,
    db: Session = Depends(get_db)
):
    """
    定向发放优惠券给目标会员
    """
    db_promotion = promotion_crud.get_by_id(db, promotion_id=promotion_id)
    if db_promotion is None:
        raise HTTPException(status_code=404, detail="活动不存在")
    
    # 获取目标会员ID列表
    target_member_ids = promotion_crud.get_target_members(db, db_promotion=db_promotion)
    
    if not target_member_ids:
        return {"message": "没有符合条件的目标会员", "distributed_count": 0}
    
    # 获取可用的优惠券
    available_coupons = coupon_crud.get_available_by_promotion(db, promotion_id=promotion_id)
    
    if not available_coupons:
        raise HTTPException(status_code=400, detail="活动没有可用的优惠券")
    
    distributed_count = 0
    coupon_index = 0
    
    for member_id in target_member_ids:
        if coupon_index >= len(available_coupons):
            break
        
        # 检查会员是否已领取
        claimed_count = member_coupon_crud.count_by_member_and_promotion(
            db, member_id=member_id, promotion_id=promotion_id
        )
        
        if claimed_count >= db_promotion.per_member_limit:
            continue
        
        # 领取优惠券
        coupon = available_coupons[coupon_index]
        coupon_crud.claim(db, db_coupon=coupon)
        member_coupon_crud.create(db, member_id=member_id, coupon_id=coupon.id)
        
        coupon_index += 1
        distributed_count += 1
    
    return {
        "message": f"成功发放 {distributed_count} 张优惠券",
        "distributed_count": distributed_count,
        "target_count": len(target_member_ids)
    }


@router.get("/members/{member_id}/coupons", response_model=List[MemberCoupon], summary="获取会员优惠券")
def get_member_coupons(
    member_id: int,
    status: Optional[str] = Query(None, description="优惠券状态"),
    db: Session = Depends(get_db)
):
    """
    获取会员的优惠券
    """
    db_member = member_crud.get_by_id(db, member_id=member_id)
    if db_member is None:
        raise HTTPException(status_code=404, detail="会员不存在")
    
    return member_coupon_crud.get_by_member_id(db, member_id=member_id, status=status)
