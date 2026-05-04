/**
 * 动态广场相关API
 */
import { get, post, put, del } from '../utils/request'

/**
 * 获取动态列表
 * @param {Object} params - 查询参数
 * @param {string} params.post_type - 动态类型筛选
 * @param {number} params.user_id - 用户ID筛选
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 */
export function getPosts(params = {}) {
    return get('/posts', params, {
        showLoading: false
    })
}

/**
 * 获取动态详情
 * @param {number} postId - 动态ID
 */
export function getPostDetail(postId) {
    return get(`/posts/${postId}`, {}, {
        showLoading: true,
        loadingText: '加载中...'
    })
}

/**
 * 发布动态
 * @param {Object} data - 动态数据
 * @param {string} data.content - 动态内容
 * @param {string} data.post_type - 动态类型
 * @param {string} data.images - 图片URL
 * @param {boolean} data.is_public - 是否公开
 */
export function createPost(data) {
    return post('/posts', data, {
        showLoading: true,
        loadingText: '发布中...'
    })
}

/**
 * 更新动态
 * @param {number} postId - 动态ID
 * @param {Object} data - 更新数据
 */
export function updatePost(postId, data) {
    return put(`/posts/${postId}`, data, {
        showLoading: true,
        loadingText: '更新中...'
    })
}

/**
 * 删除动态
 * @param {number} postId - 动态ID
 */
export function deletePost(postId) {
    return del(`/posts/${postId}`, {}, {
        showLoading: true,
        loadingText: '删除中...'
    })
}

/**
 * 点赞/取消点赞
 * @param {number} postId - 动态ID
 */
export function toggleLike(postId) {
    return post(`/posts/${postId}/like`, {}, {
        showLoading: false
    })
}

/**
 * 获取动态评论列表
 * @param {number} postId - 动态ID
 * @param {Object} params - 查询参数
 */
export function getComments(postId, params = {}) {
    return get(`/posts/${postId}/comments`, params, {
        showLoading: false
    })
}

/**
 * 发表评论
 * @param {Object} data - 评论数据
 * @param {number} data.post_id - 动态ID
 * @param {string} data.content - 评论内容
 * @param {number} data.parent_id - 父评论ID
 */
export function createComment(data) {
    return post('/posts/comments', data, {
        showLoading: true,
        loadingText: '发送中...'
    })
}

/**
 * 删除评论
 * @param {number} commentId - 评论ID
 */
export function deleteComment(commentId) {
    return del(`/posts/comments/${commentId}`, {}, {
        showLoading: true,
        loadingText: '删除中...'
    })
}

/**
 * 分享动态
 * @param {number} postId - 动态ID
 * @param {string} platform - 分享平台
 */
export function sharePost(postId, platform = null) {
    const data = platform ? { share_platform: platform } : {}
    return post(`/posts/${postId}/share`, data, {
        showLoading: false
    })
}

export const postsApi = {
    getPosts,
    getPostDetail,
    createPost,
    updatePost,
    deletePost,
    toggleLike,
    getComments,
    createComment,
    deleteComment,
    sharePost
}

export default postsApi
