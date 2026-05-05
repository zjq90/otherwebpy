from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.schemas import (
    ProductionPlanCreate, ProductionPlanUpdate, ProductionPlanResponse,
    MaterialDemandCreate, MaterialDemandResponse
)
from app.crud import production_plan_crud, material_demand_crud

router = APIRouter(
    prefix="/api/production",
    tags=["生产计划与物料需求预测"],
    responses={404: {"description": "未找到"}}
)

@router.post("/plans/", response_model=ProductionPlanResponse, summary="创建生产计划")
def create_production_plan(plan: ProductionPlanCreate, db: Session = Depends(get_db)):
    """
    创建新的生产计划
    - **plan**: 生产计划信息
    """
    db_plan = production_plan_crud.create(db, plan)
    production_plan_crud.generate_material_demands(db, db_plan.id)
    return db_plan

@router.get("/plans/", response_model=List[ProductionPlanResponse], summary="获取生产计划列表")
def read_production_plans(
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=1000), 
    db: Session = Depends(get_db)
):
    """
    获取所有生产计划列表
    - **skip**: 跳过数量
    - **limit**: 返回数量限制
    """
    plans = production_plan_crud.get_multi(db, skip=skip, limit=limit)
    return plans

@router.get("/plans/pending", response_model=List[ProductionPlanResponse], summary="获取待执行的生产计划")
def read_pending_plans(db: Session = Depends(get_db)):
    """
    获取所有待执行或执行中的生产计划
    """
    plans = production_plan_crud.get_pending_plans(db)
    return plans

@router.get("/plans/by-date", response_model=List[ProductionPlanResponse], summary="按日期获取生产计划")
def read_plans_by_date(plan_date: date, db: Session = Depends(get_db)):
    """
    按日期获取生产计划
    - **plan_date**: 计划日期
    """
    plans = production_plan_crud.get_by_date(db, plan_date)
    return plans

@router.get("/plans/{plan_id}", response_model=ProductionPlanResponse, summary="获取单个生产计划")
def read_production_plan(plan_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取生产计划
    - **plan_id**: 生产计划ID
    """
    plan = production_plan_crud.get(db, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="生产计划不存在")
    return plan

@router.put("/plans/{plan_id}", response_model=ProductionPlanResponse, summary="更新生产计划")
def update_production_plan(plan_id: int, plan: ProductionPlanUpdate, db: Session = Depends(get_db)):
    """
    更新生产计划
    - **plan_id**: 生产计划ID
    - **plan**: 更新的生产计划信息
    """
    db_plan = production_plan_crud.get(db, plan_id)
    if db_plan is None:
        raise HTTPException(status_code=404, detail="生产计划不存在")
    return production_plan_crud.update(db, db_plan, plan)

@router.delete("/plans/{plan_id}", summary="删除生产计划")
def delete_production_plan(plan_id: int, db: Session = Depends(get_db)):
    """
    删除生产计划
    - **plan_id**: 生产计划ID
    """
    db_plan = production_plan_crud.get(db, plan_id)
    if db_plan is None:
        raise HTTPException(status_code=404, detail="生产计划不存在")
    production_plan_crud.remove(db, plan_id)
    return {"message": "删除成功", "id": plan_id}

@router.post("/plans/{plan_id}/generate-demands", response_model=List[MaterialDemandResponse], summary="重新生成物料需求")
def regenerate_material_demands(plan_id: int, db: Session = Depends(get_db)):
    """
    根据生产计划重新生成物料需求预测
    - **plan_id**: 生产计划ID
    """
    plan = production_plan_crud.get(db, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="生产计划不存在")
    
    demands = production_plan_crud.generate_material_demands(db, plan_id)
    return demands

@router.get("/demands/", response_model=List[MaterialDemandResponse], summary="获取物料需求列表")
def read_material_demands(
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=1000), 
    db: Session = Depends(get_db)
):
    """
    获取所有物料需求列表
    - **skip**: 跳过数量
    - **limit**: 返回数量限制
    """
    demands = material_demand_crud.get_multi(db, skip=skip, limit=limit)
    return demands

@router.get("/demands/pending", response_model=List[MaterialDemandResponse], summary="获取待处理的物料需求")
def read_pending_demands(db: Session = Depends(get_db)):
    """
    获取所有待处理的物料需求（按优先级排序）
    """
    demands = material_demand_crud.get_pending_demands(db)
    return demands

@router.get("/demands/by-material", response_model=List[MaterialDemandResponse], summary="按物料类型获取需求")
def read_demands_by_material(material_type: str, db: Session = Depends(get_db)):
    """
    按物料类型获取物料需求
    - **material_type**: 物料类型
    """
    demands = material_demand_crud.get_by_material_type(db, material_type)
    return demands

@router.get("/demands/{demand_id}", response_model=MaterialDemandResponse, summary="获取单个物料需求")
def read_material_demand(demand_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取物料需求
    - **demand_id**: 物料需求ID
    """
    demand = material_demand_crud.get(db, demand_id)
    if demand is None:
        raise HTTPException(status_code=404, detail="物料需求不存在")
    return demand

@router.delete("/demands/{demand_id}", summary="删除物料需求")
def delete_material_demand(demand_id: int, db: Session = Depends(get_db)):
    """
    删除物料需求
    - **demand_id**: 物料需求ID
    """
    db_demand = material_demand_crud.get(db, demand_id)
    if db_demand is None:
        raise HTTPException(status_code=404, detail="物料需求不存在")
    material_demand_crud.remove(db, demand_id)
    return {"message": "删除成功", "id": demand_id}
