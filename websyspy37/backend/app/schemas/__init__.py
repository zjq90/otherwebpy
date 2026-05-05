# Pydantic schemas模块
# 用于API的数据验证和序列化

from app.schemas.sales import (
    CustomerBase, CustomerCreate, CustomerUpdate, CustomerResponse,
    OrderBase, OrderCreate, OrderUpdate, OrderResponse,
    OrderItemBase, OrderItemCreate, OrderItemUpdate, OrderItemResponse
)
from app.schemas.production import (
    ProductBase, ProductCreate, ProductUpdate, ProductResponse,
    ProductionPlanBase, ProductionPlanCreate, ProductionPlanUpdate, ProductionPlanResponse,
    ProductionTaskBase, ProductionTaskCreate, ProductionTaskUpdate, ProductionTaskResponse
)
from app.schemas.inventory import (
    WarehouseBase, WarehouseCreate, WarehouseUpdate, WarehouseResponse,
    InventoryBase, InventoryCreate, InventoryUpdate, InventoryResponse,
    StockInOrderBase, StockInOrderCreate, StockInOrderUpdate, StockInOrderResponse,
    StockOutOrderBase, StockOutOrderCreate, StockOutOrderUpdate, StockOutOrderResponse
)
from app.schemas.finance import (
    AccountBase, AccountCreate, AccountUpdate, AccountResponse,
    IncomeBase, IncomeCreate, IncomeUpdate, IncomeResponse,
    ExpenseBase, ExpenseCreate, ExpenseUpdate, ExpenseResponse,
    InvoiceBase, InvoiceCreate, InvoiceUpdate, InvoiceResponse
)
from app.schemas.hr import (
    DepartmentBase, DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    PositionBase, PositionCreate, PositionUpdate, PositionResponse,
    EmployeeBase, EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    AttendanceBase, AttendanceCreate, AttendanceUpdate, AttendanceResponse,
    SalaryRecordBase, SalaryRecordCreate, SalaryRecordUpdate, SalaryRecordResponse
)

__all__ = [
    # 销售模块
    'CustomerBase', 'CustomerCreate', 'CustomerUpdate', 'CustomerResponse',
    'OrderBase', 'OrderCreate', 'OrderUpdate', 'OrderResponse',
    'OrderItemBase', 'OrderItemCreate', 'OrderItemUpdate', 'OrderItemResponse',
    # 生产模块
    'ProductBase', 'ProductCreate', 'ProductUpdate', 'ProductResponse',
    'ProductionPlanBase', 'ProductionPlanCreate', 'ProductionPlanUpdate', 'ProductionPlanResponse',
    'ProductionTaskBase', 'ProductionTaskCreate', 'ProductionTaskUpdate', 'ProductionTaskResponse',
    # 库存模块
    'WarehouseBase', 'WarehouseCreate', 'WarehouseUpdate', 'WarehouseResponse',
    'InventoryBase', 'InventoryCreate', 'InventoryUpdate', 'InventoryResponse',
    'StockInOrderBase', 'StockInOrderCreate', 'StockInOrderUpdate', 'StockInOrderResponse',
    'StockOutOrderBase', 'StockOutOrderCreate', 'StockOutOrderUpdate', 'StockOutOrderResponse',
    # 财务模块
    'AccountBase', 'AccountCreate', 'AccountUpdate', 'AccountResponse',
    'IncomeBase', 'IncomeCreate', 'IncomeUpdate', 'IncomeResponse',
    'ExpenseBase', 'ExpenseCreate', 'ExpenseUpdate', 'ExpenseResponse',
    'InvoiceBase', 'InvoiceCreate', 'InvoiceUpdate', 'InvoiceResponse',
    # 人事模块
    'DepartmentBase', 'DepartmentCreate', 'DepartmentUpdate', 'DepartmentResponse',
    'PositionBase', 'PositionCreate', 'PositionUpdate', 'PositionResponse',
    'EmployeeBase', 'EmployeeCreate', 'EmployeeUpdate', 'EmployeeResponse',
    'AttendanceBase', 'AttendanceCreate', 'AttendanceUpdate', 'AttendanceResponse',
    'SalaryRecordBase', 'SalaryRecordCreate', 'SalaryRecordUpdate', 'SalaryRecordResponse'
]
