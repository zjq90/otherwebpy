"""
等级与权益API路由
提供会员等级查询、权益展示等功能
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.member import Member
from app.models.level import MemberLevel, LevelBenefit
from app.schemas.level import (
    MemberLevelResponse,
    LevelBenefitResponse,
    MemberLevelInfo,
)
from app.schemas.common import (
    ApiResponse,
    SuccessResponse,
)
from app.services.level_service import level_service

router = APIRouter(
    prefix="/api/levels",
    tags=["等级与权益"],
    responses={404: {"description": "未找到"}},
)


@router.get(
    "",
    response_model=ApiResponse[List[MemberLevelResponse]],
    summary="获取所有会员等级",
    description="获取系统配置的所有会员等级列表",
)
def get_all_levels(db: Session = Depends(get_db)):
    """
    获取所有会员等级
    """
    # 首先检查数据库中是否有等级配置，如果没有则创建默认配置
    levels = db.query(MemberLevel).order_by(MemberLevel.sort_order).all()
    
    if not levels:
        # 创建默认等级配置
        default_levels = [
            MemberLevel(
                level_code="bronze",
                level_name="铜卡",
                description="普通会员等级，享受基础服务",
                min_consumption=0,
                min_visits=0,
                sort_order=1,
                color_hex="#CD7F32"
            ),
            MemberLevel(
                level_code="silver",
                level_name="银卡",
                description="中级会员等级，享受折扣优惠",
                min_consumption=500000,  # 5000元
                min_visits=0,
                sort_order=2,
                color_hex="#C0C0C0"
            ),
            MemberLevel(
                level_code="gold",
                level_name="金卡",
                description="高级会员等级，享受专属权益",
                min_consumption=2000000,  # 20000元
                min_visits=0,
                sort_order=3,
                color_hex="#FFD700"
            ),
        ]
        
        for level in default_levels:
            db.add(level)
        db.commit()
        
        # 创建默认权益配置
        default_benefits = [
            # 铜卡权益
            LevelBenefit(
                level_code="bronze",
                benefit_code="basic_service",
                benefit_name="基础服务",
                description="享受健身房基础设施使用",
                benefit_type="other",
                sort_order=1
            ),
            # 银卡权益
            LevelBenefit(
                level_code="silver",
                benefit_code="basic_service",
                benefit_name="基础服务",
                description="享受健身房基础设施使用",
                benefit_type="other",
                sort_order=1
            ),
            LevelBenefit(
                level_code="silver",
                benefit_code="course_discount",
                benefit_name="课程折扣",
                description="所有课程享受9折优惠",
                benefit_type="discount",
                value=0.9,
                unit="折",
                sort_order=2
            ),
            LevelBenefit(
                level_code="silver",
                benefit_code="free_body_test",
                benefit_name="免费体测",
                description="每月免费体测1次",
                benefit_type="free",
                value=1,
                unit="次/月",
                sort_order=3
            ),
            # 金卡权益
            LevelBenefit(
                level_code="gold",
                benefit_code="basic_service",
                benefit_name="基础服务",
                description="享受健身房基础设施使用",
                benefit_type="other",
                sort_order=1
            ),
            LevelBenefit(
                level_code="gold",
                benefit_code="course_discount",
                benefit_name="课程折扣",
                description="所有课程享受8折优惠",
                benefit_type="discount",
                value=0.8,
                unit="折",
                sort_order=2
            ),
            LevelBenefit(
                level_code="gold",
                benefit_code="free_body_test",
                benefit_name="免费体测",
                description="每月免费体测2次",
                benefit_type="free",
                value=2,
                unit="次/月",
                sort_order=3
            ),
            LevelBenefit(
                level_code="gold",
                benefit_code="priority_booking",
                benefit_name="优先预约",
                description="课程预约提前24小时开放",
                benefit_type="priority",
                value=24,
                unit="小时",
                sort_order=4
            ),
        ]
        
        for benefit in default_benefits:
            db.add(benefit)
        db.commit()
        
        levels = db.query(MemberLevel).order_by(MemberLevel.sort_order).all()
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=[MemberLevelResponse.model_validate(l) for l in levels]
    )


@router.get(
    "/{level_code}",
    response_model=ApiResponse[MemberLevelResponse],
    summary="获取指定等级详情",
    description="根据等级代码获取等级详情",
)
def get_level(
    level_code: str,
    db: Session = Depends(get_db),
):
    """
    获取指定等级详情
    - **level_code**: 等级代码（bronze/silver/gold）
    """
    level = db.query(MemberLevel).filter(MemberLevel.level_code == level_code).first()
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"等级代码 {level_code} 不存在"
        )
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=MemberLevelResponse.model_validate(level)
    )


@router.get(
    "/{level_code}/benefits",
    response_model=ApiResponse[List[LevelBenefitResponse]],
    summary="获取等级权益",
    description="获取指定会员等级享有的所有权益",
)
def get_level_benefits(
    level_code: str,
    db: Session = Depends(get_db),
):
    """
    获取等级权益
    - **level_code**: 等级代码
    """
    benefits = db.query(LevelBenefit).filter(
        LevelBenefit.level_code == level_code,
        LevelBenefit.is_active == True
    ).order_by(LevelBenefit.sort_order).all()
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=[LevelBenefitResponse.model_validate(b) for b in benefits]
    )


@router.get(
    "/member/{member_id}/info",
    response_model=ApiResponse[MemberLevelInfo],
    summary="获取会员等级信息",
    description="获取指定会员的当前等级、下一等级、权益等详细信息",
)
def get_member_level_info(
    member_id: int,
    db: Session = Depends(get_db),
):
    """
    获取会员等级信息
    - **member_id**: 会员ID
    """
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会员ID {member_id} 不存在"
        )
    
    level_info = level_service.get_member_level_info(db, member)
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=MemberLevelInfo(
            current_level_code=level_info["current_level_code"],
            current_level_name=level_info["current_level_name"],
            current_level_description=level_info["current_level_description"],
            total_consumption=level_info["total_consumption"],
            total_visits=level_info["total_visits"],
            next_level_code=level_info["next_level_code"],
            next_level_name=level_info["next_level_name"],
            consumption_to_next_level=level_info["consumption_to_next_level"],
            visits_to_next_level=level_info["visits_to_next_level"],
            benefits=[LevelBenefitResponse.model_validate(b) for b in level_info["benefits"]]
        )
    )


@router.get(
    "/rules/upgrade",
    summary="获取升级规则",
    description="获取会员等级升级规则说明",
)
def get_upgrade_rules(db: Session = Depends(get_db)):
    """
    获取升级规则
    """
    levels = db.query(MemberLevel).order_by(MemberLevel.sort_order).all()
    
    rules = []
    for level in levels:
        rules.append({
            "level_code": level.level_code,
            "level_name": level.level_name,
            "min_consumption": level.min_consumption,
            "min_consumption_yuan": level.min_consumption / 100,
            "min_visits": level.min_visits,
            "sort_order": level.sort_order,
            "description": level.description
        })
    
    # 添加说明
    explanation = """
