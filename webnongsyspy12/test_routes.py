"""测试生长记录路由的导入和基本功能"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("开始测试...")
print("=" * 50)

try:
    print("\n1. 测试导入 config...")
    from app.config import settings
    print(f"   ✓ 导入成功")
    print(f"   - 数据库URL: {settings.DATABASE_URL}")
    print(f"   - 上传目录: {settings.UPLOAD_DIR}")
except Exception as e:
    print(f"   ✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n2. 测试导入 database...")
    from app.database import init_db, get_db, SessionLocal, engine
    print(f"   ✓ 导入成功")
except Exception as e:
    print(f"   ✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n3. 测试导入 models...")
    from app.models import Device, EnvironmentData, Crop, GrowthRecord
    print(f"   ✓ 导入成功")
    print(f"   - Device 表: {Device.__tablename__}")
    print(f"   - GrowthRecord 表: {GrowthRecord.__tablename__}")
except Exception as e:
    print(f"   ✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n4. 测试导入 schemas...")
    from app.schemas import (
        GrowthRecordCreate, GrowthRecordUpdate, GrowthRecordResponse,
        ApiResponse, ApiListResponse
    )
    print(f"   ✓ 导入成功")
    
    # 测试创建 GrowthRecordCreate 实例
    from datetime import datetime
    record = GrowthRecordCreate(
        crop_id=1,
        record_type="image",
        title="测试记录"
    )
    print(f"   - GrowthRecordCreate 测试: OK")
    print(f"   - recorded_at 默认值: {record.recorded_at}")
except Exception as e:
    print(f"   ✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n5. 测试导入 crud...")
    from app.crud import GrowthRecordCRUD, CropCRUD
    print(f"   ✓ 导入成功")
except Exception as e:
    print(f"   ✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n6. 测试导入 growth_record 路由...")
    from app.routers.growth_record import (
        router,
        save_upload_file,
        simulate_ai_diagnosis,
        create_growth_record
    )
    print(f"   ✓ 导入成功")
    print(f"   - 路由前缀: {router.prefix}")
    
    # 测试 simulate_ai_diagnosis
    print("\n7. 测试 AI 诊断模拟...")
    diagnosis = simulate_ai_diagnosis()
    print(f"   ✓ 诊断成功")
    print(f"   - 诊断结果: {diagnosis['ai_diagnosis'][:50]}...")
    print(f"   - 置信度: {diagnosis['diagnosis_confidence']}")
    
except Exception as e:
    print(f"   ✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n8. 测试导入所有路由...")
    from app.routers import (
        device_router,
        environment_router,
        crop_router,
        growth_record_router,
        test_router
    )
    print(f"   ✓ 导入成功")
    print(f"   - 设备路由: {device_router.prefix}")
    print(f"   - 环境数据路由: {environment_router.prefix}")
    print(f"   - 作物路由: {crop_router.prefix}")
    print(f"   - 生长记录路由: {growth_record_router.prefix}")
    print(f"   - 测试路由: {test_router.prefix}")
except Exception as e:
    print(f"   ✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n9. 测试 main.py 导入...")
    from main import app
    print(f"   ✓ 导入成功")
    print(f"   - 应用标题: {app.title}")
    print(f"   - 路由数量: {len(app.routes)}")
except Exception as e:
    print(f"   ✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("测试完成!")
print("=" * 50)
