"""
数据库模型包
包含生产数据分析、成本利润分析、环保合规监管三个模块的所有数据库模型
"""
from .production import Equipment, ProductionRecord, EquipmentUtilization, EnergyConsumption
from .cost import Material, MaterialCost, Employee, LaborCost, SalesRecord, ProfitAnalysis
from .environment import MonitoringPoint, DustMonitoring, NoiseMonitoring, WastewaterMonitoring, AlarmRecord

__all__ = [
    # 生产数据分析模型
    "Equipment",
    "ProductionRecord",
    "EquipmentUtilization",
    "EnergyConsumption",
    
    # 成本利润分析模型
    "Material",
    "MaterialCost",
    "Employee",
    "LaborCost",
    "SalesRecord",
    "ProfitAnalysis",
    
    # 环保合规监管模型
    "MonitoringPoint",
    "DustMonitoring",
    "NoiseMonitoring",
    "WastewaterMonitoring",
    "AlarmRecord",
]
