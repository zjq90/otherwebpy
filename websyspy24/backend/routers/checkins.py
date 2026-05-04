"""
签到管理API路由模块
提供会员签到验证、签到记录查询等功能
支持刷卡、扫码、人脸识别三种签到方式
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import date, datetime, timedelta
import json

from database import get_db
from models import Member, CheckIn
from schemas import (
    CheckInCreate, CheckInResponse, CheckInVerifyRequest, 
    CheckInType, ApiResponse, PaginatedResponse
)

# 创建路由实例
router = APIRouter(
    prefix="/api/checkins",
    tags=["签到管理"]
)


@router.post("/verify", response_model=ApiResponse, summary="签到验证")
def verify_checkin(
    verify_data: CheckInVerifyRequest,
    db: Session = Depends(get_db)
):
    """
    签到验证接口，支持刷卡、扫码、人脸识别三种方式
    自动判断会籍有效性并记录签到结果
    
    - **check_in_type**: 签到方式 (card: 刷卡, qr: 扫码, face: 人脸识别)
    - **identifier**: 识别信息（卡号、二维码内容、人脸数据等）
    - **device_no**: 签到设备编号（可选）
    """
    # 根据签到方式查询会员
    member = None
    verification_details = {}
    
    if verify_data.check_in_type == CheckInType.CARD:
        # 刷卡签到：根据卡号查询
        member = db.query(Member).filter(
            Member.card_no == verify_data.identifier
        ).first()
        verification_details["card_no"] = verify_data.identifier
        
    elif verify_data.check_in_type == CheckInType.QR:
        # 扫码签到：根据二维码内容查询
        member = db.query(Member).filter(
            Member.qr_code == verify_data.identifier
        ).first()
        verification_details["qr_code"] = verify_data.identifier
        
    elif verify_data.check_in_type == CheckInType.FACE:
        # 人脸识别签到：根据人脸数据查询
        # 实际应用中这里需要人脸比对算法，这里简化处理
        # 假设face_data是存储的人脸特征，直接匹配
        member = db.query(Member).filter(
            Member.face_data == verify_data.identifier
        ).first()
        verification_details["face_matched"] = bool(member)
    
    # 构建签到记录
    check_in = CheckIn(
        member_id=member.id if member else 0,
        check_in_type=verify_data.check_in_type.value,
        check_in_time=datetime.now(),
        device_no=verify_data.device_no,
        verification_details=json.dumps(verification_details, ensure_ascii=False)
    )
    
    # 检查会员是否存在
    if not member:
        check_in.status = "failed"
        check_in.fail_reason = "会员不存在"
        db.add(check_in)
        db.commit()
        
        return ApiResponse(
            success=False,
            message="签到失败：会员不存在",
            data={
                "check_in_id": check_in.id,
                "check_in_type": verify_data.check_in_type.value,
                "status": "failed",
                "fail_reason": "会员不存在"
            }
        )
    
    # 更新签到记录的会员ID
    check_in.member_id = member.id
    
    # 检查会籍有效性
    today = date.today()
    is_valid = True
    fail_reason = None
    
    if member.status != "active":
        is_valid = False
        fail_reason = f"会员状态异常: {member.status}"
    elif member.membership_end < today:
        is_valid = False
        fail_reason = "会籍已过期"
    
    if not is_valid:
        check_in.status = "failed"
        check_in.fail_reason = fail_reason
        db.add(check_in)
        db.commit()
        
        return ApiResponse(
            success=False,
            message=f"签到失败：{fail_reason}",
            data={
                "check_in_id": check_in.id,
                "member_id": member.id,
                "member_name": member.name,
                "check_in_type": verify_data.check_in_type.value,
                "status": "failed",
                "fail_reason": fail_reason
            }
        )
    
    # 签到成功
    check_in.status = "success"
    db.add(check_in)
    db.commit()
    db.refresh(check_in)
    
    return ApiResponse(
        success=True,
        message="签到成功",
        data={
            "check_in_id": check_in.id,
            "member_id": member.id,
            "member_name": member.name,
            "member_no": member.member_no,
            "membership_type": member.membership_type,
            "membership_end": member.membership_end.isoformat(),
            "check_in_type": verify_data.check_in_type.value,
            "check_in_time": check_in.check_in_time.isoformat(),
            "status": "success"
        }
    )


@router.get("/", response_model=PaginatedResponse, summary="获取签到记录列表")
def get_checkins(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    member_id: Optional[int] = Query(None, description="会员ID"),
    check_in_type: Optional[str] = Query(None, description="签到方式"),
    status: Optional[str] = Query(None, description="签到状态"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    db: Session = Depends(get_db)
):
    """
    分页获取签到记录列表，支持多条件筛选
    
    - **page**: 页码
    - **page_size**: 每页数量
    - **member_id**: 按会员ID筛选
    - **check_in_type**: 按签到方式筛选
    - **status**: 按签到状态筛选
    - **start_date**: 开始日期
    - **end_date**: 结束日期
    """
    # 构建查询
    query = db.query(CheckIn)
    
    # 会员ID筛选
    if member_id:
        query = query.filter(CheckIn.member_id == member_id)
    
    # 签到方式筛选
    if check_in_type:
        query = query.filter(CheckIn.check_in_type == check_in_type)
    
    # 状态筛选
    if status:
        query = query.filter(CheckIn.status == status)
    
    # 日期范围筛选
    if start_date:
        query = query.filter(CheckIn.check_in_time >= start_date)
    if end_date:
        query = query.filter(CheckIn.check_in_time < end_date + timedelta(days=1))
    
    # 计算总数
    total = query.count()
    
    # 分页查询
    offset = (page - 1) * page_size
    checkins = query.order_by(CheckIn.check_in_time.desc()).offset(offset).limit(page_size).all()
    
    # 转换为响应模型，关联会员信息
    items = []
    for checkin in checkins:
        member = db.query(Member).filter(Member.id == checkin.member_id).first()
        item = CheckInResponse.model_validate(checkin).model_dump()
        item["member_name"] = member.name if member else "未知会员"
        item["member_no"] = member.member_no if member else ""
        items.append(item)
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{checkin_id}", response_model=CheckInResponse, summary="根据ID获取签到记录详情")
def get_checkin(
    checkin_id: int,
    db: Session = Depends(get_db)
):
    """
    根据签到记录ID获取详细信息
    
    - **checkin_id**: 签到记录ID
    """
    checkin = db.query(CheckIn).filter(CheckIn.id == checkin_id).first()
    if not checkin:
        raise HTTPException(status_code=404, detail=f"签到记录ID {checkin_id} 不存在")
    return checkin


@router.get("/today/stats", response_model=ApiResponse, summary="获取今日签到统计")
def get_today_stats(
    db: Session = Depends(get_db)
):
    """
    获取今日签到统计数据
    """
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())
    
    # 查询今日签到总数
    total = db.query(CheckIn).filter(
        CheckIn.check_in_time >= start_of_day,
        CheckIn.check_in_time <= end_of_day
    ).count()
    
    # 查询今日成功签到数
    success = db.query(CheckIn).filter(
        CheckIn.check_in_time >= start_of_day,
        CheckIn.check_in_time <= end_of_day,
        CheckIn.status == "success"
    ).count()
    
    # 查询今日失败签到数
    failed = db.query(CheckIn).filter(
        CheckIn.check_in_time >= start_of_day,
        CheckIn.check_in_time <= end_of_day,
        CheckIn.status == "failed"
    ).count()
    
    # 按签到方式统计
    card_count = db.query(CheckIn).filter(
        CheckIn.check_in_time >= start_of_day,
        CheckIn.check_in_time <= end_of_day,
        CheckIn.check_in_type == "card"
    ).count()
    
    qr_count = db.query(CheckIn).filter(
        CheckIn.check_in_time >= start_of_day,
        CheckIn.check_in_time <= end_of_day,
        CheckIn.check_in_type == "qr"
    ).count()
    
    face_count = db.query(CheckIn).filter(
        CheckIn.check_in_time >= start_of_day,
        CheckIn.check_in_time <= end_of_day,
        CheckIn.check_in_type == "face"
    ).count()
    
    return ApiResponse(
        success=True,
        message="获取统计成功",
        data={
            "date": today.isoformat(),
            "total": total,
            "success": success,
            "failed": failed,
            "by_type": {
                "card": card_count,
                "qr": qr_count,
                "face": face_count
            }
        }
    )


@router.post("/quick/{member_id}", response_model=ApiResponse, summary="快速签到（测试用）")
def quick_checkin(
    member_id: int,
    check_in_type: CheckInType = Query(default=CheckInType.CARD, description="签到方式"),
    db: Session = Depends(get_db)
):
    """
    快速签到接口，主要用于测试
    根据会员ID直接签到，跳过验证步骤
    
    - **member_id**: 会员ID
    - **check_in_type**: 签到方式
    """
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail=f"会员ID {member_id} 不存在")
    
    # 检查会籍有效性
    today = date.today()
    if member.status != "active":
        return ApiResponse(
            success=False,
            message=f"签到失败：会员状态异常 - {member.status}",
            data={"member_id": member_id}
        )
    
    if member.membership_end < today:
        return ApiResponse(
            success=False,
            message="签到失败：会籍已过期",
            data={"member_id": member_id}
        )
    
    # 创建签到记录
    check_in = CheckIn(
        member_id=member_id,
        check_in_type=check_in_type.value,
        check_in_time=datetime.now(),
        status="success"
    )
    
    db.add(check_in)
    db.commit()
    db.refresh(check_in)
    
    return ApiResponse(
        success=True,
        message="签到成功",
        data={
            "check_in_id": check_in.id,
            "member_id": member.id,
            "member_name": member.name,
            "check_in_time": check_in.check_in_time.isoformat()
        }
    )
