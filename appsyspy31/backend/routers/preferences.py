"""
会员偏好路由模块
处理会员的课程偏好、训练频率与目标等设置
这些信息将用于智能推荐系统
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import User, UserRole, MemberPreference, Gender
from schemas import (
    MemberPreferenceCreate, MemberPreferenceUpdate, MemberPreferenceResponse,
    ResponseModel
)
from utils import (
    get_current_active_user, require_role
)

router = APIRouter()

# ========================================
# 获取当前用户的偏好设置
# ========================================

@router.get("/my", response_model=ResponseModel)
async def get_my_preferences(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的偏好设置
    
    如果用户没有设置偏好，则返回默认值
    
    Args:
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含偏好设置的响应
    """
    preferences = db.query(MemberPreference).filter(
        MemberPreference.user_id == current_user.id
    ).first()
    
    if preferences:
        preferences_response = MemberPreferenceResponse.model_validate(preferences)
        return ResponseModel(
            code=200,
            message="获取成功",
            data={"preferences": preferences_response.model_dump()}
        )
    else:
        default_preferences = {
            "user_id": current_user.id,
            "preferred_categories": None,
            "preferred_course_types": None,
            "preferred_difficulty": 2,
            "training_frequency_per_week": 3,
            "preferred_training_days": None,
            "preferred_training_time": None,
            "fitness_goals": None,
            "target_weight": None,
            "current_weight": None,
            "height": None,
            "has_injuries": False,
            "injury_details": None,
            "preferred_coach_gender": None
        }
        
        return ResponseModel(
            code=200,
            message="获取成功（使用默认设置）",
            data={"preferences": default_preferences}
        )

# ========================================
# 创建或更新用户偏好设置
# ========================================

@router.post("/my", response_model=ResponseModel)
async def create_or_update_preferences(
    preference_data: MemberPreferenceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建或更新当前用户的偏好设置
    
    如果用户已有偏好设置，则更新；否则创建新的
    
    Args:
        preference_data: 偏好数据
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含更新后偏好设置的响应
    """
    existing_preference = db.query(MemberPreference).filter(
        MemberPreference.user_id == current_user.id
    ).first()
    
    if existing_preference:
        update_data = preference_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_preference, key, value)
        
        db.commit()
        db.refresh(existing_preference)
        
        preferences_response = MemberPreferenceResponse.model_validate(existing_preference)
        
        return ResponseModel(
            code=200,
            message="偏好设置已更新",
            data={"preferences": preferences_response.model_dump()}
        )
    else:
        new_preference = MemberPreference(
            user_id=current_user.id,
            **preference_data.model_dump(exclude_unset=True)
        )
        
        db.add(new_preference)
        db.commit()
        db.refresh(new_preference)
        
        preferences_response = MemberPreferenceResponse.model_validate(new_preference)
        
        return ResponseModel(
            code=200,
            message="偏好设置已创建",
            data={"preferences": preferences_response.model_dump()}
        )

# ========================================
# 获取指定用户的偏好设置（管理员权限）
# ========================================

@router.get("/user/{user_id}", response_model=ResponseModel)
async def get_user_preferences(
    user_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.STAFF)),
    db: Session = Depends(get_db)
):
    """
    获取指定用户的偏好设置
    
    需要管理员或工作人员权限
    
    Args:
        user_id: 用户ID
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含偏好设置的响应
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    preferences = db.query(MemberPreference).filter(
        MemberPreference.user_id == user_id
    ).first()
    
    if preferences:
        preferences_response = MemberPreferenceResponse.model_validate(preferences)
        return ResponseModel(
            code=200,
            message="获取成功",
            data={"preferences": preferences_response.model_dump()}
        )
    else:
        return ResponseModel(
            code=200,
            message="用户未设置偏好",
            data={"preferences": None}
        )

# ========================================
# 获取偏好选项配置
# ========================================

@router.get("/options/config", response_model=ResponseModel)
async def get_preference_options():
    """
    获取偏好设置的选项配置
    
    包括课程分类、课程类型、健身目标、训练时间段等可选值
    
    Returns:
        ResponseModel: 包含选项配置的响应
    """
    course_categories = [
        {"value": "strength", "label": "力量训练"},
        {"value": "cardio", "label": "有氧训练"},
        {"value": "yoga", "label": "瑜伽"},
        {"value": "pilates", "label": "普拉提"},
        {"value": "dance", "label": "舞蹈"},
        {"value": "boxing", "label": "拳击"},
        {"value": "swimming", "label": "游泳"},
        {"value": "rehabilitation", "label": "康复训练"}
    ]
    
    course_types = [
        {"value": "group", "label": "团课"},
        {"value": "private", "label": "私教课"},
        {"value": "semi_private", "label": "小团体课"}
    ]
    
    fitness_goals = [
        {"value": "增肌", "label": "增肌"},
        {"value": "减脂", "label": "减脂"},
        {"value": "塑形", "label": "塑形"},
        {"value": "增强体能", "label": "增强体能"},
        {"value": "康复训练", "label": "康复训练"},
        {"value": "放松减压", "label": "放松减压"}
    ]
    
    training_times = [
        {"value": "早上", "label": "早上 (06:00-10:00)"},
        {"value": "上午", "label": "上午 (10:00-12:00)"},
        {"value": "下午", "label": "下午 (14:00-18:00)"},
        {"value": "晚上", "label": "晚上 (18:00-22:00)"}
    ]
    
    training_days = [
        {"value": "周一", "label": "周一"},
        {"value": "周二", "label": "周二"},
        {"value": "周三", "label": "周三"},
        {"value": "周四", "label": "周四"},
        {"value": "周五", "label": "周五"},
        {"value": "周六", "label": "周六"},
        {"value": "周日", "label": "周日"}
    ]
    
    difficulty_levels = [
        {"value": 1, "label": "初级"},
        {"value": 2, "label": "初级-中级"},
        {"value": 3, "label": "中级"},
        {"value": 4, "label": "中级-高级"},
        {"value": 5, "label": "高级"}
    ]
    
    coach_genders = [
        {"value": "male", "label": "男教练"},
        {"value": "female", "label": "女教练"},
        {"value": "other", "label": "无所谓"}
    ]
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={
            "course_categories": course_categories,
            "course_types": course_types,
            "fitness_goals": fitness_goals,
            "training_times": training_times,
            "training_days": training_days,
            "difficulty_levels": difficulty_levels,
            "coach_genders": coach_genders
        }
    )

