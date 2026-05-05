"""
成本核算与利润分析模块的API路由
包含原材料管理、原材料成本、员工管理、人工成本、销售记录、利润分析的增删改查和统计分析接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional
from datetime import date, datetime

from ..database import get_db
from ..models import (
    Material, MaterialCost, Employee, LaborCost, SalesRecord, ProfitAnalysis
)
from ..schemas import (
    MaterialCreate, MaterialUpdate, MaterialResponse,
    MaterialCostCreate, MaterialCostUpdate, MaterialCostResponse,
    EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    LaborCostCreate, LaborCostUpdate, LaborCostResponse,
    SalesRecordCreate, SalesRecordUpdate, SalesRecordResponse,
    ProfitAnalysisCreate, ProfitAnalysisResponse,
    DailyMaterialCostStats, MonthlyMaterialCostStats, LaborCostStats, UnitCostAnalysis
)

router = APIRouter(prefix="/api/cost", tags=["成本核算与利润分析"])


# ============ 原材料管理接口 ============

@router.post("/materials/", response_model=MaterialResponse, summary="创建原材料")
def create_material(material: MaterialCreate, db: Session = Depends(get_db)):
    """
    创建原材料信息
    """
    # 检查原材料编号是否已存在
    existing = db.query(Material).filter(Material.material_code == material.material_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="原材料编号已存在")
    
    db_material = Material(**material.model_dump())
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material


@router.get("/materials/", response_model=List[MaterialResponse], summary="获取原材料列表")
def get_materials(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    material_type: Optional[str] = Query(None),
    supplier: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取原材料列表，支持条件筛选
    """
    query = db.query(Material)
    if material_type:
        query = query.filter(Material.material_type == material_type)
    if supplier:
        query = query.filter(Material.supplier.like(f"%{supplier}%"))
    
    materials = query.order_by(Material.id.desc()).offset(skip).limit(limit).all()
    return materials


@router.get("/materials/{material_id}", response_model=MaterialResponse, summary="获取单个原材料")
def get_material(material_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取原材料详情
    """
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="原材料不存在")
    return material


@router.put("/materials/{material_id}", response_model=MaterialResponse, summary="更新原材料")
def update_material(
    material_id: int,
    material: MaterialUpdate,
    db: Session = Depends(get_db)
):
    """
    更新原材料信息
    """
    db_material = db.query(Material).filter(Material.id == material_id).first()
    if not db_material:
        raise HTTPException(status_code=404, detail="原材料不存在")
    
    update_data = material.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_material, key, value)
    
    db.commit()
    db.refresh(db_material)
    return db_material


@router.delete("/materials/{material_id}", summary="删除原材料")
def delete_material(material_id: int, db: Session = Depends(get_db)):
    """
    删除原材料
    """
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="原材料不存在")
    
    db.delete(material)
    db.commit()
    return {"message": "原材料删除成功", "id": material_id}


# ============ 原材料成本接口 ============

@router.post("/material-costs/", response_model=MaterialCostResponse, summary="创建原材料成本记录")
def create_material_cost(material_cost: MaterialCostCreate, db: Session = Depends(get_db)):
    """
    创建原材料成本记录
    自动计算总成本：consumption_quantity * unit_price
    """
    # 检查原材料是否存在
    material = db.query(Material).filter(Material.id == material_cost.material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="原材料不存在")
    
    # 计算总成本
    data = material_cost.model_dump()
    if data.get("unit_price", 0) > 0 and data.get("consumption_quantity", 0) > 0:
        data["total_cost"] = data["consumption_quantity"] * data["unit_price"]
    # 如果没有提供单价，使用原材料当前单价
    elif material.current_price > 0 and data.get("consumption_quantity", 0) > 0:
        data["unit_price"] = material.current_price
        data["total_cost"] = data["consumption_quantity"] * material.current_price
    
    db_material_cost = MaterialCost(**data)
    db.add(db_material_cost)
    db.commit()
    db.refresh(db_material_cost)
    
    result = MaterialCostResponse.model_validate(db_material_cost)
    result.material_name = material.material_name
    result.material_code = material.material_code
    return result


@router.get("/material-costs/", response_model=List[MaterialCostResponse], summary="获取原材料成本列表")
def get_material_costs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    material_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取原材料成本记录列表
    """
    query = db.query(MaterialCost).join(Material)
    if material_id:
        query = query.filter(MaterialCost.material_id == material_id)
    if start_date:
        query = query.filter(MaterialCost.record_date >= start_date)
    if end_date:
        query = query.filter(MaterialCost.record_date <= end_date)
    
    records = query.order_by(MaterialCost.record_date.desc()).offset(skip).limit(limit).all()
    
    results = []
    for record in records:
        result = MaterialCostResponse.model_validate(record)
        if record.material:
            result.material_name = record.material.material_name
            result.material_code = record.material.material_code
        results.append(result)
    return results


@router.put("/material-costs/{cost_id}", response_model=MaterialCostResponse, summary="更新原材料成本记录")
def update_material_cost(
    cost_id: int,
    material_cost: MaterialCostUpdate,
    db: Session = Depends(get_db)
):
    """
    更新原材料成本记录
    """
    db_record = db.query(MaterialCost).filter(MaterialCost.id == cost_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="原材料成本记录不存在")
    
    update_data = material_cost.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)
    
    # 重新计算总成本
    if db_record.unit_price > 0 and db_record.consumption_quantity > 0:
        db_record.total_cost = db_record.consumption_quantity * db_record.unit_price
    
    db.commit()
    db.refresh(db_record)
    
    result = MaterialCostResponse.model_validate(db_record)
    if db_record.material:
        result.material_name = db_record.material.material_name
        result.material_code = db_record.material.material_code
    return result


