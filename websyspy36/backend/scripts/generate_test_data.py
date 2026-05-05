"""
测试数据生成脚本
用于生成系统测试所需的模拟数据
包含生产数据、成本数据、环保监测数据等
"""
import sys
import os
import random
from datetime import date, datetime, timedelta
from decimal import Decimal

# 将上级目录添加到路径，以便导入app模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.models import (
    # 生产数据模型
    Equipment, ProductionRecord, EquipmentUtilization, EnergyConsumption,
    # 成本数据模型
    Material, MaterialCost, Employee, LaborCost, SalesRecord, ProfitAnalysis,
    # 环保数据模型
    MonitoringPoint, DustMonitoring, NoiseMonitoring, WastewaterMonitoring, AlarmRecord
)


def random_date(start_date, end_date):
    """生成随机日期"""
    delta = end_date - start_date
    random_days = random.randrange(delta.days)
    return start_date + timedelta(days=random_days)


def generate_equipment(db):
    """生成设备数据"""
    equipment_types = ['搅拌机', '运输车', '泵车', '装载机', '破碎机']
    manufacturers = ['中联重科', '三一重工', '徐工集团', '柳工机械', '山推股份']
    
    equipments = []
    for i in range(1, 6):
        eq = Equipment(
            equipment_code=f"EQ{str(i).zfill(3)}",
            equipment_name=f"{random.choice(equipment_types)}{i}号",
            equipment_type=random.choice(equipment_types),
            specification=f"型号-{random.choice(['A', 'B', 'C', 'D'])}",
            max_capacity=random.uniform(50, 200),
            manufacturer=random.choice(manufacturers),
            purchase_date=random_date(date(2020, 1, 1), date(2023, 12, 31)),
            status=random.choice(['正常', '正常', '正常', '维修中'])
        )
        equipments.append(eq)
        db.add(eq)
    
    db.commit()
    print(f"成功生成 {len(equipments)} 条设备数据")
    return equipments


def generate_production_records(db):
    """生成生产记录数据"""
    start_date = date(2025, 1, 1)
    end_date = date(2025, 4, 30)
    
    records = []
    current_date = start_date
    while current_date <= end_date:
        # 周末可能产量少一些
        if current_date.weekday() >= 5:
            if random.random() > 0.5:
                total_production = random.uniform(100, 300)
            else:
                current_date += timedelta(days=1)
                continue
        else:
            total_production = random.uniform(500, 1200)
        
        qualified_rate = random.uniform(0.95, 0.99)
        record = ProductionRecord(
            record_date=current_date,
            total_production=total_production,
            qualified_production=total_production * qualified_rate,
            batch_count=random.randint(5, 30),
            working_hours=random.uniform(8, 12),
            production_type=random.choice(['商砼', '商砼', '商砼', '预制件']),
            remarks=''
        )
        records.append(record)
        db.add(record)
        current_date += timedelta(days=1)
    
    db.commit()
    print(f"成功生成 {len(records)} 条生产记录数据")
    return records


def generate_equipment_utilization(db, equipments):
    """生成设备利用率数据"""
    start_date = date(2025, 1, 1)
    end_date = date(2025, 4, 30)
    
    records = []
    current_date = start_date
    
    while current_date <= end_date:
        for equipment in equipments:
            # 周末设备可能利用率低
            if current_date.weekday() >= 5:
                actual_working_hours = random.uniform(2, 8)
            else:
                actual_working_hours = random.uniform(8, 18)
            
            maintenance_hours = random.uniform(0, 2) if random.random() > 0.8 else 0
            idle_hours = 24 - actual_working_hours - maintenance_hours
            utilization_rate = (actual_working_hours / 24) * 100
            
            record = EquipmentUtilization(
                equipment_id=equipment.id,
                record_date=current_date,
                total_available_hours=24.0,
                actual_working_hours=actual_working_hours,
                maintenance_hours=maintenance_hours,
                idle_hours=idle_hours,
                utilization_rate=utilization_rate
            )
            records.append(record)
            db.add(record)
        
        current_date += timedelta(days=1)
    
    db.commit()
    print(f"成功生成 {len(records)} 条设备利用率数据")
    return records


