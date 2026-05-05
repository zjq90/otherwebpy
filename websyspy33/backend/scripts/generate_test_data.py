# -*- coding: utf-8 -*-
"""
测试数据生成脚本
================
用于生成测试数据，辅助功能测试
运行方式：python -m scripts.generate_test_data
"""

import asyncio
import json
from datetime import date, datetime, timedelta
from random import randint, uniform, choice, choices

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import async_session_maker, init_db
from app.models import (
    Supplier, RawMaterial, MaterialInspection, MixDesign,
    ProductionBatch, ProductionRecord, TestBlock, StrengthTest,
    QualityReport, SupplierRating, SettlementOrder
)


def random_date(start_date: date, end_date: date) -> date:
    """
    生成指定范围内的随机日期
    """
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = randint(0, days_between)
    return start_date + timedelta(days=random_days)


async def generate_suppliers(session, count: int = 10):
    """
    生成供应商测试数据
    """
    supplier_names = [
        "山水水泥有限公司", "海螺水泥集团", "华新水泥股份", "冀东水泥",
        "南方水泥有限公司", "中联水泥集团", "金隅集团", "台泥水泥",
        "红狮控股集团", "华润水泥", "葛洲坝水泥", "亚洲水泥",
        "天瑞水泥集团", "四川双马", "宁夏建材", "祁连山水泥"
    ]
    
    supplier_types = ["原材料供应商", "设备供应商", "服务商"]
    
    suppliers = []
    for i in range(count):
        name = choice(supplier_names)
        if name in [s.name for s in suppliers]:
            name = f"{name} (分公司{i+1})"
        
        supplier = Supplier(
            name=name,
            code=f"SUP{datetime.now().strftime('%Y%m%d')}{str(i+1).zfill(4)}",
            contact_person=f"张{['明', '华', '强', '伟', '军', '勇', '刚', '平'][i%8]}",
            phone=f"138{randint(1000, 9999)}{randint(1000, 9999)}",
            address=f"{'北京', '上海', '广州', '深圳', '杭州', '南京', '武汉', '成都'}[i%8]市经济开发区",
            supplier_type=choice(supplier_types),
            rating=round(uniform(60.0, 98.0), 1),
            rating_level=choices(["A级", "B级", "C级"], weights=[0.3, 0.5, 0.2])[0],
            status=True
        )
        session.add(supplier)
        suppliers.append(supplier)
    
    await session.commit()
    print(f"已生成 {len(suppliers)} 条供应商数据")
    return suppliers


async def generate_raw_materials(session, suppliers, count: int = 20):
    """
    生成原材料测试数据
    """
    material_types = [
        "水泥", "骨料", "外加剂", "粉煤灰", "矿渣粉", "硅灰"
    ]
    
    material_specs = {
        "水泥": ["P.O 42.5", "P.O 52.5", "P.S 32.5", "P.C 32.5"],
        "骨料": ["碎石 5-20mm", "碎石 20-40mm", "河砂", "机制砂"],
        "外加剂": ["聚羧酸减水剂", "萘系减水剂", "早强剂", "缓凝剂", "引气剂"],
        "粉煤灰": ["Ⅰ级粉煤灰", "Ⅱ级粉煤灰"],
        "矿渣粉": ["S95矿渣粉", "S105矿渣粉"],
        "硅灰": ["活性硅灰"]
    }
    
    materials = []
    for i in range(count):
        material_type = choice(material_types)
        supplier = choice(suppliers)
        
        material = RawMaterial(
            name=f"{material_type}材料",
            code=f"MAT{datetime.now().strftime('%Y%m%d')}{str(i+1).zfill(4)}",
            material_type=material_type,
            specification=choice(material_specs[material_type]),
            unit=choice(["吨", "kg", "m³"]),
            supplier_id=supplier.id,
            description=f"{material_type}原材料，规格{choice(material_specs[material_type])}",
            status=True
        )
        session.add(material)
        materials.append(material)
    
    await session.commit()
    print(f"已生成 {len(materials)} 条原材料数据")
    return materials


