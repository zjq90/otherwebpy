import request from '@/utils/request'

export function getRawMaterials(params) {
  return request({
    url: '/raw-materials/',
    method: 'get',
    params
  })
}

export function getRawMaterial(id) {
  return request({
    url: `/raw-materials/${id}`,
    method: 'get'
  })
}

export function createRawMaterial(data) {
  return request({
    url: '/raw-materials/',
    method: 'post',
    data
  })
}

export function updateRawMaterial(id, data) {
  return request({
    url: `/raw-materials/${id}`,
    method: 'put',
    data
  })
}

export function deleteRawMaterial(id) {
  return request({
    url: `/raw-materials/${id}`,
    method: 'delete'
  })
}

export function getMaterialsByType(materialType) {
  return request({
    url: `/raw-materials/type/${materialType}`,
    method: 'get'
  })
}

export function getMaterialsBySupplier(supplierId) {
  return request({
    url: `/raw-materials/supplier/${supplierId}`,
    method: 'get'
  })
}