def generate_energy_consumption(db, equipments):
    """生成能耗数据"""
    start_date = date(2025, 1, 1)
    end_date = date(2025, 4, 30)
    energy_types = ['电力', '水', '柴油']
    units = {'电力': 'kWh', '水': '立方米', '柴油': '升'}
    
    records = []
    current_date = start_date
    
    while current_date <= end_date:
        # 总能耗记录
        for energy_type in energy_types:
            if energy_type == '电力':
                amount = random.uniform(800, 2000)
                cost = amount * 0.85
            elif energy_type == '水':
                amount = random.uniform(50, 150)
                cost = amount * 4.5
            else:  # 柴油
                amount = random.uniform(100, 300)
                cost = amount * 7.5
            
            record = EnergyConsumption(
                record_date=current_date,
                equipment_id=None,
                energy_type=energy_type,
                consumption_amount=amount,
                unit=units[energy_type],
                cost=cost
            )
            records.append(record)
            db.add(record)
        
        current_date += timedelta(days=1)
    
    db.commit()
    print(f"成功生成 {len(records)} 条能耗数据")
    return records


def generate_materials(db):
    """生成原材料数据"""
    material_data = [
        ('MT001', '普通硅酸盐水泥', '水泥', '吨', 450.0, '海螺水泥', 500),
        ('MT002', '河沙', '砂石', '吨', 120.0, '本地砂石厂', 2000),
        ('MT003', '碎石1-3', '砂石', '吨', 110.0, '本地砂石厂', 1500),
        ('MT004', '粉煤灰', '粉煤灰', '吨', 80.0, '大唐电厂', 300),
        ('MT005', '减水剂', '外加剂', '吨', 3500.0, '江苏苏博特', 50),
        ('MT006', '矿粉', '矿粉', '吨', 320.0, '宝钢集团', 200),
    ]
    
    materials = []
    for code, name, mtype, unit, price, supplier, stock in material_data:
        material = Material(
            material_code=code,
            material_name=name,
            material_type=mtype,
            unit=unit,
            current_price=price,
            supplier=supplier,
            stock_quantity=stock + random.randint(-50, 50)
        )
        materials.append(material)
        db.add(material)
    
    db.commit()
    print(f"成功生成 {len(materials)} 条原材料数据")
    return materials


def generate_material_costs(db, materials):
    """生成原材料成本数据"""
    start_date = date(2025, 1, 1)
    end_date = date(2025, 4, 30)
    
    records = []
    current_date = start_date
    
    while current_date <= end_date:
        # 周末可能消耗少
        if current_date.weekday() >= 5:
            if random.random() > 0.6:
                current_date += timedelta(days=1)
                continue
        
        for material in materials:
            # 根据材料类型随机生成消耗量
            if material.material_type == '水泥':
                quantity = random.uniform(80, 150)
            elif material.material_type == '砂石':
                quantity = random.uniform(200, 400)
            elif material.material_type == '粉煤灰':
                quantity = random.uniform(20, 50)
            elif material.material_type == '外加剂':
                quantity = random.uniform(2, 8)
            else:
                quantity = random.uniform(10, 30)
            
            # 价格在当前价格基础上有小幅波动
            unit_price = material.current_price * random.uniform(0.95, 1.05)
            
            record = MaterialCost(
                record_date=current_date,
                material_id=material.id,
                consumption_quantity=quantity,
                unit_price=unit_price,
                total_cost=quantity * unit_price,
                production_batch=f"PB{current_date.strftime('%Y%m%d')}{random.randint(1, 10)}"
            )
            records.append(record)
            db.add(record)
        
        current_date += timedelta(days=1)
    
    db.commit()
    print(f"成功生成 {len(records)} 条原材料成本数据")
    return records


