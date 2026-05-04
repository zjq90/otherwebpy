"""
测试功能API模块
提供系统测试相关的接口，包括测试数据生成、清空数据、健康检查等
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, Base
from app.models import FeeItem, Property, Bill, PaymentRecord, Reminder, Invoice
from app.schemas import BillStatus, PaymentMethod, ReminderMethod, InvoiceType, InvoiceStatus
from app.test_data_generator import (
    generate_fee_items,
    generate_properties,
    generate_bills,
    generate_payment_records,
    generate_reminders,
    generate_invoices,
)

router = APIRouter(
    prefix="/api/test",
    tags=["系统测试"],
    responses={404: {"description": "Not found"}},
)


def get_db():
    """
    获取数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestDataGenerateRequest(BaseModel):
    """
    测试数据生成请求模型
    """
    property_count: int = Query(default=50, ge=1, le=500, description="生成的房产数量")
    months_count: int = Query(default=6, ge=1, le=24, description="生成过去多少个月的账单")


class TestDataGenerateResponse(BaseModel):
    """
    测试数据生成响应模型
    """
    success: bool
    message: str
    stats: dict


class DatabaseStatsResponse(BaseModel):
    """
    数据库统计响应模型
    """
    fee_items_count: int
    properties_count: int
    bills_count: int
    payment_records_count: int
    reminders_count: int
    invoices_count: int
    total_amount: Decimal
    paid_amount: Decimal
    overdue_amount: Decimal