async def generate_material_inspections(session, suppliers, materials, count: int = 30):
    """
    生成原材料检验测试数据
    """
    inspectors = ["李工", "王工", "张工", "刘工", "陈工", "杨工"]
    
    inspections = []
    today = date.today()
    start_date = today - timedelta(days=90)
    
    for i in range(count):
        material = choice(materials)
        supplier = [s for s in suppliers if s.id == material.supplier_id][0] if material.supplier_id else choice(suppliers)
        
        sample_date = random_date(start_date, today)
        inspection_date = sample_date + timedelta(days=randint(1, 3))
        
        # 随机生成检验结果
        is_qualified = choices([True, False], weights=[0.85, 0.15])[0]
        result = "合格" if is_qualified else "不合格"
        
        # 检验项目JSON
        inspection_items = json.dumps(["强度", "细度", "安定性", "凝结时间", "烧失量"], ensure_ascii=False)
        
        # 检测数据JSON
        test_data = json.dumps({
            "强度": round(uniform(40.0, 55.0), 1),
            "细度": round(uniform(5.0, 15.0), 1),
            "安定性": "合格",
            "初凝时间": randint(120, 240),
            "终凝时间": randint(300, 480),
            "烧失量": round(uniform(2.0, 5.0), 1)
        }, ensure_ascii=False)
        
        # 标准值JSON
        standard_value = json.dumps({
            "强度": "≥42.5MPa",
            "细度": "≤10%",
            "安定性": "必须合格",
            "初凝时间": "≥45min",
            "终凝时间": "≤600min",
            "烧失量": "≤5.0%"
        }, ensure_ascii=False)
        
        inspection = MaterialInspection(
            inspection_no=f"INSP{datetime.now().strftime('%Y%m%d')}{str(i+1).zfill(5)}",
            material_id=material.id,
            supplier_id=supplier.id,
            batch_no=f"BATCH{randint(10000, 99999)}",
            sample_no=f"SAMPLE{randint(1000, 9999)}",
            sample_date=sample_date,
            inspector=choice(inspectors),
            inspection_date=inspection_date,
            inspection_items=inspection_items,
            test_data=test_data,
            standard_value=standard_value,
            result=result,
            conclusion=f"该批次原材料{result}",
            is_qualified=is_qualified,
            lab_temperature=round(uniform(20.0, 25.0), 1),
            lab_humidity=round(uniform(50.0, 70.0), 1),
            status=choices(["草稿", "已提交", "已审核"], weights=[0.2, 0.3, 0.5])[0]
        )
        session.add(inspection)
        inspections.append(inspection)
    
    await session.commit()
    print(f"已生成 {len(inspections)} 条原材料检验数据")
    return inspections


async def generate_mix_designs(session, count: int = 8):
    """
    生成配比设计测试数据
    """
    strength_grades = ["C15", "C20", "C25", "C30", "C35", "C40", "C45", "C50"]
    
    designs = []
    today = date.today()
    designers = ["设计员A", "设计员B", "设计员C", "设计员D"]
    
    for i, grade in enumerate(strength_grades[:count]):
        # 根据强度等级计算配合比
        water_cement_ratio = 0.7 - int(grade[1:]) * 0.005
        cement_content = 250 + int(grade[1:]) * 3
        
        mix_design = MixDesign(
            design_no=f"MD{grade}{datetime.now().strftime('%Y%m%d')}{str(i+1).zfill(3)}",
            mix_name=f"{grade}普通混凝土配合比",
            strength_grade=grade,
            design_age=28,
            slump=uniform(100.0, 180.0),
            cement_content=cement_content,
            sand_content=750 + uniform(-50, 50),
            stone_content=1100 + uniform(-100, 100),
            water_content=175 + uniform(-20, 20),
            admixture_content=cement_content * 0.015,
            fly_ash_content=cement_content * 0.2 if int(grade[1:]) >= 30 else 0,
            water_cement_ratio=round(water_cement_ratio, 3),
            sand_ratio=round(40.0 + uniform(-5, 5), 1),
            designed_by=choice(designers),
            design_date=random_date(today - timedelta(days=365), today),
            status=choices(["草稿", "已审批", "已启用"], weights=[0.1, 0.3, 0.6])[0],
            is_active=choice([True, False])
        )
        session.add(mix_design)
        designs.append(mix_design)
    
    await session.commit()
    print(f"已生成 {len(designs)} 条配比设计数据")
    return designs


