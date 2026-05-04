import { get } from './http'

// 等级与权益API

// 获取所有等级
export function getLevels() {
  return get('/levels/')
}

// 获取等级详情
export function getLevel(levelId) {
  return get(`/levels/${levelId}`)
}

// 获取会员等级信息
export function getMemberLevel(memberId) {
  return get(`/levels/member/${memberId}`)
}

// 获取等级权益
export function getLevelBenefits() {
  return get('/levels/benefits/')
}

// 获取升级规则
export function getUpgradeRules() {
  return get('/levels/upgrade-rules/')
}
