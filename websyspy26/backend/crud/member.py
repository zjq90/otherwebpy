"""
会员相关CRUD操作
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime, timedelta
from models.member import Member, MemberCard, MemberStatus
from schemas.member import MemberCreate, MemberUpdate, MemberCardCreate, MemberCardUpdate


class MemberCRUD:
    """会员CRUD操作类"""

    def get_by_id(self, db: Session, member_id: int) -> Optional[Member]:
        """根据ID获取会员"""
        return db.query(Member).filter(Member.id == member_id, Member.is_deleted == 0).first()

    def get_by_member_no(self, db: Session, member_no: str) -> Optional[Member]:
        """根据会员编号获取会员"""
        return db.query(Member).filter(Member.member_no == member_no, Member.is_deleted == 0).first()

    def get_by_phone(self, db: Session, phone: str) -> Optional[Member]:
        """根据手机号获取会员"""
        return db.query(Member).filter(Member.phone == phone, Member.is_deleted == 0).first()

    def get_list(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 10,
        keyword: Optional[str] = None,
        level: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple[List[Member], int]:
        """
        获取会员列表
        返回：(会员列表, 总数)
        """
        query = db.query(Member).filter(Member.is_deleted == 0)
        
        # 关键词搜索（姓名、手机号、会员编号）
        if keyword:
            query = query.filter(
                or_(
                    Member.name.contains(keyword),
                    Member.phone.contains(keyword),
                    Member.member_no.contains(keyword)
                )
            )
        
        # 等级筛选
        if level:
            query = query.filter(Member.level == level)
        
        # 状态筛选
        if status:
            query = query.filter(Member.status == status)
        
        # 计算总数
        total = query.count()
        
        # 分页查询
        members = query.order_by(Member.created_at.desc()).offset(skip).limit(limit).all()
        
        return members, total

    def create(self, db: Session, member_in: MemberCreate) -> Member:
        """创建会员"""
        db_member = Member(**member_in.model_dump())
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member

    def update(self, db: Session, db_member: Member, member_in: MemberUpdate) -> Member:
        """更新会员"""
        update_data = member_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_member, key, value)
        db.commit()
        db.refresh(db_member)
        return db_member

    def delete(self, db: Session, db_member: Member) -> Member:
        """逻辑删除会员"""
        db_member.is_deleted = 1
        db.commit()
        return db_member

    def update_sleeping_status(self, db: Session) -> int:
        """
        更新沉睡会员状态
        将30天未消费的会员标记为沉睡
        返回更新的会员数量
        """
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # 查找30天未消费且状态为活跃的会员
        members_to_update = db.query(Member).filter(
            Member.is_deleted == 0,
            Member.status == MemberStatus.ACTIVE.value,
            Member.last_consumption_time < thirty_days_ago
        ).all()
        
        for member in members_to_update:
            member.status = MemberStatus.SLEEPING.value
        
        db.commit()
        return len(members_to_update)

    def get_sleeping_members(self, db: Session) -> List[Member]:
        """获取所有沉睡会员"""
        return db.query(Member).filter(
            Member.is_deleted == 0,
            Member.status == MemberStatus.SLEEPING.value
        ).all()

    def get_high_value_members(self, db: Session, min_consumption: float = 10000.0) -> List[Member]:
        """
        获取高价值会员
        默认：累计消费超过10000元的会员
        """
        return db.query(Member).filter(
            Member.is_deleted == 0,
            Member.total_consumption >= min_consumption
        ).all()


class MemberCardCRUD:
    """会员卡CRUD操作类"""

    def get_by_id(self, db: Session, card_id: int) -> Optional[MemberCard]:
        """根据ID获取会员卡"""
        return db.query(MemberCard).filter(MemberCard.id == card_id, MemberCard.is_deleted == 0).first()

    def get_by_card_no(self, db: Session, card_no: str) -> Optional[MemberCard]:
        """根据卡号获取会员卡"""
        return db.query(MemberCard).filter(MemberCard.card_no == card_no, MemberCard.is_deleted == 0).first()

    def get_by_member_id(self, db: Session, member_id: int) -> List[MemberCard]:
        """获取会员的所有会员卡"""
        return db.query(MemberCard).filter(
            MemberCard.member_id == member_id,
            MemberCard.is_deleted == 0
        ).order_by(MemberCard.created_at.desc()).all()

    def get_list(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 10,
        member_id: Optional[int] = None,
        card_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple[List[MemberCard], int]:
        """
        获取会员卡列表
        返回：(会员卡列表, 总数)
        """
        query = db.query(MemberCard).filter(MemberCard.is_deleted == 0)
        
        if member_id:
            query = query.filter(MemberCard.member_id == member_id)
        
        if card_type:
            query = query.filter(MemberCard.card_type == card_type)
        
        if status:
            query = query.filter(MemberCard.status == status)
        
        total = query.count()
        cards = query.order_by(MemberCard.created_at.desc()).offset(skip).limit(limit).all()
        
        return cards, total

    def get_expiring_soon(self, db: Session, days: int) -> List[MemberCard]:
        """
        获取即将到期的会员卡
        参数：
            days: 提前多少天到期
        """
        target_date = datetime.now().date() + timedelta(days=days)
        return db.query(MemberCard).filter(
            MemberCard.is_deleted == 0,
            MemberCard.status == "active",
            MemberCard.valid_to == target_date
        ).all()

    def create(self, db: Session, card_in: MemberCardCreate) -> MemberCard:
        """创建会员卡"""
        db_card = MemberCard(**card_in.model_dump())
        db.add(db_card)
        db.commit()
        db.refresh(db_card)
        return db_card

    def update(self, db: Session, db_card: MemberCard, card_in: MemberCardUpdate) -> MemberCard:
        """更新会员卡"""
        update_data = card_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_card, key, value)
        db.commit()
        db.refresh(db_card)
        return db_card

    def renew(
        self, 
        db: Session, 
        db_card: MemberCard, 
        new_valid_to: datetime.date,
        amount: float,
        method: str = "offline"
    ) -> MemberCard:
        """
        会员卡续费
        参数：
            db_card: 会员卡实例
            new_valid_to: 新的有效期结束日期
            amount: 续费金额
            method: 续费方式（offline到店, online线上）
        """
        db_card.valid_to = new_valid_to
        db_card.total_amount += amount
        db_card.status = "renewed"
        db.commit()
        db.refresh(db_card)
        return db_card

    def delete(self, db: Session, db_card: MemberCard) -> MemberCard:
        """逻辑删除会员卡"""
        db_card.is_deleted = 1
        db.commit()
        return db_card


# 创建全局CRUD实例
member_crud = MemberCRUD()
member_card_crud = MemberCardCRUD()