async def generate_production_batches(session, mix_designs, count: int = 15):
    """
    生成生产批次测试数据
    """
    projects = [
        "市民中心建设项目", "地铁一号线工程", "商业综合体项目", "住宅小区一期",
        "工业园区厂房建设", "桥梁工程", "高速公路项目", "水库大坝工程",
        "体育中心场馆", "医院新建项目", "学校教学楼", "会展中心"
    ]
    
    construction_sites = [
        "主体结构", "基础工程", "地下室", "地面层", "二层梁板", "三层梁板",
        "屋面工程", "楼梯间", "电梯井", "设备基础"
    ]
    
    operators = ["操作员甲", "操作员乙", "操作员丙", "操作员丁"]
    truck_nos = [f"皖A{randint(10000, 99999)}" for _ in range(10)]
    
    batches = []
    today = date.today()
    
    for i in range(count):
        mix_design = choice(mix_designs)
        project = choice(projects)
        site = choice(construction_sites)
        
        planned_volume = round(uniform(50.0, 500.0), 1)
        actual_volume = round(planned_volume * uniform(0.95, 1.05), 1)
        
        status = choice(["待生产", "生产中", "已完成"])
        
        batch = ProductionBatch(
            batch_no=f"PB{datetime.now().strftime('%Y%m%d')}{str(i+1).zfill(5)}",
            mix_design_id=mix_design.id,
            project_name=project,
            construction_site=site,
            strength_grade=mix_design.strength_grade,
            planned_volume=planned_volume,
            actual_volume=actual_volume if status == "已完成" else None,
            truck_no=choice(truck_nos),
            driver=f"司机{randint(1, 50)}",
            operator=choice(operators),
            status=status
        )
        session.add(batch)
        batches.append(batch)
    
    await session.commit()
    print(f"已生成 {len(batches)} 条生产批次数据")
    return batches


async def generate_production_records(session, batches, records_per_batch: int = 5):
    """
    生成生产记录测试数据
    """
    operators = ["操作员甲", "操作员乙", "操作员丙", "操作员丁"]
    
    records = []
    batch_no = 0
    
    for batch in batches:
        mix_design = next((md for md in mix_designs if md.id == batch.mix_design_id), None)
        if not mix_design:
            continue
        
        for i in range(records_per_batch):
            batch_no += 1
            
            # 计算实际投料（与设计值有小偏差）
            deviation = uniform(-0.05, 0.05)
            
            actual_cement = round(mix_design.cement_content * (1 + deviation), 1)
            actual_sand = round(mix_design.sand_content * (1 + uniform(-0.03, 0.03)), 1)
            actual_stone = round(mix_design.stone_content * (1 + uniform(-0.03, 0.03)), 1)
            actual_water = round(mix_design.water_content * (1 + uniform(-0.02, 0.04)), 1)
            
            # 计算实际水胶比
            total_binder = actual_cement + (mix_design.fly_ash_content or 0)
            actual_water_cement_ratio = round(actual_water / total_binder, 3) if total_binder > 0 else mix_design.water_cement_ratio
            
            # 计算偏差率
            deviation_rate = round((actual_water_cement_ratio - mix_design.water_cement_ratio) / mix_design.water_cement_ratio * 100, 2)
            
            # 判断是否正常（偏差率超过±2%视为异常）
            is_normal = abs(deviation_rate) <= 2.0
            
            # 投料顺序JSON
            feeding_sequence = json.dumps([
                "1. 投入砂石料",
                "2. 投入胶凝材料",
                "3. 投入外加剂",
                "4. 投入拌合水",
                "5. 搅拌"
            ], ensure_ascii=False)
            
            record = ProductionRecord(
                batch_id=batch.id,
                record_no=f"PR{datetime.now().strftime('%Y%m%d')}{str(batch_no).zfill(6)}",
                mix_no=i + 1,
                mixing_time=round(uniform(90.0, 150.0), 1),
                feeding_sequence=feeding_sequence,
                actual_cement=actual_cement,
                actual_sand=actual_sand,
                actual_stone=actual_stone,
                actual_water=actual_water,
                actual_admixture=round(mix_design.admixture_content * (1 + uniform(-0.05, 0.05)), 2) if mix_design.admixture_content else None,
                actual_fly_ash=round(mix_design.fly_ash_content * (1 + uniform(-0.05, 0.05)), 1) if mix_design.fly_ash_content else None,
                actual_water_cement_ratio=actual_water_cement_ratio,
                design_water_cement_ratio=mix_design.water_cement_ratio,
                deviation_rate=deviation_rate,
                slump_actual=round(uniform(100.0, 200.0), 1),
                temperature=round(uniform(15.0, 30.0), 1),
                is_normal=is_normal,
                anomaly_reason=None if is_normal else "水胶比偏差超过允许范围",
                operator=choice(operators)
            )
            session.add(record)
            records.append(record)
    
    await session.commit()
    print(f"已生成 {len(records)} 条生产记录数据")
    return records