@router.delete("/material-costs/{cost_id}", summary="删除原材料成本记录")
def delete_material_cost(cost_id: int, db: Session = Depends(get_db)):
    """
    删除原材料成本记录
    """
    record = db.query(MaterialCost).filter(MaterialCost.id == cost_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="原材料成本记录不存在")
    
    db.delete(record)
    db.commit()
    return {"message": "原材料成本记录删除成功", "id": cost_id}


# ============ 员工管理接口 ============

@router.post("/employees/", response_model=EmployeeResponse, summary="创建员工")
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    """
    创建员工信息
    """
    # 检查员工编号是否已存在
    existing = db.query(Employee).filter(Employee.employee_code == employee.employee_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="员工编号已存在")
    
    db_employee = Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


@router.get("/employees/", response_model=List[EmployeeResponse], summary="获取员工列表")
def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    department: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取员工列表，支持条件筛选
    """
    query = db.query(Employee)
    if department:
        query = query.filter(Employee.department == department)
    if status:
        query = query.filter(Employee.status == status)
    
    employees = query.order_by(Employee.id.desc()).offset(skip).limit(limit).all()
    return employees


@router.get("/employees/{employee_id}", response_model=EmployeeResponse, summary="获取单个员工")
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取员工详情
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="员工不存在")
    return employee


@router.put("/employees/{employee_id}", response_model=EmployeeResponse, summary="更新员工")
def update_employee(
    employee_id: int,
    employee: EmployeeUpdate,
    db: Session = Depends(get_db)
):
    """
    更新员工信息
    """
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="员工不存在")
    
    update_data = employee.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_employee, key, value)
    
    db.commit()
    db.refresh(db_employee)
    return db_employee


@router.delete("/employees/{employee_id}", summary="删除员工")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    """
    删除员工
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="员工不存在")
    
    db.delete(employee)
    db.commit()
    return {"message": "员工删除成功", "id": employee_id}


# ============ 人工成本接口 ============

@router.post("/labor-costs/", response_model=LaborCostResponse, summary="创建人工成本记录")
def create_labor_cost(labor_cost: LaborCostCreate, db: Session = Depends(get_db)):
    """
    创建人工成本记录
    自动计算总成本：working_hours * hourly_rate + overtime_hours * hourly_rate * overtime_rate
    """
    # 检查员工是否存在
    employee = db.query(Employee).filter(Employee.id == labor_cost.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="员工不存在")
    
    # 计算人工成本
    data = labor_cost.model_dump()
    # 如果没有提供小时工资，使用员工小时工资
    if data.get("hourly_rate", 0) <= 0 and employee.hourly_rate > 0:
        data["hourly_rate"] = employee.hourly_rate
    
    # 计算总成本
    normal_cost = data.get("working_hours", 0) * data.get("hourly_rate", 0)
    overtime_cost = data.get("overtime_hours", 0) * data.get("hourly_rate", 0) * data.get("overtime_rate", 1.5)
    data["total_labor_cost"] = normal_cost + overtime_cost
    
    db_labor_cost = LaborCost(**data)
    db.add(db_labor_cost)
    db.commit()
    db.refresh(db_labor_cost)
    
    result = LaborCostResponse.model_validate(db_labor_cost)
    result.employee_name = employee.employee_name
    result.department = employee.department
    return result


