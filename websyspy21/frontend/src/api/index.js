import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('请求错误:', error)
    ElMessage.error(error.message || '请求失败')
    return Promise.reject(error)
  }
)

const security = {
  getPersonnelList(params) {
    return request.get('/security/personnel/', { params })
  },
  getPersonnel(id) {
    return request.get(`/security/personnel/${id}`)
  },
  createPersonnel(data) {
    return request.post('/security/personnel/', data)
  },
  updatePersonnel(id, data) {
    return request.put(`/security/personnel/${id}`, data)
  },
  deletePersonnel(id) {
    return request.delete(`/security/personnel/${id}`)
  },

  getScheduleList(params) {
    return request.get('/security/schedule/', { params })
  },
  getSchedule(id) {
    return request.get(`/security/schedule/${id}`)
  },
  createSchedule(data) {
    return request.post('/security/schedule/', data)
  },
  updateSchedule(id, data) {
    return request.put(`/security/schedule/${id}`, data)
  },
  deleteSchedule(id) {
    return request.delete(`/security/schedule/${id}`)
  },

  getPatrolRouteList(params) {
    return request.get('/security/patrol-route/', { params })
  },
  getPatrolRoute(id) {
    return request.get(`/security/patrol-route/${id}`)
  },
  createPatrolRoute(data) {
    return request.post('/security/patrol-route/', data)
  },
  updatePatrolRoute(id, data) {
    return request.put(`/security/patrol-route/${id}`, data)
  },
  deletePatrolRoute(id) {
    return request.delete(`/security/patrol-route/${id}`)
  },

  getPatrolRecordList(params) {
    return request.get('/security/patrol-record/', { params })
  },
  getPatrolRecord(id) {
    return request.get(`/security/patrol-record/${id}`)
  },
  createPatrolRecord(data) {
    return request.post('/security/patrol-record/', data)
  },
  updatePatrolRecord(id, data) {
    return request.put(`/security/patrol-record/${id}`, data)
  },
  deletePatrolRecord(id) {
    return request.delete(`/security/patrol-record/${id}`)
  },

  getMonitorList(params) {
    return request.get('/security/monitor-device/', { params })
  },
  getMonitor(id) {
    return request.get(`/security/monitor-device/${id}`)
  },
  createMonitor(data) {
    return request.post('/security/monitor-device/', data)
  },
  updateMonitor(id, data) {
    return request.put(`/security/monitor-device/${id}`, data)
  },
  deleteMonitor(id) {
    return request.delete(`/security/monitor-device/${id}`)
  },

  getVehicleList(params) {
    return request.get('/security/vehicle-record/', { params })
  },
  getVehicle(id) {
    return request.get(`/security/vehicle-record/${id}`)
  },
  createVehicle(data) {
    return request.post('/security/vehicle-record/', data)
  },
  updateVehicle(id, data) {
    return request.put(`/security/vehicle-record/${id}`, data)
  },
  deleteVehicle(id) {
    return request.delete(`/security/vehicle-record/${id}`)
  },

  getVisitorList(params) {
    return request.get('/security/visitor-record/', { params })
  },
  getVisitor(id) {
    return request.get(`/security/visitor-record/${id}`)
  },
  createVisitor(data) {
    return request.post('/security/visitor-record/', data)
  },
  updateVisitor(id, data) {
    return request.put(`/security/visitor-record/${id}`, data)
  },
  deleteVisitor(id) {
    return request.delete(`/security/visitor-record/${id}`)
  },

  getEmergencyList(params) {
    return request.get('/security/emergency-report/', { params })
  },
  getEmergency(id) {
    return request.get(`/security/emergency-report/${id}`)
  },
  createEmergency(data) {
    return request.post('/security/emergency-report/', data)
  },
  updateEmergency(id, data) {
    return request.put(`/security/emergency-report/${id}`, data)
  },
  deleteEmergency(id) {
    return request.delete(`/security/emergency-report/${id}`)
  }
}

const environment = {
  getCleaningAreaList(params) {
    return request.get('/environment/cleaning-area/', { params })
  },
  getCleaningArea(id) {
    return request.get(`/environment/cleaning-area/${id}`)
  },
  createCleaningArea(data) {
    return request.post('/environment/cleaning-area/', data)
  },
  updateCleaningArea(id, data) {
    return request.put(`/environment/cleaning-area/${id}`, data)
  },
  deleteCleaningArea(id) {
    return request.delete(`/environment/cleaning-area/${id}`)
  },

  getCleaningRecordList(params) {
    return request.get('/environment/cleaning-record/', { params })
  },
  getCleaningRecord(id) {
    return request.get(`/environment/cleaning-record/${id}`)
  },
  createCleaningRecord(data) {
    return request.post('/environment/cleaning-record/', data)
  },
  updateCleaningRecord(id, data) {
    return request.put(`/environment/cleaning-record/${id}`, data)
  },
  deleteCleaningRecord(id) {
    return request.delete(`/environment/cleaning-record/${id}`)
  },

  getGreenPlantList(params) {
    return request.get('/environment/green-plant/', { params })
  },
  getGreenPlant(id) {
    return request.get(`/environment/green-plant/${id}`)
  },
  createGreenPlant(data) {
    return request.post('/environment/green-plant/', data)
  },
  updateGreenPlant(id, data) {
    return request.put(`/environment/green-plant/${id}`, data)
  },
  deleteGreenPlant(id) {
    return request.delete(`/environment/green-plant/${id}`)
  },

  getMaintenancePlanList(params) {
    return request.get('/environment/maintenance-plan/', { params })
  },
  getMaintenancePlan(id) {
    return request.get(`/environment/maintenance-plan/${id}`)
  },
  createMaintenancePlan(data) {
    return request.post('/environment/maintenance-plan/', data)
  },
  updateMaintenancePlan(id, data) {
    return request.put(`/environment/maintenance-plan/${id}`, data)
  },
  deleteMaintenancePlan(id) {
    return request.delete(`/environment/maintenance-plan/${id}`)
  },

  getMaintenanceRecordList(params) {
    return request.get('/environment/maintenance-record/', { params })
  },
  getMaintenanceRecord(id) {
    return request.get(`/environment/maintenance-record/${id}`)
  },
  createMaintenanceRecord(data) {
    return request.post('/environment/maintenance-record/', data)
  },
  updateMaintenanceRecord(id, data) {
    return request.put(`/environment/maintenance-record/${id}`, data)
  },
  deleteMaintenanceRecord(id) {
    return request.delete(`/environment/maintenance-record/${id}`)
  }
}

export { request, security, environment }
