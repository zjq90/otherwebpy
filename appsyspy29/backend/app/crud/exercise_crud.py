"""
训练项目相关CRUD操作模块
负责训练项目数据的增删改查
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..models import Exercise
from ..schemas import ExerciseCreate, ExerciseUpdate


def get_exercise_by_id(db: Session, exercise_id: int) -> Optional[Exercise]:
    """
    根据ID获取训练项目
    """
    return db.query(Exercise).filter(Exercise.id == exercise_id).first()


def get_exercises(db: Session, skip: int = 0, limit: int = 100) -> List[Exercise]:
    """
    获取训练项目列表
    """
    return db.query(Exercise).offset(skip).limit(limit).all()


def get_exercises_by_category(db: Session, category: str) -> List[Exercise]:
    """
    根据分类获取训练项目列表
    """
    return db.query(Exercise).filter(Exercise.category == category).all()


def create_exercise(db: Session, exercise: ExerciseCreate) -> Exercise:
    """
    创建新的训练项目
    """
    db_exercise = Exercise(
        name=exercise.name,
        category=exercise.category,
        description=exercise.description,
        default_calories_per_hour=exercise.default_calories_per_hour,
        icon=exercise.icon
    )
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise


def update_exercise(
    db: Session, 
    exercise_id: int, 
    exercise: ExerciseUpdate
) -> Optional[Exercise]:
    """
    更新训练项目
    """
    db_exercise = get_exercise_by_id(db, exercise_id)
    if not db_exercise:
        return None
    
    # 更新非空字段
    update_data = exercise.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_exercise, key, value)
    
    db_exercise.updated_at = datetime.now()
    db.commit()
    db.refresh(db_exercise)
    return db_exercise


def delete_exercise(db: Session, exercise_id: int) -> bool:
    """
    删除训练项目
    """
    db_exercise = get_exercise_by_id(db, exercise_id)
    if not db_exercise:
        return False
    
    db.delete(db_exercise)
    db.commit()
    return True


def get_all_categories(db: Session) -> List[str]:
    """
    获取所有训练项目分类
    """
    result = db.query(Exercise.category).distinct().all()
    return [r[0] for r in result]
