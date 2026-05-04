<template>
    <view class="index-container">
        <view class="header-bar">
            <view class="user-info" @click="goToProfile">
                <view class="avatar">
                    <text v-if="userInfo.real_name">{{ userInfo.real_name.charAt(0) }}</text>
                    <text v-else>会</text>
                </view>
                <view class="user-text">
                    <text class="greeting">{{ greeting }}</text>
                    <text class="user-name">{{ userInfo.real_name || userInfo.username }}</text>
                </view>
            </view>
            <view class="header-actions">
                <view class="action-item" @click="goToMessages">
                    <text class="action-icon">🔔</text>
                    <view class="badge" v-if="unreadCount > 0">{{ unreadCount > 99 ? '99+' : unreadCount }}</view>
                </view>
                <view class="action-item" @click="goToChat">
                    <text class="action-icon">💬</text>
                </view>
            </view>
        </view>
        
        <view class="search-bar" @click="goToSearch">
            <text class="search-icon">🔍</text>
            <text class="search-placeholder">搜索课程、教练、产品</text>
        </view>
        
        <view class="quick-entry">
            <view class="entry-item" v-for="item in quickEntries" :key="item.id" @click="navigateTo(item.path)">
                <view class="entry-icon" :style="{ background: item.bgColor }">
                    <text>{{ item.icon }}</text>
                </view>
                <text class="entry-text">{{ item.name }}</text>
            </view>
        </view>
        
        <view class="recommend-section" v-if="personalizedData">
            <view class="section-header">
                <text class="section-title">为你推荐</text>
                <text class="section-more" @click="goToRecommendations">查看更多 ></text>
            </view>
            
            <view class="recommend-content">
                <view class="recommend-block" v-if="personalizedData.courses?.length > 0">
                    <view class="block-header">
                        <text class="block-title">热门课程</text>
                    </view>
                    <scroll-view class="course-scroll" scroll-x>
                        <view class="course-card" v-for="course in personalizedData.courses.slice(0, 5)" :key="course.id" @click="goToCourseDetail(course.id)">
                            <view class="course-cover">
                                <view class="course-category">{{ getCategoryLabel(course.category) }}</view>
                            </view>
                            <view class="course-info">
                                <text class="course-name">{{ course.name }}</text>
                                <view class="course-meta">
                                    <text class="meta-item">⏱ {{ course.duration }}分钟</text>
                                    <text class="meta-item">🔥 {{ course.difficulty_level }}级</text>
                                </view>
                            </view>
                            <view class="recommend-tag" v-if="course.recommendation_reason">
                                <text>{{ course.recommendation_reason }}</text>
                            </view>
                        </view>
                    </scroll-view>
                </view>
                
                <view class="recommend-block" v-if="personalizedData.coaches?.length > 0">
                    <view class="block-header">
                        <text class="block-title">推荐教练</text>
                    </view>
                    <view class="coach-list">
                        <view class="coach-card" v-for="coach in personalizedData.coaches.slice(0, 3)" :key="coach.id" @click="goToCoachDetail(coach.id)">
                            <view class="coach-avatar">
                                <text>{{ coach.real_name?.charAt(0) || '教' }}</text>
                            </view>
                            <view class="coach-detail">
                                <view class="coach-header">
                                    <text class="coach-name">{{ coach.real_name }}</text>
                                    <view class="coach-rating">
                                        <text class="star">⭐</text>
                                        <text class="rating">{{ coach.rating }}</text>
                                        <text class="review-count">({{ coach.review_count }}评价)</text>
                                    </view>
                                </view>
                                <text class="coach-special">{{ coach.specialization }}</text>
                                <view class="coach-footer">
                                    <text class="experience">从业{{ coach.experience_years }}年</text>
                                    <text class="price">¥{{ coach.hourly_rate }}/课时</text>
                                </view>
                            </view>
                        </view>
                    </view>
                </view>
                
                <view class="recommend-block" v-if="personalizedData.products?.length > 0">
                    <view class="block-header">
                        <text class="block-title">营养产品</text>
                    </view>
                    <scroll-view class="product-scroll" scroll-x>
                        <view class="product-card" v-for="product in personalizedData.products.slice(0, 5)" :key="product.id" @click="goToProductDetail(product.id)">
                            <view class="product-cover">
                                <view class="product-tag" v-if="product.is_recommended">推荐</view>
                            </view>
                            <view class="product-info">
                                <text class="product-name">{{ product.name }}</text>
                                <text class="product-brand">{{ product.brand }}</text>
                                <view class="product-price">
                                    <text class="current-price">¥{{ product.price }}</text>
                                    <text class="original-price" v-if="product.original_price">¥{{ product.original_price }}</text>
                                </view>
                            </view>
                        </view>
                    </scroll-view>
                </view>
            </view>
        </view>
        
        <view class="hot-courses-section">
            <view class="section-header">
                <text class="section-title">热门课程</text>
                <text class="section-more" @click="goToCourses">全部课程 ></text>
            </view>
            <view class="course-grid">
                <view class="grid-item" v-for="course in hotCourses" :key="course.id" @click="goToCourseDetail(course.id)">
                    <view class="grid-cover">
                        <view class="grid-type">{{ getCourseTypeLabel(course.course_type) }}</view>
                    </view>
                    <view class="grid-info">
                        <text class="grid-name">{{ course.name }}</text>
                        <view class="grid-meta">
                            <text class="grid-duration">⏱ {{ course.duration }}分钟</text>
                            <text class="grid-calories">🔥 {{ course.calories_burned }}卡</text>
                        </view>
                    </view>
                </view>
            </view>
        </view>
        
        <view class="bottom-space"></view>
    </view>