async def generate_test_blocks(session, batches, blocks_per_batch: int = 2):
    """
    生成试块测试数据
    """
    samplers = ["取样员A", "取样员B", "取样员C", "取样员D"]
    curing_conditions = ["标准养护", "同条件养护", "自然养护"]
    sample_locations = ["出料口", "浇筑点", "搅拌车"]
    
    blocks = []
    block_no = 0
    
    for batch in batches:
        for i in range(blocks_per_batch):
            block_no += 1
            
            sample_date = random_date(date.today() - timedelta(days=60), date.today())
            casting_date = sample_date
            test_age = choice([7, 14, 28, 56])
            planned_test_date = casting_date + timedelta(days=test_age)
            
            test_block = TestBlock(
                block_no=f"TB{datetime.now().strftime('%Y%m%d')}{str(block_no).zfill(5)}",
                batch_id=batch.id,
                sample_date=sample_date,
                casting_date=casting_date,
                test_age=test_age,
                planned_test_date=planned_test_date,
                block_size="150x150x150",
                quantity=3,
                curing_condition=choice(curing_conditions),
                sample_location=choice(sample_locations),
                sampler=choice(samplers),
                status=choice(["待试验", "已试验", "已作废"])
            )
            session.add(test_block)
            blocks.append(test_block)
    
    await session.commit()
    print(f"已生成 {len(blocks)} 条试块数据")
    return blocks


async def generate_strength_tests(session, test_blocks, count: int = 20):
    """
    生成强度检测测试数据
    """
    testers = ["试验员甲", "试验员乙", "试验员丙", "试验员丁"]
    
    tests = []
    test_no = 0
    
    for block in test_blocks[:count]:
        test_no += 1
        
        # 随机生成强度数据
        # 假设设计强度为C30，即30MPa
        design_strength = 30.0
        strength_factor = uniform(0.95, 1.30)
        
        # 生成三个试块的荷载
        load_1 = round(design_strength * 22.5 * strength_factor * uniform(0.95, 1.05), 1)
        load_2 = round(design_strength * 22.5 * strength_factor * uniform(0.95, 1.05), 1)
        load_3 = round(design_strength * 22.5 * strength_factor * uniform(0.95, 1.05), 1)
        
        # 计算强度：荷载 / 受压面积 (150x150=22500mm²=225cm²)
        strength_1 = round(load_1 / 22.5, 1)
        strength_2 = round(load_2 / 22.5, 1)
        strength_3 = round(load_3 / 22.5, 1)
        
        # 计算平均强度
        avg_strength = round((strength_1 + strength_2 + strength_3) / 3, 1)
        
        # 计算强度偏差
        strength_deviation = round(abs(avg_strength - design_strength) / design_strength * 100, 2)
        
        # 计算强度比
        strength_ratio = round(avg_strength / design_strength * 100, 1)
        
        # 判断是否合格
        is_qualified = strength_ratio >= 100.0
        result = "合格" if is_qualified else "不合格"
        
        test_date = block.planned_test_date + timedelta(days=randint(-3, 3))
        
        strength_test = StrengthTest(
            test_no=f"ST{datetime.now().strftime('%Y%m%d')}{str(test_no).zfill(5)}",
            block_id=block.id,
            test_date=test_date,
            actual_age=block.test_age + randint(-1, 3),
            tester=choice(testers),
            lab_temperature=round(uniform(20.0, 25.0), 1),
            lab_humidity=round(uniform(50.0, 70.0), 1),
            load_1=load_1,
            load_2=load_2,
            load_3=load_3,
            strength_1=strength_1,
            strength_2=strength_2,
            strength_3=strength_3,
            avg_strength=avg_strength,
            strength_deviation=strength_deviation,
            design_strength=design_strength,
            strength_ratio=strength_ratio,
            result=result,
            is_qualified=is_qualified,
            conclusion=f"该组试块{result}，强度代表值为{avg_strength}MPa",
            status=choices(["草稿", "已提交", "已审核"], weights=[0.2, 0.3, 0.5])[0]
        )
        session.add(strength_test)
        tests.append(strength_test)
        
        # 更新试块状态
        block.status = "已试验"
    
    await session.commit()
    print(f"已生成 {len(tests)} 条强度检测数据")
    return tests


