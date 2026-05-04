import { get, post } from './http'

// 测试功能API

// 健康检查
export function healthCheck() {
  return get('/test/health')
}

// 批量生成测试数据
export function generateTestData(count = 10) {
  return post('/test/data/generate', { count })
}

// 生成单个测试会员
export function generateTestMember() {
  return post('/test/data/generate-member')
}

// 生成带有档案的测试会员
export function generateMemberWithArchive() {
  return post('/test/data/generate-member-with-archive')
}
