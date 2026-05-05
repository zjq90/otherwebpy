"""
Pydantic数据模型包
包含所有API请求和响应的数据验证模型
"""
from .production import (
    EquipmentBase, EquipmentCreate, EquipmentUpdate, EquipmentResponse,
    ProductionRecordBase, ProductionRecordCreate, ProductionRecordUpdate, ProductionRecordResponse,
    EquipmentUtilizationBase, EquipmentUtilizationCreate, EquipmentUtilizationUpdate, EquipmentUtilizationResponse,
    EnergyConsumptionBase, EnergyConsumptionCreate, EnergyConsumptionUpdate, EnergyConsumptionResponse,
    DailyProductionStats, MonthlyProductionStats, EquipmentUtilizationStats, EnergyConsumptionStats
)
from .cost import (
    MaterialBase, MaterialCreate, MaterialUpdate, MaterialResponse,
    MaterialCostBase, MaterialCostCreate, MaterialCostUpdate, MaterialCostResponse,
    EmployeeBase, EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    LaborCostBase, LaborCostCreate, LaborCostUpdate, LaborCostResponse,
    SalesRecordBase, SalesRecordCreate, SalesRecordUpdate, SalesRecordResponse,
    ProfitAnalysisBase, ProfitAnalysisCreate, ProfitAnalysisResponse,
    DailyMaterialCostStats, MonthlyMaterialCostStats, LaborCostStats, UnitCostAnalysis
)
from .environment import (
    MonitoringPointBase, MonitoringPointCreate, MonitoringPointUpdate, MonitoringPointResponse,
    DustMonitoringBase, DustMonitoringCreate, DustMonitoringUpdate, DustMonitoringResponse,
    NoiseMonitoringBase, NoiseMonitoringCreate, NoiseMonitoringUpdate, NoiseMonitoringResponse,
    WastewaterMonitoringBase, WastewaterMonitoringCreate, WastewaterMonitoringUpdate, WastewaterMonitoringResponse,
    AlarmRecordBase, AlarmRecordCreate, AlarmRecordUpdate, AlarmRecordResponse,
    DailyDustStats, DailyNoiseStats, DailyWastewaterStats, AlarmStats
)

__all__ = [
    # 生产数据分析模型
    "EquipmentBase", "EquipmentCreate", "EquipmentUpdate", "EquipmentResponse",
    "ProductionRecordBase", "ProductionRecordCreate", "ProductionRecordUpdate", "ProductionRecordResponse",
    "EquipmentUtilizationBase", "EquipmentUtilizationCreate", "EquipmentUtilizationUpdate", "EquipmentUtilizationResponse",
    "EnergyConsumptionBase", "EnergyConsumptionCreate", "EnergyConsumptionUpdate", "EnergyConsumptionResponse",
    "DailyProductionStats", "MonthlyProductionStats", "EquipmentUtilizationStats", "EnergyConsumptionStats",
    
    # 成本利润分析模型
    "MaterialBase", "MaterialCreate", "MaterialUpdate", "MaterialResponse",
    "MaterialCostBase", "MaterialCostCreate", "MaterialCostUpdate", "MaterialCostResponse",
    "EmployeeBase", "EmployeeCreate", "EmployeeUpdate", "EmployeeResponse",
    "LaborCostBase", "LaborCostCreate", "LaborCostUpdate", "LaborCostResponse",
    "SalesRecordBase", "SalesRecordCreate", "SalesRecordUpdate", "SalesRecordResponse",
    "ProfitAnalysisBase", "ProfitAnalysisCreate", "ProfitAnalysisResponse",
    "DailyMaterialCostStats", "MonthlyMaterialCostStats", "LaborCostStats", "UnitCostAnalysis",
    
    # 环保合规监管模型
    "MonitoringPointBase", "MonitoringPointCreate", "MonitoringPointUpdate", "MonitoringPointResponse",
    "DustMonitoringBase", "DustMonitoringCreate", "DustMonitoringUpdate", "DustMonitoringResponse",
    "NoiseMonitoringBase", "NoiseMonitoringCreate", "NoiseMonitoringUpdate", "NoiseMonitoringResponse",
    "WastewaterMonitoringBase", "WastewaterMonitoringCreate", "WastewaterMonitoringUpdate", "WastewaterMonitoringResponse",
    "AlarmRecordBase", "AlarmRecordCreate", "AlarmRecordUpdate", "AlarmRecordResponse",
    "DailyDustStats", "DailyNoiseStats", "DailyWastewaterStats", "AlarmStats",
]
