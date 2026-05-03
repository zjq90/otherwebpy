"""
检测结果API路由
提供检测结果的增删改查功能
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db

# 创建路由实例
router = APIRouter(
    prefix="/test-results",
    tags=["检测结果管理"],
    responses={404: {"description": "未找到"}},
)


@router.post("/", response_model=schemas.TestResult, status_code=status.HTTP_201_CREATED)
def create_test_result(
    result_in: schemas.TestResultCreate,
    db: Session = Depends(get_db)
):
    """
    创建新检测结果
    
    Args:
        result_in: 检测结果创建数据
        db: 数据库会话
        
    Returns:
        创建的检测结果对象
    """
    # 检查关联的批次是否存在
    batch = crud.batch.get(db, id=result_in.batch_id)
    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="关联的批次不存在"
        )
    
    # 创建检测结果
    result = crud.test_result.create(db, obj_in=result_in.model_dump())
    return result


@router.get("/", response_model=List[schemas.TestResult])
def read_test_results(
    skip: int = 0,
    limit: int = 100,
    batch_id: Optional[int] = None,
    test_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取检测结果列表（分页）
    
    Args:
        skip: 跳过的记录数
        limit: 返回的最大记录数
        batch_id: 可选，按批次ID筛选
        test_type: 可选，按检测类型筛选
        db: 数据库会话
        
    Returns:
        检测结果列表
    """
    if batch_id:
        results = crud.test_result.get_by_batch_id(
            db, batch_id=batch_id, skip=skip, limit=limit
        )
    elif test_type:
        results = crud.test_result.get_by_type(
            db, test_type=test_type, skip=skip, limit=limit
        )
    else:
        results = crud.test_result.get_multi(db, skip=skip, limit=limit)
    return results


@router.get("/{result_id}", response_model=schemas.TestResult)
def read_test_result(
    result_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取单个检测结果
    
    Args:
        result_id: 检测结果ID
        db: 数据库会话
        
    Returns:
        检测结果对象
    """
    result = crud.test_result.get(db, id=result_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="检测结果不存在"
        )
    return result


@router.put("/{result_id}", response_model=schemas.TestResult)
def update_test_result(
    result_id: int,
    result_in: schemas.TestResultUpdate,
    db: Session = Depends(get_db)
):
    """
    更新检测结果
    
    Args:
        result_id: 检测结果ID
        result_in: 更新数据
        db: 数据库会话
        
    Returns:
        更新后的检测结果对象
    """
    result = crud.test_result.get(db, id=result_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="检测结果不存在"
        )
    
    # 如果更新了批次ID，检查新批次是否存在
    update_data = result_in.model_dump(exclude_unset=True)
    if "batch_id" in update_data:
        batch = crud.batch.get(db, id=update_data["batch_id"])
        if batch is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="关联的批次不存在"
            )
    
    # 更新检测结果
    result = crud.test_result.update(db, db_obj=result, obj_in=update_data)
    return result


@router.delete("/{result_id}", response_model=schemas.TestResult)
def delete_test_result(
    result_id: int,
    db: Session = Depends(get_db)
):
    """
    删除检测结果
    
    Args:
        result_id: 检测结果ID
        db: 数据库会话
        
    Returns:
        被删除的检测结果对象
    """
    result = crud.test_result.get(db, id=result_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="检测结果不存在"
        )
    
    # 删除检测结果
    result = crud.test_result.remove(db, id=result_id)
    return result
