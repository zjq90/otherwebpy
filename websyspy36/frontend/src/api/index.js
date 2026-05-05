import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default api

export const productionApi = {
  getEquipment: (params = {}) => api.get('/production/equipment/', { params }),
  getEquipmentById: (id) => api.get(`/production/equipment/${id}`),
  createEquipment: (data) => api.post('/production/equipment/', data),
  updateEquipment: (id, data) => api.put(`/production/equipment/${id}`, data),
  deleteEquipment: (id) => api.delete(`/production/equipment/${id}`),
  
  getProductionRecords: (params = {}) => api.get('/production/records/', { params }),
  getProductionRecordById: (id) => api.get(`/production/records/${id}`),
  createProductionRecord: (data) => api.post('/production/records/', data),
  updateProductionRecord: (id, data) => api.put(`/production/records/${id}`, data),
  deleteProductionRecord: (id) => api.delete(`/production/records/${id}`),
  
  getUtilization: (params = {}) => api.get('/production/utilization/', { params }),
  createUtilization: (data) => api.post('/production/utilization/', data),
  updateUtilization: (id, data) => api.put(`/production/utilization/${id}`, data),
  deleteUtilization: (id) => api.delete(`/production/utilization/${id}`),
  
  getEnergy: (params = {}) => api.get('/production/energy/', { params }),
  createEnergy: (data) => api.post('/production/energy/', data),
  updateEnergy: (id, data) => api.put(`/production/energy/${id}`, data),
  deleteEnergy: (id) => api.delete(`/production/energy/${id}`),
  
  getDailyStats: (params = {}) => api.get('/production/stats/daily/', { params }),
  getMonthlyStats: (params = {}) => api.get('/production/stats/monthly/', { params }),
  getUtilizationStats: (params = {}) => api.get('/production/stats/equipment-utilization/', { params }),
  getEnergyStats: (params = {}) => api.get('/production/stats/energy/', { params })
}

export const costApi = {
  getMaterials: (params = {}) => api.get('/cost/materials/', { params }),
  getMaterialById: (id) => api.get(`/cost/materials/${id}`),
  createMaterial: (data) => api.post('/cost/materials/', data),
  updateMaterial: (id, data) => api.put(`/cost/materials/${id}`, data),
  deleteMaterial: (id) => api.delete(`/cost/materials/${id}`),
  
  getMaterialCosts: (params = {}) => api.get('/cost/material-costs/', { params }),
  createMaterialCost: (data) => api.post('/cost/material-costs/', data),
  updateMaterialCost: (id, data) => api.put(`/cost/material-costs/${id}`, data),
  deleteMaterialCost: (id) => api.delete(`/cost/material-costs/${id}`),
  
  getEmployees: (params = {}) => api.get('/cost/employees/', { params }),
  getEmployeeById: (id) => api.get(`/cost/employees/${id}`),
  createEmployee: (data) => api.post('/cost/employees/', data),
  updateEmployee: (id, data) => api.put(`/cost/employees/${id}`, data),
  deleteEmployee: (id) => api.delete(`/cost/employees/${id}`),
  
  getLaborCosts: (params = {}) => api.get('/cost/labor-costs/', { params }),
  createLaborCost: (data) => api.post('/cost/labor-costs/', data),
  updateLaborCost: (id, data) => api.put(`/cost/labor-costs/${id}`, data),
  deleteLaborCost: (id) => api.delete(`/cost/labor-costs/${id}`),
  
  getSales: (params = {}) => api.get('/cost/sales/', { params }),
  getSalesById: (id) => api.get(`/cost/sales/${id}`),
  createSales: (data) => api.post('/cost/sales/', data),
  updateSales: (id, data) => api.put(`/cost/sales/${id}`, data),
  deleteSales: (id) => api.delete(`/cost/sales/${id}`),
  
  getProfitAnalysis: (params = {}) => api.get('/cost/profit-analysis/', { params }),
  createProfitAnalysis: (data) => api.post('/cost/profit-analysis/', data),
  
  getDailyMaterialStats: (params = {}) => api.get('/cost/stats/material-daily/', { params }),
  getMonthlyMaterialStats: (params = {}) => api.get('/cost/stats/material-monthly/', { params }),
  getLaborStats: (params = {}) => api.get('/cost/stats/labor/', { params }),
  getUnitCostAnalysis: (params = {}) => api.get('/cost/stats/unit-cost/', { params })
}

export const environmentApi = {
  getPoints: (params = {}) => api.get('/environment/monitoring-points/', { params }),
  getPointById: (id) => api.get(`/environment/monitoring-points/${id}`),
  createPoint: (data) => api.post('/environment/monitoring-points/', data),
  updatePoint: (id, data) => api.put(`/environment/monitoring-points/${id}`, data),
  deletePoint: (id) => api.delete(`/environment/monitoring-points/${id}`),
  
  getDust: (params = {}) => api.get('/environment/dust/', { params }),
  createDust: (data) => api.post('/environment/dust/', data),
  updateDust: (id, data) => api.put(`/environment/dust/${id}`, data),
  deleteDust: (id) => api.delete(`/environment/dust/${id}`),
  
  getNoise: (params = {}) => api.get('/environment/noise/', { params }),
  createNoise: (data) => api.post('/environment/noise/', data),
  updateNoise: (id, data) => api.put(`/environment/noise/${id}`, data),
  deleteNoise: (id) => api.delete(`/environment/noise/${id}`),
  
  getWastewater: (params = {}) => api.get('/environment/wastewater/', { params }),
  createWastewater: (data) => api.post('/environment/wastewater/', data),
  updateWastewater: (id, data) => api.put(`/environment/wastewater/${id}`, data),
  deleteWastewater: (id) => api.delete(`/environment/wastewater/${id}`),
  
  getAlarms: (params = {}) => api.get('/environment/alarms/', { params }),
  getAlarmById: (id) => api.get(`/environment/alarms/${id}`),
  handleAlarm: (id, data) => api.put(`/environment/alarms/${id}/handle`, null, { params: data }),
  
  getDailyDustStats: (params = {}) => api.get('/environment/stats/dust-daily/', { params }),
  getDailyNoiseStats: (params = {}) => api.get('/environment/stats/noise-daily/', { params }),
  getDailyWastewaterStats: (params = {}) => api.get('/environment/stats/wastewater-daily/', { params }),
  getAlarmStats: (params = {}) => api.get('/environment/stats/alarms/', { params })
}
