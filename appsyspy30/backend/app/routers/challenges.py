"""
挑战活动路由模块
处理挑战活动的参与、任务进度、奖励等功能
"""
from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from app.database import get_db
from app.models import User, Challenge, UserChallenge, Achievement
from app.schemas import (
    ChallengeCreate, ChallengeResponse,
    UserChallengeCreate, UserChallengeUpdate, UserChallengeResponse,
    APIResponse, PaginatedResponse
)
from app.auth import get_current_active_user
from math import ceil

router = APIRouter(prefix="/challenges", tags=["挑战活动"])


@router.post("", response_model=ChallengeResponse, summary="创建挑战活动（管理员）")
async def create_challenge(
    challenge_data: ChallengeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建新的挑战活动
    通常由管理员创建
    """
    # 验证日期逻辑
    if challenge_data.start_date >= challenge_data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="开始日期必须早于结束日期"
        )
    
    new_challenge = Challenge(
        title=challenge_data.title,
        description=challenge_data.description,
        challenge_type=challenge_data.challenge_type,
        duration_days=challenge_data.duration_days,
        start_date=challenge_data.start_date,
        end_date=challenge_data.end_date,
        reward_points=challenge_data.reward_points,
        reward_description=challenge_data.reward_description,
        max_participants=challenge_data.max_participants
    )
    
    db.add(new_challenge)
    db.commit()
    db.refresh(new_challenge)
    
    return ChallengeResponse.from_orm(new_challenge)


@router.get("", response_model=PaginatedResponse, summary="获取挑战活动列表")
async def get_challenges(
    challenge_type: Optional[str] = Query(None, description="挑战类型筛选"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取挑战活动列表
    
    - **challenge_type**: 挑战类型 (fat_loss, steps, strength等)
    - **is_active**: 是否只显示激活的活动
    """
    query = db.query(Challenge)
    
    if challenge_type:
        query = query.filter(Challenge.challenge_type == challenge_type)
    
    if is_active is not None:
        query = query.filter(Challenge.is_active == is_active)
    else:
        query = query.filter(Challenge.is_active == True)
    
    query = query.order_by(desc(Challenge.start_date))
    
    total = query.count()
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    
    challenges = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=[ChallengeResponse.from_orm(c) for c in challenges],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{challenge_id}", response_model=ChallengeResponse, summary="获取挑战活动详情")
async def get_challenge(
    challenge_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取单条挑战活动详情
    """
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="挑战活动不存在"
        )
    
    return ChallengeResponse.from_orm(challenge)


@router.post("/join", response_model=UserChallengeResponse, summary="参与挑战活动")
async def join_challenge(
    join_data: UserChallengeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    参与挑战活动
    
    - **challenge_id**: 挑战活动ID
    """
    # 检查挑战活动是否存在且激活
    challenge = db.query(Challenge).filter(
        Challenge.id == join_data.challenge_id,
        Challenge.is_active == True
    ).first()
    
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="挑战活动不存在或已结束"
        )
    
    # 检查是否在活动时间内
    today = date.today()
    if today < challenge.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="挑战活动尚未开始"
        )
    if today > challenge.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="挑战活动已结束"
        )
    
    # 检查是否已参与
    existing_participation = db.query(UserChallenge).filter(
        UserChallenge.user_id == current_user.id,
        UserChallenge.challenge_id == join_data.challenge_id
    ).first()
    
    if existing_participation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已参与此挑战活动"
        )
    
    # 检查人数限制
    if challenge.max_participants and challenge.current_participants >= challenge.max_participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="参与人数已达上限"
        )
    
    # 创建参与记录
    new_user_challenge = UserChallenge(
        user_id=current_user.id,
        challenge_id=join_data.challenge_id,
        progress=0.0,
        is_completed=False,
        reward_claimed=False
    )
    
    db.add(new_user_challenge)
    challenge.current_participants += 1
    db.commit()
    db.refresh(new_user_challenge)
    
    response = UserChallengeResponse.from_orm(new_user_challenge)
    response.challenge = ChallengeResponse.from_orm(challenge)
    
    return response


