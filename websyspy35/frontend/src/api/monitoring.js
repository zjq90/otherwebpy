import request from '@/utils/request'

export function getSensorDataList(params) {
  return request({
    url: '/api/monitoring/sensor-data/',
    method: 'get',
    params
  })
}

export function getSensorDataStatistics(params) {
  return request({
    url: '/api/monitoring/sensor-data/statistics',
    method: 'get',
    params
  })
}

export function createSensorData(data) {
  return request({
    url: '/api/monitoring/sensor-data/',
    method: 'post',
    data
  })
}

export function batchCreateSensorData(data) {
  return request({
    url: '/api/monitoring/sensor-data/batch',
    method: 'post',
    data
  })
}

export function getOperationLogList(params) {
  return request({
    url: '/api/monitoring/operation-logs/',
    method: 'get',
    params
  })
}

export function createOperationLog(data) {
  return request({
    url: '/api/monitoring/operation-logs/',
    method: 'post',
    data
  })
}

export function getControlSystemStatusList(params) {
  return request({
    url: '/api/monitoring/control-system/',
    method: 'get',
    params
  })
}

export function createControlSystemStatus(data) {
  return request({
    url: '/api/monitoring/control-system/',
    method: 'post',
    data
  })
}

export function updateControlSystemStatus(id, data) {
  return request({
    url: `/api/monitoring/control-system/${id}`,
    method: 'put',
    data
  })
}

export function deleteControlSystemStatus(id) {
  return request({
    url: `/api/monitoring/control-system/${id}`,
    method: 'delete'
  })
}

export function refreshControlSystemStatus() {
  return request({
    url: '/api/monitoring/control-system/refresh',
    method: 'post'
  })
}
