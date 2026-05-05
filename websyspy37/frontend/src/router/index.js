import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/views/Layout.vue'
import Dashboard from '@/views/Dashboard.vue'

// 销售模块
import Customer from '@/views/sales/Customer.vue'
import Order from '@/views/sales/Order.vue'

// 生产模块
import Product from '@/views/production/Product.vue'
import ProductionPlan from '@/views/production/ProductionPlan.vue'
import ProductionTask from '@/views/production/ProductionTask.vue'

// 库存模块
import Warehouse from '@/views/inventory/Warehouse.vue'
import Inventory from '@/views/inventory/Inventory.vue'
import StockIn from '@/views/inventory/StockIn.vue'
import StockOut from '@/views/inventory/StockOut.vue'

// 财务模块
import Account from '@/views/finance/Account.vue'
import Income from '@/views/finance/Income.vue'
import Expense from '@/views/finance/Expense.vue'
import Invoice from '@/views/finance/Invoice.vue'

// 人事模块
import Department from '@/views/hr/Department.vue'
import Position from '@/views/hr/Position.vue'
import Employee from '@/views/hr/Employee.vue'
import Attendance from '@/views/hr/Attendance.vue'
import SalaryRecord from '@/views/hr/SalaryRecord.vue'

// 测试功能
import TestData from '@/views/TestData.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: { title: '首页', icon: 'HomeFilled' }
      },
      // 销售模块
      {
        path: 'sales/customer',
        name: 'Customer',
        component: Customer,
        meta: { title: '客户管理', icon: 'User' }
      },
      {
        path: 'sales/order',
        name: 'Order',
        component: Order,
        meta: { title: '订单管理', icon: 'Document' }
      },
      // 生产模块
      {
        path: 'production/product',
        name: 'Product',
        component: Product,
        meta: { title: '产品管理', icon: 'Goods' }
      },
      {
        path: 'production/plan',
        name: 'ProductionPlan',
        component: ProductionPlan,
        meta: { title: '生产计划', icon: 'Calendar' }
      },
      {
        path: 'production/task',
        name: 'ProductionTask',
        component: ProductionTask,
        meta: { title: '生产任务', icon: 'List' }
      },
      // 库存模块
      {
        path: 'inventory/warehouse',
        name: 'Warehouse',
        component: Warehouse,
        meta: { title: '仓库管理', icon: 'OfficeBuilding' }
      },
      {
        path: 'inventory/inventory',
        name: 'Inventory',
        component: Inventory,
        meta: { title: '库存管理', icon: 'Box' }
      },
      {
        path: 'inventory/stock-in',
        name: 'StockIn',
        component: StockIn,
        meta: { title: '入库管理', icon: 'Download' }
      },
      {
        path: 'inventory/stock-out',
        name: 'StockOut',
        component: StockOut,
        meta: { title: '出库管理', icon: 'Upload' }
      },
      // 财务模块
      {
        path: 'finance/account',
        name: 'Account',
        component: Account,
        meta: { title: '账户管理', icon: 'Wallet' }
      },
      {
        path: 'finance/income',
        name: 'Income',
        component: Income,
        meta: { title: '收入管理', icon: 'Plus' }
      },
      {
        path: 'finance/expense',
        name: 'Expense',
        component: Expense,
        meta: { title: '支出管理', icon: 'Minus' }
      },
      {
        path: 'finance/invoice',
        name: 'Invoice',
        component: Invoice,
        meta: { title: '发票管理', icon: 'Ticket' }
      },
      // 人事模块
      {
        path: 'hr/department',
        name: 'Department',
        component: Department,
        meta: { title: '部门管理', icon: 'OfficeBuilding' }
      },
      {
        path: 'hr/position',
        name: 'Position',
        component: Position,
        meta: { title: '职位管理', icon: 'Medal' }
      },
      {
        path: 'hr/employee',
        name: 'Employee',
        component: Employee,
        meta: { title: '员工管理', icon: 'User' }
      },
      {
        path: 'hr/attendance',
        name: 'Attendance',
        component: Attendance,
        meta: { title: '考勤管理', icon: 'Clock' }
      },
      {
        path: 'hr/salary',
        name: 'SalaryRecord',
        component: SalaryRecord,
        meta: { title: '薪资管理', icon: 'Money' }
      },
      // 测试功能
      {
        path: 'test-data',
        name: 'TestData',
        component: TestData,
        meta: { title: '测试数据', icon: 'DataAnalysis' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
