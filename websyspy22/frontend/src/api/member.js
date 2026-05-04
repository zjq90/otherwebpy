import { get, post, put, del } from './http'

// 会员管理API

// 获取会员列表
export function getMemberList(params = {}) {
  return get('/members/', params)
}

// 获取会员详情
export function getMemberDetail(memberId) {
  return get(`/members/${memberId}`)
}

// 新增会员
export function createMember(data) {
  return post('/members/', data)
}

// 更新会员
export function updateMember(memberId, data) {
  return put(`/members/${memberId}`, data)
}

// 删除会员（注销）
export function deleteMember(memberId) {
  return del(`/members/${memberId}`)
}

// 发送验证码
export function sendVerificationCode(phone) {
  return post('/members/send-verification-code', { phone })
}

// 实名认证
export function verifyMember(memberId, data) {
  return post(`/members/${memberId}/verify`, data)
}

// 冻结账户
export function freezeMember(memberId, reason) {
  return post(`/status/${memberId}/freeze`, { reason })
}

// 解冻账户
export function unfreezeMember(memberId, reason) {
  return post(`/status/${memberId}/unfreeze`, { reason })
}

// 获取状态变更日志
export function getStatusLogs(memberId) {
  return get(`/status/${memberId}/logs`)
}
