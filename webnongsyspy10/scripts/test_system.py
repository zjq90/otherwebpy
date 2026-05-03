"""
智慧农业管理系统功能测试脚本
用于测试系统的各项功能，包括数据库操作和API接口
"""
import sys
import os
from datetime import date, datetime, timedelta
from decimal import Decimal
import random

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


class TestResult:
    """测试结果类"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = 0
        self.results = []
    
    def add_success(self, test_name):
        self.passed += 1
        self.results.append(f"[✓] {test_name}")
        print(f"[✓] {test_name}")
    
    def add_failure(self, test_name, error):
        self.failed += 1
        self.results.append(f"[✗] {test_name}: {error}")
        print(f"[✗] {test_name}: {error}")
    
    def add_error(self, test_name, error):
        self.errors += 1
        self.results.append(f"[!] {test_name}: {error}")
        print(f"[!] {test_name}: {error}")
    
    def print_summary(self):
        print("\n" + "=" * 60)
        print("测试结果汇总")
        print("=" * 60)
        print(f"通过: {self.passed}")
        print(f"失败: {self.failed}")
        print(f"错误: {self.errors}")
        print(f"总计: {self.passed + self.failed + self.errors}")
        print("=" * 60)


def test_database_connection(result: TestResult):
    """测试数据库连接"""
    print("\n【测试1】数据库连接测试")
    print("-" * 40)
    
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        result.add_success("数据库连接正常")
        db.close()
    except Exception as e:
        result.add_failure("数据库连接失败", str(e))


def test_planting_plan_crud(result: TestResult):
    """测试种植计划CRUD操作"""
    print("\n【测试2】种植计划CRUD测试")
    print("-" * 40)
    
    db = SessionLocal()
    try:
        plan = PlantingPlan(
            plan_code="PPTEST0001",
            plan_name="测试水稻种植计划",
            plan_type=PlanTypeEnum.ANNUAL,
            year=2024,
            crop_type="水稻",
            crop_variety="杂交稻",
            planting_area=Decimal("20.5"),
            sowing_date=date(2024, 5, 15),
            expected_harvest_date=date(2024, 9, 20),
            target_yield_per_mu=Decimal("600.0"),
            location="东区一号田",
            status=PlanStatusEnum.PLANNED,
            progress=Decimal("0.0"),
            responsible_person="测试员",
            created_by="测试系统",
            remarks="这是一条测试计划"
        )
        
        plan.calculate_target_total_yield()
        db.add(plan)
        db.commit()
        db.refresh(plan)
        result.add_success(f"创建种植计划成功 - ID: {plan.id}")
        
        retrieved = db.query(PlantingPlan).filter(PlantingPlan.id == plan.id).first()
        assert retrieved.plan_code == "PPTEST0001"
        assert retrieved.crop_type == "水稻"
        result.add_success("查询种植计划成功")
        
        retrieved.status = PlanStatusEnum.IN_PROGRESS
        retrieved.progress = Decimal("25.5")
        db.commit()
        db.refresh(retrieved)
        assert retrieved.status == PlanStatusEnum.IN_PROGRESS
        assert retrieved.progress == Decimal("25.5")
        result.add_success("更新种植计划成功")
        
        plan_id = retrieved.id
        db.delete(retrieved)
        db.commit()
        deleted = db.query(PlantingPlan).filter(PlantingPlan.id == plan_id).first()
        assert deleted is None
        result.add_success("删除种植计划成功")
        
    except Exception as e:
        result.add_error("种植计划CRUD测试出错", str(e))
        db.rollback()
    finally:
        db.close()


def test_farm_operation_crud(result: TestResult):
    """测试农事作业记录CRUD操作"""
    print("\n【测试3】农事作业记录CRUD测试")
    print("-" * 40)
    
    db = SessionLocal()
    try:
        test_plan = PlantingPlan(
            plan_code="PPFO0001",
            plan_name="农事作业测试计划",
            plan_type=PlanTypeEnum.ANNUAL,
            year=2024,
            crop_type="小麦",
            crop_variety="冬小麦",
            planting_area=Decimal("15.0"),
            sowing_date=date(2024, 10, 1),
            expected_harvest_date=date(2025, 6, 1),
            target_yield_per_mu=Decimal("450.0"),
            location="西区二号田",
            status=PlanStatusEnum.IN_PROGRESS,
            progress=Decimal("30.0"),
            responsible_person="测试员",
            created_by="测试系统"
        )
        db.add(test_plan)
        db.commit()
        db.refresh(test_plan)
        
        operation = FarmOperation(
            planting_plan_id=test_plan.id,
            operation_code="FOTEST0001",
            operation_type=OperationTypeEnum.SOWING,
            operation_name="小麦播种作业",
            actual_date=date(2024, 10, 5),
            crop_type="小麦",
            plot_location="西区二号田",
            operation_area=Decimal("15.0"),
            operator="李四",
            operator_contact="13812345678",
            is_app_entry=1,
            entry_device="iPhone 14",
            quantity=Decimal("8.5"),
            quantity_unit="公斤",
            operation_method="机械条播",
            tools_used="播种机",
            weather_condition="晴天",
            status=OperationStatusEnum.COMPLETED,
            effect_assessment="作业效果良好",
            created_by="测试系统"
        )
        
        db.add(operation)
        db.commit()
        db.refresh(operation)
        result.add_success(f"创建农事作业记录成功 - ID: {operation.id}")
        
        retrieved = db.query(FarmOperation).filter(FarmOperation.id == operation.id).first()
        assert retrieved.operation_type == OperationTypeEnum.SOWING
        assert retrieved.operator == "李四"
        result.add_success("查询农事作业记录成功")
        
        retrieved.status = OperationStatusEnum.COMPLETED
        retrieved.effect_assessment = "作业效果优秀，播种均匀"
        db.commit()
        db.refresh(retrieved)
        assert retrieved.effect_assessment == "作业效果优秀，播种均匀"
        result.add_success("更新农事作业记录成功")
        
        op_id = retrieved.id
        db.delete(retrieved)
        db.delete(test_plan)
        db.commit()
        deleted = db.query(FarmOperation).filter(FarmOperation.id == op_id).first()
        assert deleted is None
        result.add_success("删除农事作业记录成功")
        
    except Exception as e:
        result.add_error("农事作业记录CRUD测试出错", str(e))
        db.rollback()
    finally:
        db.close()


def test_fertilization_irrigation_crud(result: TestResult):
    """测试精准施肥与灌溉CRUD操作"""
    print("\n【测试4】精准施肥与灌溉CRUD测试")
    print("-" * 40)
    
    db = SessionLocal()
    try:
        test_plan = PlantingPlan(
            plan_code="PPFI0001",
            plan_name="施肥灌溉测试计划",
            plan_type=PlanTypeEnum.ANNUAL,
            year=2024,
            crop_type="玉米",
            crop_variety="甜玉米",
            planting_area=Decimal("25.0"),
            sowing_date=date(2024, 6, 1),
            expected_harvest_date=date(2024, 10, 1),
            target_yield_per_mu=Decimal("700.0"),
            location="南区试验田",
            status=PlanStatusEnum.IN_PROGRESS,
            progress=Decimal("50.0"),
            responsible_person="测试员",
            created_by="测试系统"
        )
        db.add(test_plan)
        db.commit()
        db.refresh(test_plan)
        
        record = FertilizationIrrigation(
            planting_plan_id=test_plan.id,
            record_code="FITEST0001",
            record_type="水肥一体化",
            record_date=date(2024, 7, 15),
            crop_type="玉米",
            growth_stage="拔节期",
            plot_location="南区试验田",
            operation_area=Decimal("25.0"),
            
            soil_test_date=date(2024, 7, 10),
            soil_ph=Decimal("6.5"),
            organic_matter=Decimal("25.0"),
            total_nitrogen=Decimal("1.8"),
            available_phosphorus=Decimal("30.0"),
            available_potassium=Decimal("120.0"),
            soil_moisture=Decimal("20.0"),
            
            planned_fertilizer_type=FertilizerTypeEnum.NITROGEN,
            planned_fertilizer_name="尿素",
            planned_fertilizer_amount_per_mu=Decimal("25.0"),
            planned_fertilization_method="随水冲施",
            
            actual_fertilizer_type=FertilizerTypeEnum.NITROGEN,
            actual_fertilizer_name="尿素",
            actual_fertilizer_amount_per_mu=Decimal("24.5"),
            actual_fertilization_method="随水冲施",
            fertilization_date=date(2024, 7, 15),
            
            planned_irrigation_type=IrrigationTypeEnum.DRIP,
            planned_water_source=WaterSourceEnum.GROUND_WATER,
            planned_irrigation_amount_per_mu=Decimal("50.0"),
            planned_irrigation_duration=Decimal("4.0"),
            
            actual_irrigation_type=IrrigationTypeEnum.DRIP,
            actual_water_source=WaterSourceEnum.GROUND_WATER,
            actual_irrigation_amount_per_mu=Decimal("48.0"),
            actual_irrigation_duration=Decimal("3.8"),
            irrigation_date=date(2024, 7, 15),
            
            is_fertigation=1,
            fertigation_ratio="1:150",
            
            operator="王五",
            equipment_code="EQ-123",
            weather_condition="多云",
            created_by="测试系统"
        )
        
        record.calculate_totals()
        record.calculate_deviations()
        
        db.add(record)
        db.commit()
        db.refresh(record)
        result.add_success(f"创建施肥灌溉记录成功 - ID: {record.id}")
        
        retrieved = db.query(FertilizationIrrigation).filter(FertilizationIrrigation.id == record.id).first()
        assert retrieved.record_type == "水肥一体化"
        assert retrieved.soil_ph == Decimal("6.5")
        result.add_success("查询施肥灌溉记录成功")
        
        assert retrieved.fertilizer_deviation is not None
        assert retrieved.irrigation_deviation is not None
        result.add_success(f"用量偏差计算成功 - 施肥偏差: {retrieved.fertilizer_deviation}%, 灌溉偏差: {retrieved.irrigation_deviation}%")
        
        retrieved.remarks = "更新后的测试备注"
        db.commit()
        result.add_success("更新施肥灌溉记录成功")
        
        rec_id = retrieved.id
        db.delete(retrieved)
        db.delete(test_plan)
        db.commit()
        deleted = db.query(FertilizationIrrigation).filter(FertilizationIrrigation.id == rec_id).first()
        assert deleted is None
        result.add_success("删除施肥灌溉记录成功")
        
    except Exception as e:
        result.add_error("施肥灌溉记录CRUD测试出错", str(e))
        db.rollback()
    finally:
        db.close()


def test_pest_disease_control_crud(result: TestResult):
    """测试病虫害防治管理CRUD操作"""
    print("\n【测试5】病虫害防治管理CRUD测试")
    print("-" * 40)
    
    db = SessionLocal()
    try:
        test_plan = PlantingPlan(
            plan_code="PPPD0001",
            plan_name="病虫害防治测试计划",
            plan_type=PlanTypeEnum.ANNUAL,
            year=2024,
            crop_type="水稻",
            crop_variety="籼稻",
            planting_area=Decimal("30.0"),
            sowing_date=date(2024, 5, 1),
            expected_harvest_date=date(2024, 9, 15),
            target_yield_per_mu=Decimal("550.0"),
            location="北区示范田",
            status=PlanStatusEnum.IN_PROGRESS,
            progress=Decimal("60.0"),
            responsible_person="测试员",
            created_by="测试系统"
        )
        db.add(test_plan)
        db.commit()
        db.refresh(test_plan)
        
        record = PestDiseaseControl(
            planting_plan_id=test_plan.id,
            record_code="PDTEST0001",
            discovery_date=date(2024, 7, 20),
            pest_disease_type=PestDiseaseTypeEnum.PEST,
            pest_disease_name="稻飞虱",
            scientific_name="Nilaparvata lugens",
            crop_type="水稻",
            growth_stage="孕穗期",
            plot_location="北区示范田",
            affected_area=Decimal("8.0"),
            severity=SeverityLevelEnum.MODERATE,
            incidence_rate=Decimal("15.0"),
            symptoms_description="叶片出现黄化，茎秆有虫粪，发现大量稻飞虱若虫。",
            control_method=ControlMethodEnum.CHEMICAL,
            treatment_date=date(2024, 7, 22),
            operator="赵六",
            treatment_status=TreatmentStatusEnum.COMPLETED,
            weather_condition="晴天无风",
            
            pesticide_name="吡虫啉",
            pesticide_type="杀虫剂",
            registration_number="PD20101234",
            manufacturer="某农药厂",
            dosage_per_mu=Decimal("0.05"),
            dosage_unit="公斤",
            dilution_ratio=1000,
            application_method="喷雾",
            equipment_used="背负式喷雾器",
            safety_interval_days=7,
            
            assessment_date=date(2024, 7, 29),
            control_effect=Decimal("85.0"),
            effect_description="防治效果良好，稻飞虱数量显著减少。",
            
            created_by="测试系统"
        )
        
        record.calculate_allowed_use_date()
        record.update_warning_status()
        
        db.add(record)
        db.commit()
        db.refresh(record)
        result.add_success(f"创建病虫害防治记录成功 - ID: {record.id}")
        
        retrieved = db.query(PestDiseaseControl).filter(PestDiseaseControl.id == record.id).first()
        assert retrieved.pest_disease_name == "稻飞虱"
        assert retrieved.severity == SeverityLevelEnum.MODERATE
        result.add_success("查询病虫害防治记录成功")
        
        assert retrieved.allowed_use_date is not None
        result.add_success(f"安全间隔期计算成功 - 允许采收日期: {retrieved.allowed_use_date}")
        
        assert retrieved.is_highly_toxic_warning in [0, 1]
        result.add_success(f"高毒农药预警检查完成 - 预警状态: {'是' if retrieved.is_highly_toxic_warning else '否'}")
        
        retrieved.remarks = "更新后的病虫害防治测试备注"
        db.commit()
        result.add_success("更新病虫害防治记录成功")
        
        rec_id = retrieved.id
        db.delete(retrieved)
        db.delete(test_plan)
        db.commit()
        deleted = db.query(PestDiseaseControl).filter(PestDiseaseControl.id == rec_id).first()
        assert deleted is None
        result.add_success("删除病虫害防治记录成功")
        
    except Exception as e:
        result.add_error("病虫害防治记录CRUD测试出错", str(e))
        db.rollback()
    finally:
        db.close()


def test_highly_toxic_pesticide_warning(result: TestResult):
    """测试高毒农药预警功能"""
    print("\n【测试6】高毒农药预警功能测试")
    print("-" * 40)
    
    db = SessionLocal()
    try:
        test_plan = PlantingPlan(
            plan_code="PPHT0001",
            plan_name="高毒农药预警测试计划",
            plan_type=PlanTypeEnum.ANNUAL,
            year=2024,
            crop_type="水稻",
            crop_variety="杂交稻",
            planting_area=Decimal("10.0"),
            sowing_date=date(2024, 5, 1),
            expected_harvest_date=date(2024, 9, 1),
            target_yield_per_mu=Decimal("600.0"),
            location="测试田",
            status=PlanStatusEnum.IN_PROGRESS,
            responsible_person="测试员",
            created_by="测试系统"
        )
        db.add(test_plan)
        db.commit()
        db.refresh(test_plan)
        
        high_toxic_record = PestDiseaseControl(
            planting_plan_id=test_plan.id,
            record_code="PDHT0001",
            discovery_date=date(2024, 7, 1),
            pest_disease_type=PestDiseaseTypeEnum.PEST,
            pest_disease_name="稻纵卷叶螟",
            crop_type="水稻",
            plot_location="测试田",
            affected_area=Decimal("5.0"),
            severity=SeverityLevelEnum.SEVERE,
            control_method=ControlMethodEnum.CHEMICAL,
            treatment_date=date(2024, 7, 2),
            operator="测试员",
            treatment_status=TreatmentStatusEnum.COMPLETED,
            
            pesticide_name="甲胺磷乳油",
            pesticide_type="杀虫剂",
            dosage_per_mu=Decimal("0.1"),
            dosage_unit="公斤",
            safety_interval_days=60,
            
            created_by="测试系统"
        )
        
        high_toxic_record.update_warning_status()
        db.add(high_toxic_record)
        db.commit()
        db.refresh(high_toxic_record)
        
        assert high_toxic_record.is_highly_toxic_warning == 1
        result.add_success("高毒农药预警触发成功 - 检测到'甲胺磷乳油'")
        
        normal_record = PestDiseaseControl(
            planting_plan_id=test_plan.id,
            record_code="PDHT0002",
            discovery_date=date(2024, 7, 5),
            pest_disease_type=PestDiseaseTypeEnum.PEST,
            pest_disease_name="蚜虫",
            crop_type="水稻",
            plot_location="测试田",
            affected_area=Decimal("2.0"),
            severity=SeverityLevelEnum.MILD,
            control_method=ControlMethodEnum.CHEMICAL,
            treatment_date=date(2024, 7, 6),
            operator="测试员",
            treatment_status=TreatmentStatusEnum.COMPLETED,
            
            pesticide_name="吡虫啉",
            pesticide_type="杀虫剂",
            dosage_per_mu=Decimal("0.03"),
            dosage_unit="公斤",
            safety_interval_days=7,
            
            created_by="测试系统"
        )
        
        normal_record.update_warning_status()
        db.add(normal_record)
        db.commit()
        db.refresh(normal_record)
        
        assert normal_record.is_highly_toxic_warning == 0
        result.add_success("普通农药不触发预警 - '吡虫啉'检测正常")
        
        warning_count = db.query(PestDiseaseControl).filter(
            PestDiseaseControl.is_highly_toxic_warning == 1
        ).count()
        result.add_success(f"高毒预警记录查询成功 - 共 {warning_count} 条预警记录")
        
        db.query(PestDiseaseControl).filter(PestDiseaseControl.planting_plan_id == test_plan.id).delete()
        db.delete(test_plan)
        db.commit()
        result.add_success("清理测试数据成功")
        
    except Exception as e:
        result.add_error("高毒农药预警功能测试出错", str(e))
        db.rollback()
    finally:
        db.close()


def test_statistics_functions(result: TestResult):
    """测试统计功能"""
    print("\n【测试7】统计功能测试")
    print("-" * 40)
    
    db = SessionLocal()
    try:
        plan_count = db.query(PlantingPlan).count()
        result.add_success(f"种植计划总数统计: {plan_count} 条")
        
        in_progress_count = db.query(PlantingPlan).filter(
            PlantingPlan.status == PlanStatusEnum.IN_PROGRESS
        ).count()
        result.add_success(f"进行中计划统计: {in_progress_count} 条")
        
        operation_count = db.query(FarmOperation).count()
        result.add_success(f"农事作业记录总数统计: {operation_count} 条")
        
        fi_count = db.query(FertilizationIrrigation).count()
        result.add_success(f"施肥灌溉记录总数统计: {fi_count} 条")
        
        pd_count = db.query(PestDiseaseControl).count()
        result.add_success(f"病虫害防治记录总数统计: {pd_count} 条")
        
        high_toxic_count = db.query(PestDiseaseControl).filter(
            PestDiseaseControl.is_highly_toxic_warning == 1
        ).count()
        result.add_success(f"高毒农药预警记录统计: {high_toxic_count} 条")
        
    except Exception as e:
        result.add_error("统计功能测试出错", str(e))
    finally:
        db.close()


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("智慧农业管理系统功能测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    result = TestResult()
    
    test_database_connection(result)
    test_planting_plan_crud(result)
    test_farm_operation_crud(result)
    test_fertilization_irrigation_crud(result)
    test_pest_disease_control_crud(result)
    test_highly_toxic_pesticide_warning(result)
    test_statistics_functions(result)
    
    result.print_summary()
    
    if result.failed == 0 and result.errors == 0:
        print("\n[✓] 所有测试通过！系统功能正常。")
        return True
    else:
        print("\n[✗] 部分测试失败，请检查系统功能。")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="智慧农业管理系统功能测试")
    parser.add_argument("--init-db", action="store_true", help="先初始化数据库并生成测试数据")
    
    args = parser.parse_args()
    
    if args.init_db:
        print("正在初始化数据库...")
        from scripts.init_database import init_database
        init_database(generate_test_data=True)
    
    run_all_tests()
