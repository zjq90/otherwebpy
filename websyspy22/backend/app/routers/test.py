"""
测试功能API路由
提供测试数据生成和API测试功能
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import ApiResponse, SuccessResponse
from app.test_utils.test_data_generator import test_data_generator
from app.test_utils.test_helper import test_helper

router = APIRouter(
    prefix="/api/test",
    tags=["测试功能"],
    responses={404: {"description": "未找到"}},
)


@router.post(
    "/data/generate",
    response_model=ApiResponse[dict],
    summary="生成测试数据",
    description="批量生成测试用的会员数据及其关联档案数据",
)
def generate_test_data(
    member_count: int = Query(10, ge=1, le=100, description="生成会员数量"),
    tests_per_member: int = Query(3, ge=0, le=20, description="每会员体测数据数量"),
    goals_per_member: int = Query(2, ge=0, le=10, description="每会员运动目标数量"),
    consumptions_per_member: int = Query(5, ge=0, le=20, description="每会员消费记录数量"),
    courses_per_member: int = Query(8, ge=0, le=30, description="每会员课程参与数量"),
    db: Session = Depends(get_db),
):
    """
    生成测试数据
    - **member_count**: 生成会员数量（1-100）
    - **tests_per_member**: 每会员体测数据数量
    - **goals_per_member**: 每会员运动目标数量
    - **consumptions_per_member**: 每会员消费记录数量
    - **courses_per_member**: 每会员课程参与数量
    """
    result = test_data_generator.generate_complete_member_data(
        db=db,
        member_count=member_count,
        tests_per_member=tests_per_member,
        goals_per_member=goals_per_member,
        consumptions_per_member=consumptions_per_member,
        courses_per_member=courses_per_member
    )
    
    return ApiResponse(
        code=200,
        message="测试数据生成成功",
        data={
            "generated_counts": {
                "members": len(result["members"]),
                "physical_tests": len(result["physical_tests"]),
                "fitness_goals": len(result["fitness_goals"]),
                "consumption_records": len(result["consumption_records"]),
                "course_participations": len(result["course_participations"])
            }
        }
    )


@router.post(
    "/data/generate-member",
    response_model=ApiResponse[dict],
    summary="生成单个测试会员",
    description="生成一个测试会员及其基本信息",
)
def generate_single_member(
    db: Session = Depends(get_db),
):
    """
    生成单个测试会员
    """
    member = test_data_generator.generate_member(db)
    
    return ApiResponse(
        code=200,
        message="测试会员生成成功",
        data={
            "member_id": member.id,
            "name": member.name,
            "phone": member.phone,
            "current_level": member.current_level,
            "status": member.status.value
        }
    )


@router.get(
    "/data/info",
    response_model=ApiResponse[dict],
    summary="获取测试数据生成器信息",
    description="获取测试数据生成器的配置信息和预设数据",
)
def get_generator_info():
    """
    获取测试数据生成器信息
    """
    return ApiResponse(
        code=200,
        message="获取成功",
        data={
            "preset_names": test_data_generator.CHINESE_NAMES,
            "preset_health_statuses": test_data_generator.HEALTH_STATUSES,
            "preset_courses": test_data_generator.COURSES,
            "preset_coaches": test_data_generator.COACHES,
            "consumption_types": test_data_generator.CONSUMPTION_TYPES,
            "goal_types": test_data_generator.GOAL_TYPES
        }
    )


@router.post(
    "/run/crud",
    response_model=ApiResponse[dict],
    summary="运行会员CRUD测试",
    description="测试会员的创建、读取、更新、删除操作",
)
def run_crud_test(db: Session = Depends(get_db)):
    """
    运行会员CRUD测试
    """
    # 注意：这里需要实际的TestClient
    # 简化版：直接通过数据库操作模拟测试
    results = {
        "create": None,
        "read": None,
        "update": None,
        "delete": None
    }
    
    try:
        # 1. 创建
        member = test_data_generator.generate_member(db)
        results["create"] = {
            "success": True,
            "member_id": member.id,
            "name": member.name
        }
        
        # 2. 读取
        from app.models.member import Member
        read_member = db.query(Member).filter(Member.id == member.id).first()
        results["read"] = {
            "success": read_member is not None
        }
        
        # 3. 更新
        original_name = read_member.name
        read_member.name = "已更新_" + original_name
        db.commit()
        db.refresh(read_member)
        results["update"] = {
            "success": "已更新_" in read_member.name
        }
        
        # 4. 删除（逻辑删除）
        from app.models.member import MemberStatus
        read_member.status = MemberStatus.CANCELLED
        db.commit()
        db.refresh(read_member)
        results["delete"] = {
            "success": read_member.status == MemberStatus.CANCELLED
        }
        
        all_success = all(
            r.get("success", False) if isinstance(r, dict) else False
            for r in results.values()
        )
        
        return ApiResponse(
            code=200,
            message="CRUD测试完成" if all_success else "CRUD测试部分失败",
            data={
                "all_success": all_success,
                "results": results
            }
        )
        
    except Exception as e:
        return ApiResponse(
            code=500,
            message=f"测试执行异常: {str(e)}",
            data={"error": str(e)}
        )


@router.get(
    "/health",
    response_model=ApiResponse[dict],
    summary="健康检查",
    description="检查API服务和数据库连接状态",
)
def health_check(db: Session = Depends(get_db)):
    """
    健康检查
    """
    try:
        # 测试数据库连接
        from app.models.member import Member
        db.query(Member).limit(1).all()
        
        return ApiResponse(
            code=200,
            message="服务健康",
            data={
                "status": "healthy",
                "database": "connected",
                "timestamp": __import__("datetime").datetime.now().isoformat()
            }
        )
    except Exception as e:
        return ApiResponse(
            code=503,
            message="服务异常",
            data={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )


@router.get(
    "/summary",
    response_model=ApiResponse[dict],
    summary="获取测试功能摘要",
    description="获取所有可用的测试功能列表和说明",
)
def get_test_summary():
    """
    获取测试功能摘要
    """
    return ApiResponse(
        code=200,
        message="获取成功",
        data={
            "available_features": [
                {
                    "name": "批量测试数据生成",
                    "endpoint": "POST /api/test/data/generate",
                    "description": "生成批量测试数据，可指定会员数量和各类档案数据数量"
                },
                {
                    "name": "单个测试会员生成",
                    "endpoint": "POST /api/test/data/generate-member",
                    "description": "快速生成一个测试会员"
                },
                {
                    "name": "生成器信息",
                    "endpoint": "GET /api/test/data/info",
                    "description": "查看预设的测试数据选项（姓名、课程、教练等）"
                },
                {
                    "name": "CRUD测试",
                    "endpoint": "POST /api/test/run/crud",
                    "description": "运行会员CRUD操作测试"
                },
                {
                    "name": "健康检查",
                    "endpoint": "GET /api/test/health",
                    "description": "检查API服务和数据库连接状态"
                }
            ],
            "recommended_workflow": [
                "1. 先调用 /api/test/health 确认服务正常",
                "2. 调用 /api/test/data/generate 生成测试数据",
                "3. 使用 Swagger UI (/docs) 测试各API接口",
                "4. 开发前端时可使用生成的测试数据进行联调"
            ]
        }
    )
