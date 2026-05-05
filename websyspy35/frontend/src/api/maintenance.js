import request from '@/utils/request'

export function getMaintenancePlanList(params) {
  return request({
    url: '/api/maintenance/plans/',
    method: 'get',
    params
  })
}

export function getMaintenancePlan(id) {
  return request({
    url: `/api/maintenance/plans/${id}`,
    method: 'get'
  })
}

export function createMaintenancePlan(data) {
  return request({
    url: '/api/maintenance/plans/',
    method: 'post',
    data
  })
}

export function updateMaintenancePlan(id, data) {
  return request({
    url: `/api/maintenance/plans/${id}`,
    method: 'put',
    data
  })
}

export function deleteMaintenancePlan(id) {
  return request({
    url: `/api/maintenance/plans/${id}`,
    method: 'delete'
  })
}

export function getMaintenanceTaskList(params) {
  return request({
    url: '/api/maintenance/tasks/',
    method: 'get',
    params
  })
}

export function getMaintenanceTask(id) {
  return request({
    url: `/api/maintenance/tasks/${id}`,
    method: 'get'
  })
}

export function createMaintenanceTask(data) {
  return request({
    url: '/api/maintenance/tasks/',
    method: 'post',
    data
  })
}

export function updateMaintenanceTask(id, data) {
  return request({
    url: `/api/maintenance/tasks/${id}`,
    method: 'put',
    data
  })
}

export function deleteMaintenanceTask(id) {
  return request({
    url: `/api/maintenance/tasks/${id}`,
    method: 'delete'
  })
}

export function completeMaintenanceTask(id, data) {
  return request({
    url: `/api/maintenance/tasks/${id}/complete`,
    method: 'post',
    params: data
  })
}

export function getMaintenanceTaskStatistics() {
  return request({
    url: '/api/maintenance/tasks/statistics',
    method: 'get'
  })
}

export function getMaintenanceRecordList(params) {
  return request({
    url: '/api/maintenance/records/',
    method: 'get',
    params
  })
}

export function getMaintenanceRecord(id) {
  return request({
    url: `/api/maintenance/records/${id}`,
    method: 'get'
  })
}

export function createMaintenanceRecord(data) {
  return request({
    url: '/api/maintenance/records/',
    method: 'post',
    data
  })
}

export function updateMaintenanceRecord(id, data) {
  return request({
    url: `/api/maintenance/records/${id}`,
    method: 'put',
    data
  })
}

export function deleteMaintenanceRecord(id) {
  return request({
    url: `/api/maintenance/records/${id}`,
    method: 'delete'
  })
}

export function getTaskStatuses() {
  return request({
    url: '/api/maintenance/task-statuses/all',
    method: 'get'
  })
}

export function getMaintenanceTypes() {
  return request({
    url: '/api/maintenance/maintenance-types/all',
    method: 'get'
  })
}
