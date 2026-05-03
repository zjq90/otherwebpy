"""
数据库初始化脚本
用于创建数据库表结构和生成测试数据
"""
import sys
import os
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session

from backend.app.database import engine, Base, SessionLocal
from backend.app.models import (
    PlantingPlan, FarmOperation, FertilizationIrrigation, PestDiseaseControl
)
from backend.app.models.planting_plan import PlanTypeEnum, PlanStatusEnum
from backend.app.models.farm_operation import OperationTypeEnum, OperationStatusEnum
from backend.app.models.fertilization_irrigation import (
    FertilizerTypeEnum, IrrigationTypeEnum, WaterSourceEnum
)
from backend.app.models.pest_disease_control import (
    PestDiseaseTypeEnum, ControlMethodEnum, SeverityLevelEnum, TreatmentStatusEnum
)


def create_tables():
    """
    创建所有数据库表
    """
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")


def drop_tables():
    """
    删除所有数据库表（谨慎使用）
    """
    print("正在删除数据库表...")
    Base.metadata.drop_all(bind=engine)
    print("数据库表删除完成！")


def generate_random_date(start_date: date, end_date: date) -> date:
    """
    生成指定范围内的随机日期
    
    参数:
        start_date: 开始日期
        end_date: 结束日期
    
    返回:
        随机日期
    """
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)


def generate_planting_plan_test_data(db: Session):
    """
    生成种植计划测试数据
    
    参数:
        db: 数据库会话
    """
    print("正在生成种植计划测试数据...")
    
    # 测试用的作物数据
    crops = [
        {"type": "水稻", "varieties": ["籼稻", "粳稻", "糯稻", "杂交稻"], "yield_range": (400, 800)},
        {"type": "小麦", "varieties": ["冬小麦", "春小麦", "优质麦"], "yield_range": (300, 600)},
        {"type": "玉米", "varieties": ["甜玉米", "糯玉米", "饲料玉米", "鲜食玉米"], "yield_range": (500, 900)},
        {"type": "大豆", "varieties": ["黄豆", "黑豆", "青豆"], "yield_range": (150, 300)},
        {"type": "蔬菜", "varieties": ["番茄", "黄瓜", "茄子", "辣椒", "白菜"], "yield_range": (2000, 5000)},
        {"type": "水果", "varieties": ["苹果", "梨", "桃", "葡萄", "草莓"], "yield_range": (1000, 3000)},
    ]
    
    # 地块信息
    plots = ["东区一号田", "东区二号田", "西区一号田", "西区二号田", "南区试验田", "北区示范田"]
    
    # 责任人
    persons = ["张三", "李四", "王五", "赵六", "钱七", "孙八"]
    
    # 生成2024年和2025年的测试数据
    current_year = datetime.now().year
    years = [current_year - 1, current_year]
    
    plan_counter = 1
    
    for year in years:
        for crop in crops:
            # 每年每个作物生成1-3个计划
            plan_count = random.randint(1, 3)
            
            for _ in range(plan_count):
                # 随机选择计划类型
                plan_type = random.choice(list(PlanTypeEnum))
                
                # 确定季度和月份
                quarter = None
                month = None
                
                if plan_type == PlanTypeEnum.QUARTERLY:
                    quarter = random.randint(1, 4)
                elif plan_type == PlanTypeEnum.MONTHLY:
                    month = random.randint(1, 12)
                
                # 随机选择作物品种
                variety = random.choice(crop["varieties"])
                
                # 随机生成种植面积
                planting_area = Decimal(str(round(random.uniform(5.0, 50.0), 2)))
                
                # 随机生成目标亩产量
                target_yield = Decimal(str(round(random.uniform(*crop["yield_range"]), 2)))
                
                # 随机生成播种时间和收获时间
                # 根据作物类型确定大致的种植周期
                if crop["type"] in ["水稻", "小麦", "玉米", "大豆"]:
                    # 粮食作物，生长周期较长
                    sowing_month = random.randint(3, 6)
                    sowing_date = date(year, sowing_month, random.randint(1, 28))
                    harvest_days = random.randint(100, 150)
                else:
                    # 蔬菜水果，生长周期较短
                    sowing_month = random.randint(1, 10)
                    sowing_date = date(year, sowing_month, random.randint(1, 28))
                    harvest_days = random.randint(60, 120)
                
                expected_harvest_date = sowing_date + timedelta(days=harvest_days)
                
                # 随机决定是否有实际收获数据
                actual_harvest_date = None
                actual_yield = None
                progress = Decimal("0.00")
                status = random.choice(list(PlanStatusEnum))
                
                if status in [PlanStatusEnum.COMPLETED, PlanStatusEnum.IN_PROGRESS]:
                    if status == PlanStatusEnum.COMPLETED:
                        # 已完成的计划有实际收获数据
                        actual_harvest_date = expected_harvest_date + timedelta(days=random.randint(-10, 10))
                        actual_yield = Decimal(str(round(target_yield * Decimal(str(random.uniform(0.8, 1.2))), 2)))
                        progress = Decimal("100.00")
                    else:
                        # 执行中的计划有部分进度
                        progress = Decimal(str(round(random.uniform(10, 90), 2)))
                
                # 创建种植计划
                plan = PlantingPlan(
                    plan_code=f"PP{year}{plan_counter:04d}",
                    plan_name=f"{year}年{crop['type']}{'年度' if plan_type == PlanTypeEnum.ANNUAL else '季度' if plan_type == PlanTypeEnum.QUARTERLY else '月度'}种植计划",
                    plan_type=plan_type,
                    year=year,
                    quarter=quarter,
                    month=month,
                    crop_type=crop["type"],
                    crop_variety=variety,
                    planting_area=planting_area,
                    sowing_date=sowing_date,
                    expected_harvest_date=expected_harvest_date,
                    actual_harvest_date=actual_harvest_date,
                    target_yield_per_mu=target_yield,
                    actual_yield_per_mu=actual_yield,
                    location=random.choice(plots),
                    status=status,
                    progress=progress,
                    responsible_person=random.choice(persons),
                    created_by="系统管理员",
                    remarks=f"这是{year}年{crop['type']}种植的测试计划数据。"
                )
                
                # 计算目标总产量
                plan.calculate_target_total_yield()
                if actual_yield:
                    plan.calculate_actual_total_yield()
                
                db.add(plan)
                plan_counter += 1
    
    db.commit()
    print(f"已生成 {plan_counter - 1} 条种植计划测试数据！")


