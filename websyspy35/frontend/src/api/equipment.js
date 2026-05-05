import request from '@/utils/request'

export function getEquipmentList(params) {
  return request({
    url: '/api/equipment/',
    method: 'get',
    params
  })
}

export function getEquipment(id) {
  return request({
    url: `/api/equipment/${id}`,
    method: 'get'
  })
}

export function createEquipment(data) {
  return request({
    url: '/api/equipment/',
    method: 'post',
    data
  })
}

export function updateEquipment(id, data) {
  return request({
    url: `/api/equipment/${id}`,
    method: 'put',
    data
  })
}

export function deleteEquipment(id) {
  return request({
    url: `/api/equipment/${id}`,
    method: 'delete'
  })
}

export function getEquipmentTypes() {
  return request({
    url: '/api/equipment/types/all',
    method: 'get'
  })
}

export function getSensorList(params) {
  return request({
    url: '/api/equipment/sensors/',
    method: 'get',
    params
  })
}

export function getSensor(id) {
  return request({
    url: `/api/equipment/sensors/${id}`,
    method: 'get'
  })
}

export function createSensor(data) {
  return request({
    url: '/api/equipment/sensors/',
    method: 'post',
    data
  })
}

export function updateSensor(id, data) {
  return request({
    url: `/api/equipment/sensors/${id}`,
    method: 'put',
    data
  })
}

export function deleteSensor(id) {
  return request({
    url: `/api/equipment/sensors/${id}`,
    method: 'delete'
  })
}
