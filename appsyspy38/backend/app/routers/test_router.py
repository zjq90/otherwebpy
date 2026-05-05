"""
测试功能路由
用于提供测试辅助功能和测试数据接口
注意：生产环境应禁用此路由
"""

from datetime import datetime, timedelta, date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models.user_models import User, Role
from ..models.business_models import (
    ProductionTask, ProductionRecord,
    MaterialInspection, QualityReport, QualityAlert,
    MaterialInventory, PurchaseRequest, Supplier,
    Vehicle, TransportTask
)
from ..schemas.user_schemas import ApiResponse
from ..utils.security import get_password_hash, require_role

router = APIRouter(prefix="/test", tags=["测试功能"])


@router.post("/init-data", response_model=ApiResponse)
async def init_test_data(
    db: AsyncSession = Depends(get_db)
):
    """
    初始化测试数据
    注意：此接口仅用于开发测试，生产环境应禁用
    """
    from ..init_data import (
        init_roles_and_permissions, init_admin_user,
        init_test_users, init_test_business_data
    )
    
    await init_roles_and_permissions(db)
    await init_admin_user(db)
    await init_test_users(db)
    await init_test_business_data(db)
    
    return ApiResponse(message="测试数据初始化完成")


@router.get("/test-accounts", response_model=ApiResponse)
async def get_test_accounts():
    """
    获取测试账号列表
    用于测试登录功能
    """
    test_accounts = [
        {
            "role": "管理员",
            "username": "admin",
            "password": "admin123",
            "phone": "13800138000",
            "description": "拥有全部权限"
        },
        {
            "role": "拌合站操作员",
            "username": "operator1",
            "password": "123456",
            "phone": "13900000001",
            "description": "查看生产任务、提交生产记录"
        },
        {
            "role": "试验检测员",
            "username": "inspector1",
            "password": "123456",
            "phone": "13900000002",
            "description": "录入检验数据、查看质量报告、发起质量预警"
        },
        {
            "role": "物资采购员",
            "username": "purchaser1",
            "password": "123456",
            "phone": "13900000003",
            "description": "查看库存、提交采购申请、管理供应商"
        },
        {
            "role": "资源调度员",
            "username": "scheduler1",
            "password": "123456",
            "phone": "13900000004",
            "description": "查看车辆位置、安排运输任务、更新进度"
        }
    ]
    
    return ApiResponse(
        message="测试账号列表",
        data={"accounts": test_accounts}
    )