def generate_farm_operation_test_data(db: Session):
    """
    生成农事作业记录测试数据
    
    参数:
        db: 数据库会话
    """
    print("正在生成农事作业记录测试数据...")
    
    # 获取所有种植计划
    plans = db.query(PlantingPlan).all()
    
    if not plans:
        print("没有找到种植计划，无法生成农事作业记录！")
        return
    
    operation_counter = 1
    persons = ["张三", "李四", "王五", "赵六", "钱七", "孙八"]
    
    for plan in plans:
        # 每个种植计划生成3-8条作业记录
        operation_count = random.randint(3, 8)
        
        for _ in range(operation_count):
            # 随机选择作业类型
            operation_type = random.choice(list(OperationTypeEnum))
            
            # 根据作业类型确定作业名称
            operation_names = {
                OperationTypeEnum.SOWING: ["播种作业", "机械播种", "人工点播", "撒播作业"],
                OperationTypeEnum.FERTILIZATION: ["基肥施用", "追肥作业", "叶面施肥", "测土配方施肥"],
                OperationTypeEnum.IRRIGATION: ["滴灌作业", "喷灌作业", "漫灌作业", "水肥一体化灌溉"],
                OperationTypeEnum.WEEDING: ["人工除草", "机械除草", "化学除草", "中耕除草"],
                OperationTypeEnum.PEST_CONTROL: ["病虫害防治", "生物防治", "化学防治", "综合防治"],
                OperationTypeEnum.HARVEST: ["人工收获", "机械收获", "联合收割", "分批收获"],
                OperationTypeEnum.OTHER: ["田间管理", "土壤改良", "设施维护", "其他作业"]
            }
            
            operation_name = random.choice(operation_names[operation_type])
            
            # 随机生成作业日期（在播种和收获之间）
            if plan.sowing_date and plan.expected_harvest_date:
                actual_date = generate_random_date(plan.sowing_date, plan.expected_harvest_date)
            else:
                actual_date = date(plan.year, random.randint(1, 12), random.randint(1, 28))
            
            # 随机生成用量
            quantity = None
            quantity_unit = None
            
            if operation_type == OperationTypeEnum.SOWING:
                quantity = Decimal(str(round(random.uniform(1.0, 10.0), 2)))
                quantity_unit = "公斤"
            elif operation_type == OperationTypeEnum.FERTILIZATION:
                quantity = Decimal(str(round(random.uniform(10.0, 100.0), 2)))
                quantity_unit = "公斤"
            elif operation_type == OperationTypeEnum.IRRIGATION:
                quantity = Decimal(str(round(random.uniform(20.0, 200.0), 2)))
                quantity_unit = "立方米"
            elif operation_type in [OperationTypeEnum.WEEDING, OperationTypeEnum.HARVEST]:
                quantity = Decimal(str(round(random.uniform(5.0, 50.0), 2)))
                quantity_unit = "亩"
            
            # 创建作业记录
            operation = FarmOperation(
                planting_plan_id=plan.id,
                operation_code=f"FO{plan.year}{operation_counter:06d}",
                operation_type=operation_type,
                operation_name=operation_name,
                actual_date=actual_date,
                crop_type=plan.crop_type,
                plot_location=plan.location,
                operation_area=plan.planting_area if random.random() > 0.3 else None,
                operator=random.choice(persons),
                operator_contact=f"138{random.randint(10000000, 99999999)}",
                is_app_entry=1 if random.random() > 0.5 else 0,
                entry_device="iPhone 14" if random.random() > 0.5 else "Android手机",
                quantity=quantity,
                quantity_unit=quantity_unit,
                operation_method=f"采用{operation_type.value}作业方法，按照标准操作规程进行。",
                tools_used=random.choice(["拖拉机", "插秧机", "喷雾器", "灌溉设备", "人工工具", "联合收割机"]),
                weather_condition=random.choice(["晴天", "多云", "阴天", "小雨", "适宜作业"]),
                status=random.choice(list(OperationStatusEnum)),
                effect_assessment=random.choice(["作业效果良好", "作业效果一般", "作业效果较差", "需要复查"]),
                created_by="系统管理员",
                remarks=f"与种植计划 {plan.plan_code} 关联的{operation_type.value}记录。"
            )
            
            db.add(operation)
            operation_counter += 1
    
    db.commit()
    print(f"已生成 {operation_counter - 1} 条农事作业记录测试数据！")


