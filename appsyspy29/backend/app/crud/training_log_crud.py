"""
训练日志相关CRUD操作模块
负责训练日志数据的增删改查
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from ..models import TrainingLog, TrainingLogItem, Exercise
from ..schemas import TrainingLogCreate, TrainingLogUpdate, TrainingLogItemCreate


def get_training_log_by_id(db: Session, log_id: int) -> Optional[TrainingLog]:
    """
    根据ID获取训练日志
    """
    return db.query(TrainingLog).filter(TrainingLog.id == log_id).first()


def get_user_training_logs(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[TrainingLog]:
    """
    获取用户的训练日志列表
    按训练日期倒序排列
    """
    return db.query(TrainingLog)\
        .filter(TrainingLog.user_id == user_id)\
        .order_by(TrainingLog.training_date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_user_training_logs_by_date(
    db: Session, 
    user_id: int, 
    log_date: date
) -> List[TrainingLog]:
    """
    获取用户指定日期的训练日志
    """
    return db.query(TrainingLog)\
        .filter(
            TrainingLog.user_id == user_id,
            TrainingLog.training_date >= datetime.combine(log_date, datetime.min.time()),
            TrainingLog.training_date <= datetime.combine(log_date, datetime.max.time())
        )\
        .all()


def calculate_item_calories(
    exercise: Optional[Exercise], 
    duration: int, 
    weight: float, 
    sets: int, 
    reps: int
) -> float:
    """
    计算单个训练项目的消耗卡路里
    简单估算公式，实际项目中可能需要更复杂的算法
    """
    calories = 0.0
    
    # 如果有训练项目的参考值，优先使用
    if exercise and exercise.default_calories_per_hour:
        calories = exercise.default_calories_per_hour * (duration / 60)
    else:
        # 简单估算：力量训练
        # 假设每组消耗约3-5卡路里，根据重量调整
        base_calories_per_set = 3.0
        weight_factor = 1 + (weight / 100)  # 重量系数
        calories = sets * base_calories_per_set * weight_factor
    
    return round(calories, 1)


def calculate_total_calories(items: List[TrainingLogItem]) -> float:
    """
    计算总消耗卡路里
    """
    return sum(item.calories for item in items)


def create_training_log(db: Session, user_id: int, log: TrainingLogCreate) -> TrainingLog:
    """
    创建新的训练日志
    同时创建训练日志详情
    """
    # 创建训练日志主记录
    db_log = TrainingLog(
        user_id=user_id,
        training_date=log.training_date or datetime.now(),
        duration=log.duration,
        total_calories=log.total_calories,
        notes=log.notes,
        mood=log.mood
    )
    db.add(db_log)
    db.flush()  # 刷新以获取ID
    
    # 创建训练日志详情
    total_calories = 0.0
    for item in log.items:
        exercise = db.query(Exercise).filter(Exercise.id == item.exercise_id).first()
        calories = item.calories
        if calories <= 0:
            calories = calculate_item_calories(
                exercise, item.duration, item.weight, item.sets, item.reps
            )
        
        db_item = TrainingLogItem(
            training_log_id=db_log.id,
            exercise_id=item.exercise_id,
            sets=item.sets,
            reps=item.reps,
            weight=item.weight,
            duration=item.duration,
            calories=calories,
            notes=item.notes
        )
        db.add(db_item)
        total_calories += calories
    
    # 更新总卡路里
    if log.total_calories <= 0:
        db_log.total_calories = total_calories
    
    db.commit()
    db.refresh(db_log)
    return db_log


def update_training_log(
    db: Session, 
    log_id: int, 
    log: TrainingLogUpdate
) -> Optional[TrainingLog]:
    """
    更新训练日志
    """
    db_log = get_training_log_by_id(db, log_id)
    if not db_log:
        return None
    
    # 更新非空字段
    update_data = log.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_log, key, value)
    
    db_log.updated_at = datetime.now()
    db.commit()
    db.refresh(db_log)
    return db_log


def delete_training_log(db: Session, log_id: int) -> bool:
    """
    删除训练日志
    """
    db_log = get_training_log_by_id(db, log_id)
    if not db_log:
        return False
    
    db.delete(db_log)
    db.commit()
    return True


def add_training_log_item(
    db: Session, 
    log_id: int, 
    item: TrainingLogItemCreate
) -> Optional[TrainingLogItem]:
    """
    向训练日志添加训练项目
    """
    db_log = get_training_log_by_id(db, log_id)
    if not db_log:
        return None
    
    # 计算卡路里
    exercise = db.query(Exercise).filter(Exercise.id == item.exercise_id).first()
    calories = item.calories
    if calories <= 0:
        calories = calculate_item_calories(
            exercise, item.duration, item.weight, item.sets, item.reps
        )
    
    db_item = TrainingLogItem(
        training_log_id=log_id,
        exercise_id=item.exercise_id,
        sets=item.sets,
        reps=item.reps,
        weight=item.weight,
        duration=item.duration,
        calories=calories,
        notes=item.notes
    )
    db.add(db_item)
    db.flush()
    
    # 更新总卡路里和时长
    db_log.total_calories += calories
    db_log.duration += item.duration
    db_log.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_item)
    return db_item


def remove_training_log_item(db: Session, item_id: int) -> bool:
    """
    从训练日志中移除训练项目
    """
    db_item = db.query(TrainingLogItem).filter(TrainingLogItem.id == item_id).first()
    if not db_item:
        return False
    
    # 更新训练日志的总卡路里和时长
    db_log = db_item.training_log
    if db_log:
        db_log.total_calories -= db_item.calories
        db_log.duration -= db_item.duration
        db_log.updated_at = datetime.now()
    
    db.delete(db_item)
    db.commit()
    return True


def get_training_log_with_items(db: Session, log_id: int) -> Optional[TrainingLog]:
    """
    获取训练日志及其详情
    """
    return db.query(TrainingLog)\
        .filter(TrainingLog.id == log_id)\
        .first()


def get_user_monthly_stats(db: Session, user_id: int, year: int, month: int) -> dict:
    """
    获取用户月度训练统计
    """
    from sqlalchemy import func
    
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    # 查询月度数据
    result = db.query(
        func.count(TrainingLog.id).label('total_sessions'),
        func.sum(TrainingLog.duration).label('total_duration'),
        func.sum(TrainingLog.total_calories).label('total_calories')
    ).filter(
        TrainingLog.user_id == user_id,
        TrainingLog.training_date >= start_date,
        TrainingLog.training_date < end_date
    ).first()
    
    return {
        'total_sessions': result.total_sessions or 0,
        'total_duration': result.total_duration or 0,
        'total_calories': result.total_calories or 0.0
    }
