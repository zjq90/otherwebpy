from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User, CardType
from app.schemas.schemas import (
    MemberCardCreate, MemberCardResponse, MemberCardUpdate
)
from app.crud.crud import card_crud
from app.core.security import get_current_active_member, get_current_active_admin

router = APIRouter(prefix="/api/cards", tags=["会员卡"])

@router.get("/my", response_model=List[MemberCardResponse])
def get_my_cards(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    cards = card_crud.get_by_user(db, user_id=current_user.id, is_active=is_active)
    
    result = []
    for card in cards:
        categories = []
        for link in card.card_category_links:
            categories.append({
                "id": link.category.id,
                "name": link.category.name,
                "description": link.category.description
            })
        
        result.append(MemberCardResponse(
            id=card.id,
            user_id=card.user_id,
            card_type=card.card_type,
            card_name=card.card_name,
            total_times=card.total_times,
            used_times=card.used_times,
            start_date=card.start_date,
            end_date=card.end_date,
            is_active=card.is_active,
            created_at=card.created_at,
            updated_at=card.updated_at,
            categories=categories
        ))
    
    return result

@router.get("/my-valid", response_model=List[MemberCardResponse])
def get_my_valid_cards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    cards = card_crud.get_active_valid_cards(db, user_id=current_user.id)
    
    result = []
    for card in cards:
        categories = []
        for link in card.card_category_links:
            categories.append({
                "id": link.category.id,
                "name": link.category.name,
                "description": link.category.description
            })
        
        result.append(MemberCardResponse(
            id=card.id,
            user_id=card.user_id,
            card_type=card.card_type,
            card_name=card.card_name,
            total_times=card.total_times,
            used_times=card.used_times,
            start_date=card.start_date,
            end_date=card.end_date,
            is_active=card.is_active,
            created_at=card.created_at,
            updated_at=card.updated_at,
            categories=categories
        ))
    
    return result

@router.get("/{card_id}", response_model=MemberCardResponse)
def get_card_detail(
    card_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    card = card_crud.get_by_id(db, card_id=card_id)
    if not card:
        raise HTTPException(status_code=404, detail="会员卡不存在")
    
    if card.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看该会员卡")
    
    categories = []
    for link in card.card_category_links:
        categories.append({
            "id": link.category.id,
            "name": link.category.name,
            "description": link.category.description
        })
    
    return MemberCardResponse(
        id=card.id,
        user_id=card.user_id,
        card_type=card.card_type,
        card_name=card.card_name,
        total_times=card.total_times,
        used_times=card.used_times,
        start_date=card.start_date,
        end_date=card.end_date,
        is_active=card.is_active,
        created_at=card.created_at,
        updated_at=card.updated_at,
        categories=categories
    )

@router.post("/", response_model=MemberCardResponse, status_code=201)
def create_card(
    card_in: MemberCardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    card = card_crud.create(db, card_in=card_in)
    return get_card_detail(card_id=card.id, db=db, current_user=current_user)

@router.get("/", response_model=List[MemberCardResponse])
def get_all_cards(
    user_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    if user_id:
        cards = card_crud.get_by_user(db, user_id=user_id, is_active=is_active)
    else:
        from app.models.models import MemberCard as DBMemberCard
        query = db.query(DBMemberCard)
        if is_active is not None:
            query = query.filter(DBMemberCard.is_active == is_active)
        cards = query.all()
    
    result = []
    for card in cards:
        categories = []
        for link in card.card_category_links:
            categories.append({
                "id": link.category.id,
                "name": link.category.name,
                "description": link.category.description
            })
        
        result.append(MemberCardResponse(
            id=card.id,
            user_id=card.user_id,
            card_type=card.card_type,
            card_name=card.card_name,
            total_times=card.total_times,
            used_times=card.used_times,
            start_date=card.start_date,
            end_date=card.end_date,
            is_active=card.is_active,
            created_at=card.created_at,
            updated_at=card.updated_at,
            categories=categories
        ))
    
    return result