async def generate_quality_reports(session, batches, count: int = 10):
    """
    生成质量报告测试数据
    """
    report_types = ["出厂合格证", "质量追溯报告", "强度检测报告"]
    generated_by = ["技术员A", "技术员B", "技术员C", "质量管理员"]
    
    reports = []
    report_no = 0
    
    for batch in batches[:count]:
        report_no += 1
        
        report_date = random_date(date.today() - timedelta(days=30), date.today())
        
        # 简单判定
        is_qualified = choice([True, False])
        overall_result = "合格" if is_qualified else "不合格"
        
        quality_report = QualityReport(
            report_no=f"QR{datetime.now().strftime('%Y%m%d')}{str(report_no).zfill(5)}",
            batch_id=batch.id,
            report_type=choice(report_types),
            report_date=report_date,
            generated_by=choice(generated_by),
            summary=f"生产批次{batch.batch_no}质量报告摘要",
            conclusion=f"本批次混凝土{overall_result}",
            overall_result=overall_result,
            is_qualified=is_qualified,
            status=choices(["草稿", "已发布", "已作废"], weights=[0.2, 0.7, 0.1])[0]
        )
        session.add(quality_report)
        reports.append(quality_report)
    
    await session.commit()
    print(f"已生成 {len(reports)} 条质量报告数据")
    return reports


async def generate_supplier_ratings(session, suppliers, count: int = 15):
    """
    生成供应商评级测试数据
    """
    rating_periods = ["2024年第一季度", "2024年第二季度", "2024年第三季度", "2024年第四季度"]
    raters = ["评级员A", "评级员B", "评级员C", "质量经理"]
    
    ratings = []
    rating_no = 0
    
    for supplier in suppliers:
        rating_no += 1
        
        # 计算评分
        quality_score = round(uniform(25.0, 40.0), 1)
        delivery_score = round(uniform(20.0, 30.0), 1)
        price_score = round(uniform(15.0, 20.0), 1)
        service_score = round(uniform(7.0, 10.0), 1)
        
        total_score = round(quality_score + delivery_score + price_score + service_score, 1)
        
        # 确定评级等级
        if total_score >= 90:
            rating_level = "A级"
        elif total_score >= 75:
            rating_level = "B级"
        elif total_score >= 60:
            rating_level = "C级"
        else:
            rating_level = "D级"
        
        supplier_rating = SupplierRating(
            rating_no=f"SR{datetime.now().strftime('%Y%m%d')}{str(rating_no).zfill(5)}",
            supplier_id=supplier.id,
            rating_period=choice(rating_periods),
            rating_date=random_date(date.today() - timedelta(days=180), date.today()),
            quality_score=quality_score,
            delivery_score=delivery_score,
            price_score=price_score,
            service_score=service_score,
            total_score=total_score,
            rating_level=rating_level,
            inspection_count=randint(5, 50),
            pass_rate=round(uniform(85.0, 100.0), 1),
            delivery_count=randint(10, 100),
            on_time_rate=round(uniform(90.0, 100.0), 1),
            rater=choice(raters),
            status=choices(["草稿", "已生效"], weights=[0.3, 0.7])[0]
        )
        session.add(supplier_rating)
        ratings.append(supplier_rating)
        
        # 更新供应商评级信息
        supplier.rating = total_score
        supplier.rating_level = rating_level
    
    await session.commit()
    print(f"已生成 {len(ratings)} 条供应商评级数据")
    return ratings


