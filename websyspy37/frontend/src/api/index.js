import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    let message = '请求失败'
    if (error.response) {
      switch (error.response.status) {
        case 400:
          message = error.response.data.detail || '请求参数错误'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = error.response.data.detail || '请求失败'
      }
    }
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// 导出API方法
export default {
  // ==================== 销售模块 ====================
  // 客户管理
  getCustomers: (params) => api.get('/customers/', { params }),
  getCustomer: (id) => api.get(`/customers/${id}`),
  createCustomer: (data) => api.post('/customers/', data),
  updateCustomer: (id, data) => api.put(`/customers/${id}`, data),
  deleteCustomer: (id) => api.delete(`/customers/${id}`),

  // 订单管理
  getOrders: (params) => api.get('/orders/', { params }),
  getOrder: (id) => api.get(`/orders/${id}`),
  createOrder: (data) => api.post('/orders/', data),
  updateOrder: (id, data) => api.put(`/orders/${id}`, data),
  deleteOrder: (id) => api.delete(`/orders/${id}`),

  // ==================== 生产模块 ====================
  // 产品管理
  getProducts: (params) => api.get('/products/', { params }),
  getProduct: (id) => api.get(`/products/${id}`),
  createProduct: (data) => api.post('/products/', data),
  updateProduct: (id, data) => api.put(`/products/${id}`, data),
  deleteProduct: (id) => api.delete(`/products/${id}`),

  // 生产计划
  getProductionPlans: (params) => api.get('/production-plans/', { params }),
  getProductionPlan: (id) => api.get(`/production-plans/${id}`),
  createProductionPlan: (data) => api.post('/production-plans/', data),
  updateProductionPlan: (id, data) => api.put(`/production-plans/${id}`, data),
  deleteProductionPlan: (id) => api.delete(`/production-plans/${id}`),

  // 生产任务
  getProductionTasks: (params) => api.get('/production-tasks/', { params }),
  getProductionTask: (id) => api.get(`/production-tasks/${id}`),
  createProductionTask: (data) => api.post('/production-tasks/', data),
  updateProductionTask: (id, data) => api.put(`/production-tasks/${id}`, data),
  deleteProductionTask: (id) => api.delete(`/production-tasks/${id}`),

  // ==================== 库存模块 ====================
  // 仓库管理
  getWarehouses: (params) => api.get('/warehouses/', { params }),
  getWarehouse: (id) => api.get(`/warehouses/${id}`),
  createWarehouse: (data) => api.post('/warehouses/', data),
  updateWarehouse: (id, data) => api.put(`/warehouses/${id}`, data),
  deleteWarehouse: (id) => api.delete(`/warehouses/${id}`),

  // 库存管理
  getInventories: (params) => api.get('/inventories/', { params }),
  getInventory: (id) => api.get(`/inventories/${id}`),
  createInventory: (data) => api.post('/inventories/', data),
  updateInventory: (id, data) => api.put(`/inventories/${id}`, data),

  // 入库管理
  getStockInOrders: (params) => api.get('/stock-in-orders/', { params }),
  createStockInOrder: (data) => api.post('/stock-in-orders/', data),

  // 出库管理
  getStockOutOrders: (params) => api.get('/stock-out-orders/', { params }),
  createStockOutOrder: (data) => api.post('/stock-out-orders/', data),

  // ==================== 财务模块 ====================
  // 账户管理
  getAccounts: (params) => api.get('/accounts/', { params }),
  getAccount: (id) => api.get(`/accounts/${id}`),
  createAccount: (data) => api.post('/accounts/', data),
  updateAccount: (id, data) => api.put(`/accounts/${id}`, data),
  deleteAccount: (id) => api.delete(`/accounts/${id}`),

  // 收入管理
  getIncomes: (params) => api.get('/incomes/', { params }),
  createIncome: (data) => api.post('/incomes/', data),

  // 支出管理
  getExpenses: (params) => api.get('/expenses/', { params }),
  createExpense: (data) => api.post('/expenses/', data),

  // 发票管理
  getInvoices: (params) => api.get('/invoices/', { params }),
  createInvoice: (data) => api.post('/invoices/', data),

  // ==================== 人事模块 ====================
  // 部门管理
  getDepartments: (params) => api.get('/departments/', { params }),
  getDepartment: (id) => api.get(`/departments/${id}`),
  createDepartment: (data) => api.post('/departments/', data),
  updateDepartment: (id, data) => api.put(`/departments/${id}`, data),
  deleteDepartment: (id) => api.delete(`/departments/${id}`),

  // 职位管理
  getPositions: (params) => api.get('/positions/', { params }),
  getPosition: (id) => api.get(`/positions/${id}`),
  createPosition: (data) => api.post('/positions/', data),
  updatePosition: (id, data) => api.put(`/positions/${id}`, data),
  deletePosition: (id) => api.delete(`/positions/${id}`),

  // 员工管理
  getEmployees: (params) => api.get('/employees/', { params }),
  getEmployee: (id) => api.get(`/employees/${id}`),
  createEmployee: (data) => api.post('/employees/', data),
  updateEmployee: (id, data) => api.put(`/employees/${id}`, data),
  deleteEmployee: (id) => api.delete(`/employees/${id}`),

  // 考勤管理
  getAttendances: (params) => api.get('/attendances/', { params }),
  createAttendance: (data) => api.post('/attendances/', data),

  // 薪资管理
  getSalaryRecords: (params) => api.get('/salary-records/', { params }),
  createSalaryRecord: (data) => api.post('/salary-records/', data),

  // ==================== 测试功能 ====================
  generateTestData: () => api.post('/test-data/generate'),
  getTestDataStatus: () => api.get('/test-data/status'),

  // ==================== 系统信息 ====================
  getHealth: () => api.get('/health')
}
