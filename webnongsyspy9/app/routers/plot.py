from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas import PlotCreate, PlotUpdate, PlotResponse
from ..crud import plot_crud, farm_crud

# 创建路由对象
router = APIRouter(
    prefix="/api/plots",
    tags=["地块管理"],
    responses={404: {"description": "未找到"}},
)


@router.get("/", response_model=List[PlotResponse])
def read_plots(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    获取地块列表
    - **skip**: 跳过的记录数（用于分页）
    - **limit**: 返回的最大记录数（用于分页）
    """
    plots = plot_crud.get_all(db, skip=skip, limit=limit)
    return plots


@router.get("/count", response_model=int)
def count_plots(db: Session = Depends(get_db)):
    """
    统计地块总数
    """
    return plot_crud.count(db)


@router.get("/farm/{farm_id}", response_model=List[PlotResponse])
def read_plots_by_farm(
    farm_id: int, 
    db: Session = Depends(get_db)
):
    """
    根据农场ID获取地块列表
    - **farm_id**: 农场ID
    """
    # 检查农场是否存在
    farm = farm_crud.get_by_id(db, farm_id=farm_id)
    if farm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"农场ID {farm_id} 不存在"
        )
    plots = plot_crud.get_by_farm_id(db, farm_id=farm_id)
    return plots


@router.get("/{plot_id}", response_model=PlotResponse)
def read_plot(
    plot_id: int, 
    db: Session = Depends(get_db)
):
    """
    根据ID获取单个地块信息
    - **plot_id**: 地块ID
    """
    plot = plot_crud.get_by_id(db, plot_id=plot_id)
    if plot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"地块ID {plot_id} 不存在"
        )
    return plot


@router.post("/", response_model=PlotResponse, status_code=status.HTTP_201_CREATED)
def create_plot(
    plot: PlotCreate, 
    db: Session = Depends(get_db)
):
    """
    创建新地块
    - **plot**: 地块信息
    """
    # 检查地块编号是否已存在
    existing_plot = plot_crud.get_by_plot_number(db, plot_number=plot.plot_number)
    if existing_plot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"地块编号 '{plot.plot_number}' 已存在"
        )
    
    # 检查农场是否存在
    farm = farm_crud.get_by_id(db, farm_id=plot.farm_id)
    if farm is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"农场ID {plot.farm_id} 不存在"
        )
    
    return plot_crud.create(db=db, plot=plot)


@router.put("/{plot_id}", response_model=PlotResponse)
def update_plot(
    plot_id: int, 
    plot: PlotUpdate, 
    db: Session = Depends(get_db)
):
    """
    更新地块信息
    - **plot_id**: 地块ID
    - **plot**: 更新的地块信息
    """
    db_plot = plot_crud.get_by_id(db, plot_id=plot_id)
    if db_plot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"地块ID {plot_id} 不存在"
        )
    
    # 如果更新了农场ID，检查新农场是否存在
    if plot.farm_id:
        farm = farm_crud.get_by_id(db, farm_id=plot.farm_id)
        if farm is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"农场ID {plot.farm_id} 不存在"
            )
    
    return plot_crud.update(db=db, plot_id=plot_id, plot=plot)


@router.delete("/{plot_id}", response_model=dict)
def delete_plot(
    plot_id: int, 
    db: Session = Depends(get_db)
):
    """
    删除地块
    - **plot_id**: 地块ID
    """
    success = plot_crud.delete(db=db, plot_id=plot_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"地块ID {plot_id} 不存在"
        )
    return {"message": "删除成功", "plot_id": plot_id}