# ========================================
# 更新偏好设置
# ========================================

@router.put("/my", response_model=ResponseModel)
async def update_my_preferences(
    preference_data: MemberPreferenceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新当前用户的偏好设置
    
    Args:
        preference_data: 偏好数据
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含更新后偏好设置的响应
    """
    preferences = db.query(MemberPreference).filter(
        MemberPreference.user_id == current_user.id
    ).first()
    
    if not preferences:
        new_preference = MemberPreference(
            user_id=current_user.id,
            **preference_data.model_dump(exclude_unset=True)
        )
        
        db.add(new_preference)
        db.commit()
        db.refresh(new_preference)
        
        preferences_response = MemberPreferenceResponse.model_validate(new_preference)
        
        return ResponseModel(
            code=200,
            message="偏好设置已创建",
            data={"preferences": preferences_response.model_dump()}
        )
    
    update_data = preference_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(preferences, key, value)
    
    db.commit()
    db.refresh(preferences)
    
    preferences_response = MemberPreferenceResponse.model_validate(preferences)
    
    return ResponseModel(
        code=200,
        message="偏好设置已更新",
        data={"preferences": preferences_response.model_dump()}
    )

# ========================================
# 清除偏好设置
# ========================================

@router.delete("/my", response_model=ResponseModel)
async def clear_my_preferences(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    清除当前用户的偏好设置
    
    Args:
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 操作结果
    """
    preferences = db.query(MemberPreference).filter(
        MemberPreference.user_id == current_user.id
    ).first()
    
    if preferences:
        db.delete(preferences)
        db.commit()
        
        return ResponseModel(
            code=200,
            message="偏好设置已清除",
            data=None
        )
    
    return ResponseModel(
        code=200,
        message="没有偏好设置需要清除",
        data=None
    )
