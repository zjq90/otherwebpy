# 数据库模型模块
# 包含销售、生产、库存、财务、人事等模块的数据模型

from app.models.sales import Customer, Order, OrderItem
from app.models.production import Product, ProductionPlan, ProductionTask
from app.models.inventory import Warehouse, Inventory, StockInOrder, StockInItem, StockOutOrder, StockOutItem
from app.models.finance import Account, Income, Expense, Invoice
from app.models.hr import Department, Position, Employee, Attendance, SalaryRecord

__all__ = [
    # 销售模块
    'Customer', 'Order', 'OrderItem',
    # 生产模块
    'Product', 'ProductionPlan', 'ProductionTask',
    # 库存模块
    'Warehouse', 'Inventory', 'StockInOrder', 'StockInItem', 'StockOutOrder', 'StockOutItem',
    # 财务模块
    'Account', 'Income', 'Expense', 'Invoice',
    # 人事模块
    'Department', 'Position', 'Employee', 'Attendance', 'SalaryRecord'
]
