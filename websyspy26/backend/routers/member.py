"""
会员相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from config.database import get_db
from schemas.member import (
    Member, MemberCreate, MemberUpdate, MemberListResponse,
    MemberCard, MemberCardCreate, MemberCardUpdate
)
from crud.member import member_crud, member_card_crud

router = APIRouter(prefix="/api/members", tags=["会员管理"])


@router.get("/", response_model=MemberListResponse, summary="获取会员列表")
def get_members(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词（姓名、手机号、会员编号）"),
    level: Optional[str] = Query(None, description="会员等级"),
    status: Optional[str] = Query(None, description="会员状态"),
    db: Session = Depends(get_db)
):
    """
    获取会员列表，支持分页和筛选
    """
    skip = (page - 1) * page_size
    members, total = member_crud.get_list(
        db, skip=skip, limit=page_size,
        keyword=keyword, level=level, status=status
    )
    return MemberListResponse(
        total=total,
        items=members,
        page=page,
        page_size=page_size
    )


@router.get("/{member_id}", response_model=Member, summary="获取会员详情")
def get_member(member_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取会员详情
    """
    db_member = member_crud.get_by_id(db, member_id=member_id)
    if db_member is None:
        raise HTTPException(status_code=404, detail="会员不存在")
    return db_member


@router.post("/", response_model=Member, summary="创建会员")
def create_member(member_in: MemberCreate, db: Session = Depends(get_db)):
    """
    创建新会员
    """
    # 检查会员编号是否已存在
    existing = member_crud.get_by_member_no(db, member_no=member_in.member_no)
    if existing:
        raise HTTPException(status_code=400, detail="会员编号已存在")
    
    # 检查手机号是否已存在
    existing = member_crud.get_by_phone(db, phone=member_in.phone)
    if existing:
        raise HTTPException(status_code=400, detail="手机号已存在")
    
    return member_crud.create(db, member_in=member_in)


@router.put("/{member_id}", response_model=Member, summary="更新会员")
def update_member(
    member_id: int,
    member_in: MemberUpdate,
    db: Session = Depends(get_db)
):
    """
    更新会员信息
    """
    db_member = member_crud.get_by_id(db, member_id=member_id)
    if db_member is None:
        raise HTTPException(status_code=404, detail="会员不存在")
    
    return member_crud.update(db, db_member=db_member, member_in=member_in)


@router.delete("/{member_id}", response_model=Member, summary="删除会员")
def delete_member(member_id: int, db: Session = Depends(get_db)):
    """
    逻辑删除会员
    """
    db_member = member_crud.get_by_id(db, member_id=member_id)
    if db_member is None:
        raise HTTPException(status_code=404, detail="会员不存在")
    
    return member_crud.delete(db, db_member=db_member)


@router.get("/{member_id}/cards", response_model=List[MemberCard], summary="获取会员的会员卡")
def get_member_cards(member_id: int, db: Session = Depends(get_db)):
    """
    获取会员的所有会员卡
    """
    db_member = member_crud.get_by_id(db, member_id=member_id)
    if db_member is None:
        raise HTTPException(status_code=404, detail="会员不存在")
    
    return member_card_crud.get_by_member_id(db, member_id=member_id)


@router.post("/cards/", response_model=MemberCard, summary="创建会员卡")
def create_member_card(card_in: MemberCardCreate, db: Session = Depends(get_db)):
    """
    为会员创建会员卡
    """
    # 检查会员是否存在
    db_member = member_crud.get_by_id(db, member_id=card_in.member_id)
    if db_member is None:
        raise HTTPException(status_code=404, detail="会员不存在")
    
    # 检查卡号是否已存在
    existing = member_card_crud.get_by_card_no(db, card_no=card_in.card_no)
    if existing:
        raise HTTPException(status_code=400, detail="会员卡编号已存在")
    
    return member_card_crud.create(db, card_in=card_in)


@router.put("/cards/{card_id}", response_model=MemberCard, summary="更新会员卡")
def update_member_card(
    card_id: int,
    card_in: MemberCardUpdate,
    db: Session = Depends(get_db)
):
    """
    更新会员卡信息
    """
    db_card = member_card_crud.get_by_id(db, card_id=card_id)
    if db_card is None:
        raise HTTPException(status_code=404, detail="会员卡不存在")
    
    return member_card_crud.update(db, db_card=db_card, card_in=card_in)


@router.delete("/cards/{card_id}", response_model=MemberCard, summary="删除会员卡")
def delete_member_card(card_id: int, db: Session = Depends(get_db)):
    """
    逻辑删除会员卡
    """
    db_card = member_card_crud.get_by_id(db, card_id=card_id)
    if db_card is None:
        raise HTTPException(status_code=404, detail="会员卡不存在")
    
    return member_card_crud.delete(db, db_card=db_card)


@router.post("/cards/{card_id}/renew", response_model=MemberCard, summary="会员卡续费")
def renew_member_card(
    card_id: int,
    renew_days: int = Query(..., description="续费天数"),
    amount: float = Query(..., description="续费金额"),
    method: str = Query("offline", description="续费方式（offline/online）"),
    db: Session = Depends(get_db)
):
    """
    会员卡续费
    """
    db_card = member_card_crud.get_by_id(db, card_id=card_id)
    if db_card is None:
        raise HTTPException(status_code=404, detail="会员卡不存在")
    
    from datetime import timedelta
    new_valid_to = db_card.valid_to + timedelta(days=renew_days)
    
    return member_card_crud.renew(
        db, db_card=db_card,
        new_valid_to=new_valid_to,
        amount=amount,
        method=method
    )
