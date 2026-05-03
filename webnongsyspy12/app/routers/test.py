"""
测试数据生成器
用于生成演示数据和测试系统功能
"""
import random
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ApiResponse
from app.crud import DeviceCRUD, EnvironmentDataCRUD, CropCRUD, GrowthRecordCRUD
from app.schemas import (
    DeviceCreate, EnvironmentDataCreate,
    CropCreate, GrowthRecordCreate
)

router = APIRouter(prefix="/test", tags=["测试功能"])


class TestDataConfig(BaseModel):
    """测试数据生成配置"""
    device_count: int = Field(3, ge=1, le=10, description="设备数量")
    crop_count: int = Field(5, ge=1, le=20, description="作物数量")
    env_data_count: int = Field(50, ge=10, le=500, description="每设备环境数据数量")
    growth_count: int = Field(10, ge=5, le=50, description="生长记录数量")


# 设备名称和类型配置
DEVICE_CONFIGS = [
    {"name": "温湿度监测站-001", "type": "综合监测站", "location": "A区1号大棚"},
    {"name": "温湿度监测站-002", "type": "综合监测站", "location": "A区2号大棚"},
    {"name": "光照传感器-001", "type": "光照传感器", "location": "B区1号大棚"},
    {"name": "土壤水分监测站-001", "type": "土壤传感器", "location": "A区3号大棚"},
    {"name": "CO2传感器-001", "type": "CO2传感器", "location": "B区2号大棚"},
    {"name": "综合监测站-001", "type": "综合监测站", "location": "C区1号大棚"},
]

# 作物配置
CROP_CONFIGS = [
    {"name": "番茄", "type": "蔬菜", "variety": "樱桃番茄", "location": "A区1号大棚"},
    {"name": "黄瓜", "type": "蔬菜", "variety": "荷兰黄瓜", "location": "A区2号大棚"},
    {"name": "草莓", "type": "水果", "variety": "红颜草莓", "location": "B区1号大棚"},
    {"name": "辣椒", "type": "蔬菜", "variety": "朝天椒", "location": "A区3号大棚"},
    {"name": "番茄", "type": "蔬菜", "variety": "大番茄", "location": "B区2号大棚"},
    {"name": "生菜", "type": "蔬菜", "variety": "罗马生菜", "location": "C区1号大棚"},
    {"name": "玫瑰", "type": "花卉", "variety": "红玫瑰", "location": "C区2号大棚"},
    {"name": "菊花", "type": "花卉", "variety": "白菊", "location": "C区3号大棚"},
]

# 生育期
GROWTH_STAGES = ["出苗期", "幼苗期", "开花期", "结果期", "成熟期"]

# AI诊断模拟
DISEASES = [None, None, None, "白粉病", "叶斑病", "霜霉病"]
NUTRITIONS = ["营养充足", "营养充足", "氮肥稍缺", "磷肥稍缺"]


def generate_device_code(prefix: str = "DEV", index: int = 1) -> str:
    """生成设备编号"""
    return f"{prefix}{datetime.now().strftime('%m%d')}{index:03d}"


def generate_environment_data(
    device_id: int,
    count: int,
    start_time: Optional[datetime] = None
) -> List[EnvironmentDataCreate]:
    """
    生成模拟环境数据
    
    Args:
        device_id: 设备ID
        count: 数据数量
        start_time: 开始时间，默认24小时前
    
    Returns:
        环境数据列表
    """
    if not start_time:
        start_time = datetime.now() - timedelta(hours=24)
    
    data_list = []
    interval = timedelta(hours=24 / count) if count > 0 else timedelta(hours=1)
    
    for i in range(count):
        # 生成模拟数据，包含合理的波动
        base_temp = 25 + random.uniform(-5, 5)  # 基础温度25℃ ±5℃
        base_humidity = 65 + random.uniform(-20, 20)  # 基础湿度65% ±20%
        base_light = 30000 + random.uniform(-20000, 50000)  # 光照强度
        base_soil = 55 + random.uniform(-15, 15)  # 土壤水分
        base_co2 = 800 + random.uniform(-200, 400)  # CO2浓度
        
        # 记录时间
        recorded_at = start_time + interval * i
        
        data = EnvironmentDataCreate(
            device_id=device_id,
            temperature=round(base_temp + random.uniform(-2, 2), 1),
            humidity=round(max(0, min(100, base_humidity + random.uniform(-5, 5))), 1),
            light_intensity=round(max(0, base_light + random.uniform(-5000, 5000)), 0),
            soil_moisture=round(max(0, min(100, base_soil + random.uniform(-3, 3))), 1),
            co2_concentration=round(max(0, base_co2 + random.uniform(-100, 100)), 0)
        )
        data_list.append(data)
    
    return data_list


