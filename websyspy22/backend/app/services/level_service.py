"""
会员等级服务模块
负责会员等级计算和权益管理
"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from app.models.member import Member
from app.models.level import MemberLevel, LevelBenefit
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class LevelService:
    """
    会员等级服务类
    负责会员等级升级判断、权益查询等功能
    """
    
    # 等级代码到名称的映射
    LEVEL_NAMES = {
        "bronze": "铜卡",
        "silver": "银卡", 
        "gold": "金卡"
    }
    
    # 等级排序（数值越大等级越高）
    LEVEL_ORDER = ["bronze", "silver", "gold"]
    
    def calculate_level(
        self, 
        total_consumption: int,  # 分
        total_visits: int
    ) -> str:
        """
        根据消费金额和到店次数计算会员等级
        Args:
            total_consumption: 累计消费金额（分）
            total_visits: 累计到店次数
        Returns:
            会员等级代码
        """
        consumption_yuan = total_consumption / 100  # 转换为元
        
        # 金卡门槛：消费 >= 20000元
        if consumption_yuan >= settings.GOLD_THRESHOLD:
            return "gold"
        
        # 银卡门槛：消费 >= 5000元
        if consumption_yuan >= settings.SILVER_THRESHOLD:
            return "silver"
        
        # 铜卡门槛：默认
        return "bronze"
    
    def check_and_upgrade_level(self, db: Session, member: Member) -> Tuple[bool, str]:
        """
        检查会员等级并在需要时升级
        Args:
            db: 数据库会话
            member: 会员对象
        Returns:
            (是否升级, 新等级代码)
        """
        new_level = self.calculate_level(member.total_consumption, member.total_visits)
        
        if new_level != member.current_level:
            old_level = member.current_level
            member.current_level = new_level
            db.commit()
            db.refresh(member)
            
            logger.info(f"会员 {member.id} ({member.name}) 等级变更: {old_level} -> {new_level}")
            return True, new_level
        
        return False, new_level
    
    def get_level_name(self, level_code: str) -> str:
        """
        获取等级名称
        Args:
            level_code: 等级代码
        Returns:
            等级名称
        """
        return self.LEVEL_NAMES.get(level_code, level_code)
    
    def get_next_level(self, current_level: str) -> Optional[str]:
        """
        获取下一等级
        Args:
            current_level: 当前等级代码
        Returns:
            下一等级代码，如果已是最高等级返回None
        """
        try:
            current_index = self.LEVEL_ORDER.index(current_level)
            if current_index < len(self.LEVEL_ORDER) - 1:
                return self.LEVEL_ORDER[current_index + 1]
        except ValueError:
            pass
        return None
    
    def get_level_threshold(self, level_code: str) -> Tuple[int, int]:
        """
        获取指定等级的门槛
        Args:
            level_code: 等级代码
        Returns:
            (最低消费金额分, 最低到店次数)
        """
        thresholds = {
            "bronze": (0, 0),
            "silver": (int(settings.SILVER_THRESHOLD * 100), 0),
            "gold": (int(settings.GOLD_THRESHOLD * 100), 0)
        }
        return thresholds.get(level_code, (0, 0))
    
    def get_member_level_info(self, db: Session, member: Member) -> dict:
        """
        获取会员等级信息（包含当前等级、下一等级、权益等）
        Args:
            db: 数据库会话
            member: 会员对象
        Returns:
            包含等级信息的字典
        """
        current_level = member.current_level
        next_level = self.get_next_level(current_level)
        
        # 获取当前等级权益
        benefits = db.query(LevelBenefit).filter(
            LevelBenefit.level_code == current_level,
            LevelBenefit.is_active == True
        ).order_by(LevelBenefit.sort_order).all()
        
        # 计算到下一等级的差距
        consumption_to_next = None
        visits_to_next = None
        
        if next_level:
            next_threshold_consumption, next_threshold_visits = self.get_level_threshold(next_level)
            consumption_to_next = max(0, next_threshold_consumption - member.total_consumption)
            visits_to_next = max(0, next_threshold_visits - member.total_visits)
        
        return {
            "current_level_code": current_level,
            "current_level_name": self.get_level_name(current_level),
            "current_level_description": f"{self.get_level_name(current_level)}会员",
            "total_consumption": member.total_consumption,
            "total_visits": member.total_visits,
            "next_level_code": next_level,
            "next_level_name": self.get_level_name(next_level) if next_level else None,
            "consumption_to_next_level": consumption_to_next,
            "visits_to_next_level": visits_to_next,
            "benefits": benefits
        }
    
    def get_all_levels(self, db: Session) -> List[MemberLevel]:
        """
        获取所有会员等级配置
        Args:
            db: 数据库会话
        Returns:
            等级列表
        """
        return db.query(MemberLevel).order_by(MemberLevel.sort_order).all()
    
    def get_level_benefits(self, db: Session, level_code: str) -> List[LevelBenefit]:
        """
        获取指定等级的权益列表
        Args:
            db: 数据库会话
            level_code: 等级代码
        Returns:
            权益列表
        """
        return db.query(LevelBenefit).filter(
            LevelBenefit.level_code == level_code,
            LevelBenefit.is_active == True
        ).order_by(LevelBenefit.sort_order).all()
    
    def calculate_discount(self, level_code: str, original_amount: int) -> int:
        """
        根据会员等级计算折扣后的金额
        Args:
            level_code: 会员等级代码
            original_amount: 原始金额（分）
        Returns:
            折扣后金额（分）
        """
        # 定义各等级折扣率
        discounts = {
            "bronze": 1.0,    # 无折扣
            "silver": 0.9,    # 9折
            "gold": 0.8       # 8折
        }
        
        discount_rate = discounts.get(level_code, 1.0)
        return int(original_amount * discount_rate)
    
    def get_discount_rate(self, level_code: str) -> float:
        """
        获取会员等级的折扣率
        Args:
            level_code: 会员等级代码
        Returns:
            折扣率（1.0表示无折扣）
        """
        discounts = {
            "bronze": 1.0,
            "silver": 0.9,
            "gold": 0.8
        }
        return discounts.get(level_code, 1.0)


# 创建全局服务实例
level_service = LevelService()
