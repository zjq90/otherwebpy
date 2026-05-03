from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    CropCreate, CropUpdate, CropResponse,
    ApiResponse, ApiListResponse
)
from app.crud import CropCRUD

router = APIRouter(prefix="/crops", tags=["作物管理"])


@router.get("", response_model=ApiListResponse)
def get_crops(
    skip: int = 0,
    limit: int = 100,
    crop_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取作物列表（支持分页和筛选）
    
    Args:
        skip: 跳过条数
        limit: 获取条数
        crop_type: 作物类型筛选
        status: 作物状态筛选
        db: 数据库会话
    
    Returns:
        作物列表数据
    """
    total, crops = CropCRUD.get_list(
        db, skip=skip, limit=limit,
        crop_type=crop_type, status=status
    )
    
    return ApiListResponse(
        success=True,
        message="获取作物列表成功",
        total=total,
        data=[CropResponse.model_validate(crop) for crop in crops]
    )


@router.get("/statistics", response_model=ApiResponse)
def get_crop_statistics(db: Session = Depends(get_db)):
    """
    获取作物统计信息
    
    Args:
        db: 数据库会话
    
    Returns:
        统计信息
    """
    statistics = CropCRUD.get_statistics(db)
    
    return ApiResponse(
        success=True,
        message="获取统计信息成功",
        data=statistics
    )


@router.get("/{crop_id}", response_model=ApiResponse)
def get_crop(crop_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取作物详情
    
    Args:
        crop_id: 作物ID
        db: 数据库会话
    
    Returns:
        作物详情
    """
    crop = CropCRUD.get_by_id(db, crop_id)
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"作物ID {crop_id} 不存在"
        )
    
    return ApiResponse(
        success=True,
        message="获取作物详情成功",
        data=CropResponse.model_validate(crop).model_dump()
    )


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_crop(crop_in: CropCreate, db: Session = Depends(get_db)):
    """
    创建作物
    
    Args:
        crop_in: 作物创建数据
        db: 数据库会话
    
    Returns:
        创建的作物信息
    """
    crop = CropCRUD.create(db, crop_in)
    
    return ApiResponse(
        success=True,
        message="创建作物成功",
        data=CropResponse.model_validate(crop).model_dump()
    )


@router.put("/{crop_id}", response_model=ApiResponse)
def update_crop(
    crop_id: int,
    crop_in: CropUpdate,
    db: Session = Depends(get_db)
):
    """
    更新作物信息
    
    Args:
        crop_id: 作物ID
        crop_in: 更新数据
        db: 数据库会话
    
    Returns:
        更新后的作物信息
    """
    crop = CropCRUD.get_by_id(db, crop_id)
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"作物ID {crop_id} 不存在"
        )
    
    updated_crop = CropCRUD.update(db, crop, crop_in)
    
    return ApiResponse(
        success=True,
        message="更新作物成功",
        data=CropResponse.model_validate(updated_crop).model_dump()
    )


@router.delete("/{crop_id}", response_model=ApiResponse)
def delete_crop(crop_id: int, db: Session = Depends(get_db)):
    """
    删除作物
    
    Args:
        crop_id: 作物ID
        db: 数据库会话
    
    Returns:
        删除结果
    """
    crop = CropCRUD.get_by_id(db, crop_id)
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"作物ID {crop_id} 不存在"
        )
    
    CropCRUD.delete(db, crop)
    
    return ApiResponse(
        success=True,
        message="删除作物成功",
        data={"id": crop_id}
    )