def generate_fertilization_irrigation_test_data(db: Session):
    """
    生成精准施肥与灌溉测试数据
    
    参数:
        db: 数据库会话
    """
    print("正在生成精准施肥与灌溉测试数据...")
    
    # 获取所有种植计划
    plans = db.query(PlantingPlan).all()
    
    if not plans:
        print("没有找到种植计划，无法生成施肥灌溉记录！")
        return
    
    record_counter = 1
    persons = ["张三", "李四", "王五", "赵六", "钱七", "孙八"]
    
    for plan in plans:
        # 每个种植计划生成2-5条施肥灌溉记录
        record_count = random.randint(2, 5)
        
        for _ in range(record_count):
            # 随机选择记录类型
            record_type = random.choice(["施肥", "灌溉", "水肥一体化"])
            is_fertigation = 1 if record_type == "水肥一体化" else 0
            
            # 随机生成记录日期
            if plan.sowing_date and plan.expected_harvest_date:
                record_date = generate_random_date(plan.sowing_date, plan.expected_harvest_date)
            else:
                record_date = date(plan.year, random.randint(1, 12), random.randint(1, 28))
            
            # 生成土壤检测数据
            soil_test_date = record_date - timedelta(days=random.randint(1, 7))
            soil_ph = Decimal(str(round(random.uniform(5.5, 7.5), 2)))
            organic_matter = Decimal(str(round(random.uniform(10.0, 40.0), 2)))
            total_nitrogen = Decimal(str(round(random.uniform(1.0, 3.0), 2)))
            available_phosphorus = Decimal(str(round(random.uniform(10.0, 50.0), 2)))
            available_potassium = Decimal(str(round(random.uniform(80.0, 200.0), 2)))
            soil_moisture = Decimal(str(round(random.uniform(15.0, 35.0), 2)))
            
            # 生成计划施肥数据
            planned_fertilizer_type = random.choice(list(FertilizerTypeEnum))
            fertilizer_names = {
                FertilizerTypeEnum.NITROGEN: ["尿素", "碳酸氢铵", "氯化铵", "硝酸铵"],
                FertilizerTypeEnum.PHOSPHATE: ["过磷酸钙", "重过磷酸钙", "钙镁磷肥"],
                FertilizerTypeEnum.POTASSIUM: ["氯化钾", "硫酸钾", "硝酸钾"],
                FertilizerTypeEnum.COMPOUND: ["三元复合肥", "掺混肥", "缓释复合肥"],
                FertilizerTypeEnum.ORGANIC: ["腐熟有机肥", "商品有机肥", "生物有机肥"],
                FertilizerTypeEnum.MICROELEMENT: ["硼肥", "锌肥", "铁肥", "锰肥"],
                FertilizerTypeEnum.BIOLOGICAL: ["根瘤菌肥", "EM菌肥", "生物菌剂"],
                FertilizerTypeEnum.OTHER: ["叶面肥", "冲施肥", "水溶肥"]
            }
            planned_fertilizer_name = random.choice(fertilizer_names[planned_fertilizer_type])
            
            # 计划施肥量（公斤/亩）
            planned_fertilizer_amount = Decimal(str(round(random.uniform(15.0, 60.0), 3)))
            
            # 实际施肥量（在计划值的±10%范围内）
            actual_fertilizer_amount = Decimal(str(
                round(float(planned_fertilizer_amount) * random.uniform(0.9, 1.1), 3)
            ))
            
            # 生成灌溉数据
            planned_irrigation_type = random.choice(list(IrrigationTypeEnum))
            planned_water_source = random.choice(list(WaterSourceEnum))
            
            # 计划灌溉量（立方米/亩）
            planned_irrigation_amount = Decimal(str(round(random.uniform(30.0, 80.0), 3)))
            
            # 实际灌溉量
            actual_irrigation_amount = Decimal(str(
                round(float(planned_irrigation_amount) * random.uniform(0.85, 1.15), 3)
            ))
            
            # 创建施肥灌溉记录
            record = FertilizationIrrigation(
                planting_plan_id=plan.id,
                record_code=f"FI{plan.year}{record_counter:06d}",
                record_type=record_type,
                record_date=record_date,
                crop_type=plan.crop_type,
                growth_stage=random.choice(["苗期", "分蘖期", "拔节期", "孕穗期", "灌浆期", "成熟期"]),
                plot_location=plan.location,
                operation_area=plan.planting_area,
                
                # 土壤检测数据
                soil_test_date=soil_test_date,
                soil_ph=soil_ph,
                organic_matter=organic_matter,
                total_nitrogen=total_nitrogen,
                available_phosphorus=available_phosphorus,
                available_potassium=available_potassium,
                alkali_hydrolyzable_nitrogen=Decimal(str(round(random.uniform(60.0, 150.0), 2))),
                soil_moisture=soil_moisture,
                
                # 计划施肥数据
                planned_fertilizer_type=planned_fertilizer_type,
                planned_fertilizer_name=planned_fertilizer_name,
                planned_fertilizer_amount_per_mu=planned_fertilizer_amount,
                planned_fertilization_method=random.choice(["撒施", "条施", "穴施", "叶面喷施", "随水冲施"]),
                
                # 实际施肥数据
                actual_fertilizer_type=planned_fertilizer_type if random.random() > 0.2 else random.choice(list(FertilizerTypeEnum)),
                actual_fertilizer_name=planned_fertilizer_name if random.random() > 0.2 else random.choice(fertilizer_names[planned_fertilizer_type]),
                actual_fertilizer_amount_per_mu=actual_fertilizer_amount,
                actual_fertilization_method=random.choice(["撒施", "条施", "穴施", "叶面喷施", "随水冲施"]),
                fertilization_date=record_date,
                
                # 计划灌溉数据
                planned_irrigation_type=planned_irrigation_type,
                planned_water_source=planned_water_source,
                planned_irrigation_amount_per_mu=planned_irrigation_amount,
                planned_irrigation_duration=Decimal(str(round(random.uniform(2.0, 8.0), 2))),
                
                # 实际灌溉数据
                actual_irrigation_type=planned_irrigation_type,
                actual_water_source=planned_water_source,
                actual_irrigation_amount_per_mu=actual_irrigation_amount,
                actual_irrigation_duration=Decimal(str(round(random.uniform(1.5, 9.0), 2))),
                irrigation_date=record_date,
                
                # 水肥一体化
                is_fertigation=is_fertigation,
                fertigation_ratio="1:200" if is_fertigation else None,
                
                # 操作人员
                operator=random.choice(persons),
                equipment_code=f"EQ-{random.randint(100, 999)}",
                weather_condition=random.choice(["晴天", "多云", "阴天", "适宜作业"]),
                created_by="系统管理员",
                remarks=f"与种植计划 {plan.plan_code} 关联的{record_type}记录。根据土壤检测数据制定施肥灌溉方案。"
            )
            
            # 计算总量和偏差
            record.calculate_totals()
            record.calculate_deviations()
            
            db.add(record)
            record_counter += 1
    
    db.commit()
    print(f"已生成 {record_counter - 1} 条精准施肥与灌溉测试数据！")