async def generate_settlement_orders(session, suppliers, count: int = 10):
    """
    生成结算单测试数据
    """
    settlement_periods = ["2024年1月", "2024年2月", "2024年3月", "2024年4月", "2024年5月", "2024年6月"]
    created_by = ["财务员A", "财务员B", "财务员C", "会计"]
    
    orders = []
    order_no = 0
    
    for supplier in suppliers[:count]:
        order_no += 1
        
        total_quantity = round(uniform(100.0, 1000.0), 2)
        total_amount = round(total_quantity * uniform(400.0, 600.0), 2)
        discount_amount = round(total_amount * uniform(0.02, 0.08), 2)
        final_amount = round(total_amount - discount_amount, 2)
        
        # 材料汇总JSON
        material_summary = json.dumps([
            {
                "material_type": "水泥",
                "quantity": round(total_quantity * 0.4, 2),
                "unit_price": round(uniform(500.0, 700.0), 2),
                "amount": round(total_quantity * 0.4 * uniform(500.0, 700.0), 2)
            },
            {
                "material_type": "骨料",
                "quantity": round(total_quantity * 0.5, 2),
                "unit_price": round(uniform(100.0, 200.0), 2),
                "amount": round(total_quantity * 0.5 * uniform(100.0, 200.0), 2)
            }
        ], ensure_ascii=False)
        
        start_date = random_date(date.today() - timedelta(days=180), date.today())
        end_date = start_date + timedelta(days=30)
        
        settlement_order = SettlementOrder(
            settlement_no=f"SO{datetime.now().strftime('%Y%m%d')}{str(order_no).zfill(5)}",
            supplier_id=supplier.id,
            settlement_period=choice(settlement_periods),
            start_date=start_date,
            end_date=end_date,
            material_summary=material_summary,
            total_quantity=total_quantity,
            total_amount=total_amount,
            discount_amount=discount_amount,
            final_amount=final_amount,
            status=choices(["待确认", "已确认", "已付款"], weights=[0.3, 0.4, 0.3])[0],
            created_by=choice(created_by),
            created_date=start_date + timedelta(days=2),
            remark=f"自动生成的结算单，共{randint(5, 20)}批货物"
        )
        session.add(settlement_order)
        orders.append(settlement_order)
    
    await session.commit()
    print(f"已生成 {len(orders)} 条结算单数据")
    return orders


async def main():
    """
    主函数：生成所有测试数据
    """
    print("=" * 60)
    print("开始生成测试数据...")
    print("=" * 60)
    
    # 初始化数据库
    await init_db()
    
    async with async_session_maker() as session:
        try:
            # 1. 生成供应商数据
            print("\n1. 生成供应商数据...")
            suppliers = await generate_suppliers(session, count=10)
            
            # 2. 生成原材料数据
            print("\n2. 生成原材料数据...")
            materials = await generate_raw_materials(session, suppliers, count=20)
            
            # 3. 生成原材料检验数据
            print("\n3. 生成原材料检验数据...")
            inspections = await generate_material_inspections(session, suppliers, materials, count=30)
            
            # 4. 生成配比设计数据
            print("\n4. 生成配比设计数据...")
            mix_designs = await generate_mix_designs(session, count=8)
            
            # 5. 生成生产批次数据
            print("\n5. 生成生产批次数据...")
            batches = await generate_production_batches(session, mix_designs, count=15)
            
            # 6. 生成生产记录数据
            print("\n6. 生成生产记录数据...")
            records = await generate_production_records(session, batches, records_per_batch=5)
            
            # 7. 生成试块数据
            print("\n7. 生成试块数据...")
            test_blocks = await generate_test_blocks(session, batches, blocks_per_batch=2)
            
            # 8. 生成强度检测数据
            print("\n8. 生成强度检测数据...")
            strength_tests = await generate_strength_tests(session, test_blocks, count=20)
            
            # 9. 生成质量报告数据
            print("\n9. 生成质量报告数据...")
            reports = await generate_quality_reports(session, batches, count=10)
            
            # 10. 生成供应商评级数据
            print("\n10. 生成供应商评级数据...")
            ratings = await generate_supplier_ratings(session, suppliers, count=15)
            
            # 11. 生成结算单数据
            print("\n11. 生成结算单数据...")
            settlements = await generate_settlement_orders(session, suppliers, count=10)
            
            print("\n" + "=" * 60)
            print("测试数据生成完成！")
            print("=" * 60)
            print(f"\n总计生成数据统计：")
            print(f"- 供应商: {len(suppliers)} 条")
            print(f"- 原材料: {len(materials)} 条")
            print(f"- 原材料检验: {len(inspections)} 条")
            print(f"- 配比设计: {len(mix_designs)} 条")
            print(f"- 生产批次: {len(batches)} 条")
            print(f"- 生产记录: {len(records)} 条")
            print(f"- 试块: {len(test_blocks)} 条")
            print(f"- 强度检测: {len(strength_tests)} 条")
            print(f"- 质量报告: {len(reports)} 条")
            print(f"- 供应商评级: {len(ratings)} 条")
            print(f"- 结算单: {len(settlements)} 条")
            
        except Exception as e:
            print(f"生成测试数据时出错: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