@router.get("/db-stats", response_model=ApiResponse)
async def get_database_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    获取数据库统计信息
    用于了解当前数据量
    """
    stats = {}
    
    # 用户统计
    result = await db.execute(select(User))
    stats["users_count"] = len(result.scalars().all())
    
    # 角色统计
    result = await db.execute(select(Role))
    stats["roles_count"] = len(result.scalars().all())
    
    # 生产任务统计
    result = await db.execute(select(ProductionTask))
    stats["production_tasks_count"] = len(result.scalars().all())
    
    # 生产记录统计
    result = await db.execute(select(ProductionRecord))
    stats["production_records_count"] = len(result.scalars().all())
    
    # 原材料检验统计
    result = await db.execute(select(MaterialInspection))
    stats["material_inspections_count"] = len(result.scalars().all())
    
    # 质量报告统计
    result = await db.execute(select(QualityReport))
    stats["quality_reports_count"] = len(result.scalars().all())
    
    # 质量预警统计
    result = await db.execute(select(QualityAlert))
    stats["quality_alerts_count"] = len(result.scalars().all())
    
    # 库存统计
    result = await db.execute(select(MaterialInventory))
    stats["material_inventories_count"] = len(result.scalars().all())
    
    # 采购申请统计
    result = await db.execute(select(PurchaseRequest))
    stats["purchase_requests_count"] = len(result.scalars().all())
    
    # 供应商统计
    result = await db.execute(select(Supplier))
    stats["suppliers_count"] = len(result.scalars().all())
    
    # 车辆统计
    result = await db.execute(select(Vehicle))
    stats["vehicles_count"] = len(result.scalars().all())
    
    # 运输任务统计
    result = await db.execute(select(TransportTask))
    stats["transport_tasks_count"] = len(result.scalars().all())
    
    return ApiResponse(
        message="数据库统计信息",
        data=stats
    )


@router.post("/generate-sample-data", response_model=ApiResponse)
async def generate_sample_data(
    db: AsyncSession = Depends(get_db)
):
    """
    生成示例业务数据
    用于测试各业务功能
    """
    # 查询测试用户
    result = await db.execute(select(User))
    users = {u.username: u for u in result.scalars().all()}
    
    # 查询角色
    result = await db.execute(select(Role))
    roles = {r.code: r for r in result.scalars().all()}
    
    # 查询车辆
    result = await db.execute(select(Vehicle))
    vehicles = result.scalars().all()
    
    # 创建生产任务示例
    if "operator1" in users:
        production_tasks = [
            ProductionTask(
                task_no=f"PT{int(datetime.now().timestamp())}001",
                project_name="幸福小区三期工程",
                concrete_type="C30",
                volume=500,
                delivery_location="幸福小区工地",
                required_time=datetime.now() + timedelta(days=1),
                operator_id=users["operator1"].id,
                status="pending"
            ),
            ProductionTask(
                task_no=f"PT{int(datetime.now().timestamp())}002",
                project_name="科技园区办公楼",
                concrete_type="C40",
                volume=300,
                delivery_location="科技园区",
                required_time=datetime.now() + timedelta(days=2),
                operator_id=users["operator1"].id,
                status="executing"
            )
        ]
        for task in production_tasks:
            db.add(task)
    
    # 创建原材料检验示例
    if "inspector1" in users:
        inspections = [
            MaterialInspection(
                inspection_no=f"MI{int(datetime.now().timestamp())}001",
                material_type="水泥",
                material_name="PO42.5水泥",
                batch_no="B20260501001",
                supplier="海螺水泥",
                quantity=200,
                inspector_id=users["inspector1"].id,
                inspection_date=date.today(),
                inspection_result="qualified"
            )
        ]
        for inspection in inspections:
            db.add(inspection)
    
    # 创建质量报告示例
    if "inspector1" in users:
        reports = [
            QualityReport(
                report_no=f"QR{int(datetime.now().timestamp())}001",
                project_name="幸福小区三期工程",
                concrete_type="C30",
                batch_no="B20260501001",
                production_date=date.today(),
                strength_grade="C30",
                test_age=28,
                compressive_strength=35.5,
                inspector_id=users["inspector1"].id,
                report_date=date.today(),
                conclusion="qualified"
            )
        ]
        for report in reports:
            db.add(report)
    
    # 创建采购申请示例
    if "purchaser1" in users:
        purchase_requests = [
            PurchaseRequest(
                request_no=f"PR{int(datetime.now().timestamp())}001",
                applicant_id=users["purchaser1"].id,
                material_name="PO42.5水泥",
                specification="PO42.5",
                quantity=500,
                unit="吨",
                expected_price=450,
                supplier="海螺水泥",
                reason="库存不足，需要补充",
                urgency="normal",
                status="pending"
            )
        ]
        for pr in purchase_requests:
            db.add(pr)
    
    # 创建运输任务示例
    if "scheduler1" in users and vehicles:
        vehicle = vehicles[0] if vehicles else None
        if vehicle:
            transport_tasks = [
                TransportTask(
                    task_no=f"TT{int(datetime.now().timestamp())}001",
                    project_name="幸福小区三期工程",
                    delivery_location="幸福小区工地",
                    concrete_type="C30",
                    volume=100,
                    vehicle_id=vehicle.id,
                    scheduler_id=users["scheduler1"].id,
                    scheduled_time=datetime.now() + timedelta(hours=2),
                    status="pending",
                    progress=0
                )
            ]
            for tt in transport_tasks:
                db.add(tt)
    
    await db.commit()
    
    return ApiResponse(message="示例业务数据生成完成")


@router.get("/api-docs-info", response_model=ApiResponse)
async def get_api_docs_info():
    """
    获取API文档信息
    用于前端开发参考
    """
    api_info = {
        "base_url": "http://localhost:8000",
        "api_prefix": "/api/v1",
        "docs_url": "/api/v1/docs",
        "redoc_url": "/api/v1/redoc",
        "openapi_url": "/api/v1/openapi.json",
        "endpoints": {
            "认证": [
                "POST /auth/send-code - 发送验证码",
                "POST /auth/login/password - 账号密码登录",
                "POST /auth/login/phone - 手机号验证码登录",
                "POST /auth/real-name-verify - 实名认证",
                "GET /auth/me - 获取当前用户信息",
                "GET /auth/permissions - 获取当前用户权限",
                "POST /auth/change-password - 修改密码",
                "POST /auth/logout - 退出登录"
            ],
            "用户管理（管理员）": [
                "GET /users - 获取用户列表",
                "POST /users - 创建用户",
                "GET /users/{id} - 获取用户详情",
                "PUT /users/{id} - 更新用户信息",
                "DELETE /users/{id} - 删除用户",
                "GET /users/roles - 获取角色列表",
                "POST /users/roles - 创建角色",
                "GET /users/permissions - 获取权限列表"
            ],
            "拌合站生产": [
                "GET /production/tasks - 获取生产任务列表",
                "POST /production/tasks - 创建生产任务（管理员）",
                "GET /production/tasks/{id} - 获取任务详情",
                "PUT /production/tasks/{id} - 更新任务状态",
                "POST /production/records - 提交生产记录",
                "GET /production/records - 获取生产记录列表",
                "POST /production/tasks/{id}/complete - 完成任务"
            ],
            "试验检测": [
                "POST /quality/inspections - 录入原材料检验数据",
                "GET /quality/inspections - 获取检验记录列表",
                "GET /quality/inspections/{id} - 获取检验详情",
                "POST /quality/reports - 创建质量报告",
                "GET /quality/reports - 获取质量报告列表",
                "GET /quality/reports/{id} - 获取报告详情",
                "POST /quality/alerts - 发起质量预警",
                "GET /quality/alerts - 获取预警列表",
                "PUT /quality/alerts/{id} - 处理预警"
            ],
            "物资采购": [
                "GET /material/inventory - 获取库存列表",
                "POST /material/inventory - 创建库存（管理员）",
                "PUT /material/inventory/{id} - 更新库存",
                "POST /material/purchase-requests - 提交采购申请",
                "GET /material/purchase-requests - 获取采购申请列表",
                "PUT /material/purchase-requests/{id}/approve - 审批申请（管理员）",
                "POST /material/suppliers - 创建供应商",
                "GET /material/suppliers - 获取供应商列表"
            ],
            "资源调度": [
                "GET /transport/vehicles - 获取车辆列表",
                "POST /transport/vehicles - 创建车辆（管理员）",
                "GET /transport/vehicles/available - 获取可用车辆",
                "PUT /transport/vehicles/{id} - 更新车辆信息",
                "PUT /transport/vehicles/{id}/location - 更新车辆位置",
                "POST /transport/tasks - 安排运输任务",
                "GET /transport/tasks - 获取运输任务列表",
                "PUT /transport/tasks/{id} - 更新运输进度"
            ],
            "测试功能": [
                "POST /test/init-data - 初始化测试数据",
                "GET /test/test-accounts - 获取测试账号",
                "GET /test/db-stats - 获取数据库统计",
                "POST /test/generate-sample-data - 生成示例数据"
            ]
        }
    }
    
    return ApiResponse(
        message="API文档信息",
        data=api_info
    )