def generate_pest_disease_control_test_data(db: Session):
    """
    生成病虫害防治管理测试数据
    
    参数:
        db: 数据库会话
    """
    print("正在生成病虫害防治测试数据...")
    
    # 获取所有种植计划
    plans = db.query(PlantingPlan).all()
    
    if not plans:
        print("没有找到种植计划，无法生成病虫害防治记录！")
        return
    
    record_counter = 1
    persons = ["张三", "李四", "王五", "赵六", "钱七", "孙八"]
    
    # 常见病虫害数据
    pests_diseases = [
        {"type": PestDiseaseTypeEnum.PEST, "name": "稻飞虱", "scientific": "Nilaparvata lugens"},
        {"type": PestDiseaseTypeEnum.PEST, "name": "稻纵卷叶螟", "scientific": "Cnaphalocrocis medinalis"},
        {"type": PestDiseaseTypeEnum.PEST, "name": "二化螟", "scientific": "Chilo suppressalis"},
        {"type": PestDiseaseTypeEnum.PEST, "name": "蚜虫", "scientific": "Aphidoidea"},
        {"type": PestDiseaseTypeEnum.PEST, "name": "红蜘蛛", "scientific": "Tetranychus cinnabarinus"},
        {"type": PestDiseaseTypeEnum.DISEASE, "name": "稻瘟病", "scientific": "Magnaporthe oryzae"},
        {"type": PestDiseaseTypeEnum.DISEASE, "name": "纹枯病", "scientific": "Rhizoctonia solani"},
        {"type": PestDiseaseTypeEnum.DISEASE, "name": "白粉病", "scientific": "Erysiphaceae"},
        {"type": PestDiseaseTypeEnum.DISEASE, "name": "霜霉病", "scientific": "Peronosporaceae"},
        {"type": PestDiseaseTypeEnum.DISEASE, "name": "炭疽病", "scientific": "Colletotrichum"},
        {"type": PestDiseaseTypeEnum.WEED, "name": "稗草", "scientific": "Echinochloa crus-galli"},
        {"type": PestDiseaseTypeEnum.WEED, "name": "千金子", "scientific": "Leptochloa chinensis"},
        {"type": PestDiseaseTypeEnum.OTHER, "name": "鼠害", "scientific": "Rodentia"},
    ]
    
    # 农药数据（包含一些高毒农药用于测试预警功能）
    pesticides = [
        {"name": "吡虫啉", "type": "杀虫剂", "safe_interval": 7},
        {"name": "阿维菌素", "type": "杀虫剂", "safe_interval": 14},
        {"name": "氯氰菊酯", "type": "杀虫剂", "safe_interval": 7},
        {"name": "多菌灵", "type": "杀菌剂", "safe_interval": 15},
        {"name": "甲基托布津", "type": "杀菌剂", "safe_interval": 30},
        {"name": "百菌清", "type": "杀菌剂", "safe_interval": 7},
        {"name": "草甘膦", "type": "除草剂", "safe_interval": 3},
        {"name": "丁草胺", "type": "除草剂", "safe_interval": 30},
        # 以下是高毒农药，用于测试预警功能
        {"name": "甲胺磷乳油", "type": "杀虫剂", "safe_interval": 60},
        {"name": "甲基对硫磷", "type": "杀虫剂", "safe_interval": 60},
    ]
    
    for plan in plans:
        # 每个种植计划生成1-3条病虫害记录
        record_count = random.randint(1, 3)
        
        for _ in range(record_count):
            # 随机选择病虫害
            pest_disease = random.choice(pests_diseases)
            
            # 随机生成发现日期
            if plan.sowing_date and plan.expected_harvest_date:
                discovery_date = generate_random_date(plan.sowing_date, plan.expected_harvest_date)
            else:
                discovery_date = date(plan.year, random.randint(1, 12), random.randint(1, 28))
            
            # 随机生成影响面积
            affected_area = Decimal(str(round(random.uniform(1.0, float(plan.planting_area)), 2)))
            
            # 随机选择严重程度
            severity = random.choice(list(SeverityLevelEnum))
            
            # 随机选择防治措施
            control_method = random.choice(list(ControlMethodEnum))
            
            # 防治日期
            treatment_date = discovery_date + timedelta(days=random.randint(1, 5))
            
            # 创建病虫害记录
            record = PestDiseaseControl(
                planting_plan_id=plan.id,
                record_code=f"PD{plan.year}{record_counter:06d}",
                discovery_date=discovery_date,
                pest_disease_type=pest_disease["type"],
                pest_disease_name=pest_disease["name"],
                scientific_name=pest_disease["scientific"],
                crop_type=plan.crop_type,
                growth_stage=random.choice(["苗期", "分蘖期", "拔节期", "孕穗期", "灌浆期"]),
                plot_location=plan.location,
                affected_area=affected_area,
                severity=severity,
                incidence_rate=Decimal(str(round(random.uniform(5.0, 40.0), 2))),
                symptoms_description=f"{pest_disease['name']}危害症状：叶片出现{random.choice(['黄斑', '褐斑', '卷曲', '枯萎', '穿孔'])}，{random.choice(['有虫粪', '有霉层', '有粉状物', '有菌核'])}。",
                control_method=control_method,
                treatment_date=treatment_date,
                operator=random.choice(persons),
                treatment_status=random.choice(list(TreatmentStatusEnum)),
                weather_condition=random.choice(["晴天", "多云", "阴天", "风力小"]),
                created_by="系统管理员",
                remarks=f"与种植计划 {plan.plan_code} 关联的病虫害防治记录。发现{pest_disease['name']}危害，已采取{control_method.value}措施。"
            )
            
            # 根据防治措施类型填充相应字段
            if control_method == ControlMethodEnum.CHEMICAL:
                # 化学防治
                pesticide = random.choice(pesticides)
                record.pesticide_name = pesticide["name"]
                record.pesticide_type = pesticide["type"]
                record.registration_number = f"PD{random.randint(20100000, 20259999)}"
                record.manufacturer = random.choice(["某农药厂", "绿色农药公司", "农化科技公司", "植保服务中心"])
                record.dosage_per_mu = Decimal(str(round(random.uniform(0.02, 0.5), 3)))
                record.dosage_unit = random.choice(["公斤", "毫升", "克"])
                record.dilution_ratio = random.randint(500, 2000)
                record.application_method = random.choice(["喷雾", "撒施", "灌根", "拌种"])
                record.equipment_used = random.choice(["背负式喷雾器", "机动喷雾机", "无人机喷药", "人工撒施"])
                record.safety_interval_days = pesticide["safe_interval"]
                record.calculate_allowed_use_date()
                
                # 检查高毒农药并更新预警状态
                record.update_warning_status()
                
                # 防治效果
                record.assessment_date = treatment_date + timedelta(days=random.randint(7, 14))
                record.control_effect = Decimal(str(round(random.uniform(60.0, 95.0), 2)))
                if record.control_effect >= 80:
                    record.effect_description = f"防治效果良好，{pest_disease['name']}危害得到有效控制。"
                elif record.control_effect >= 60:
                    record.effect_description = f"防治效果一般，{pest_disease['name']}危害有所减轻，建议再次防治。"
                    record.needs_retreatment = True
                    record.suggested_retreatment_date = record.assessment_date + timedelta(days=random.randint(7, 14))
            
            elif control_method == ControlMethodEnum.BIOLOGICAL:
                # 生物防治
                natural_enemies = ["赤眼蜂", "瓢虫", "草蛉", "捕食螨", "寄生蜂", "白僵菌", "绿僵菌", "苏云金杆菌"]
                record.natural_enemy_type = random.choice(natural_enemies)
                record.release_quantity = Decimal(str(round(random.uniform(1000.0, 50000.0), 2)))
                record.release_method = random.choice(["人工释放", "无人机释放", "挂卡释放", "撒施"])
                
                record.assessment_date = treatment_date + timedelta(days=random.randint(14, 21))
                record.control_effect = Decimal(str(round(random.uniform(50.0, 85.0), 2)))
                record.effect_description = f"生物防治效果：{record.natural_enemy_type}已定殖，{pest_disease['name']}种群数量呈下降趋势。"
            
            elif control_method == ControlMethodEnum.PHYSICAL:
                # 物理防治
                physical_measures = [
                    ("黄色诱虫板", "30块/亩"),
                    ("蓝色诱虫板", "25块/亩"),
                    ("杀虫灯", "1盏/10亩"),
                    ("防虫网", "全覆盖"),
                    ("人工捕捉", "人工捕杀"),
                    ("高温闷棚", "高温处理"),
                ]
                measure = random.choice(physical_measures)
                record.physical_measure_type = measure[0]
                record.quantity_density = measure[1]
                
                record.assessment_date = treatment_date + timedelta(days=random.randint(5, 10))
                record.control_effect = Decimal(str(round(random.uniform(40.0, 75.0), 2)))
                record.effect_description = f"物理防治效果：{record.physical_measure_type}已布设，诱杀效果明显。"
            
            elif control_method == ControlMethodEnum.AGRICULTURAL:
                # 农业防治
                agricultural_measures = [
                    "合理轮作",
                    "深耕晒垡",
                    "清洁田园",
                    "选用抗病品种",
                    "合理密植",
                    "科学施肥",
                    "适时播种",
                ]
                record.remarks = record.remarks + f" 采用农业防治措施：{random.choice(agricultural_measures)}。"
            
            else:  # 综合防治
                record.remarks = record.remarks + " 采用综合防治策略，结合多种防治方法。"
            
            db.add(record)
            record_counter += 1
    
    db.commit()
    print(f"已生成 {record_counter - 1} 条病虫害防治测试数据！")


