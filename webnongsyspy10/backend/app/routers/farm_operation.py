"""
农事作业记录API路由
提供农事作业记录的增删改查、快速录入等功能
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.database import get_db
from backend.app.models import FarmOperation
from backend.app.models.farm_operation import OperationTypeEnum, OperationStatusEnum
from backend.app.schemas.farm_operation import (
    FarmOperationCreate,
    FarmOperationUpdate,
    FarmOperationResponse,
    FarmOperationListResponse,
)

# 创建路由
router = APIRouter(
    prefix="/farm-operations",
    tags=["农事作业记录"],
    responses={404: {"description": "未找到"}},
)


@router.post("/", response_model=FarmOperationResponse, status_code=status.HTTP_201_CREATED)
def create_farm_operation(
    operation_data: FarmOperationCreate,
    db: Session = Depends(get_db)
):
    """
    创建新的农事作业记录
    
    参数:
        operation_data: 作业记录创建数据
        db: 数据库会话
    
    返回:
        创建的作业记录详情
    
    异常:
        HTTPException: 作业编号已存在时抛出400错误
    """
    # 检查作业编号是否已存在
    existing = db.query(FarmOperation).filter(
        FarmOperation.operation_code == operation_data.operation_code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"作业编号 {operation_data.operation_code} 已存在"
        )
    
    # 创建作业记录
    db_operation = FarmOperation(**operation_data.model_dump())
    
    db.add(db_operation)
    db.commit()
    db.refresh(db_operation)
    
    return db_operation


@router.get("/", response_model=FarmOperationListResponse)
def get_farm_operations(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    operation_type: Optional[str] = Query(None, description="筛选作业类型"),
    crop_type: Optional[str] = Query(None, description="筛选作物种类"),
    plot_location: Optional[str] = Query(None, description="筛选作业地块"),
    operator: Optional[str] = Query(None, description="筛选操作人员"),
    status: Optional[str] = Query(None, description="筛选状态"),
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
    is_app_entry: Optional[int] = Query(None, description="是否APP端录入"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    db: Session = Depends(get_db)
):
    """
    分页查询农事作业记录列表
    
    参数:
        page: 页码，从1开始
        page_size: 每页数量，最大100
        operation_type: 按作业类型筛选
        crop_type: 按作物种类筛选
        plot_location: 按作业地块筛选
        operator: 按操作人员筛选
        status: 按状态筛选
        start_date: 开始日期筛选
        end_date: 结束日期筛选
        is_app_entry: 是否APP端录入
        keyword: 关键词搜索
        db: 数据库会话
    
    返回:
        包含分页信息的作业记录列表
    """
    # 构建查询
    query = db.query(FarmOperation)
    
    # 应用筛选条件
    if operation_type:
        try:
            op_type_enum = OperationTypeEnum(operation_type)
            query = query.filter(FarmOperation.operation_type == op_type_enum)
        except ValueError:
            pass
    
    if crop_type:
        query = query.filter(FarmOperation.crop_type.contains(crop_type))
    
    if plot_location:
        query = query.filter(FarmOperation.plot_location.contains(plot_location))
    
    if operator:
        query = query.filter(FarmOperation.operator.contains(operator))
    
    if status:
        try:
            status_enum = OperationStatusEnum(status)
            query = query.filter(FarmOperation.status == status_enum)
        except ValueError:
            pass
    
    if start_date:
        from datetime import datetime
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(FarmOperation.actual_date >= start_dt)
        except ValueError:
            pass
    
    if end_date:
        from datetime import datetime
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(FarmOperation.actual_date <= end_dt)
        except ValueError:
            pass
    
    if is_app_entry is not None:
        query = query.filter(FarmOperation.is_app_entry == is_app_entry)
    
    if keyword:
        query = query.filter(
            or_(
                FarmOperation.operation_name.contains(keyword),
                FarmOperation.operation_code.contains(keyword),
                FarmOperation.crop_type.contains(keyword),
                FarmOperation.plot_location.contains(keyword),
                FarmOperation.operator.contains(keyword)
            )
        )
    
    # 获取总记录数
    total = query.count()
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 执行分页查询
    items = query.order_by(FarmOperation.actual_date.desc(), FarmOperation.created_at.desc()).offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }


@router.get("/{operation_id}", response_model=FarmOperationResponse)
def get_farm_operation(
    operation_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取农事作业记录详情
    
    参数:
        operation_id: 作业记录ID
        db: 数据库会话
    
    返回:
        作业记录详情
    
    异常:
        HTTPException: 记录不存在时抛出404错误
    """
    operation = db.query(FarmOperation).filter(FarmOperation.id == operation_id).first()
    
    if not operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"农事作业记录 ID {operation_id} 不存在"
        )
    
    return operation