def generate_employees(db):
    """生成员工数据"""
    employee_names = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十',
                      '郑一', '冯二', '陈三', '褚四', '卫五', '蒋六', '沈七', '韩八']
    departments = ['生产部', '生产部', '生产部', '质量部', '销售部', '财务部', '行政部']
    positions = ['操作工', '操作工', '班长', '质检员', '销售员', '会计', '司机', '维修工']
    
    employees = []
    for i in range(1, 13):
        hourly_rate = random.uniform(25, 60)
        emp = Employee(
            employee_code=f"EMP{str(i).zfill(3)}",
            employee_name=random.choice(employee_names),
            department=random.choice(departments),
            position=random.choice(positions),
            base_salary=hourly_rate * 8 * 22,
            hourly_rate=hourly_rate,
            status='在职'
        )
        employees.append(emp)
        db.add(emp)
    
    db.commit()
    print(f"成功生成 {len(employees)} 条员工数据")
    return employees


def generate_labor_costs(db, employees):
    """生成人工成本数据"""
    start_date = date(2025, 1, 1)
    end_date = date(2025, 4, 30)
    
    records = []
    current_date = start_date
    
    while current_date <= end_date:
        for employee in employees:
            # 周末加班情况
            if current_date.weekday() >= 5:
                if random.random() > 0.7:
                    working_hours = random.uniform(4, 8)
                    overtime_hours = working_hours if random.random() > 0.5 else 0
                else:
                    continue
            else:
                working_hours = random.uniform(8, 9)
                overtime_hours = random.uniform(0, 3) if random.random() > 0.7 else 0
            
            total_cost = working_hours * employee.hourly_rate + overtime_hours * employee.hourly_rate * 1.5
            
            record = LaborCost(
                record_date=current_date,
                employee_id=employee.id,
                working_hours=working_hours,
                overtime_hours=overtime_hours,
                hourly_rate=employee.hourly_rate,
                overtime_rate=1.5,
                total_labor_cost=total_cost,
                work_content='正常生产'
            )
            records.append(record)
            db.add(record)
        
        current_date += timedelta(days=1)
    
    db.commit()
    print(f"成功生成 {len(records)} 条人工成本数据")
    return records


def generate_sales_records(db):
    """生成销售记录数据"""
    start_date = date(2025, 1, 1)
    end_date = date(2025, 4, 30)
    customers = ['中建一局', '中建二局', '中建三局', '中铁一局', '中铁二局',
                 '万科地产', '恒大地产', '碧桂园', '保利地产', '本地建筑公司']
    concrete_types = ['C20', 'C25', 'C30', 'C35', 'C40', 'C45']
    locations = ['工地A', '工地B', '工地C', '工地D', '工地E']
    
    records = []
    current_date = start_date
    sale_count = 1
    
    while current_date <= end_date:
        # 每天生成1-3条销售记录
        daily_count = random.randint(1, 3)
        for _ in range(daily_count):
            quantity = random.uniform(50, 300)
            concrete_type = random.choice(concrete_types)
            
            # 根据强度等级定价
            if concrete_type == 'C20':
                unit_price = 380
            elif concrete_type == 'C25':
                unit_price = 400
            elif concrete_type == 'C30':
                unit_price = 430
            elif concrete_type == 'C35':
                unit_price = 460
            elif concrete_type == 'C40':
                unit_price = 490
            else:
                unit_price = 520
            
            unit_price *= random.uniform(0.98, 1.02)
            
            record = SalesRecord(
                sale_date=current_date,
                sale_code=f"XS{current_date.strftime('%Y%m%d')}{str(sale_count).zfill(4)}",
                customer_name=random.choice(customers),
                concrete_type=concrete_type,
                quantity=quantity,
                unit_price=unit_price,
                total_amount=quantity * unit_price,
                delivery_location=random.choice(locations),
                status=random.choice(['已确认', '已发货', '已收款'])
            )
            records.append(record)
            db.add(record)
            sale_count += 1
        
        current_date += timedelta(days=1)
    
    db.commit()
    print(f"成功生成 {len(records)} 条销售记录数据")
    return records