@router.get("/labor-costs/", response_model=List[LaborCostResponse], summary="获取人工成本列表")
def get_labor_costs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    employee_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取人工成本记录列表
    """
    query = db.query(LaborCost).join(Employee)
    if employee_id:
        query = query.filter(LaborCost.employee_id == employee_id)
    if start_date:
        query = query.filter(LaborCost.record_date >= start_date)
    if end_date:
        query = query.filter(LaborCost.record_date <= end_date)
    
    records = query.order_by(LaborCost.record_date.desc()).offset(skip).limit(limit).all()
    
    results = []
    for record in records:
        result = LaborCostResponse.model_validate(record)
        if record.employee:
            result.employee_name = record.employee.employee_name
            result.department = record.employee.department
        results.append(result)
    return results


@router.put("/labor-costs/{cost_id}", response_model=LaborCostResponse, summary="更新人工成本记录")
def update_labor_cost(
    cost_id: int,
    labor_cost: LaborCostUpdate,
    db: Session = Depends(get_db)
):
    """
    更新人工成本记录
    """
    db_record = db.query(LaborCost).filter(LaborCost.id == cost_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="人工成本记录不存在")
    
    update_data = labor_cost.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)
    
    # 重新计算总成本
    normal_cost = db_record.working_hours * db_record.hourly_rate
    overtime_cost = db_record.overtime_hours * db_record.hourly_rate * db_record.overtime_rate
    db_record.total_labor_cost = normal_cost + overtime_cost
    
    db.commit()
    db.refresh(db_record)
    
    result = LaborCostResponse.model_validate(db_record)
    if db_record.employee:
        result.employee_name = db_record.employee.employee_name
        result.department = db_record.employee.department
    return result


@router.delete("/labor-costs/{cost_id}", summary="删除人工成本记录")
def delete_labor_cost(cost_id: int, db: Session = Depends(get_db)):
    """
    删除人工成本记录
    """
    record = db.query(LaborCost).filter(LaborCost.id == cost_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="人工成本记录不存在")
    
    db.delete(record)
    db.commit()
    return {"message": "人工成本记录删除成功", "id": cost_id}


# ============ 销售记录接口 ============

@router.post("/sales/", response_model=SalesRecordResponse, summary="创建销售记录")
def create_sales_record(sales: SalesRecordCreate, db: Session = Depends(get_db)):
    """
    创建销售记录
    自动计算销售总额：quantity * unit_price
    """
    data = sales.model_dump()
    # 自动生成销售单号
    if not data.get("sale_code"):
        today = datetime.now().strftime("%Y%m%d")
        # 查询今日销售单数量
        count = db.query(func.count(SalesRecord.id)).filter(
            extract('year', SalesRecord.sale_date) == datetime.now().year,
            extract('month', SalesRecord.sale_date) == datetime.now().month,
            extract('day', SalesRecord.sale_date) == datetime.now().day
        ).scalar()
        data["sale_code"] = f"XS{today}{str(count + 1).zfill(4)}"
    
    # 计算销售总额
    if data.get("quantity", 0) > 0 and data.get("unit_price", 0) > 0:
        data["total_amount"] = data["quantity"] * data["unit_price"]
    
    db_sales = SalesRecord(**data)
    db.add(db_sales)
    db.commit()
    db.refresh(db_sales)
    return db_sales


@router.get("/sales/", response_model=List[SalesRecordResponse], summary="获取销售记录列表")
def get_sales_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    concrete_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取销售记录列表，支持条件筛选
    """
    query = db.query(SalesRecord)
    if start_date:
        query = query.filter(SalesRecord.sale_date >= start_date)
    if end_date:
        query = query.filter(SalesRecord.sale_date <= end_date)
    if concrete_type:
        query = query.filter(SalesRecord.concrete_type == concrete_type)
    if status:
        query = query.filter(SalesRecord.status == status)
    
    records = query.order_by(SalesRecord.sale_date.desc()).offset(skip).limit(limit).all()
    return records


