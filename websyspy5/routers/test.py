"""
测试数据生成API路由
用于生成测试数据，方便系统功能测试
"""
import random
from datetime import datetime, date, timedelta, time
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.staff import Staff
from models.device import Device
from models.access_record import AccessRecord

router = APIRouter(prefix="/api/test", tags=["测试数据生成"])

# 测试数据配置
TEST_STAFF_NAMES = [
    ("张三", "男"), ("李四", "男"), ("王五", "男"), ("赵六", "男"), ("钱七", "女"),
    ("孙八", "女"), ("周九", "男"), ("吴十", "女"), ("郑一", "男"), ("王二", "女")
]

TEST_DEPARTMENTS = ["技术部", "市场部", "人事部", "财务部", "运营部"]
TEST_POSITIONS = ["工程师", "经理", "主管", "专员", "总监"]

TEST_DEVICES = [
    ("DEV001", "大门入口人脸识别机", "人脸识别终端V1.0", "公司大门入口", "192.168.1.101"),
    ("DEV002", "办公区A门人脸识别机", "人脸识别终端V1.0", "办公区A门", "192.168.1.102"),
    ("DEV003", "停车场出口人脸识别机", "人脸识别终端V1.0", "地下停车场出口", "192.168.1.103")
]


@router.post("/generate-staff")
def generate_test_staff(db: Session = Depends(get_db)):
    """
    生成测试工作人员数据
    生成10个测试工作人员
    """
    # 检查是否已有测试数据
    existing_count = db.query(Staff).count()
    if existing_count > 0:
        return {
            "code": 200,
            "message": "已存在工作人员数据",
            "data": {"count": existing_count, "is_new": False}
        }
    
    generated_count = 0
    
    for i, (name, gender) in enumerate(TEST_STAFF_NAMES):
        staff_no = f"ST{1001 + i:04d}"
        department = random.choice(TEST_DEPARTMENTS)
        position = random.choice(TEST_POSITIONS)
        
        staff = Staff(
            staff_no=staff_no,
            name=name,
            gender=gender,
            department=department,
            position=position,
            phone=f"138{random.randint(1000, 9999)}{random.randint(1000, 9999)}",
            email=f"{name.lower()}@company.com",
            id_card=f"110101{1980 + random.randint(0, 30)}{random.randint(1, 12):02d}{random.randint(1, 28):02d}{random.randint(1000, 9999)}",
            status=1,
            remark=f"测试数据 - {department}员工"
        )
        
        db.add(staff)
        generated_count += 1
    
    db.commit()
    
    return {
        "code": 200,
        "message": "测试工作人员数据生成成功",
        "data": {"count": generated_count, "is_new": True}
    }


@router.post("/generate-devices")
def generate_test_devices(db: Session = Depends(get_db)):
    """
    生成测试设备数据
    生成3个测试门禁设备
    """
    # 检查是否已有测试数据
    existing_count = db.query(Device).count()
    if existing_count > 0:
        return {
            "code": 200,
            "message": "已存在设备数据",
            "data": {"count": existing_count, "is_new": False}
        }
    
    generated_count = 0
    
    for device_no, device_name, device_model, location, ip_address in TEST_DEVICES:
        device = Device(
            device_no=device_no,
            device_name=device_name,
            device_model=device_model,
            location=location,
            ip_address=ip_address,
            mac_address=f"{random.randint(0, 255):02x}:{random.randint(0, 255):02x}:{random.randint(0, 255):02x}:{random.randint(0, 255):02x}:{random.randint(0, 255):02x}:{random.randint(0, 255):02x}",
            status=1,
            last_online_time=datetime.now(),
            remark=f"测试数据 - {location}门禁设备"
        )
        
        db.add(device)
        generated_count += 1
    
    db.commit()
    
    return {
        "code": 200,
        "message": "测试设备数据生成成功",
        "data": {"count": generated_count, "is_new": True}
    }