def generate_profit_analysis(db, sales_records):
    """生成利润分析数据"""
    records = []
    
    for sale in sales_records:
        # 根据混凝土类型计算成本
        if sale.concrete_type == 'C20':
            material_cost = 200
            labor_cost = 30
            energy_cost = 25
        elif sale.concrete_type == 'C25':
            material_cost = 220
            labor_cost = 32
            energy_cost = 26
        elif sale.concrete_type == 'C30':
            material_cost = 240
            labor_cost = 35
            energy_cost = 28
        elif sale.concrete_type == 'C35':
            material_cost = 260
            labor_cost = 38
            energy_cost = 30
        elif sale.concrete_type == 'C40':
            material_cost = 280
            labor_cost = 42
            energy_cost = 33
        else:
            material_cost = 300
            labor_cost = 45
            energy_cost = 35
        
        other_cost = random.uniform(10, 20)
        total_cost = material_cost + labor_cost + energy_cost + other_cost
        
        sales_price = sale.unit_price
        gross_profit = sales_price - total_cost
        gross_margin = (gross_profit / sales_price) * 100
        
        analysis = ProfitAnalysis(
            analysis_date=sale.sale_date,
            sales_record_id=sale.id,
            concrete_type=sale.concrete_type,
            material_cost_per_cubic=material_cost,
            labor_cost_per_cubic=labor_cost,
            energy_cost_per_cubic=energy_cost,
            other_cost_per_cubic=other_cost,
            total_cost_per_cubic=total_cost,
            sales_price_per_cubic=sales_price,
            gross_profit_per_cubic=gross_profit,
            gross_profit_margin=gross_margin,
            total_quantity=sale.quantity,
            total_cost=sale.quantity * total_cost,
            total_sales=sale.total_amount,
            total_gross_profit=sale.quantity * gross_profit
        )
        records.append(analysis)
        db.add(analysis)
    
    db.commit()
    print(f"成功生成 {len(records)} 条利润分析数据")
    return records


def generate_monitoring_points(db):
    """生成监测点位数据"""
    point_data = [
        ('MP001', '生产区入口', '厂区大门东侧', '粉尘'),
        ('MP002', '搅拌楼一层', '搅拌楼1楼操作区', '粉尘'),
        ('MP003', '料场北侧', '砂石料场北侧', '粉尘'),
        ('MP004', '生产区西边界', '厂区西侧围墙', '噪音'),
        ('MP005', '生产区南边界', '厂区南侧围墙', '噪音'),
        ('MP006', '办公区北侧', '办公楼北侧区域', '噪音'),
        ('MP007', '废水排放口A', '沉淀池排放口', '废水'),
        ('MP008', '废水排放口B', '处理后排放口', '废水'),
    ]
    
    points = []
    for code, name, location, mtype in point_data:
        point = MonitoringPoint(
            point_code=code,
            point_name=name,
            location=location,
            monitoring_type=mtype,
            equipment_model=f"{mtype}监测仪-{random.choice(['X1', 'X2', 'X3'])}",
            installation_date=random_date(date(2022, 1, 1), date(2024, 6, 30)),
            status='正常'
        )
        points.append(point)
        db.add(point)
    
    db.commit()
    print(f"成功生成 {len(points)} 条监测点位数据")
    return points


def generate_dust_monitoring(db, points):
    """生成粉尘监测数据"""
    dust_points = [p for p in points if p.monitoring_type == '粉尘']
    start_date = date(2025, 1, 1)
    end_date = date(2025, 4, 30)
    
    records = []
    current_date = start_date
    
    while current_date <= end_date:
        for point in dust_points:
            # 每天生成3-6条记录
            for _ in range(random.randint(3, 6)):
                # 随机时间
                hour = random.randint(6, 22)
                minute = random.randint(0, 59)
                record_time = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=hour, minutes=minute)
                
                # 正常范围: PM2.5 10-50, PM10 20-80, TSP 0.05-0.12
                # 偶尔超标
                if random.random() > 0.95:
                    pm25 = random.uniform(50, 150)
                    pm10 = random.uniform(80, 200)
                    tsp = random.uniform(0.15, 0.5)
                    is_over_limit = True
                else:
                    pm25 = random.uniform(10, 50)
                    pm10 = random.uniform(20, 80)
                    tsp = random.uniform(0.05, 0.12)
                    is_over_limit = False
                
                record = DustMonitoring(
                    monitoring_point_id=point.id,
                    record_time=record_time,
                    record_date=current_date,
                    pm25_concentration=pm25,
                    pm10_concentration=pm10,
                    tsp_concentration=tsp,
                    is_over_limit=is_over_limit,
                    threshold_value=0.15
                )
                records.append(record)
                db.add(record)
        
        current_date += timedelta(days=1)
    
    db.commit()
    print(f"成功生成 {len(records)} 条粉尘监测数据")
    return records