@router.put("/{operation_id}", response_model=FarmOperationResponse)
def update_farm_operation(
    operation_id: int,
    operation_data: FarmOperationUpdate,
    db: Session = Depends(get_db)
):
    """
    更新农事作业记录
    
    参数:
        operation_id: 作业记录ID
        operation_data: 更新数据
        db: 数据库会话
    
    返回:
        更新后的作业记录详情
    
    异常:
        HTTPException: 记录不存在时抛出404错误
    """
    db_operation = db.query(FarmOperation).filter(FarmOperation.id == operation_id).first()
    
    if not db_operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"农事作业记录 ID {operation_id} 不存在"
        )
    
    # 更新字段
    update_data = operation_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_operation, key, value)
    
    db.commit()
    db.refresh(db_operation)
    
    return db_operation


@router.delete("/{operation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farm_operation(
    operation_id: int,
    db: Session = Depends(get_db)
):
    """
    删除农事作业记录
    
    参数:
        operation_id: 作业记录ID
        db: 数据库会话
    
    异常:
        HTTPException: 记录不存在时抛出404错误
    """
    db_operation = db.query(FarmOperation).filter(FarmOperation.id == operation_id).first()
    
    if not db_operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"农事作业记录 ID {operation_id} 不存在"
        )
    
    db.delete(db_operation)
    db.commit()


@router.post("/quick-entry", response_model=FarmOperationResponse, status_code=status.HTTP_201_CREATED)
def quick_entry_operation(
    operation_data: FarmOperationCreate,
    db: Session = Depends(get_db)
):
    """
    快速录入农事作业记录
    支持扫码或APP端快速录入
    
    参数:
        operation_data: 作业记录数据
        db: 数据库会话
    
    返回:
        创建的作业记录详情
    """
    # 设置APP录入标志
    operation_data.is_app_entry = 1
    
    # 调用创建函数
    return create_farm_operation(operation_data, db)


@router.get("/statistics/summary")
def get_operation_statistics(
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    db: Session = Depends(get_db)
):
    """
    获取农事作业统计数据
    
    参数:
        start_date: 开始日期
        end_date: 结束日期
        db: 数据库会话
    
    返回:
        统计数据，包括：
        - 按作业类型统计
        - 按操作人员统计
        - 总作业数量和面积
    """
    query = db.query(FarmOperation)
    
    # 日期筛选
    if start_date:
        from datetime import datetime
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(FarmOperation.actual_date >= start_dt)
        except ValueError:
            pass
    
    if end_date:
        from datetime import datetime
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(FarmOperation.actual_date <= end_dt)
        except ValueError:
            pass
    
    operations = query.all()
    
    # 统计数据
    type_stats = {}
    operator_stats = {}
    status_stats = {}
    total_operations = len(operations)
    total_area = 0
    
    for op in operations:
        # 按作业类型统计
        type_val = op.operation_type.value if op.operation_type else "未知"
        if type_val not in type_stats:
            type_stats[type_val] = {
                "count": 0,
                "area": 0
            }
        type_stats[type_val]["count"] += 1
        type_stats[type_val]["area"] += float(op.operation_area) if op.operation_area else 0
        
        # 按操作人员统计
        if op.operator:
            if op.operator not in operator_stats:
                operator_stats[op.operator] = 0
            operator_stats[op.operator] += 1
        
        # 按状态统计
        status_val = op.status.value if op.status else "未知"
        if status_val not in status_stats:
            status_stats[status_val] = 0
        status_stats[status_val] += 1
        
        # 总面积
        total_area += float(op.operation_area) if op.operation_area else 0
    
    return {
        "total_operations": total_operations,
        "total_area": round(total_area, 2),
        "type_statistics": type_stats,
        "operator_statistics": operator_stats,
        "status_statistics": status_stats
    }


@router.get("/stats")
def get_operation_stats(
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    db: Session = Depends(get_db)
):
    """
    获取农事作业统计数据（前端调用别名）
    与 /statistics/summary 功能相同，方便前端调用
    """
    return get_operation_statistics(start_date=start_date, end_date=end_date, db=db)
