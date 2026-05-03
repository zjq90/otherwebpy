"""测试导入脚本"""
print("开始测试导入...")

try:
    from app.config import settings
    print("✓ config 导入成功")
    print(f"  数据库URL: {settings.DATABASE_URL}")
    print(f"  上传目录: {settings.UPLOAD_DIR}")
except Exception as e:
    print(f"✗ config 导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    from app.database import init_db, get_db
    print("✓ database 导入成功")
except Exception as e:
    print(f"✗ database 导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    from app.models import Device, EnvironmentData, Crop, GrowthRecord
    print("✓ models 导入成功")
    print(f"  设备表: {Device.__tablename__}")
    print(f"  环境数据表: {EnvironmentData.__tablename__}")
    print(f"  作物表: {Crop.__tablename__}")
    print(f"  生长记录表: {GrowthRecord.__tablename__}")
except Exception as e:
    print(f"✗ models 导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    from app.schemas import (
        DeviceCreate, DeviceResponse, 
        EnvironmentDataCreate, EnvironmentDataResponse,
        CropCreate, CropResponse,
        GrowthRecordCreate, GrowthRecordResponse,
        ApiResponse
    )
    print("✓ schemas 导入成功")
except Exception as e:
    print(f"✗ schemas 导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    from app.crud import DeviceCRUD, EnvironmentDataCRUD, CropCRUD, GrowthRecordCRUD
    print("✓ crud 导入成功")
except Exception as e:
    print(f"✗ crud 导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    from app.routers import (
        device_router,
        environment_router,
        crop_router,
        growth_record_router,
        test_router
    )
    print("✓ routers 导入成功")
except Exception as e:
    print(f"✗ routers 导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n导入测试完成!")