def generate_noise_monitoring(db, points):
    """生成噪音监测数据"""
    noise_points = [p for p in points if p.monitoring_type == '噪音']
    start_date = date(2025, 1, 1)
    end_date = date(2025, 4, 30)
    
    records = []
    current_date = start_date
    
    while current_date <= end_date:
        for point in noise_points:
            for _ in range(random.randint(4, 8)):
                hour = random.randint(6, 22)
                minute = random.randint(0, 59)
                record_time = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=hour, minutes=minute)
                
                # 正常范围: 60-80 dB
                # 偶尔超标
                if random.random() > 0.93:
                    db_value = random.uniform(85, 110)
                    is_over_limit = True
                else:
                    db_value = random.uniform(60, 80)
                    is_over_limit = False
                
                record = NoiseMonitoring(
                    monitoring_point_id=point.id,
                    record_time=record_time,
                    record_date=current_date,
                    db_value=db_value,
                    frequency='50-1000Hz',
                    is_over_limit=is_over_limit,
                    threshold_value=85.0
                )
                records.append(record)
                db.add(record)
        
        current_date += timedelta(days=1)
    
    db.commit()
    print(f"成功生成 {len(records)} 条噪音监测数据")
    return records


def generate_wastewater_monitoring(db, points):
    """生成废水监测数据"""
    wastewater_points = [p for p in points if p.monitoring_type == '废水']
    start_date = date(2025, 1, 1)
    end_date = date(2025, 4, 30)
    
    records = []
    current_date = start_date
    
    while current_date <= end_date:
        for point in wastewater_points:
            for _ in range(random.randint(2, 4)):
                hour = random.randint(8, 20)
                minute = random.randint(0, 59)
                record_time = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=hour, minutes=minute)
                
                # 正常范围: PH 6.5-8.5
                # 偶尔超标
                if random.random() > 0.96:
                    ph_value = random.choice([random.uniform(3, 5.5), random.uniform(9.5, 12)])
                    is_over_limit = True
                else:
                    ph_value = random.uniform(6.5, 8.5)
                    is_over_limit = False
                
                record = WastewaterMonitoring(
                    monitoring_point_id=point.id,
                    record_time=record_time,
                    record_date=current_date,
                    ph_value=ph_value,
                    cod_value=random.uniform(30, 100),
                    ss_value=random.uniform(20, 80),
                    ammonia_nitrogen=random.uniform(2, 15),
                    flow_rate=random.uniform(5, 30),
                    is_over_limit=is_over_limit,
                    ph_threshold_min=6.0,
                    ph_threshold_max=9.0
                )
                records.append(record)
                db.add(record)
        
        current_date += timedelta(days=1)
    
    db.commit()
    print(f"成功生成 {len(records)} 条废水监测数据")
    return records