@router.post("/generate-test-data", summary="生成测试数据", response_model=TestDataGenerateResponse)
def generate_test_data(
    property_count: int = Query(default=50, ge=1, le=500, description="房产数量"),
    months_count: int = Query(default=6, ge=1, le=24, description="账单月份数"),
    db: Session = Depends(get_db)
):
    """
    生成测试数据
    
    - **property_count**: 生成的房产数量（1-500）
    - **months_count**: 生成过去多少个月的账单（1-24）
    
    将生成以下数据：
    - 默认费用项目（物业费、停车费、水电公摊、维修基金等）
    - 指定数量的房产信息（含业主信息）
    - 指定月份的账单数据
    - 缴费记录
    - 催缴记录
    - 票据记录
    """
    try:
        print(f"开始生成测试数据: 房产数量={property_count}, 账单月份数={months_count}")
        
        print("正在生成费用项目数据...")
        fee_items = generate_fee_items(db)
        print(f"已生成 {len(fee_items)} 个费用项目")
        
        print(f"正在生成房产数据 ({property_count} 个)...")
        properties = generate_properties(db, property_count)
        print(f"已生成 {len(properties)} 个房产")
        
        print(f"正在生成账单数据 (过去 {months_count} 个月)...")
        bills = generate_bills(db, properties, fee_items, months_count)
        print(f"已生成 {len(bills)} 个账单")
        
        print("正在生成缴费记录数据...")
        payment_records = generate_payment_records(db, bills)
        print(f"已生成 {len(payment_records)} 条缴费记录")
        
        print("正在生成催缴记录数据...")
        reminders = generate_reminders(db, bills)
        print(f"已生成 {len(reminders)} 条催缴记录")
        
        print("正在生成票据数据...")
        invoices = generate_invoices(db, bills)
        print(f"已生成 {len(invoices)} 张票据")
        
        return TestDataGenerateResponse(
            success=True,
            message="测试数据生成成功",
            stats={
                "fee_items": len(fee_items),
                "properties": len(properties),
                "bills": len(bills),
                "payment_records": len(payment_records),
                "reminders": len(reminders),
                "invoices": len(invoices),
            }
        )
        
    except Exception as e:
        print(f"生成测试数据时发生错误: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"生成测试数据失败: {str(e)}")


@router.post("/clear-all-data", summary="清空所有测试数据")
def clear_all_data(db: Session = Depends(get_db)):
    """
    清空所有测试数据
    
    此操作将删除所有表中的数据，重置数据库状态。
    请谨慎使用此操作。
    """
    try:
        print("正在清空所有数据...")
        
        db.query(Invoice).delete()
        db.query(Reminder).delete()
        db.query(PaymentRecord).delete()
        db.query(Bill).delete()
        db.query(Property).delete()
        db.query(FeeItem).delete()
        
        db.commit()
        
        return {
            "success": True,
            "message": "所有数据已清空"
        }
        
    except Exception as e:
        print(f"清空数据时发生错误: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"清空数据失败: {str(e)}")


@router.get("/database-stats", summary="获取数据库统计信息", response_model=DatabaseStatsResponse)
def get_database_stats(db: Session = Depends(get_db)):
    """
    获取数据库统计信息
    
    返回各表的数据量以及财务统计信息
    """
    try:
        fee_items_count = db.query(FeeItem).count()
        properties_count = db.query(Property).count()
        bills_count = db.query(Bill).count()
        payment_records_count = db.query(PaymentRecord).count()
        reminders_count = db.query(Reminder).count()
        invoices_count = db.query(Invoice).count()
        
        from sqlalchemy import func
        
        total_amount_result = db.query(func.sum(Bill.amount)).scalar()
        total_amount = total_amount_result or Decimal(0)
        
        paid_amount_result = db.query(func.sum(Bill.paid_amount)).scalar()
        paid_amount = paid_amount_result or Decimal(0)
        
        overdue_amount_result = db.query(func.sum(Bill.amount - Bill.paid_amount)).filter(
            Bill.status == BillStatus.OVERDUE.value
        ).scalar()
        overdue_amount = overdue_amount_result or Decimal(0)
        
        return DatabaseStatsResponse(
            fee_items_count=fee_items_count,
            properties_count=properties_count,
            bills_count=bills_count,
            payment_records_count=payment_records_count,
            reminders_count=reminders_count,
            invoices_count=invoices_count,
            total_amount=total_amount,
            paid_amount=paid_amount,
            overdue_amount=overdue_amount,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get("/health-check", summary="系统健康检查")
def health_check():
    """
    系统健康检查接口
    
    用于检查系统是否正常运行，返回系统信息
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "database": "SQLite",
        "framework": "FastAPI"
    }


@router.post("/reset-database", summary="重置数据库")
def reset_database(db: Session = Depends(get_db)):
    """
    重置数据库
    
    此操作将删除所有表并重新创建表结构。
    这是最彻底的重置方式，请谨慎使用。
    """
    try:
        print("正在重置数据库...")
        
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        
        return {
            "success": True,
            "message": "数据库已重置，所有表已重新创建"
        }
        
    except Exception as e:
        print(f"重置数据库时发生错误: {e}")
        raise HTTPException(status_code=500, detail=f"重置数据库失败: {str(e)}")


@router.get("/quick-test", summary="快速测试")
def quick_test(db: Session = Depends(get_db)):
    """
    快速测试接口
    
    执行快速的系统功能测试，返回测试结果
    """
    try:
        results = {}
        
        results["database_connection"] = {
            "status": "ok",
            "message": "数据库连接正常"
        }
        
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db.commit()
        
        fee_items_count = db.query(FeeItem).count()
        properties_count = db.query(Property).count()
        bills_count = db.query(Bill).count()
        
        results["data_counts"] = {
            "fee_items": fee_items_count,
            "properties": properties_count,
            "bills": bills_count,
        }
        
        results["recommendations"] = []
        if fee_items_count == 0:
            results["recommendations"].append("建议先调用 /api/test/generate-test-data 生成测试数据")
        if properties_count == 0:
            results["recommendations"].append("没有房产数据，请添加房产或生成测试数据")
        
        results["api_docs"] = {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "description": "访问上述地址查看完整的API文档"
        }
        
        return {
            "success": True,
            "message": "快速测试完成",
            "results": results
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"快速测试失败: {str(e)}",
            "error": str(e)
        }
