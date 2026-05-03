from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas import FarmCreate, FarmUpdate, FarmResponse
from ..crud import farm_crud

# 创建路由对象
router = APIRouter(
    prefix="/api/farms",
    tags=["农场管理"],
    responses={404: {"description": "未找到"}},
)


@router.get("/", response_model=List[FarmResponse])
def read_farms(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    获取农场列表
    - **skip**: 跳过的记录数（用于分页）
    - **limit**: 返回的最大记录数（用于分页）
    """
    farms = farm_crud.get_all(db, skip=skip, limit=limit)
    return farms


@router.get("/count", response_model=int)
def count_farms(db: Session = Depends(get_db)):
    """
    统计农场总数
    """
    return farm_crud.count(db)


@router.get("/{farm_id}", response_model=FarmResponse)
def read_farm(
    farm_id: int, 
    db: Session = Depends(get_db)
):
    """
    根据ID获取单个农场信息
    - **farm_id**: 农场ID
    """
    farm = farm_crud.get_by_id(db, farm_id=farm_id)
    if farm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"农场ID {farm_id} 不存在"
        )
    return farm


@router.post("/", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
def create_farm(
    farm: FarmCreate, 
    db: Session = Depends(get_db)
):
    """
    创建新农场
    - **farm**: 农场信息
    """
    # 检查农场名称是否已存在
    existing_farm = farm_crud.get_by_name(db, name=farm.name)
    if existing_farm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"农场名称 '{farm.name}' 已存在"
        )
    return farm_crud.create(db=db, farm=farm)


@router.put("/{farm_id}", response_model=FarmResponse)
def update_farm(
    farm_id: int, 
    farm: FarmUpdate, 
    db: Session = Depends(get_db)
):
    """
    更新农场信息
    - **farm_id**: 农场ID
    - **farm**: 更新的农场信息
    """
    db_farm = farm_crud.get_by_id(db, farm_id=farm_id)
    if db_farm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"农场ID {farm_id} 不存在"
        )
    return farm_crud.update(db=db, farm_id=farm_id, farm=farm)


@router.delete("/{farm_id}", response_model=dict)
def delete_farm(
    farm_id: int, 
    db: Session = Depends(get_db)
):
    """
    删除农场
    - **farm_id**: 农场ID
    """
    success = farm_crud.delete(db=db, farm_id=farm_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"农场ID {farm_id} 不存在"
        )
    return {"message": "删除成功", "farm_id": farm_id}