@router.post("/generate-access-records")
def generate_test_access_records(
    start_date: str = Query(..., description="开始日期，格式：YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期，格式：YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    生成测试出入记录数据
    根据日期范围生成模拟的出入记录
    """
    # 解析日期
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，请使用YYYY-MM-DD格式")
    
    if start_dt > end_dt:
        raise HTTPException(status_code=400, detail="开始日期不能晚于结束日期")
    
    # 获取所有在职员工和在线设备
    staff_list = db.query(Staff).filter(Staff.status == 1).all()
    device_list = db.query(Device).filter(Device.status == 1).all()
    
    if not staff_list:
        raise HTTPException(status_code=400, detail="没有可用的工作人员数据，请先生成工作人员测试数据")
    
    if not device_list:
        raise HTTPException(status_code=400, detail="没有可用的设备数据，请先生成设备测试数据")
    
    generated_count = 0
    
    # 遍历每个日期
    current_date = start_dt
    while current_date <= end_dt:
        # 跳过周末（周一到周五为工作日，1=周一，5=周五，6=周六，7=周日）
        weekday = current_date.isoweekday()
        if weekday in [6, 7]:
            current_date += timedelta(days=1)
            continue
        
        # 为每个员工生成出入记录
        for staff in staff_list:
            # 随机决定是否缺勤（10%概率缺勤）
            if random.random() < 0.1:
                continue
            
            # 随机选择设备
            enter_device = random.choice(device_list)
            exit_device = random.choice(device_list)
            
            # 生成上午上班时间（8:30-9:30之间）
            morning_in_hour = random.randint(8, 9)
            morning_in_minute = random.randint(30, 59) if morning_in_hour == 8 else random.randint(0, 30)
            morning_in_time = datetime.combine(current_date, time(morning_in_hour, morning_in_minute))
            
            # 生成上午下班时间（12:00-12:30之间）
            morning_out_hour = 12
            morning_out_minute = random.randint(0, 30)
            morning_out_time = datetime.combine(current_date, time(morning_out_hour, morning_out_minute))
            
            # 生成下午上班时间（13:30-14:30之间）
            afternoon_in_hour = random.randint(13, 14)
            afternoon_in_minute = random.randint(30, 59) if afternoon_in_hour == 13 else random.randint(0, 30)
            afternoon_in_time = datetime.combine(current_date, time(afternoon_in_hour, afternoon_in_minute))
            
            # 生成下午下班时间（17:30-19:00之间）
            afternoon_out_hour = random.randint(17, 19)
            afternoon_out_minute = random.randint(30, 59) if afternoon_out_hour == 17 else random.randint(0, 59) if afternoon_out_hour == 18 else 0
            afternoon_out_time = datetime.combine(current_date, time(afternoon_out_hour, afternoon_out_minute))
            
            # 创建上午进入记录
            enter_record1 = AccessRecord(
                staff_id=staff.id,
                device_id=enter_device.id,
                access_type=1,
                access_time=morning_in_time,
                similarity=round(random.uniform(0.85, 0.99), 2),
                verify_result=1,
                remark="模拟测试数据 - 上午上班"
            )
            db.add(enter_record1)
            generated_count += 1
            
            # 创建上午离开记录
            exit_record1 = AccessRecord(
                staff_id=staff.id,
                device_id=exit_device.id,
                access_type=0,
                access_time=morning_out_time,
                similarity=round(random.uniform(0.85, 0.99), 2),
                verify_result=1,
                remark="模拟测试数据 - 上午下班"
            )
            db.add(exit_record1)
            generated_count += 1
            
            # 创建下午进入记录（80%概率有下午记录）
            if random.random() < 0.8:
                enter_record2 = AccessRecord(
                    staff_id=staff.id,
                    device_id=enter_device.id,
                    access_type=1,
                    access_time=afternoon_in_time,
                    similarity=round(random.uniform(0.85, 0.99), 2),
                    verify_result=1,
                    remark="模拟测试数据 - 下午上班"
                )
                db.add(enter_record2)
                generated_count += 1
                
                # 创建下午离开记录
                exit_record2 = AccessRecord(
                    staff_id=staff.id,
                    device_id=exit_device.id,
                    access_type=0,
                    access_time=afternoon_out_time,
                    similarity=round(random.uniform(0.85, 0.99), 2),
                    verify_result=1,
                    remark="模拟测试数据 - 下午下班"
                )
                db.add(exit_record2)
                generated_count += 1
        
        current_date += timedelta(days=1)
    
    db.commit()
    
    return {
        "code": 200,
        "message": "测试出入记录生成成功",
        "data": {"count": generated_count}
    }