@router.get("/sales/{sales_id}", response_model=SalesRecordResponse, summary="获取单个销售记录")
def get_sales_record(sales_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取销售记录详情
    """
    record = db.query(SalesRecord).filter(SalesRecord.id == sales_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="销售记录不存在")
    return record


@router.put("/sales/{sales_id}", response_model=SalesRecordResponse, summary="更新销售记录")
def update_sales_record(
    sales_id: int,
    sales: SalesRecordUpdate,
    db: Session = Depends(get_db)
):
    """
    更新销售记录
    """
    db_record = db.query(SalesRecord).filter(SalesRecord.id == sales_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="销售记录不存在")
    
    update_data = sales.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)
    
    # 重新计算销售总额
    if db_record.quantity > 0 and db_record.unit_price > 0:
        db_record.total_amount = db_record.quantity * db_record.unit_price
    
    db.commit()
    db.refresh(db_record)
    return db_record


@router.delete("/sales/{sales_id}", summary="删除销售记录")
def delete_sales_record(sales_id: int, db: Session = Depends(get_db)):
    """
    删除销售记录
    """
    record = db.query(SalesRecord).filter(SalesRecord.id == sales_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="销售记录不存在")
    
    db.delete(record)
    db.commit()
    return {"message": "销售记录删除成功", "id": sales_id}


# ============ 利润分析接口 ============

@router.post("/profit-analysis/", response_model=ProfitAnalysisResponse, summary="创建利润分析")
def create_profit_analysis(analysis: ProfitAnalysisCreate, db: Session = Depends(get_db)):
    """
    创建利润分析记录
    自动计算毛利和毛利率
    """
    # 检查销售记录是否存在
    sales_record = db.query(SalesRecord).filter(SalesRecord.id == analysis.sales_record_id).first()
    if not sales_record:
        raise HTTPException(status_code=404, detail="销售记录不存在")
    
    data = analysis.model_dump()
    
    # 计算单方总成本
    data["total_cost_per_cubic"] = (
        data.get("material_cost_per_cubic", 0) +
        data.get("labor_cost_per_cubic", 0) +
        data.get("energy_cost_per_cubic", 0) +
        data.get("other_cost_per_cubic", 0)
    )
    
    # 如果没有提供销售价格，使用销售记录中的价格
    if data.get("sales_price_per_cubic", 0) <= 0 and sales_record.unit_price > 0:
        data["sales_price_per_cubic"] = sales_record.unit_price
    
    # 计算单方毛利和毛利率
    if data.get("sales_price_per_cubic", 0) > 0:
        data["gross_profit_per_cubic"] = data["sales_price_per_cubic"] - data["total_cost_per_cubic"]
        data["gross_profit_margin"] = (data["gross_profit_per_cubic"] / data["sales_price_per_cubic"]) * 100
    
    # 计算汇总数据
    quantity = data.get("total_quantity", 0) if data.get("total_quantity", 0) > 0 else sales_record.quantity
    data["total_quantity"] = quantity
    data["total_cost"] = quantity * data["total_cost_per_cubic"]
    data["total_sales"] = quantity * data["sales_price_per_cubic"]
    data["total_gross_profit"] = quantity * data["gross_profit_per_cubic"]
    
    db_analysis = ProfitAnalysis(**data)
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    
    result = ProfitAnalysisResponse.model_validate(db_analysis)
    result.customer_name = sales_record.customer_name
    return result


@router.get("/profit-analysis/", response_model=List[ProfitAnalysisResponse], summary="获取利润分析列表")
def get_profit_analyses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    concrete_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取利润分析记录列表
    """
    query = db.query(ProfitAnalysis).join(SalesRecord)
    if start_date:
        query = query.filter(ProfitAnalysis.analysis_date >= start_date)
    if end_date:
        query = query.filter(ProfitAnalysis.analysis_date <= end_date)
    if concrete_type:
        query = query.filter(ProfitAnalysis.concrete_type == concrete_type)
    
    records = query.order_by(ProfitAnalysis.analysis_date.desc()).offset(skip).limit(limit).all()
    
    results = []
    for record in records:
        result = ProfitAnalysisResponse.model_validate(record)
        if record.sales_record:
            result.customer_name = record.sales_record.customer_name
        results.append(result)
    return results


# ============ 统计分析接口 ============

@router.get("/stats/material-daily/", response_model=List[DailyMaterialCostStats], summary="日原材料成本统计")
def get_daily_material_cost_stats(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """
    日原材料成本统计
    按日期和原材料类型统计消耗数量和成本
    """
    query = db.query(
        MaterialCost.record_date,
        Material.material_type,
        func.sum(MaterialCost.consumption_quantity).label('total_quantity'),
        func.sum(MaterialCost.total_cost).label('total_cost'),
        Material.unit
    ).join(Material)
    
    if start_date:
        query = query.filter(MaterialCost.record_date >= start_date)
    if end_date:
        query = query.filter(MaterialCost.record_date <= end_date)
    
    results = query.group_by(MaterialCost.record_date, Material.material_type).order_by(MaterialCost.record_date).all()
    
    stats = []
    for result in results:
        stats.append(DailyMaterialCostStats(
            record_date=result.record_date,
            material_type=result.material_type,
            total_quantity=result.total_quantity or 0,
            total_cost=result.total_cost or 0,
            unit=result.unit or "吨"
        ))
    return stats


@router.get("/stats/material-monthly/", response_model=List[MonthlyMaterialCostStats], summary="月原材料成本统计")
def get_monthly_material_cost_stats(
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    月原材料成本统计
    按月和原材料类型统计
    """
    query = db.query(
        extract('year', MaterialCost.record_date).label('year'),
        extract('month', MaterialCost.record_date).label('month'),
        Material.material_type,
        func.sum(MaterialCost.consumption_quantity).label('total_quantity'),
        func.sum(MaterialCost.total_cost).label('total_cost')
    ).join(Material)
    
    if year:
        query = query.filter(extract('year', MaterialCost.record_date) == year)
    
    results = query.group_by('year', 'month', Material.material_type).order_by('year', 'month').all()
    
    stats = []
    for result in results:
        stats.append(MonthlyMaterialCostStats(
            year=int(result.year),
            month=int(result.month),
            material_type=result.material_type,
            total_quantity=result.total_quantity or 0,
            total_cost=result.total_cost or 0
        ))
    return stats


@router.get("/stats/labor/", response_model=List[LaborCostStats], summary="人工成本统计")
def get_labor_cost_stats(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """
    人工成本统计
    按日期和部门统计工时和成本
    """
    query = db.query(
        LaborCost.record_date,
        Employee.department,
        func.sum(LaborCost.working_hours).label('total_working_hours'),
        func.sum(LaborCost.overtime_hours).label('total_overtime_hours'),
        func.sum(LaborCost.total_labor_cost).label('total_labor_cost')
    ).join(Employee)
    
    if start_date:
        query = query.filter(LaborCost.record_date >= start_date)
    if end_date:
        query = query.filter(LaborCost.record_date <= end_date)
    
    results = query.group_by(LaborCost.record_date, Employee.department).order_by(LaborCost.record_date).all()
    
    stats = []
    for result in results:
        stats.append(LaborCostStats(
            record_date=result.record_date,
            department=result.department or "未知部门",
            total_working_hours=result.total_working_hours or 0,
            total_overtime_hours=result.total_overtime_hours or 0,
            total_labor_cost=result.total_labor_cost or 0
        ))
    return stats


@router.get("/stats/unit-cost/", response_model=List[UnitCostAnalysis], summary="单方成本分析")
def get_unit_cost_analysis(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """
    单方成本分析
    按混凝土强度等级统计平均单方成本、销售价格和毛利
    """
    query = db.query(
        ProfitAnalysis.concrete_type,
        func.avg(ProfitAnalysis.material_cost_per_cubic).label('avg_material_cost'),
        func.avg(ProfitAnalysis.labor_cost_per_cubic).label('avg_labor_cost'),
        func.avg(ProfitAnalysis.energy_cost_per_cubic).label('avg_energy_cost'),
        func.avg(ProfitAnalysis.total_cost_per_cubic).label('avg_total_cost'),
        func.avg(ProfitAnalysis.sales_price_per_cubic).label('avg_sales_price'),
        func.avg(ProfitAnalysis.gross_profit_per_cubic).label('avg_gross_profit'),
        func.avg(ProfitAnalysis.gross_profit_margin).label('avg_margin'),
        func.sum(ProfitAnalysis.total_quantity).label('total_quantity')
    )
    
    if start_date:
        query = query.filter(ProfitAnalysis.analysis_date >= start_date)
    if end_date:
        query = query.filter(ProfitAnalysis.analysis_date <= end_date)
    
    results = query.group_by(ProfitAnalysis.concrete_type).all()
    
    stats = []
    for result in results:
        stats.append(UnitCostAnalysis(
            concrete_type=result.concrete_type or "未知型号",
            average_material_cost=round(result.avg_material_cost or 0, 2),
            average_labor_cost=round(result.avg_labor_cost or 0, 2),
            average_energy_cost=round(result.avg_energy_cost or 0, 2),
            average_total_cost=round(result.avg_total_cost or 0, 2),
            average_sales_price=round(result.avg_sales_price or 0, 2),
            average_gross_profit=round(result.avg_gross_profit or 0, 2),
            average_margin=round(result.avg_margin or 0, 2),
            total_quantity=result.total_quantity or 0
        ))
    return stats