@router.get("/my/participating", response_model=PaginatedResponse, summary="获取我参与的挑战")
async def get_my_challenges(
    is_completed: Optional[bool] = Query(None, description="是否已完成"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户参与的挑战活动列表
    
    - **is_completed**: 是否只显示已完成的挑战
    """
    query = db.query(UserChallenge).filter(
        UserChallenge.user_id == current_user.id
    ).join(Challenge).filter(Challenge.is_active == True)
    
    if is_completed is not None:
        query = query.filter(UserChallenge.is_completed == is_completed)
    
    query = query.order_by(desc(UserChallenge.joined_at))
    
    total = query.count()
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    
    user_challenges = query.offset((page - 1) * page_size).limit(page_size).all()
    
    responses = []
    for uc in user_challenges:
        response = UserChallengeResponse.from_orm(uc)
        response.challenge = ChallengeResponse.from_orm(uc.challenge)
        responses.append(response)
    
    return PaginatedResponse(
        items=responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.put("/progress/{user_challenge_id}", response_model=UserChallengeResponse, summary="更新挑战进度")
async def update_challenge_progress(
    user_challenge_id: int,
    progress_data: UserChallengeUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新挑战活动的完成进度
    
    - **user_challenge_id**: 用户挑战记录ID
    - **progress**: 完成进度(0-100)
    - **daily_data**: 每日数据(JSON格式)
    """
    user_challenge = db.query(UserChallenge).filter(
        UserChallenge.id == user_challenge_id,
        UserChallenge.user_id == current_user.id
    ).first()
    
    if not user_challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到该挑战记录"
        )
    
    if user_challenge.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该挑战已完成"
        )
    
    # 更新进度
    user_challenge.progress = progress_data.progress
    if progress_data.daily_data:
        user_challenge.daily_data = progress_data.daily_data
    
    # 检查是否完成
    if user_challenge.progress >= 100.0:
        user_challenge.is_completed = True
        user_challenge.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user_challenge)
    
    response = UserChallengeResponse.from_orm(user_challenge)
    response.challenge = ChallengeResponse.from_orm(user_challenge.challenge)
    
    return response


@router.post("/claim-reward/{user_challenge_id}", response_model=APIResponse, summary="领取挑战奖励")
async def claim_challenge_reward(
    user_challenge_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    领取挑战完成后的奖励
    """
    user_challenge = db.query(UserChallenge).filter(
        UserChallenge.id == user_challenge_id,
        UserChallenge.user_id == current_user.id
    ).first()
    
    if not user_challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到该挑战记录"
        )
    
    if not user_challenge.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="挑战尚未完成，无法领取奖励"
        )
    
    if user_challenge.reward_claimed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="奖励已领取"
        )
    
    challenge = user_challenge.challenge
    
    # 发放积分奖励
    if challenge.reward_points > 0:
        current_user.points += challenge.reward_points
    
    # 标记奖励已领取
    user_challenge.reward_claimed = True
    
    # 创建成就记录
    achievement = Achievement(
        user_id=current_user.id,
        title=f"完成挑战: {challenge.title}",
        description=challenge.description,
        achievement_type=challenge.challenge_type,
        points_awarded=challenge.reward_points
    )
    db.add(achievement)
    
    db.commit()
    
    return APIResponse(
        code=200,
        message="奖励领取成功",
        data={
            "points_awarded": challenge.reward_points,
            "new_points_balance": current_user.points
        }
    )


@router.get("/my/achievements", response_model=PaginatedResponse, summary="获取我的成就")
async def get_my_achievements(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户获得的成就列表
    """
    query = db.query(Achievement).filter(
        Achievement.user_id == current_user.id
    ).order_by(desc(Achievement.created_at))
    
    total = query.count()
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    
    achievements = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=achievements,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
