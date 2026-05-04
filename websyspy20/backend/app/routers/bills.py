"""
账单管理API路由
实现账单的增删改查、支付、批量生成等功能
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.models import (
    Bill as BillModel,
    Property as PropertyModel,
    FeeItem as FeeItemModel,
    PaymentRecord as PaymentRecordModel,
)
from app.schemas import (
    Bill as BillSchema,
    BillCreate as BillCreateSchema,
    BillUpdate as BillUpdateSchema,
    BillPayment as BillPaymentSchema,
    BatchBillGenerate as BatchBillGenerateSchema,
    PaymentRecord as PaymentRecordSchema,
    BillStatus,
)

router = APIRouter(
    prefix="/api/bills",
    tags=["账单管理"],
    responses={404: {"description": "未找到"}},
)


def generate_bill_number(billing_year: int, billing_month: int, property_id: int, fee_item_id: int) -> str:
    """生成账单编号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"B{billing_year:04d}{billing_month:02d}{property_id:06d}{fee_item_id:04d}{timestamp[-4:]}"


def generate_record_number() -> str:
    """生成缴费记录编号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"R{timestamp}"


def calculate_bill_amount(property_obj: PropertyModel, fee_item: FeeItemModel) -> Decimal:
    """
    根据房产信息和费用项目计算账单金额
    
    计算逻辑：
    - 按面积计费: 房产面积 × 单位价格
    - 按单位计费: 1 × 单位价格
    - 固定金额: 单位价格
    """
    if fee_item.billing_type == "area":
        return property_obj.area * fee_item.unit_price
    elif fee_item.billing_type == "unit":
        return fee_item.unit_price
    elif fee_item.billing_type == "fixed":
        return fee_item.unit_price
    return Decimal(0)


@router.get("/", response_model=List[BillSchema], summary="获取账单列表")
def get_bills(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    status: Optional[str] = Query(None, description="账单状态过滤"),
    billing_year: Optional[int] = Query(None, description="计费年份"),
    billing_month: Optional[int] = Query(None, description="计费月份"),
    property_id: Optional[int] = Query(None, description="房产ID"),
    db: Session = Depends(get_db)
):
    """
    获取所有账单列表，支持分页和筛选
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    - **status**: 按账单状态筛选
    - **billing_year**: 按计费年份筛选
    - **billing_month**: 按计费月份筛选
    - **property_id**: 按房产ID筛选
    """
    query = db.query(BillModel)
    
    if status:
        query = query.filter(BillModel.status == status)
    if billing_year:
        query = query.filter(BillModel.billing_year == billing_year)
    if billing_month:
        query = query.filter(BillModel.billing_month == billing_month)
    if property_id:
        query = query.filter(BillModel.property_id == property_id)
    
    bills = query.order_by(BillModel.created_at.desc()).offset(skip).limit(limit).all()
    
    # 填充关联信息
    for bill in bills:
        bill.property_info = bill.property
        bill.fee_item_info = bill.fee_item
    
    return bills


@router.get("/{bill_id}", response_model=BillSchema, summary="获取单个账单详情")
def get_bill(bill_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取单个账单详情
    
    - **bill_id**: 账单ID
    """
    bill = db.query(BillModel).filter(BillModel.id == bill_id).first()
    if bill is None:
        raise HTTPException(status_code=404, detail="账单不存在")
    
    bill.property_info = bill.property
    bill.fee_item_info = bill.fee_item
    return bill


