import asyncio
from datetime import datetime, date, time, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models import (
    Base, SecurityPersonnel, SecuritySchedule, PatrolRoute, PatrolRecord,
    MonitorDevice, VehicleRecord, VisitorRecord, EmergencyReport,
    CleaningArea, CleaningRecord, GreenPlant, MaintenancePlan, MaintenanceRecord
)

DATABASE_URL = "sqlite+aiosqlite:///./property_management.db"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def generate_test_data():
    async with async_session_maker() as session:
        try:
            print("正在生成安保人员数据...")
            personnel_list = [
                SecurityPersonnel(name="张三", gender="男", phone="13800138001", id_card="110101199001011001", position="安保队长", status="在职"),
                SecurityPersonnel(name="李四", gender="男", phone="13800138002", id_card="110101199001011002", position="安保队员", status="在职"),
                SecurityPersonnel(name="王五", gender="男", phone="13800138003", id_card="110101199001011003", position="安保队员", status="在职"),
                SecurityPersonnel(name="赵六", gender="女", phone="13800138004", id_card="110101199001011004", position="门岗", status="在职"),
                SecurityPersonnel(name="钱七", gender="男", phone="13800138005", id_card="110101199001011005", position="巡逻队员", status="在职"),
            ]
            session.add_all(personnel_list)
            await session.commit()
            
            for p in personnel_list:
                await session.refresh(p)
            
            print("正在生成安保排班数据...")
            today = date.today()
            schedules = [
                SecuritySchedule(
                    personnel_id=personnel_list[0].id,
                    schedule_date=today,
                    shift_type="早班",
                    start_time=time(8, 0),
                    end_time=time(16, 0),
                    post="正门岗",
                    status="执行中"
                ),
                SecuritySchedule(
                    personnel_id=personnel_list[1].id,
                    schedule_date=today,
                    shift_type="中班",
                    start_time=time(12, 0),
                    end_time=time(20, 0),
                    post="巡逻岗",
                    status="待执行"
                ),
                SecuritySchedule(
                    personnel_id=personnel_list[2].id,
                    schedule_date=today,
                    shift_type="晚班",
                    start_time=time(20, 0),
                    end_time=time(4, 0),
                    post="监控室",
                    status="待执行"
                ),
                SecuritySchedule(
                    personnel_id=personnel_list[3].id,
                    schedule_date=today + timedelta(days=1),
                    shift_type="早班",
                    start_time=time(8, 0),
                    end_time=time(16, 0),
                    post="侧门岗",
                    status="待执行"
                ),
            ]
            session.add_all(schedules)
            await session.commit()
            
            print("正在生成巡逻路线数据...")
            routes = [
                PatrolRoute(
                    route_name="园区主干道巡逻路线",
                    route_code="PR001",
                    description="从正门开始，沿主干道绕行一周",
                    checkpoints='[{"name": "正门岗", "order": 1}, {"name": "办公楼", "order": 2}, {"name": "员工宿舍", "order": 3}, {"name": "食堂", "order": 4}]',
                    patrol_frequency="每2小时一次",
                    status="启用"
                ),
                PatrolRoute(
                    route_name="停车场巡逻路线",
                    route_code="PR002",
                    description="地下停车场巡逻路线",
                    checkpoints='[{"name": "A区入口", "order": 1}, {"name": "B区", "order": 2}, {"name": "C区", "order": 3}]',
                    patrol_frequency="每1小时一次",
                    status="启用"
                ),
            ]
            session.add_all(routes)
            await session.commit()
            
            for r in routes:
                await session.refresh(r)
            
            print("正在生成监控设备数据...")
            devices = [
                MonitorDevice(
                    device_name="正门监控1号",
                    device_code="CAM001",
                    location="园区正门入口",
                    ip_address="192.168.1.101",
                    device_type="球机",
                    status="正常",
                    installation_date=date(2023, 1, 15)
                ),
                MonitorDevice(
                    device_name="正门监控2号",
                    device_code="CAM002",
                    location="园区正门出口",
                    ip_address="192.168.1.102",
                    device_type="枪机",
                    status="正常",
                    installation_date=date(2023, 1, 15)
                ),
                MonitorDevice(
                    device_name="办公楼大厅监控",
                    device_code="CAM003",
                    location="办公楼一楼大厅",
                    ip_address="192.168.1.201",
                    device_type="球机",
                    status="正常",
                    installation_date=date(2023, 2, 20)
                ),
                MonitorDevice(
                    device_name="地下停车场A区",
                    device_code="CAM004",
                    location="地下停车场A区",
                    ip_address="192.168.1.301",
                    device_type="枪机",
                    status="离线",
                    installation_date=date(2023, 3, 10)
                ),
            ]
            session.add_all(devices)
            await session.commit()
            
            print("正在生成车辆出入记录数据...")
            vehicles = [
                VehicleRecord(
                    plate_number="京A12345",
                    vehicle_type="轿车",
                    owner_name="张经理",
                    owner_phone="13900139001",
                    entry_time=datetime.now() - timedelta(hours=2),
                    entry_gate="正门",
                    purpose="上班",
                    status="在场"
                ),
                VehicleRecord(
                    plate_number="京B67890",
                    vehicle_type="SUV",
                    owner_name="李总",
                    owner_phone="13900139002",
                    entry_time=datetime.now() - timedelta(days=1, hours=3),
                    exit_time=datetime.now() - timedelta(days=1),
                    entry_gate="正门",
                    exit_gate="正门",
                    purpose="会议",
                    status="已离开"
                ),
                VehicleRecord(
                    plate_number="京C54321",
                    vehicle_type="货车",
                    owner_name="王师傅",
                    owner_phone="13900139003",
                    entry_time=datetime.now() - timedelta(hours=1),
                    entry_gate="侧门",
                    purpose="送货",
                    status="在场"
                ),
            ]
            session.add_all(vehicles)
            await session.commit()
            
            print("正在生成外来人员记录数据...")
            visitors = [
                VisitorRecord(
                    visitor_name="陈先生",
                    visitor_phone="13700137001",
                    visitor_id_card="110102199002022001",
                    visit_unit="科技公司",
                    visited_person="张经理",
                    visit_purpose="商务洽谈",
                    entry_time=datetime.now() - timedelta(hours=1),
                    visitor_count=2,
                    credentials="身份证",
                    status="在场"
                ),
                VisitorRecord(
                    visitor_name="刘女士",
                    visitor_phone="13700137002",
                    visitor_id_card="110102199002022002",
                    visit_unit="物流公司",
                    visited_person="李总",
                    visit_purpose="面试",
                    entry_time=datetime.now() - timedelta(days=1, hours=4),
                    exit_time=datetime.now() - timedelta(days=1, hours=2),
                    visitor_count=1,
                    credentials="身份证",
                    status="已离开"
                ),
            ]
            session.add_all(visitors)
            await session.commit()
            
            print("正在生成突发事件上报数据...")
            emergencies = [
                EmergencyReport(
                    report_title="办公楼3楼发现火情隐患",
                    event_type="火灾",
                    location="办公楼3楼走廊",
                    reporter_name="李四",
                    reporter_phone="13800138002",
                    report_time=datetime.now() - timedelta(hours=3),
                    event_description="发现3楼走廊有烟雾，疑似电路短路导致",
                    handle_person="张三",
                    handle_time=datetime.now() - timedelta(hours=2),
                    handle_result="已切断电源，确认无明火，联系电工维修",
                    status="已处理",
                    priority="紧急"
                ),
                EmergencyReport(
                    report_title="停车场发现可疑人员",
                    event_type="盗窃",
                    location="地下停车场B区",
                    reporter_name="王五",
                    reporter_phone="13800138003",
                    report_time=datetime.now() - timedelta(hours=1),
                    event_description="发现一名可疑人员在停车场徘徊，形迹可疑",
                    status="处理中",
                    priority="重要"
                ),
            ]
            session.add_all(emergencies)
            await session.commit()
            
            print("正在生成保洁区域数据...")
            cleaning_areas = [
                CleaningArea(
                    area_name="办公楼区域",
                    area_code="CA001",
                    area_type="楼栋",
                    area_size=5000,
                    cleaning_frequency="每日清洁",
                    cleaning_standard="地面干净无杂物，门窗无灰尘",
                    responsible_person="陈阿姨",
                    responsible_phone="13600136001",
                    status="启用"
                ),
                CleaningArea(
                    area_name="园区主干道",
                    area_code="CA002",
                    area_type="道路",
                    area_size=3000,
                    cleaning_frequency="每日两次",
                    cleaning_standard="路面整洁，无垃圾",
                    responsible_person="王阿姨",
                    responsible_phone="13600136002",
                    status="启用"
                ),
                CleaningArea(
                    area_name="办公楼1楼",
                    area_code="CA003",
                    parent_id=1,
                    area_type="楼层",
                    area_size=1000,
                    cleaning_frequency="每日清洁",
                    cleaning_standard="大厅整洁，卫生间无异味",
                    responsible_person="陈阿姨",
                    responsible_phone="13600136001",
                    status="启用"
                ),
                CleaningArea(
                    area_name="员工宿舍区域",
                    area_code="CA004",
                    area_type="楼栋",
                    area_size=4000,
                    cleaning_frequency="每日清洁",
                    cleaning_standard="走廊整洁，公共区域无杂物",
                    responsible_person="李阿姨",
                    responsible_phone="13600136003",
                    status="启用"
                ),
            ]
            session.add_all(cleaning_areas)
            await session.commit()
            
            for ca in cleaning_areas:
                await session.refresh(ca)
            
            print("正在生成清洁记录数据...")
            cleaning_records = [
                CleaningRecord(
                    area_id=cleaning_areas[0].id,
                    cleaning_date=today,
                    cleaner_name="陈阿姨",
                    start_time=datetime.now() - timedelta(hours=4),
                    end_time=datetime.now() - timedelta(hours=2),
                    cleaning_items="地面清扫、门窗擦拭、卫生间清洁",
                    cleaning_quality="优秀",
                    remarks="清洁完成"
                ),
                CleaningRecord(
                    area_id=cleaning_areas[1].id,
                    cleaning_date=today,
                    cleaner_name="王阿姨",
                    start_time=datetime.now() - timedelta(hours=3),
                    end_time=datetime.now() - timedelta(hours=1),
                    cleaning_items="路面清扫、绿化带垃圾清理",
                    cleaning_quality="良好",
                    remarks="基本完成"
                ),
            ]
            session.add_all(cleaning_records)
            await session.commit()
            
            print("正在生成绿化植物数据...")
            plants = [
                GreenPlant(
                    plant_name="香樟树",
                    plant_code="GP001",
                    plant_type="乔木",
                    scientific_name="Cinnamomum camphora",
                    location="园区正门两侧",
                    planting_date=date(2020, 3, 15),
                    quantity=10,
                    growth_status="良好",
                    responsible_person="园丁小张",
                    remarks="树龄5年"
                ),
                GreenPlant(
                    plant_name="桂花树",
                    plant_code="GP002",
                    plant_type="灌木",
                    scientific_name="Osmanthus fragrans",
                    location="办公楼前",
                    planting_date=date(2021, 4, 20),
                    quantity=8,
                    growth_status="良好",
                    responsible_person="园丁小张",
                    remarks="花期9-10月"
                ),
                GreenPlant(
                    plant_name="月季花",
                    plant_code="GP003",
                    plant_type="花卉",
                    scientific_name="Rosa chinensis",
                    location="园区花坛",
                    planting_date=date(2022, 5, 10),
                    quantity=50,
                    growth_status="良好",
                    responsible_person="园丁小李",
                    remarks="花期4-9月"
                ),
                GreenPlant(
                    plant_name="马尼拉草",
                    plant_code="GP004",
                    plant_type="草坪",
                    scientific_name="Zoysia matrella",
                    location="足球场",
                    planting_date=date(2023, 3, 1),
                    quantity=200,
                    growth_status="一般",
                    responsible_person="园丁小李",
                    remarks="部分区域需要补种"
                ),
            ]
            session.add_all(plants)
            await session.commit()
            
            for p in plants:
                await session.refresh(p)
            
            print("正在生成养护计划数据...")
            maintenance_plans = [
                MaintenancePlan(
                    plant_id=plants[0].id,
                    plan_name="香樟树春季施肥计划",
                    maintenance_type="施肥",
                    frequency="每月一次",
                    start_date=date(2024, 3, 1),
                    end_date=date(2024, 5, 31),
                    description="使用复合肥，每株施肥200克",
                    responsible_person="园丁小张",
                    status="执行中"
                ),
                MaintenancePlan(
                    plant_id=plants[1].id,
                    plan_name="桂花树修剪计划",
                    maintenance_type="修剪",
                    frequency="每季度一次",
                    start_date=date(2024, 1, 1),
                    end_date=date(2024, 12, 31),
                    description="修剪过密枝条，保持树形美观",
                    responsible_person="园丁小张",
                    status="待执行"
                ),
                MaintenancePlan(
                    plant_id=plants[2].id,
                    plan_name="月季花病虫害防治计划",
                    maintenance_type="病虫害防治",
                    frequency="每两周一次",
                    start_date=date(2024, 4, 1),
                    end_date=date(2024, 10, 31),
                    description="定期喷洒杀虫剂，预防蚜虫和白粉病",
                    responsible_person="园丁小李",
                    status="待执行"
                ),
            ]
            session.add_all(maintenance_plans)
            await session.commit()
            
            for mp in maintenance_plans:
                await session.refresh(mp)
            
            print("正在生成养护记录数据...")
            maintenance_records = [
                MaintenanceRecord(
                    plan_id=maintenance_plans[0].id,
                    plant_id=plants[0].id,
                    maintenance_date=today - timedelta(days=10),
                    maintenance_type="施肥",
                    operator="园丁小张",
                    work_content="为10株香樟树施肥",
                    materials_used="复合肥20kg",
                    quality="优秀",
                    remarks="施肥完成"
                ),
                MaintenanceRecord(
                    plant_id=plants[3].id,
                    maintenance_date=today - timedelta(days=5),
                    maintenance_type="浇水",
                    operator="园丁小李",
                    work_content="足球场草坪浇水",
                    materials_used="",
                    quality="良好",
                    remarks="部分区域需要补种"
                ),
            ]
            session.add_all(maintenance_records)
            await session.commit()
            
            print("\n✅ 测试数据生成完成！")
            print("\n生成的数据统计：")
            print(f"  安保人员: {len(personnel_list)} 条")
            print(f"  安保排班: {len(schedules)} 条")
            print(f"  巡逻路线: {len(routes)} 条")
            print(f"  监控设备: {len(devices)} 条")
            print(f"  车辆出入记录: {len(vehicles)} 条")
            print(f"  外来人员记录: {len(visitors)} 条")
            print(f"  突发事件上报: {len(emergencies)} 条")
            print(f"  保洁区域: {len(cleaning_areas)} 条")
            print(f"  清洁记录: {len(cleaning_records)} 条")
            print(f"  绿化植物: {len(plants)} 条")
            print(f"  养护计划: {len(maintenance_plans)} 条")
            print(f"  养护记录: {len(maintenance_records)} 条")
            
        except Exception as e:
            print(f"❌ 生成测试数据失败: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    print("=" * 50)
    print("物业秩序与环境管理系统 - 测试数据生成器")
    print("=" * 50)
    
    async def main():
        print("\n正在初始化数据库...")
        await init_db()
        
        print("\n开始生成测试数据...")
        await generate_test_data()
        
        print("\n" + "=" * 50)
        print("测试数据生成完成！")
        print("=" * 50)
    
    asyncio.run(main())
