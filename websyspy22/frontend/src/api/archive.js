import { get, post, put, del } from './http'

// 档案管理API

// 体测数据
export function getPhysicalTests(params = {}) {
  return get('/archive/physical-tests/', params)
}

export function getPhysicalTest(id) {
  return get(`/archive/physical-tests/${id}`)
}

export function createPhysicalTest(data) {
  return post('/archive/physical-tests/', data)
}

export function updatePhysicalTest(id, data) {
  return put(`/archive/physical-tests/${id}`, data)
}

export function deletePhysicalTest(id) {
  return del(`/archive/physical-tests/${id}`)
}

export function getMemberPhysicalTests(memberId) {
  return get(`/archive/physical-tests/member/${memberId}`)
}

// 运动目标
export function getFitnessGoals(params = {}) {
  return get('/archive/fitness-goals/', params)
}

export function getFitnessGoal(id) {
  return get(`/archive/fitness-goals/${id}`)
}

export function createFitnessGoal(data) {
  return post('/archive/fitness-goals/', data)
}

export function updateFitnessGoal(id, data) {
  return put(`/archive/fitness-goals/${id}`, data)
}

export function deleteFitnessGoal(id) {
  return del(`/archive/fitness-goals/${id}`)
}

export function getMemberFitnessGoals(memberId) {
  return get(`/archive/fitness-goals/member/${memberId}`)
}

// 消费记录
export function getConsumptions(params = {}) {
  return get('/archive/consumptions/', params)
}

export function getConsumption(id) {
  return get(`/archive/consumptions/${id}`)
}

export function createConsumption(data) {
  return post('/archive/consumptions/', data)
}

export function updateConsumption(id, data) {
  return put(`/archive/consumptions/${id}`, data)
}

export function deleteConsumption(id) {
  return del(`/archive/consumptions/${id}`)
}

export function getMemberConsumptions(memberId) {
  return get(`/archive/consumptions/member/${memberId}`)
}

// 课程参与
export function getCourseParticipations(params = {}) {
  return get('/archive/courses/', params)
}

export function getCourseParticipation(id) {
  return get(`/archive/courses/${id}`)
}

export function createCourseParticipation(data) {
  return post('/archive/courses/', data)
}

export function updateCourseParticipation(id, data) {
  return put(`/archive/courses/${id}`, data)
}

export function deleteCourseParticipation(id) {
  return del(`/archive/courses/${id}`)
}

export function getMemberCourseParticipations(memberId) {
  return get(`/archive/courses/member/${memberId}`)
}
