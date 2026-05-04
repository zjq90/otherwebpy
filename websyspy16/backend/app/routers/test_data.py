"""
测试数据生成API路由
提供通过API生成测试数据的接口，用于功能测试
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.config import get_db
from app.test_data import generate_all_test_data

router = APIRouter(
    prefix="/api/test-data",
    tags=["测试数据生成"]
)


@router.post("/generate", summary="生成测试数据")
def generate_test_data(
    clear_existing: bool = Query(True, description="是否清除现有数据"),
    db: Session = Depends(get_db)
):
    """
    生成测试数据接口
    
    - 会生成物业项目、房产、业主/住户、家庭成员、车辆信息等测试数据
    - 可以选择是否在生成前清除现有数据
    
    Args:
        clear_existing: 是否清除现有数据，默认为True
        db: 数据库会话
    
    Returns:
        包含生成状态和消息的响应
    """
    try:
        generate_all_test_data(db, clear_existing=clear_existing)
        return {
            "success": True,
            "message": "测试数据生成成功",
            "details": "已生成物业项目、房产、业主、家庭成员、车辆等测试数据"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"测试数据生成失败: {str(e)}"
        }