@router.post("/", response_model=BillSchema, summary="创建账单")
def create_bill(
    bill_data: BillCreateSchema,
    db: Session = Depends(get_db)
):
    """
    创建新的账单
    
    - **bill_data**: 账单信息
    """
    # 验证房产是否存在
    property_obj = db.query(PropertyModel).filter(
        PropertyModel.id == bill_data.property_id
    ).first()
    if property_obj is None:
        raise HTTPException(status_code=400, detail="房产信息不存在")
    
    # 验证费用项目是否存在
    fee_item = db.query(FeeItemModel).filter(
        FeeItemModel.id == bill_data.fee_item_id
    ).first()
    if fee_item is None:
        raise HTTPException(status_code=400, detail="费用项目不存在")
    
    # 检查该房产该月份该费用项目的账单是否已存在
    existing = db.query(BillModel).filter(
        BillModel.property_id == bill_data.property_id,
        BillModel.fee_item_id == bill_data.fee_item_id,
        BillModel.billing_year == bill_data.billing_year,
        BillModel.billing_month == bill_data.billing_month
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该账单已存在")
    
    # 如果金额为0，则自动计算
    amount = bill_data.amount
    if amount == 0:
        amount = calculate_bill_amount(property_obj, fee_item)
    
    # 生成账单编号
    bill_number = generate_bill_number(
        bill_data.billing_year,
        bill_data.billing_month,
        bill_data.property_id,
        bill_data.fee_item_id
    )
    
    # 计算缴费截止日期（默认当月25号）
    if bill_data.due_date is None:
        due_date = date(bill_data.billing_year, bill_data.billing_month, 25)
    else:
        due_date = bill_data.due_date
    
    db_bill = BillModel(
        **bill_data.dict(exclude={"amount", "due_date"}),
        bill_number=bill_number,
        amount=amount,
        paid_amount=Decimal(0),
        due_date=due_date
    )
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    
    db_bill.property_info = db_bill.property
    db_bill.fee_item_info = db_bill.fee_item
    return db_bill


@router.post("/batch-generate", summary="批量生成账单")
def batch_generate_bills(
    batch_data: BatchBillGenerateSchema,
    db: Session = Depends(get_db)
):
    """
    批量生成账单
    
    - **batch_data**: 批量生成参数
    """
    # 获取需要生成账单的费用项目
    if batch_data.fee_item_ids:
        fee_items = db.query(FeeItemModel).filter(
            FeeItemModel.id.in_(batch_data.fee_item_ids),
            FeeItemModel.is_active == True
        ).all()
    else:
        fee_items = db.query(FeeItemModel).filter(
            FeeItemModel.is_active == True
        ).all()
    
    if not fee_items:
        raise HTTPException(status_code=400, detail="没有可用的费用项目")
    
    # 获取需要生成账单的房产
    if batch_data.property_ids:
        properties = db.query(PropertyModel).filter(
            PropertyModel.id.in_(batch_data.property_ids),
            PropertyModel.is_active == True
        ).all()
    else:
        properties = db.query(PropertyModel).filter(
            PropertyModel.is_active == True
        ).all()
    
    if not properties:
        raise HTTPException(status_code=400, detail="没有可用的房产信息")
    
    generated_count = 0
    skipped_count = 0
    
    # 遍历所有组合生成账单
    for property_obj in properties:
        for fee_item in fee_items:
            # 检查是否已存在
            existing = db.query(BillModel).filter(
                BillModel.property_id == property_obj.id,
                BillModel.fee_item_id == fee_item.id,
                BillModel.billing_year == batch_data.billing_year,
                BillModel.billing_month == batch_data.billing_month
            ).first()
            
            if existing:
                skipped_count += 1
                continue
            
            # 计算金额
            amount = calculate_bill_amount(property_obj, fee_item)
            
            # 生成账单编号
            bill_number = generate_bill_number(
                batch_data.billing_year,
                batch_data.billing_month,
                property_obj.id,
                fee_item.id
            )
            
            # 计算缴费截止日期
            due_date = date(batch_data.billing_year, batch_data.billing_month, 25)
            
            db_bill = BillModel(
                bill_number=bill_number,
                property_id=property_obj.id,
                fee_item_id=fee_item.id,
                billing_year=batch_data.billing_year,
                billing_month=batch_data.billing_month,
                amount=amount,
                paid_amount=Decimal(0),
                status=BillStatus.PENDING.value,
                due_date=due_date
            )
            db.add(db_bill)
            generated_count += 1
    
    db.commit()
    
    return {
        "message": "批量生成完成",
        "generated_count": generated_count,
        "skipped_count": skipped_count
    }


@router.put("/{bill_id}", response_model=BillSchema, summary="更新账单")
def update_bill(
    bill_id: int,
    bill_data: BillUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    更新账单信息
    
    - **bill_id**: 账单ID
    - **bill_data**: 更新的账单信息
    """
    db_bill = db.query(BillModel).filter(BillModel.id == bill_id).first()
    if db_bill is None:
        raise HTTPException(status_code=404, detail="账单不存在")
    
    # 只更新传入的字段
    update_data = bill_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_bill, key, value)
    
    db.commit()
    db.refresh(db_bill)
    
    db_bill.property_info = db_bill.property
    db_bill.fee_item_info = db_bill.fee_item
    return db_bill


@router.post("/{bill_id}/pay", response_model=PaymentRecordSchema, summary="支付账单")
def pay_bill(
    bill_id: int,
    payment_data: BillPaymentSchema,
    db: Session = Depends(get_db)
):
    """
    支付账单
    
    - **bill_id**: 账单ID
    - **payment_data**: 支付信息
    """
    db_bill = db.query(BillModel).filter(BillModel.id == bill_id).first()
    if db_bill is None:
        raise HTTPException(status_code=404, detail="账单不存在")
    
    # 检查账单状态
    if db_bill.status == BillStatus.CANCELLED.value:
        raise HTTPException(status_code=400, detail="账单已取消，无法支付")
    if db_bill.status == BillStatus.PAID.value:
        raise HTTPException(status_code=400, detail="账单已全部支付")
    
    # 检查支付金额
    remaining = db_bill.amount - db_bill.paid_amount
    if payment_data.amount > remaining:
        raise HTTPException(
            status_code=400,
            detail=f"支付金额超过待付金额，剩余待付: {remaining}"
        )
    
    # 创建缴费记录
    record_number = generate_record_number()
    db_record = PaymentRecordModel(
        record_number=record_number,
        bill_id=bill_id,
        amount=payment_data.amount,
        payment_method=payment_data.payment_method.value,
        transaction_id=payment_data.transaction_id,
        collector=payment_data.collector
    )
    db.add(db_record)
    
    # 更新账单状态
    db_bill.paid_amount += payment_data.amount
    db_bill.payment_method = payment_data.payment_method.value
    
    if db_bill.paid_amount >= db_bill.amount:
        db_bill.status = BillStatus.PAID.value
        db_bill.paid_at = datetime.now()
    else:
        db_bill.status = BillStatus.PARTIAL.value
    
    db.commit()
    db.refresh(db_record)
    
    return db_record


@router.get("/property/{property_id}", response_model=List[BillSchema], summary="获取指定房产的账单")
def get_property_bills(
    property_id: int,
    status: Optional[str] = Query(None, description="账单状态过滤"),
    db: Session = Depends(get_db)
):
    """
    获取指定房产的所有账单
    
    - **property_id**: 房产ID
    - **status**: 按账单状态筛选
    """
    query = db.query(BillModel).filter(BillModel.property_id == property_id)
    
    if status:
        query = query.filter(BillModel.status == status)
    
    bills = query.order_by(BillModel.billing_year.desc(), BillModel.billing_month.desc()).all()
    
    for bill in bills:
        bill.property_info = bill.property
        bill.fee_item_info = bill.fee_item
    
    return bills


@router.get("/overdue/list", response_model=List[BillSchema], summary="获取逾期账单列表")
def get_overdue_bills(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    db: Session = Depends(get_db)
):
    """
    获取逾期未缴费的账单列表
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    """
    today = date.today()
    
    # 更新逾期状态
    db.query(BillModel).filter(
        BillModel.status.in_([BillStatus.PENDING.value, BillStatus.PARTIAL.value]),
        BillModel.due_date < today
    ).update({"status": BillStatus.OVERDUE.value}, synchronize_session=False)
    db.commit()
    
    # 查询逾期账单
    bills = db.query(BillModel).filter(
        BillModel.status == BillStatus.OVERDUE.value
    ).order_by(BillModel.due_date.asc()).offset(skip).limit(limit).all()
    
    for bill in bills:
        bill.property_info = bill.property
        bill.fee_item_info = bill.fee_item
    
    return bills