</template>

<script setup>
import { ref, computed, onMounted, onShow } from 'vue'
import { courseApi, coachApi, productApi, recommendationApi, messageApi, chatApi } from '@/utils/api'
import { showLoading, hideLoading, showToast } from '@/utils'

const userInfo = ref({})
const unreadCount = ref(0)
const personalizedData = ref(null)
const hotCourses = ref([])

const greeting = computed(() => {
    const hour = new Date().getHours()
    if (hour < 6) return '夜深了'
    if (hour < 9) return '早上好'
    if (hour < 12) return '上午好'
    if (hour < 14) return '中午好'
    if (hour < 18) return '下午好'
    if (hour < 22) return '晚上好'
    return '夜深了'
})

const quickEntries = [
    { id: 1, name: '预约课程', icon: '📅', path: '/pages/bookings/create', bgColor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
    { id: 2, name: '我的预约', icon: '📋', path: '/pages/bookings/bookings', bgColor: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
    { id: 3, name: '在线客服', icon: '💬', path: '/pages/chat/chat', bgColor: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
    { id: 4, name: '待评价', icon: '⭐', path: '/pages/reviews/reviews', bgColor: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' },
]

const getCategoryLabel = (category) => {
    const labels = {
        strength: '力量训练',
        cardio: '有氧训练',
        yoga: '瑜伽',
        pilates: '普拉提',
        dance: '舞蹈',
        boxing: '拳击',
        swimming: '游泳',
        rehabilitation: '康复训练'
    }
    return labels[category] || category
}

const getCourseTypeLabel = (type) => {
    const labels = {
        group: '团课',
        private: '私教',
        semi_private: '小团体'
    }
    return labels[type] || type
}

const navigateTo = (path) => {
    uni.navigateTo({ url: path })
}

const goToProfile = () => {
    uni.switchTab({ url: '/pages/profile/profile' })
}

const goToMessages = () => {
    uni.switchTab({ url: '/pages/messages/messages' })
}

const goToChat = () => {
    uni.navigateTo({ url: '/pages/chat/chat' })
}

const goToSearch = () => {
    showToast('搜索功能开发中')
}

const goToRecommendations = () => {
    showToast('推荐页面开发中')
}

const goToCourseDetail = (id) => {
    uni.navigateTo({ url: `/pages/courses/detail?id=${id}` })
}

const goToCoachDetail = (id) => {
    uni.navigateTo({ url: `/pages/coaches/detail?id=${id}` })
}

const goToProductDetail = (id) => {
    uni.navigateTo({ url: `/pages/products/detail?id=${id}` })
}

const goToCourses = () => {
    uni.switchTab({ url: '/pages/courses/courses' })
}

const fetchUserInfo = () => {
    const stored = uni.getStorageSync('userInfo')
    if (stored) {
        userInfo.value = JSON.parse(stored)
    }
}

const fetchUnreadCount = async () => {
    try {
        const [messageRes, chatRes] = await Promise.all([
            messageApi.getUnreadCount().catch(() => ({ data: { count: 0 } })),
            chatApi.getUnreadCount().catch(() => ({ data: { count: 0 } }))
        ])
        unreadCount.value = (messageRes.data?.count || 0) + (chatRes.data?.count || 0)
    } catch (error) {
        console.error('获取未读数量失败:', error)
    }
}

const fetchPersonalizedData = async () => {
    try {
        showLoading('加载中...')
        const res = await recommendationApi.getPersonalized()
        if (res.code === 200) {
            personalizedData.value = res.data
        }
    } catch (error) {
        console.error('获取个性化推荐失败:', error)
    } finally {
        hideLoading()
    }
}

const fetchHotCourses = async () => {
    try {
        const res = await courseApi.getPopular(6)
        if (res.code === 200) {
            hotCourses.value = res.data.products || []
        }
    } catch (error) {
        console.error('获取热门课程失败:', error)
    }
}

onShow(() => {
    fetchUserInfo()
    fetchUnreadCount()
})

onMounted(() => {
    fetchPersonalizedData()
    fetchHotCourses()
})
</script>

<style lang="scss" scoped>
.index-container {
    min-height: 100vh;
    background: $bg-color;
    padding-bottom: 40rpx;
}

.header-bar {
    background: linear-gradient(135deg, $primary-color 0%, $secondary-color 100%);
    padding: 60rpx 30rpx 40rpx;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.user-info {
    display: flex;
    align-items: center;
}

.avatar {
    width: 88rpx;
    height: 88rpx;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 20rpx;
    
    text {
        font-size: 36rpx;
        color: #ffffff;
        font-weight: bold;
    }
}

.user-text {
    display: flex;
    flex-direction: column;
}

.greeting {
    font-size: 24rpx;
    color: rgba(255, 255, 255, 0.8);
}

.user-name {
    font-size: 32rpx;
    color: #ffffff;
    font-weight: 500;
    margin-top: 6rpx;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 30rpx;
}

.action-item {
    position: relative;
    width: 64rpx;
    height: 64rpx;
    background: rgba(255, 255, 255, 0.15);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.action-icon {
    font-size: 32rpx;
}

.badge {
    position: absolute;
    top: -8rpx;
    right: -8rpx;
    min-width: 32rpx;
    height: 32rpx;
    background: #ff4757;
    border-radius: 16rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 8rpx;
    font-size: 20rpx;
    color: #ffffff;
}

.search-bar {
    margin: -20rpx 30rpx 30rpx;
    background: #ffffff;
    border-radius: 50rpx;
    padding: 24rpx 30rpx;
    display: flex;
    align-items: center;
    box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.search-icon {
    font-size: 32rpx;
    margin-right: 16rpx;
}

.search-placeholder {
    font-size: 26rpx;
    color: #999999;
}

.quick-entry {
    display: flex;
    justify-content: space-around;
    padding: 20rpx 30rpx;
    background: #ffffff;
    margin-bottom: 20rpx;
}

.entry-item {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.entry-icon {
    width: 96rpx;
    height: 96rpx;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 12rpx;
    
    text {
        font-size: 40rpx;
    }
}

.entry-text {
    font-size: 24rpx;
    color: #333333;
}

.recommend-section {
    margin-bottom: 20rpx;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20rpx 30rpx;
    background: #ffffff;
}

.section-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333333;
}

.section-more {
    font-size: 24rpx;
    color: $primary-color;
}

.recommend-content {
    padding: 0 30rpx;
    background: #ffffff;
    padding-bottom: 30rpx;
}

.recommend-block {
    margin-bottom: 30rpx;
    
    &:last-child {
        margin-bottom: 0;
    }
}

.block-header {
    padding: 20rpx 0;
}

.block-title {
    font-size: 28rpx;
    font-weight: 500;
    color: #333333;
    border-left: 6rpx solid $primary-color;
    padding-left: 16rpx;
}

.course-scroll {
    white-space: nowrap;
}

.course-card {
    display: inline-block;
    width: 280rpx;
    margin-right: 20rpx;
    background: #f5f7fa;
    border-radius: 16rpx;
    overflow: hidden;
    vertical-align: top;
}

.course-cover {
    height: 160rpx;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    
    text {
        font-size: 60rpx;
        color: rgba(255, 255, 255, 0.3);
    }
}

.course-category {
    position: absolute;
    top: 12rpx;
    left: 12rpx;
    background: rgba(255, 255, 255, 0.9);
    padding: 6rpx 16rpx;
    border-radius: 20rpx;
    font-size: 20rpx;
    color: $primary-color;
}

.course-info {
    padding: 16rpx;
}

.course-name {
    font-size: 26rpx;
    color: #333333;
    font-weight: 500;
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.course-meta {
    display: flex;
    gap: 16rpx;
    margin-top: 10rpx;
}

.meta-item {
    font-size: 20rpx;
    color: #999999;
}

.recommend-tag {
    padding: 8rpx 16rpx;
    background: rgba(102, 126, 234, 0.1);
    border-radius: 0 0 16rpx 16rpx;
    
    text {
        font-size: 20rpx;
        color: $primary-color;
    }
}

.coach-list {
    display: flex;
    flex-direction: column;
    gap: 20rpx;
}

.coach-card {
    display: flex;
    background: #f5f7fa;
    border-radius: 16rpx;
    padding: 20rpx;
}

.coach-avatar {
    width: 100rpx;
    height: 100rpx;
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 20rpx;
    flex-shrink: 0;
    
    text {
        font-size: 40rpx;
        color: #ffffff;
        font-weight: bold;
    }
}

.coach-detail {
    flex: 1;
}

.coach-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.coach-name {
    font-size: 28rpx;
    font-weight: 500;
    color: #333333;
}

.coach-rating {
    display: flex;
    align-items: center;
}

.star {
    font-size: 24rpx;
    margin-right: 4rpx;
}

.rating {
    font-size: 24rpx;
    color: #ffa502;
    font-weight: 500;
}

.review-count {
    font-size: 20rpx;
    color: #999999;
    margin-left: 6rpx;
}

.coach-special {
    font-size: 22rpx;
    color: #666666;
    margin-top: 8rpx;
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.coach-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 12rpx;
}

.experience {
    font-size: 20rpx;
    color: #999999;
}

.price {
    font-size: 24rpx;
    color: $primary-color;
    font-weight: 500;
}

.product-scroll {
    white-space: nowrap;
}

.product-card {
    display: inline-block;
    width: 200rpx;
    margin-right: 20rpx;
    background: #f5f7fa;
    border-radius: 16rpx;
    overflow: hidden;
    vertical-align: top;
}

.product-cover {
    height: 140rpx;
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    
    text {
        font-size: 50rpx;
        color: rgba(255, 255, 255, 0.3);
    }
}

.product-tag {
    position: absolute;
    top: 0;
    left: 0;
    background: linear-gradient(135deg, #ffa502 0%, #ff6348 100%);
    padding: 6rpx 16rpx;
    border-radius: 0 0 16rpx 0;
    font-size: 20rpx;
    color: #ffffff;
}

.product-info {
    padding: 16rpx;
}

.product-name {
    font-size: 24rpx;
    color: #333333;
    font-weight: 500;
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.product-brand {
    font-size: 20rpx;
    color: #999999;
    margin-top: 6rpx;
    display: block;
}

.product-price {
    display: flex;
    align-items: baseline;
    margin-top: 10rpx;
}

.current-price {
    font-size: 26rpx;
    color: $danger-color;
    font-weight: 500;
}

.original-price {
    font-size: 20rpx;
    color: #999999;
    text-decoration: line-through;
    margin-left: 8rpx;
}

.hot-courses-section {
    background: #ffffff;
}

.course-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 20rpx;
    padding: 0 30rpx 30rpx;
}

.grid-item {
    width: calc(50% - 10rpx);
    background: #f5f7fa;
    border-radius: 16rpx;
    overflow: hidden;
}

.grid-cover {
    height: 180rpx;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    
    text {
        font-size: 60rpx;
        color: rgba(255, 255, 255, 0.3);
    }
}

.grid-type {
    position: absolute;
    top: 12rpx;
    right: 12rpx;
    background: rgba(255, 255, 255, 0.9);
    padding: 6rpx 16rpx;
    border-radius: 20rpx;
    font-size: 20rpx;
    color: $primary-color;
}

.grid-info {
    padding: 16rpx;
}

.grid-name {
    font-size: 26rpx;
    color: #333333;
    font-weight: 500;
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.grid-meta {
    display: flex;
    justify-content: space-between;
    margin-top: 10rpx;
}

.grid-duration,
.grid-calories {
    font-size: 20rpx;
    color: #999999;
}

.bottom-space {
    height: 40rpx;
}
</style>
