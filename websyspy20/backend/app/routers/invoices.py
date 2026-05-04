"""
票据管理API路由
实现票据（收据、发票）的管理功能
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.database import get_db
from app.models import (
    Invoice as InvoiceModel,
    Bill as BillModel,
    Property as PropertyModel,
    FeeItem as FeeItemModel,
)
from app.schemas import (
    Invoice as InvoiceSchema,
    InvoiceCreate as InvoiceCreateSchema,
    InvoiceStatus,
    InvoiceType,
    BillStatus,
)

router = APIRouter(
    prefix="/api/invoices",
    tags=["票据管理"],
    responses={404: {"description": "未找到"}},
)


def generate_invoice_number() -> str:
    """生成票据编号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return f"INV{timestamp}"


@router.get("/", response_model=List[InvoiceSchema], summary="获取票据列表")
def get_invoices(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    bill_id: Optional[int] = Query(None, description="账单ID筛选"),
    invoice_type: Optional[str] = Query(None, description="票据类型筛选: receipt/invoice"),
    status: Optional[str] = Query(None, description="票据状态筛选"),
    db: Session = Depends(get_db)
):
    """
    获取所有票据列表，支持分页和筛选
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    - **bill_id**: 按账单ID筛选
    - **invoice_type**: 按票据类型筛选
    - **status**: 按票据状态筛选
    """
    query = db.query(InvoiceModel)
    
    if bill_id:
        query = query.filter(InvoiceModel.bill_id == bill_id)
    if invoice_type:
        query = query.filter(InvoiceModel.invoice_type == invoice_type)
    if status:
        query = query.filter(InvoiceModel.status == status)
    
    invoices = query.order_by(InvoiceModel.created_at.desc()).offset(skip).limit(limit).all()
    return invoices


