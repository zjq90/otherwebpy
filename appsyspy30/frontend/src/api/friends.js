/**
 * 好友系统相关API
 */
import { get, post } from '../utils/request'

/**
 * 搜索用户
 * @param {string} keyword - 搜索关键词
 * @param {Object} params - 查询参数
 */
export function searchUsers(keyword, params = {}) {
    return get('/friends/search', { keyword, ...params }, {
        showLoading: false
    })
}

/**
 * 获取用户公开资料
 * @param {number} userId - 用户ID
 */
export function getUserProfile(userId) {
    return get(`/friends/profile/${userId}`, {}, {
        showLoading: true,
        loadingText: '加载中...'
    })
}

/**
 * 添加好友
 * @param {number} userId - 要添加的用户ID
 */
export function addFriend(userId) {
    return post('/friends/add', { user_id_2: userId }, {
        showLoading: true,
        loadingText: '发送中...'
    })
}

/**
 * 获取收到的好友请求列表
 * @param {Object} params - 查询参数
 * @param {string} params.status - 状态筛选
 */
export function getFriendRequests(params = {}) {
    return get('/friends/requests', params, {
        showLoading: false
    })
}

/**
 * 获取已发送的好友请求列表
 * @param {Object} params - 查询参数
 */
export function getSentFriendRequests(params = {}) {
    return get('/friends/sent-requests', params, {
        showLoading: false
    })
}

/**
 * 接受好友请求
 * @param {number} friendshipId - 好友关系ID
 */
export function acceptFriendRequest(friendshipId) {
    return post(`/friends/requests/${friendshipId}/accept`, {}, {
        showLoading: true,
        loadingText: '处理中...'
    })
}

/**
 * 拒绝好友请求
 * @param {number} friendshipId - 好友关系ID
 */
export function rejectFriendRequest(friendshipId) {
    return post(`/friends/requests/${friendshipId}/reject`, {}, {
        showLoading: true,
        loadingText: '处理中...'
    })
}

/**
 * 获取好友列表
 * @param {Object} params - 查询参数
 */
export function getFriends(params = {}) {
    return get('/friends', params, {
        showLoading: false
    })
}

/**
 * 删除好友
 * @param {number} friendId - 好友ID
 */
export function deleteFriend(friendId) {
    return post(`/friends/${friendId}`, {}, {
        showLoading: true,
        loadingText: '删除中...'
    })
}

/**
 * 发送私信
 * @param {Object} data - 消息数据
 * @param {number} data.receiver_id - 接收者ID
 * @param {string} data.content - 消息内容
 */
export function sendMessage(data) {
    return post('/friends/messages', data, {
        showLoading: false
    })
}

/**
 * 获取会话列表
 */
export function getConversations() {
    return get('/friends/messages/conversations', {}, {
        showLoading: false
    })
}

/**
 * 获取与指定用户的消息记录
 * @param {number} userId - 对方用户ID
 * @param {Object} params - 查询参数
 */
export function getMessagesWithUser(userId, params = {}) {
    return get(`/friends/messages/${userId}`, params, {
        showLoading: false
    })
}

/**
 * 获取未读消息数量
 */
export function getUnreadMessageCount() {
    return get('/friends/messages/unread/count', {}, {
        showLoading: false
    })
}

export const friendsApi = {
    searchUsers,
    getUserProfile,
    addFriend,
    getFriendRequests,
    getSentFriendRequests,
    acceptFriendRequest,
    rejectFriendRequest,
    getFriends,
    deleteFriend,
    sendMessage,
    getConversations,
    getMessagesWithUser,
    getUnreadMessageCount
}

export default friendsApi
