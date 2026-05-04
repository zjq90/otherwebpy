/**
 * 挑战活动相关API
 */
import { get, post, put } from '../utils/request'

/**
 * 获取挑战活动列表
 * @param {Object} params - 查询参数
 * @param {string} params.challenge_type - 挑战类型筛选
 * @param {boolean} params.is_active - 是否激活
 */
export function getChallenges(params = {}) {
    return get('/challenges', params, {
        showLoading: false
    })
}

/**
 * 获取挑战活动详情
 * @param {number} challengeId - 挑战活动ID
 */
export function getChallengeDetail(challengeId) {
    return get(`/challenges/${challengeId}`, {}, {
        showLoading: true,
        loadingText: '加载中...'
    })
}

/**
 * 参与挑战活动
 * @param {number} challengeId - 挑战活动ID
 */
export function joinChallenge(challengeId) {
    return post('/challenges/join', { challenge_id: challengeId }, {
        showLoading: true,
        loadingText: '参与中...'
    })
}

/**
 * 获取我参与的挑战
 * @param {Object} params - 查询参数
 * @param {boolean} params.is_completed - 是否已完成
 */
export function getMyChallenges(params = {}) {
    return get('/challenges/my/participating', params, {
        showLoading: false
    })
}

/**
 * 更新挑战进度
 * @param {number} userChallengeId - 用户挑战记录ID
 * @param {Object} data - 进度数据
 * @param {number} data.progress - 完成进度(0-100)
 * @param {string} data.daily_data - 每日数据
 */
export function updateChallengeProgress(userChallengeId, data) {
    return put(`/challenges/progress/${userChallengeId}`, data, {
        showLoading: true,
        loadingText: '更新中...'
    })
}

/**
 * 领取挑战奖励
 * @param {number} userChallengeId - 用户挑战记录ID
 */
export function claimChallengeReward(userChallengeId) {
    return post(`/challenges/claim-reward/${userChallengeId}`, {}, {
        showLoading: true,
        loadingText: '领取中...'
    })
}

/**
 * 获取我的成就
 * @param {Object} params - 查询参数
 */
export function getMyAchievements(params = {}) {
    return get('/challenges/my/achievements', params, {
        showLoading: false
    })
}

export const challengesApi = {
    getChallenges,
    getChallengeDetail,
    joinChallenge,
    getMyChallenges,
    updateChallengeProgress,
    claimChallengeReward,
    getMyAchievements
}

export default challengesApi