@router.get("/{invoice_id}", response_model=InvoiceSchema, summary="获取单个票据详情")
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取单个票据详情
    
    - **invoice_id**: 票据ID
    """
    invoice = db.query(InvoiceModel).filter(InvoiceModel.id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="票据不存在")
    return invoice


@router.post("/", response_model=InvoiceSchema, summary="创建票据")
def create_invoice(
    invoice_data: InvoiceCreateSchema,
    db: Session = Depends(get_db)
):
    """
    创建新的票据
    
    - **invoice_data**: 票据信息
    """
    # 验证账单是否存在
    bill = db.query(BillModel).filter(BillModel.id == invoice_data.bill_id).first()
    if bill is None:
        raise HTTPException(status_code=400, detail="账单不存在")
    
    # 检查账单是否已支付
    if bill.status not in [BillStatus.PAID.value, BillStatus.PARTIAL.value]:
        raise HTTPException(status_code=400, detail="该账单未支付，无法开具票据")
    
    # 生成票据编号
    invoice_number = generate_invoice_number()
    
    # 如果金额为0，使用账单的已支付金额
    amount = invoice_data.amount
    if amount == 0:
        amount = bill.paid_amount
    
    db_invoice = InvoiceModel(
        **invoice_data.dict(exclude={"amount"}),
        invoice_number=invoice_number,
        amount=amount
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


@router.post("/issue/{invoice_id}", response_model=InvoiceSchema, summary="开具票据")
def issue_invoice(
    invoice_id: int,
    issuer: Optional[str] = Query(None, description="开票人"),
    db: Session = Depends(get_db)
):
    """
    开具票据（将状态改为已开具）
    
    - **invoice_id**: 票据ID
    - **issuer**: 开票人
    """
    invoice = db.query(InvoiceModel).filter(InvoiceModel.id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="票据不存在")
    
    if invoice.status != InvoiceStatus.PENDING.value:
        raise HTTPException(status_code=400, detail="该票据无法开具")
    
    invoice.status = InvoiceStatus.ISSUED.value
    invoice.issued_at = datetime.now()
    if issuer:
        invoice.issuer = issuer
    
    db.commit()
    db.refresh(invoice)
    return invoice


@router.post("/void/{invoice_id}", response_model=InvoiceSchema, summary="作废票据")
def void_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    """
    作废票据
    
    - **invoice_id**: 票据ID
    """
    invoice = db.query(InvoiceModel).filter(InvoiceModel.id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="票据不存在")
    
    if invoice.status == InvoiceStatus.VOIDED.value:
        raise HTTPException(status_code=400, detail="该票据已作废")
    
    invoice.status = InvoiceStatus.VOIDED.value
    
    db.commit()
    db.refresh(invoice)
    return invoice


@router.post("/from-bill/{bill_id}", response_model=InvoiceSchema, summary="根据账单开具票据")
def create_invoice_from_bill(
    bill_id: int,
    invoice_type: str = Query("receipt", description="票据类型: receipt/invoice"),
    invoice_title: Optional[str] = Query(None, description="发票抬头"),
    tax_number: Optional[str] = Query(None, description="税号"),
    issuer: Optional[str] = Query(None, description="开票人"),
    db: Session = Depends(get_db)
):
    """
    根据账单快速开具票据
    
    - **bill_id**: 账单ID
    - **invoice_type**: 票据类型
    - **invoice_title**: 发票抬头（仅发票类型需要）
    - **tax_number**: 税号（仅发票类型需要）
    - **issuer**: 开票人
    """
    # 验证账单是否存在
    bill = db.query(BillModel).filter(BillModel.id == bill_id).first()
    if bill is None:
        raise HTTPException(status_code=404, detail="账单不存在")
    
    # 检查账单是否已支付
    if bill.status not in [BillStatus.PAID.value, BillStatus.PARTIAL.value]:
        raise HTTPException(status_code=400, detail="该账单未支付，无法开具票据")
    
    # 检查该账单是否已有已开具的票据
    existing = db.query(InvoiceModel).filter(
        InvoiceModel.bill_id == bill_id,
        InvoiceModel.status == InvoiceStatus.ISSUED.value
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该账单已开具票据")
    
    # 生成票据编号
    invoice_number = generate_invoice_number()
    
    db_invoice = InvoiceModel(
        invoice_number=invoice_number,
        bill_id=bill_id,
        invoice_type=invoice_type,
        amount=bill.paid_amount,
        invoice_title=invoice_title,
        tax_number=tax_number,
        issuer=issuer,
        status=InvoiceStatus.ISSUED.value,
        issued_at=datetime.now()
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


@router.get("/stats/financial", summary="获取财务统计信息")
def get_financial_stats(
    year: Optional[int] = Query(None, description="年份筛选"),
    month: Optional[int] = Query(None, description="月份筛选"),
    db: Session = Depends(get_db)
):
    """
    获取财务统计信息，支持按年月筛选
    
    - **year**: 年份
    - **month**: 月份
    """
    # 基础查询
    bill_query = db.query(BillModel)
    invoice_query = db.query(InvoiceModel).filter(
        InvoiceModel.status == InvoiceStatus.ISSUED.value
    )
    
    # 按年月筛选
    if year:
        bill_query = bill_query.filter(BillModel.billing_year == year)
        invoice_query = invoice_query.filter(
            InvoiceModel.issued_at >= datetime(year, 1, 1),
            InvoiceModel.issued_at < datetime(year + 1, 1, 1)
        )
    if month and year:
        bill_query = bill_query.filter(BillModel.billing_month == month)
        invoice_query = invoice_query.filter(
            InvoiceModel.issued_at >= datetime(year, month, 1),
            InvoiceModel.issued_at < (
                datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
            )
        )
    
    # 统计账单
    total_bills = bill_query.count()
    total_amount = db.query(func.sum(BillModel.amount)).filter(
        BillModel.id.in_([b.id for b in bill_query.all()])
    ).scalar() or Decimal(0)
    paid_amount = db.query(func.sum(BillModel.paid_amount)).filter(
        BillModel.id.in_([b.id for b in bill_query.all()])
    ).scalar() or Decimal(0)
    
    # 统计待付和逾期
    pending_query = bill_query.filter(BillModel.status.in_(
        [BillStatus.PENDING.value, BillStatus.PARTIAL.value]
    ))
    overdue_query = bill_query.filter(BillModel.status == BillStatus.OVERDUE.value)
    
    unpaid_amount = db.query(func.sum(BillModel.amount - BillModel.paid_amount)).filter(
        BillModel.id.in_([b.id for b in pending_query.all()])
    ).scalar() or Decimal(0)
    overdue_amount = db.query(func.sum(BillModel.amount - BillModel.paid_amount)).filter(
        BillModel.id.in_([b.id for b in overdue_query.all()])
    ).scalar() or Decimal(0)
    
    # 统计票据
    total_invoices = invoice_query.count()
    invoice_amount = db.query(func.sum(InvoiceModel.amount)).filter(
        InvoiceModel.id.in_([i.id for i in invoice_query.all()])
    ).scalar() or Decimal(0)
    
    # 按费用项目统计
    fee_item_stats = db.query(
        func.coalesce(BillModel.fee_item_id, 0).label("fee_item_id"),
        func.count(BillModel.id).label("count"),
        func.sum(BillModel.amount).label("total_amount"),
        func.sum(BillModel.paid_amount).label("paid_amount")
    ).filter(
        BillModel.id.in_([b.id for b in bill_query.all()])
    ).group_by(BillModel.fee_item_id).all()
    
    return {
        "period": {
            "year": year,
            "month": month
        },
        "bills": {
            "total_count": total_bills,
            "total_amount": total_amount,
            "paid_amount": paid_amount,
            "unpaid_amount": unpaid_amount,
            "overdue_amount": overdue_amount
        },
        "invoices": {
            "total_count": total_invoices,
            "total_amount": invoice_amount
        },
        "fee_item_breakdown": [
            {
                "fee_item_id": stat.fee_item_id,
                "bill_count": stat.count,
                "total_amount": stat.total_amount,
                "paid_amount": stat.paid_amount
            }
            for stat in fee_item_stats
        ]
    }


@router.get("/bill/{bill_id}", response_model=List[InvoiceSchema], summary="获取账单的票据")
def get_bill_invoices(
    bill_id: int,
    db: Session = Depends(get_db)
):
    """
    获取指定账单的所有票据
    
    - **bill_id**: 账单ID
    """
    bill = db.query(BillModel).filter(BillModel.id == bill_id).first()
    if bill is None:
        raise HTTPException(status_code=404, detail="账单不存在")
    
    invoices = db.query(InvoiceModel).filter(
        InvoiceModel.bill_id == bill_id
    ).order_by(InvoiceModel.created_at.desc()).all()
    
    return invoices


class BillInvoiceInfo(BaseModel):
    """待开票账单信息模型"""
    id: int
    bill_number: str
    billing_year: int
    billing_month: int
    amount: Decimal
    paid_amount: Decimal
    status: str
    due_date: Optional[date]
    paid_at: Optional[datetime]
    property_number: Optional[str]
    owner_name: Optional[str]
    fee_item_name: Optional[str]
    has_invoice: bool


@router.get("/pending/list", summary="获取待开票账单列表")
def get_pending_invoice_bills(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    billing_year: Optional[int] = Query(None, description="计费年份"),
    billing_month: Optional[int] = Query(None, description="计费月份"),
    db: Session = Depends(get_db)
):
    """
    获取待开票的账单列表（已支付但未开票的账单）
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    - **search**: 搜索关键词（房产编号、业主姓名、账单编号）
    - **billing_year**: 计费年份筛选
    - **billing_month**: 计费月份筛选
    """
    paid_bills = db.query(BillModel).filter(
        BillModel.status.in_([BillStatus.PAID.value, BillStatus.PARTIAL.value]),
        BillModel.paid_amount > 0
    )
    
    if billing_year:
        paid_bills = paid_bills.filter(BillModel.billing_year == billing_year)
    if billing_month:
        paid_bills = paid_bills.filter(BillModel.billing_month == billing_month)
    
    if search:
        search_pattern = f"%{search}%"
        paid_bills = paid_bills.join(
            PropertyModel, BillModel.property_id == PropertyModel.id, isouter=True
        ).filter(
            or_(
                BillModel.bill_number.ilike(search_pattern),
                PropertyModel.property_number.ilike(search_pattern),
                PropertyModel.owner_name.ilike(search_pattern)
            )
        )
    
    paid_bills = paid_bills.order_by(BillModel.paid_at.desc())
    
    bills = paid_bills.offset(skip).limit(limit).all()
    total = paid_bills.count()
    
    result = []
    for bill in bills:
        has_invoice = db.query(InvoiceModel).filter(
            InvoiceModel.bill_id == bill.id,
            InvoiceModel.status == InvoiceStatus.ISSUED.value
        ).first() is not None
        
        property_obj = bill.property
        fee_item = bill.fee_item
        
        result.append(BillInvoiceInfo(
            id=bill.id,
            bill_number=bill.bill_number,
            billing_year=bill.billing_year,
            billing_month=bill.billing_month,
            amount=bill.amount,
            paid_amount=bill.paid_amount,
            status=bill.status,
            due_date=bill.due_date,
            paid_at=bill.paid_at,
            property_number=property_obj.property_number if property_obj else None,
            owner_name=property_obj.owner_name if property_obj else None,
            fee_item_name=fee_item.name if fee_item else None,
            has_invoice=has_invoice
        ))
    
    return {
        "items": result,
        "total": total,
        "skip": skip,
        "limit": limit
    }


class BatchInvoiceRequest(BaseModel):
    """批量开票请求模型"""
    bill_ids: List[int] = Field(..., description="账单ID列表")
    invoice_type: str = Field(default="invoice", description="票据类型: receipt/invoice")
    invoice_title: Optional[str] = Field(None, description="发票抬头")
    tax_number: Optional[str] = Field(None, description="税号")
    issuer: Optional[str] = Field(None, description="开票人")


@router.post("/batch-issue", summary="批量开具发票")
def batch_issue_invoices(
    request: BatchInvoiceRequest,
    db: Session = Depends(get_db)
):
    """
    批量开具发票/收据
    
    - **bill_ids**: 账单ID列表
    - **invoice_type**: 票据类型
    - **invoice_title**: 发票抬头
    - **tax_number**: 税号
    - **issuer**: 开票人
    """
    success_count = 0
    fail_count = 0
    failed_bills = []
    created_invoices = []
    
    for bill_id in request.bill_ids:
        try:
            bill = db.query(BillModel).filter(BillModel.id == bill_id).first()
            if bill is None:
                fail_count += 1
                failed_bills.append({"bill_id": bill_id, "reason": "账单不存在"})
                continue
            
            if bill.status not in [BillStatus.PAID.value, BillStatus.PARTIAL.value]:
                fail_count += 1
                failed_bills.append({"bill_id": bill_id, "reason": "该账单未支付"})
                continue
            
            existing = db.query(InvoiceModel).filter(
                InvoiceModel.bill_id == bill_id,
                InvoiceModel.status == InvoiceStatus.ISSUED.value
            ).first()
            if existing:
                fail_count += 1
                failed_bills.append({"bill_id": bill_id, "reason": "该账单已开具票据"})
                continue
            
            invoice_number = generate_invoice_number()
            
            db_invoice = InvoiceModel(
                invoice_number=invoice_number,
                bill_id=bill_id,
                invoice_type=request.invoice_type,
                amount=bill.paid_amount,
                invoice_title=request.invoice_title,
                tax_number=request.tax_number,
                issuer=request.issuer,
                status=InvoiceStatus.ISSUED.value,
                issued_at=datetime.now()
            )
            db.add(db_invoice)
            db.flush()
            
            created_invoices.append({
                "id": db_invoice.id,
                "invoice_number": db_invoice.invoice_number,
                "bill_id": bill_id,
                "amount": float(db_invoice.amount)
            })
            
            success_count += 1
            
        except Exception as e:
            fail_count += 1
            failed_bills.append({"bill_id": bill_id, "reason": str(e)})
            db.rollback()
        else:
            db.commit()
    
    return {
        "success": True,
        "message": f"批量开票完成：成功 {success_count} 张，失败 {fail_count} 张",
        "result": {
            "success_count": success_count,
            "fail_count": fail_count,
            "failed_bills": failed_bills,
            "created_invoices": created_invoices
        }
    }


@router.get("/invoice-preview/{bill_id}", summary="获取发票预览数据")
def get_invoice_preview(
    bill_id: int,
    invoice_type: str = Query("invoice", description="票据类型: receipt/invoice"),
    db: Session = Depends(get_db)
):
    """
    获取发票/收据预览数据
    
    - **bill_id**: 账单ID
    - **invoice_type**: 票据类型
    """
    bill = db.query(BillModel).filter(BillModel.id == bill_id).first()
    if bill is None:
        raise HTTPException(status_code=404, detail="账单不存在")
    
    property_obj = bill.property
    fee_item = bill.fee_item
    
    return {
        "bill_number": bill.bill_number,
        "invoice_type": invoice_type,
        "invoice_type_name": "增值税普通发票" if invoice_type == "invoice" else "收款收据",
        "amount": bill.paid_amount,
        "amount_cn": decimal_to_cn(bill.paid_amount),
        "billing_period": f"{bill.billing_year}年{bill.billing_month}月",
        
        "property_info": {
            "property_number": property_obj.property_number if property_obj else None,
            "building": property_obj.building if property_obj else None,
            "unit": property_obj.unit if property_obj else None,
            "room_number": property_obj.room_number if property_obj else None,
            "area": property_obj.area if property_obj else None,
            "owner_name": property_obj.owner_name if property_obj else None,
            "owner_phone": property_obj.owner_phone if property_obj else None,
        } if property_obj else None,
        
        "fee_item_info": {
            "name": fee_item.name if fee_item else None,
            "code": fee_item.code if fee_item else None,
            "billing_cycle": fee_item.billing_cycle if fee_item else None,
        } if fee_item else None,
        
        "paid_info": {
            "paid_at": bill.paid_at,
            "payment_method": bill.payment_method,
            "total_amount": bill.amount,
            "paid_amount": bill.paid_amount,
            "unpaid_amount": bill.amount - bill.paid_amount,
        },
        
        "preview_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def decimal_to_cn(amount: Decimal) -> str:
    """
    将金额转换为中文大写
    """
    cn_nums = ["零", "壹", "贰", "叁", "肆", "伍", "陆", "柒", "捌", "玖"]
    cn_units = ["", "拾", "佰", "仟", "万", "拾", "佰", "仟", "亿"]
    cn_decimal = ["角", "分"]
    
    amount_str = f"{amount:.2f}"
    integer_part, decimal_part = amount_str.split(".")
    
    result = ""
    
    if integer_part == "0":
        result = "零元"
    else:
        integer_digits = list(integer_part)
        length = len(integer_digits)
        for i, digit in enumerate(integer_digits):
            d = int(digit)
            pos = length - 1 - i
            
            if d != 0:
                result += cn_nums[d] + cn_units[pos]
            else:
                if pos % 4 == 0:
                    result += cn_units[pos]
                elif result and not result.endswith("零"):
                    result += "零"
        
        result = result.replace("零零", "零").replace("零万", "万").replace("零亿", "亿")
        if result.endswith("零"):
            result = result[:-1]
        result += "元"
    
    jiao = int(decimal_part[0])
    fen = int(decimal_part[1])
    
    if jiao == 0 and fen == 0:
        result += "整"
    else:
        if jiao != 0:
            result += cn_nums[jiao] + "角"
        elif jiao == 0 and integer_part != "0":
            result += "零"
        
        if fen != 0:
            result += cn_nums[fen] + "分"
    
    return result


@router.get("/stats/overview", summary="获取票据统计概览")
def get_invoice_overview(
    start_date: Optional[str] = Query(None, description="开始日期(YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期(YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    获取票据统计概览
    
    - **start_date**: 开始日期
    - **end_date**: 结束日期
    """
    query = db.query(InvoiceModel).filter(InvoiceModel.status == InvoiceStatus.ISSUED.value)
    
    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.filter(InvoiceModel.issued_at >= start_dt)
    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        query = query.filter(InvoiceModel.issued_at < end_dt)
    
    total_count = query.count()
    total_amount = db.query(func.sum(InvoiceModel.amount)).filter(
        InvoiceModel.id.in_([i.id for i in query.all()])
    ).scalar() or Decimal(0)
    
    invoice_count = query.filter(InvoiceModel.invoice_type == InvoiceType.INVOICE.value).count()
    receipt_count = query.filter(InvoiceModel.invoice_type == InvoiceType.RECEIPT.value).count()
    
    invoice_amount = db.query(func.sum(InvoiceModel.amount)).filter(
        InvoiceModel.invoice_type == InvoiceType.INVOICE.value,
        InvoiceModel.status == InvoiceStatus.ISSUED.value
    ).scalar() or Decimal(0)
    
    receipt_amount = total_amount - invoice_amount
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "summary": {
            "total_count": total_count,
            "total_amount": total_amount,
            "invoice_count": invoice_count,
            "invoice_amount": invoice_amount,
            "receipt_count": receipt_count,
            "receipt_amount": receipt_amount
        }
    }
