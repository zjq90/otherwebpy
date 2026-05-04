/**
 * 邀请有礼相关API
 */
import { get, post } from '../utils/request'

/**
 * 获取我的邀请码
 */
export function getMyInviteCode() {
    return get('/invitations/my-code', {}, {
        showLoading: false
    })
}

/**
 * 发起邀请
 * @param {Object} data - 邀请数据
 * @param {string} data.invitee_phone - 被邀请者手机号
 * @param {string} data.invitee_email - 被邀请者邮箱
 */
export function createInvitation(data) {
    return post('/invitations/create', data, {
        showLoading: true,
        loadingText: '发送中...'
    })
}

/**
 * 获取我发出的邀请记录
 * @param {Object} params - 查询参数
 * @param {string} params.status - 状态筛选
 */
export function getSentInvitations(params = {}) {
    return get('/invitations/sent', params, {
        showLoading: false
    })
}

/**
 * 获取我收到的邀请记录
 * @param {Object} params - 查询参数
 */
export function getReceivedInvitations(params = {}) {
    return get('/invitations/received', params, {
        showLoading: false
    })
}

/**
 * 获取邀请详情
 * @param {number} invitationId - 邀请记录ID
 */
export function getInvitationDetail(invitationId) {
    return get(`/invitations/${invitationId}`, {}, {
        showLoading: true,
        loadingText: '加载中...'
    })
}

/**
 * 验证邀请码
 * @param {string} inviteCode - 邀请码
 */
export function verifyInviteCode(inviteCode) {
    return post(`/invitations/verify/${inviteCode}`, {}, {
        showLoading: true,
        loadingText: '验证中...'
    })
}

/**
 * 领取邀请奖励
 * @param {number} invitationId - 邀请记录ID
 */
export function claimInvitationReward(invitationId) {
    return post(`/invitations/claim-reward/${invitationId}`, {}, {
        showLoading: true,
        loadingText: '领取中...'
    })
}

/**
 * 获取邀请统计
 */
export function getInvitationStats() {
    return get('/invitations/stats/overview', {}, {
        showLoading: false
    })
}

export const invitationsApi = {
    getMyInviteCode,
    createInvitation,
    getSentInvitations,
    getReceivedInvitations,
    getInvitationDetail,
    verifyInviteCode,
    claimInvitationReward,
    getInvitationStats
}

export default invitationsApi
