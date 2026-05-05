# -*- coding: utf-8 -*-
"""
结算单管理API路由
==================
提供结算单的增删改查接口
自动生成供应商结算单
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import SettlementOrder, Supplier, MaterialInspection
from app.schemas import SettlementOrderCreate, SettlementOrderUpdate, SettlementOrderResponse

router = APIRouter()


@router.get("/", response_model=List[SettlementOrderResponse], summary="获取结算单列表")
async def get_settlement_orders(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(50, ge=1, le=100, description="返回记录数"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    supplier_id: Optional[int] = Query(None, description="供应商ID筛选"),
    settlement_period: Optional[str] = Query(None, description="结算周期筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取结算单列表，支持分页和筛选
    """
    query = select(SettlementOrder)
    
    if keyword:
        query = query.where(
            (SettlementOrder.settlement_no.like(f"%{keyword}%")) |
            (SettlementOrder.settlement_period.like(f"%{keyword}%"))
        )
    
    if supplier_id:
        query = query.where(SettlementOrder.supplier_id == supplier_id)
    
    if settlement_period:
        query = query.where(SettlementOrder.settlement_period == settlement_period)
    
    if status:
        query = query.where(SettlementOrder.status == status)
    
    query = query.order_by(SettlementOrder.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    return orders


@router.get("/count", response_model=int, summary="获取结算单总数")
async def get_settlement_orders_count(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    supplier_id: Optional[int] = Query(None, description="供应商ID筛选"),
    settlement_period: Optional[str] = Query(None, description="结算周期筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取结算单总数
    """
    query = select(func.count(SettlementOrder.id))
    
    if keyword:
        query = query.where(
            (SettlementOrder.settlement_no.like(f"%{keyword}%")) |
            (SettlementOrder.settlement_period.like(f"%{keyword}%"))
        )
    
    if supplier_id:
        query = query.where(SettlementOrder.supplier_id == supplier_id)
    
    if settlement_period:
        query = query.where(SettlementOrder.settlement_period == settlement_period)
    
    if status:
        query = query.where(SettlementOrder.status == status)
    
    result = await db.execute(query)
    count = result.scalar_one()
    
    return count


@router.get("/status-options", response_model=List[str], summary="获取状态选项")
async def get_status_options():
    """
    获取所有状态选项，用于下拉选择
    """
    return ["待确认", "已确认", "已付款"]


@router.get("/{order_id}", response_model=SettlementOrderResponse, summary="获取单个结算单")
async def get_settlement_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    根据ID获取结算单详情
    """
    query = select(SettlementOrder).where(SettlementOrder.id == order_id)
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    
    if order is None:
        raise HTTPException(status_code=404, detail=f"结算单 ID: {order_id} 不存在")
    
    return order


@router.post("/", response_model=SettlementOrderResponse, status_code=201, summary="创建结算单")
async def create_settlement_order(
    order: SettlementOrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的结算单
    """
    # 检查结算单号是否已存在
    query = select(SettlementOrder).where(SettlementOrder.settlement_no == order.settlement_no)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"结算单号 {order.settlement_no} 已存在")
    
    # 检查供应商是否存在
    supplier_query = select(Supplier).where(Supplier.id == order.supplier_id)
    supplier_result = await db.execute(supplier_query)
    supplier = supplier_result.scalar_one_or_none()
    if supplier is None:
        raise HTTPException(status_code=400, detail=f"供应商 ID: {order.supplier_id} 不存在")
    
    new_order = SettlementOrder(**order.model_dump())
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    
    return new_order


@router.put("/{order_id}", response_model=SettlementOrderResponse, summary="更新结算单")
async def update_settlement_order(
    order_id: int,
    order: SettlementOrderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新结算单
    """
    query = select(SettlementOrder).where(SettlementOrder.id == order_id)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing is None:
        raise HTTPException(status_code=404, detail=f"结算单 ID: {order_id} 不存在")
    
    update_data = order.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing, key, value)
    
    await db.commit()
    await db.refresh(existing)
    
    return existing


@router.delete("/{order_id}", status_code=204, summary="删除结算单")
async def delete_settlement_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除结算单
    """
    query = select(SettlementOrder).where(SettlementOrder.id == order_id)
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    
    if order is None:
        raise HTTPException(status_code=404, detail=f"结算单 ID: {order_id} 不存在")
    
    await db.delete(order)
    await db.commit()


@router.post("/{order_id}/confirm", response_model=SettlementOrderResponse, summary="确认结算单")
async def confirm_settlement_order(
    order_id: int,
    confirmer: str,
    db: AsyncSession = Depends(get_db)
):
    """
    确认结算单
    """
    from datetime import date
    
    query = select(SettlementOrder).where(SettlementOrder.id == order_id)
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    
    if order is None:
        raise HTTPException(status_code=404, detail=f"结算单 ID: {order_id} 不存在")
    
    if order.status != "待确认":
        raise HTTPException(status_code=400, detail="只能确认待确认状态的结算单")
    
    order.status = "已确认"
    order.confirmed_by = confirmer
    order.confirm_date = date.today()
    
    await db.commit()
    await db.refresh(order)
    
    return order


@router.post("/{order_id}/pay", response_model=SettlementOrderResponse, summary="付款结算单")
async def pay_settlement_order(
    order_id: int,
    payer: str,
    db: AsyncSession = Depends(get_db)
):
    """
    标记结算单为已付款
    """
    from datetime import date
    
    query = select(SettlementOrder).where(SettlementOrder.id == order_id)
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    
    if order is None:
        raise HTTPException(status_code=404, detail=f"结算单 ID: {order_id} 不存在")
    
    if order.status != "已确认":
        raise HTTPException(status_code=400, detail="只能对已确认的结算单进行付款")
    
    order.status = "已付款"
    order.paid_by = payer
    order.paid_date = date.today()
    
    await db.commit()
    await db.refresh(order)
    
    return order


@router.post("/generate/{supplier_id}", response_model=SettlementOrderResponse, summary="生成结算单")
async def generate_settlement_order(
    supplier_id: int,
    settlement_period: str,
    created_by: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    根据供应商和结算周期自动生成结算单
    """
    from datetime import date, datetime
    
    # 检查供应商是否存在
    supplier_query = select(Supplier).where(Supplier.id == supplier_id)
    supplier_result = await db.execute(supplier_query)
    supplier = supplier_result.scalar_one_or_none()
    if supplier is None:
        raise HTTPException(status_code=404, detail=f"供应商 ID: {supplier_id} 不存在")
    
    # 生成结算单号
    settlement_no = f"SO{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 获取该供应商的检验记录（简化逻辑）
    # 实际应用中应该根据日期范围查询
    inspection_query = select(MaterialInspection).where(
        MaterialInspection.supplier_id == supplier_id
    )
    inspection_result = await db.execute(inspection_query)
    inspections = inspection_result.scalars().all()
    
    # 计算统计数据
    inspection_count = len(inspections)
    
    # 简化计算：假设每批平均数量和金额
    # 实际应用中应该有详细的供货记录
    avg_quantity = 100.0  # 假设每批平均100吨
    avg_price = 500.0     # 假设每吨500元
    
    total_quantity = inspection_count * avg_quantity
    total_amount = total_quantity * avg_price
    
    # 计算优惠和最终金额
    discount_amount = total_amount * 0.05  # 假设5%优惠
    final_amount = total_amount - discount_amount
    
    # 解析日期
    today = date.today()
    if start_date:
        try:
            start_date_parsed = date.fromisoformat(start_date)
        except:
            start_date_parsed = today
    else:
        start_date_parsed = today
    
    if end_date:
        try:
            end_date_parsed = date.fromisoformat(end_date)
        except:
            end_date_parsed = today
    else:
        end_date_parsed = today
    
    # 构建材料汇总
    import json
    material_summary = json.dumps([
        {
            "material_type": "水泥",
            "quantity": total_quantity * 0.4,
            "unit_price": avg_price * 1.2,
            "amount": total_quantity * 0.4 * avg_price * 1.2
        },
        {
            "material_type": "骨料",
            "quantity": total_quantity * 0.5,
            "unit_price": avg_price * 0.8,
            "amount": total_quantity * 0.5 * avg_price * 0.8
        },
        {
            "material_type": "外加剂",
            "quantity": total_quantity * 0.1,
            "unit_price": avg_price * 2.0,
            "amount": total_quantity * 0.1 * avg_price * 2.0
        }
    ], ensure_ascii=False)
    
    # 创建结算单
    new_order = SettlementOrder(
        settlement_no=settlement_no,
        supplier_id=supplier_id,
        settlement_period=settlement_period,
        start_date=start_date_parsed,
        end_date=end_date_parsed,
        material_summary=material_summary,
        total_quantity=round(total_quantity, 2),
        total_amount=round(total_amount, 2),
        discount_amount=round(discount_amount, 2),
        final_amount=round(final_amount, 2),
        status="待确认",
        created_by=created_by,
        created_date=today,
        remark=f"系统自动生成结算单，共{inspection_count}批检验记录"
    )
    
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    
    return new_order