@router.post("/generate-data", response_model=ApiResponse)
def generate_test_data(
    config: TestDataConfig,
    db: Session = Depends(get_db)
):
    """
    生成测试数据接口
    
    Args:
        config: 生成配置
        db: 数据库会话
    
    Returns:
        生成结果统计
    """
    created_devices = 0
    created_crops = 0
    created_env_data = 0
    created_growth_records = 0
    
    # 生成设备
    device_ids = []
    for i in range(min(config.device_count, len(DEVICE_CONFIGS))):
        cfg = DEVICE_CONFIGS[i]
        device_in = DeviceCreate(
            device_code=generate_device_code(index=i+1),
            device_name=cfg["name"],
            device_type=cfg["type"],
            location=cfg["location"],
            status="online"
        )
        device = DeviceCRUD.create(db, device_in)
        device_ids.append(device.id)
        created_devices += 1
    
    # 如果设备数量超过预设配置，添加额外设备
    for i in range(len(DEVICE_CONFIGS), config.device_count):
        device_in = DeviceCreate(
            device_code=generate_device_code(index=i+1),
            device_name=f"监测设备-{i+1:03d}",
            device_type="综合监测站",
            location=f"D区{i%3 + 1}号大棚",
            status="online"
        )
        device = DeviceCRUD.create(db, device_in)
        device_ids.append(device.id)
        created_devices += 1
    
    # 生成环境数据
    for device_id in device_ids:
        env_data_list = generate_environment_data(device_id, config.env_data_count)
        for env_data in env_data_list:
            EnvironmentDataCRUD.create(db, env_data)
            created_env_data += 1
    
    # 生成作物
    crop_ids = []
    for i in range(min(config.crop_count, len(CROP_CONFIGS))):
        cfg = CROP_CONFIGS[i]
        crop_in = CropCreate(
            crop_name=cfg["name"],
            crop_type=cfg["type"],
            variety=cfg["variety"],
            planting_date=datetime.now() - timedelta(days=random.randint(30, 90)),
            expected_harvest_date=datetime.now() + timedelta(days=random.randint(30, 60)),
            location=cfg["location"],
            status="growing"
        )
        crop = CropCRUD.create(db, crop_in)
        crop_ids.append(crop.id)
        created_crops += 1
    
    # 如果作物数量超过预设配置，添加额外作物
    for i in range(len(CROP_CONFIGS), config.crop_count):
        crop_in = CropCreate(
            crop_name=f"作物-{i+1:03d}",
            crop_type="蔬菜",
            variety=f"品种-{i+1}",
            planting_date=datetime.now() - timedelta(days=random.randint(30, 90)),
            expected_harvest_date=datetime.now() + timedelta(days=random.randint(30, 60)),
            location=f"E区{i%3 + 1}号大棚",
            status="growing"
        )
        crop = CropCRUD.create(db, crop_in)
        crop_ids.append(crop.id)
        created_crops += 1
    
    # 生成生长记录
    record_types = ["image", "image", "text", "video"]
    for i in range(config.growth_count):
        if not crop_ids:
            break
            
        crop_id = random.choice(crop_ids)
        record_type = random.choice(record_types)
        growth_stage = random.choice(GROWTH_STAGES)
        
        # 模拟AI诊断
        disease = random.choice(DISEASES)
        nutrition = random.choice(NUTRITIONS)
        
        if disease:
            ai_diagnosis = f"AI图像识别检测到作物叶片存在{disease}症状，建议及时采取防治措施。营养状况评估：{nutrition}。"
        else:
            ai_diagnosis = f"AI图像识别未检测到明显病害症状，作物生长状态良好。营养状况评估：{nutrition}。"
        
        record_in = GrowthRecordCreate(
            crop_id=crop_id,
            record_type=record_type,
            title=f"{growth_stage}观察记录",
            description=f"作物在{growth_stage}的生长情况记录。植株长势{'良好' if not disease else '一般'}，需{'继续观察' if not disease else '加强管理'}。",
            growth_stage=growth_stage,
            recorded_at=datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        )
        
        record = GrowthRecordCRUD.create(db, record_in)
        
        # 添加AI诊断信息（如果是图片类型）
        if record_type == "image":
            GrowthRecordCRUD.update_ai_diagnosis(
                db, record,
                ai_diagnosis=ai_diagnosis,
                disease_detected=disease,
                nutrition_status=nutrition,
                confidence=round(random.uniform(0.75, 0.98), 2)
            )
        
        created_growth_records += 1
    
    return ApiResponse(
        success=True,
        message="测试数据生成成功",
        data={
            "devices": created_devices,
            "crops": created_crops,
            "environment_data": created_env_data,
            "growth_records": created_growth_records
        }
    )


@router.post("/clear-all", response_model=ApiResponse)
def clear_all_data(db: Session = Depends(get_db)):
    """
    清空所有测试数据接口
    
    Args:
        db: 数据库会话
    
    Returns:
        操作结果
    """
    from app.models import Device, EnvironmentData, Crop, GrowthRecord
    
    # 按依赖顺序删除
    db.query(GrowthRecord).delete()
    db.query(EnvironmentData).delete()
    db.query(Crop).delete()
    db.query(Device).delete()
    db.commit()
    
    return ApiResponse(
        success=True,
        message="所有数据已清空",
        data=None
    )
