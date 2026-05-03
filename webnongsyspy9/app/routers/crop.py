from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas import CropCreate, CropUpdate, CropResponse
from ..crud import crop_crud

# 创建路由对象
router = APIRouter(
    prefix="/api/crops",
    tags=["作物档案"],
    responses={404: {"description": "未找到"}},
)


@router.get("/", response_model=List[CropResponse])
def read_crops(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    获取作物列表
    - **skip**: 跳过的记录数（用于分页）
    - **limit**: 返回的最大记录数（用于分页）
    """
    crops = crop_crud.get_all(db, skip=skip, limit=limit)
    return crops


@router.get("/count", response_model=int)
def count_crops(db: Session = Depends(get_db)):
    """
    统计作物总数
    """
    return crop_crud.count(db)


@router.get("/name/{name}", response_model=List[CropResponse])
def read_crops_by_name(
    name: str, 
    db: Session = Depends(get_db)
):
    """
    根据名称获取作物列表
    - **name**: 作物名称
    """
    crops = crop_crud.get_by_name(db, name=name)
    return crops


@router.get("/{crop_id}", response_model=CropResponse)
def read_crop(
    crop_id: int, 
    db: Session = Depends(get_db)
):
    """
    根据ID获取单个作物信息
    - **crop_id**: 作物ID
    """
    crop = crop_crud.get_by_id(db, crop_id=crop_id)
    if crop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"作物ID {crop_id} 不存在"
        )
    return crop


@router.post("/", response_model=CropResponse, status_code=status.HTTP_201_CREATED)
def create_crop(
    crop: CropCreate, 
    db: Session = Depends(get_db)
):
    """
    创建新作物
    - **crop**: 作物信息
    """
    # 检查同名同品种的作物是否已存在
    existing_crop = crop_crud.get_by_name_and_variety(
        db, 
        name=crop.name, 
        variety=crop.variety
    )
    if existing_crop:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"作物 '{crop.name}' 品种 '{crop.variety}' 已存在"
        )
    
    return crop_crud.create(db=db, crop=crop)


@router.put("/{crop_id}", response_model=CropResponse)
def update_crop(
    crop_id: int, 
    crop: CropUpdate, 
    db: Session = Depends(get_db)
):
    """
    更新作物信息
    - **crop_id**: 作物ID
    - **crop**: 更新的作物信息
    """
    db_crop = crop_crud.get_by_id(db, crop_id=crop_id)
    if db_crop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"作物ID {crop_id} 不存在"
        )
    return crop_crud.update(db=db, crop_id=crop_id, crop=crop)


@router.delete("/{crop_id}", response_model=dict)
def delete_crop(
    crop_id: int, 
    db: Session = Depends(get_db)
):
    """
    删除作物
    - **crop_id**: 作物ID
    """
    success = crop_crud.delete(db=db, crop_id=crop_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"作物ID {crop_id} 不存在"
        )
    return {"message": "删除成功", "crop_id": crop_id}
