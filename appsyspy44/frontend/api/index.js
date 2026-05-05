import request from '@/utils/request.js'

const productionApi = {
  getProductionDataList(skip = 0, limit = 100) {
    return request.get('/production/production-data', { skip, limit })
  },

  getProductionDataById(id) {
    return request.get(`/production/production-data/${id}`)
  },

  createProductionData(data) {
    return request.post('/production/production-data', data)
  },

  updateProductionData(id, data) {
    return request.put(`/production/production-data/${id}`, data)
  },

  deleteProductionData(id) {
    return request.delete(`/production/production-data/${id}`)
  },

  getDailyReport(date) {
    return request.get('/production/report/daily', { report_date: date })
  },

  getWeeklyReport(weekStart) {
    return request.get('/production/report/weekly', { week_start: weekStart })
  },

  getMonthlyReport(year, month) {
    return request.get('/production/report/monthly', { year, month })
  },

  getProductionChart(chartType, startDate, endDate) {
    return request.get('/production/chart/production', {
      chart_type: chartType,
      start_date: startDate,
      end_date: endDate
    })
  },

  getCompletionRateChart(chartType, startDate, endDate) {
    return request.get('/production/chart/completion-rate', {
      chart_type: chartType,
      start_date: startDate,
      end_date: endDate
    })
  },

  getTasksList(skip = 0, limit = 100) {
    return request.get('/production/tasks', { skip, limit })
  },

  getTaskById(id) {
    return request.get(`/production/tasks/${id}`)
  },

  createTask(data) {
    return request.post('/production/tasks', data)
  },

  updateTask(id, data) {
    return request.put(`/production/tasks/${id}`, data)
  },

  deleteTask(id) {
    return request.delete(`/production/tasks/${id}`)
  }
}

const qualityApi = {
  getQualityDataList(skip = 0, limit = 100) {
    return request.get('/quality/quality-data', { skip, limit })
  },

  getQualityDataById(id) {
    return request.get(`/quality/quality-data/${id}`)
  },

  createQualityData(data) {
    return request.post('/quality/quality-data', data)
  },

  updateQualityData(id, data) {
    return request.put(`/quality/quality-data/${id}`, data)
  },

  deleteQualityData(id) {
    return request.delete(`/quality/quality-data/${id}`)
  },

  getQualityTrend(startDate, endDate) {
    return request.get('/quality/quality-trend', {
      start_date: startDate,
      end_date: endDate
    })
  },

  getQualityPassRateChart(chartType, startDate, endDate) {
    return request.get('/quality/chart/quality-pass-rate', {
      chart_type: chartType,
      start_date: startDate,
      end_date: endDate
    })
  },

  getProductStrengthList(skip = 0, limit = 100) {
    return request.get('/quality/product-strength', { skip, limit })
  },

  getProductStrengthById(id) {
    return request.get(`/quality/product-strength/${id}`)
  },

  createProductStrength(data) {
    return request.post('/quality/product-strength', data)
  },

  updateProductStrength(id, data) {
    return request.put(`/quality/product-strength/${id}`, data)
  },

  deleteProductStrength(id) {
    return request.delete(`/quality/product-strength/${id}`)
  },

  getStrengthTrend(startDate, endDate) {
    return request.get('/quality/strength-trend', {
      start_date: startDate,
      end_date: endDate
    })
  },

  getStrengthTrendChart(chartType, startDate, endDate) {
    return request.get('/quality/chart/strength-trend', {
      chart_type: chartType,
      start_date: startDate,
      end_date: endDate
    })
  }
}

const equipmentApi = {
  getEquipmentList(skip = 0, limit = 100) {
    return request.get('/equipment/equipment', { skip, limit })
  },

  getEquipmentById(id) {
    return request.get(`/equipment/equipment/${id}`)
  },

  createEquipment(data) {
    return request.post('/equipment/equipment', data)
  },

  updateEquipment(id, data) {
    return request.put(`/equipment/equipment/${id}`, data)
  },

  deleteEquipment(id) {
    return request.delete(`/equipment/equipment/${id}`)
  },

  getRuntimeList(skip = 0, limit = 100) {
    return request.get('/equipment/runtime', { skip, limit })
  },

  createRuntime(data) {
    return request.post('/equipment/runtime', data)
  },

  getFaultsList(skip = 0, limit = 100) {
    return request.get('/equipment/faults', { skip, limit })
  },

  createFault(data) {
    return request.post('/equipment/faults', data)
  },

  getMaintenanceList(skip = 0, limit = 100) {
    return request.get('/equipment/maintenance', { skip, limit })
  },

  createMaintenance(data) {
    return request.post('/equipment/maintenance', data)
  },

  getOperatingRateChart(chartType, startDate, endDate) {
    return request.get('/equipment/operating-rate-chart', {
      chart_type: chartType,
      start_date: startDate,
      end_date: endDate
    })
  },

  getDowntimeChart(chartType, startDate, endDate) {
    return request.get('/equipment/downtime-chart', {
      chart_type: chartType,
      start_date: startDate,
      end_date: endDate
    })
  },

  getMaintenanceRateChart(chartType, startDate, endDate) {
    return request.get('/equipment/maintenance-rate-chart', {
      chart_type: chartType,
      start_date: startDate,
      end_date: endDate
    })
  }
}

const systemApi = {
  healthCheck() {
    return request.get('/health')
  }
}

export {
  productionApi,
  qualityApi,
  equipmentApi,
  systemApi
}
