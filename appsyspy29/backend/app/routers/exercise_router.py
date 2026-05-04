"""
训练项目相关API路由模块
包含训练项目的增删改查等接口
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from ..config import get_db
from ..schemas import (
    ExerciseCreate, ExerciseUpdate, ExerciseResponse, ApiResponse
)
from ..crud import (
    get_exercise_by_id, get_exercises, get_exercises_by_category,
    create_exercise, update_exercise, delete_exercise, get_all_categories
)

router = APIRouter(prefix="/api/exercises", tags=["训练项目"])


@router.post("/", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
def add_exercise(exercise: ExerciseCreate, db: Session = Depends(get_db)):
    """
    添加训练项目接口
    
    创建新的训练项目
    """
    return create_exercise(db=db, exercise=exercise)


@router.get("/", response_model=List[ExerciseResponse])
def list_exercises(
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=1000), 
    db: Session = Depends(get_db)
):
    """
    获取训练项目列表接口
    
    支持分页查询
    """
    exercises = get_exercises(db, skip=skip, limit=limit)
    return exercises


@router.get("/{exercise_id}", response_model=ExerciseResponse)
def get_exercise(exercise_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取训练项目接口
    """
    db_exercise = get_exercise_by_id(db, exercise_id=exercise_id)
    if not db_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练项目不存在"
        )
    return db_exercise


@router.put("/{exercise_id}", response_model=ExerciseResponse)
def update_exercise_info(
    exercise_id: int, 
    exercise: ExerciseUpdate, 
    db: Session = Depends(get_db)
):
    """
    更新训练项目接口
    """
    db_exercise = update_exercise(db, exercise_id=exercise_id, exercise=exercise)
    if not db_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练项目不存在"
        )
    return db_exercise


@router.delete("/{exercise_id}", response_model=ApiResponse)
def delete_exercise_info(exercise_id: int, db: Session = Depends(get_db)):
    """
    删除训练项目接口
    """
    success = delete_exercise(db, exercise_id=exercise_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练项目不存在"
        )
    return ApiResponse(
        code=status.HTTP_200_OK,
        message="训练项目删除成功"
    )


@router.get("/category/{category}", response_model=List[ExerciseResponse])
def list_exercises_by_category(category: str, db: Session = Depends(get_db)):
    """
    根据分类获取训练项目列表接口
    
    例如：力量训练、有氧运动、柔韧训练等
    """
    exercises = get_exercises_by_category(db, category=category)
    return exercises


@router.get("/categories/list", response_model=List[str])
def list_categories(db: Session = Depends(get_db)):
    """
    获取所有训练项目分类接口
    
    返回所有已存在的分类名称列表
    """
    categories = get_all_categories(db)
    return categories