def init_database(generate_test_data: bool = True):
    """
    初始化数据库
    
    参数:
        generate_test_data: 是否生成测试数据
    """
    print("=" * 50)
    print("开始初始化数据库...")
    print("=" * 50)
    
    # 创建数据库表
    create_tables()
    
    if generate_test_data:
        print("\n" + "=" * 50)
        print("开始生成测试数据...")
        print("=" * 50)
        
        db = SessionLocal()
        
        try:
            generate_planting_plan_test_data(db)
            generate_farm_operation_test_data(db)
            generate_fertilization_irrigation_test_data(db)
            generate_pest_disease_control_test_data(db)
            
            print("\n" + "=" * 50)
            print("测试数据生成完成！")
            print("=" * 50)
            
        except Exception as e:
            print(f"生成测试数据时发生错误: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
        finally:
            db.close()
    
    print("\n" + "=" * 50)
    print("数据库初始化完成！")
    print("=" * 50)


def reset_database():
    """
    重置数据库（删除所有表后重新创建）
    """
    print("警告：此操作将删除所有现有数据！")
    confirm = input("是否继续？(y/N): ")
    
    if confirm.lower() == 'y':
        db = SessionLocal()
        
        try:
            # 删除所有表
            drop_tables()
            
            # 重新创建并初始化
            init_database(generate_test_data=True)
            
        except Exception as e:
            print(f"重置数据库时发生错误: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
        finally:
            db.close()
    else:
        print("操作已取消。")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库初始化脚本")
    parser.add_argument("--reset", action="store_true", help="重置数据库（删除所有数据）")
    parser.add_argument("--no-test-data", action="store_true", help="不生成测试数据")
    
    args = parser.parse_args()
    
    if args.reset:
        reset_database()
    else:
        init_database(generate_test_data=not args.no_test_data)