def generate_alarm_records(db, dust_records, noise_records, wastewater_records):
    """生成报警记录数据"""
    # 获取超标记录
    alarms = []
    
    # 粉尘超标报警
    over_dust = [r for r in dust_records if r.is_over_limit]
    for record in over_dust:
        level = '一般'
        if record.tsp_concentration > record.threshold_value * 2:
            level = '紧急'
        elif record.tsp_concentration > record.threshold_value * 1.5:
            level = '重要'
        
        alarm = AlarmRecord(
            alarm_time=record.record_time,
            alarm_type='粉尘超标',
            monitoring_point_id=record.monitoring_point_id,
            dust_monitoring_id=record.id,
            alarm_level=level,
            actual_value=record.tsp_concentration,
            threshold_value=record.threshold_value,
            message=f"粉尘浓度超标，当前值：{record.tsp_concentration}mg/m³",
            is_handled=random.random() > 0.3,
            handled_by='管理员' if random.random() > 0.3 else None,
            handled_time=record.record_time + timedelta(hours=random.randint(1, 24)) if random.random() > 0.3 else None,
            handling_method='已加强通风除尘措施' if random.random() > 0.3 else None
        )
        alarms.append(alarm)
        db.add(alarm)
    
    # 噪音超标报警
    over_noise = [r for r in noise_records if r.is_over_limit]
    for record in over_noise:
        level = '一般'
        if record.db_value > record.threshold_value * 1.3:
            level = '紧急'
        elif record.db_value > record.threshold_value * 1.15:
            level = '重要'
        
        alarm = AlarmRecord(
            alarm_time=record.record_time,
            alarm_type='噪音超标',
            monitoring_point_id=record.monitoring_point_id,
            noise_monitoring_id=record.id,
            alarm_level=level,
            actual_value=record.db_value,
            threshold_value=record.threshold_value,
            message=f"噪音超标，当前值：{record.db_value}dB",
            is_handled=random.random() > 0.4,
            handled_by='管理员' if random.random() > 0.4 else None,
            handled_time=record.record_time + timedelta(hours=random.randint(1, 24)) if random.random() > 0.4 else None,
            handling_method='已采取降噪措施' if random.random() > 0.4 else None
        )
        alarms.append(alarm)
        db.add(alarm)
    
    # 废水超标报警
    over_wastewater = [r for r in wastewater_records if r.is_over_limit]
    for record in over_wastewater:
        level = '一般'
        ph_deviation = abs(record.ph_value - (record.ph_threshold_min + record.ph_threshold_max) / 2)
        if ph_deviation > 3:
            level = '紧急'
        elif ph_deviation > 1.5:
            level = '重要'
        
        alarm = AlarmRecord(
            alarm_time=record.record_time,
            alarm_type='废水超标',
            monitoring_point_id=record.monitoring_point_id,
            wastewater_monitoring_id=record.id,
            alarm_level=level,
            actual_value=record.ph_value,
            threshold_value=(record.ph_threshold_min + record.ph_threshold_max) / 2,
            message=f"废水PH值超标，当前值：{record.ph_value}",
            is_handled=random.random() > 0.2,
            handled_by='管理员' if random.random() > 0.2 else None,
            handled_time=record.record_time + timedelta(hours=random.randint(1, 24)) if random.random() > 0.2 else None,
            handling_method='已调整污水处理参数' if random.random() > 0.2 else None
        )
        alarms.append(alarm)
        db.add(alarm)
    
    db.commit()
    print(f"成功生成 {len(alarms)} 条报警记录数据")
    return alarms


def main():
    """主函数"""
    print("=" * 60)
    print("开始生成测试数据...")
    print("=" * 60)
    
    # 初始化数据库
    init_db()
    
    db = SessionLocal()
    
    try:
        # 生成生产数据
        print("\n[1/7] 生成生产数据...")
        equipments = generate_equipment(db)
        production_records = generate_production_records(db)
        generate_equipment_utilization(db, equipments)
        generate_energy_consumption(db, equipments)
        
        # 生成成本数据
        print("\n[2/7] 生成成本数据...")
        materials = generate_materials(db)
        generate_material_costs(db, materials)
        employees = generate_employees(db)
        generate_labor_costs(db, employees)
        sales_records = generate_sales_records(db)
        generate_profit_analysis(db, sales_records)
        
        # 生成环保监测数据
        print("\n[3/7] 生成环保监测数据...")
        monitoring_points = generate_monitoring_points(db)
        dust_records = generate_dust_monitoring(db, monitoring_points)
        noise_records = generate_noise_monitoring(db, monitoring_points)
        wastewater_records = generate_wastewater_monitoring(db, monitoring_points)
        
        # 生成报警数据
        print("\n[4/7] 生成报警数据...")
        generate_alarm_records(db, dust_records, noise_records, wastewater_records)
        
        print("\n" + "=" * 60)
        print("测试数据生成完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"生成数据时发生错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