会员等级升级规则说明：

1. 升级依据
   - 主要根据累计消费金额自动升级
   - 累计到店次数作为辅助参考

2. 等级划分
   - 铜卡：新会员默认等级
   - 银卡：累计消费满5000元
   - 金卡：累计消费满20000元

3. 等级权益
   - 不同等级享受不同的折扣和专属服务
   - 高级别会员享有低级别会员的所有权益
"""
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data={
            "rules": rules,
            "explanation": explanation.strip()
        }
    )


@router.post(
    "/member/{member_id}/check-upgrade",
    response_model=ApiResponse[dict],
    summary="检查并升级会员等级",
    description="手动触发会员等级检查，如果符合升级条件则自动升级",
)
def check_and_upgrade_member(
    member_id: int,
    db: Session = Depends(get_db),
):
    """
    检查并升级会员等级
    - **member_id**: 会员ID
    """
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会员ID {member_id} 不存在"
        )
    
    old_level = member.current_level
    upgraded, new_level = level_service.check_and_upgrade_level(db, member)
    
    if upgraded:
        return ApiResponse(
            code=200,
            message=f"会员等级已升级：{level_service.get_level_name(old_level)} -> {level_service.get_level_name(new_level)}",
            data={
                "upgraded": True,
                "old_level": old_level,
                "old_level_name": level_service.get_level_name(old_level),
                "new_level": new_level,
                "new_level_name": level_service.get_level_name(new_level)
            }
        )
    else:
        return ApiResponse(
            code=200,
            message=f"会员等级未变化，当前等级：{level_service.get_level_name(old_level)}",
            data={
                "upgraded": False,
                "current_level": old_level,
                "current_level_name": level_service.get_level_name(old_level),
                "total_consumption": member.total_consumption,
                "total_consumption_yuan": member.total_consumption / 100,
                "total_visits": member.total_visits
            }
        )
