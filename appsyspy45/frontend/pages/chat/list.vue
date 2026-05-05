<template>
  <view class="page">
    <view class="header-section">
      <view class="header-bg">
        <text class="header-title">客服咨询</text>
        <text class="header-subtitle">有问题？随时联系我们</text>
      </view>
    </view>
    
    <view class="quick-section">
      <view class="section-header">
        <text class="section-title">快捷咨询</text>
      </view>
      <view class="quick-list">
        <view class="quick-item" @click="quickConsult('order')">
          <view class="quick-icon">📋</view>
          <text class="quick-text">订单问题</text>
        </view>
        <view class="quick-item" @click="quickConsult('points')">
          <view class="quick-icon">💰</view>
          <text class="quick-text">积分问题</text>
        </view>
        <view class="quick-item" @click="quickConsult('exchange')">
          <view class="quick-icon">📦</view>
          <text class="quick-text">兑换问题</text>
        </view>
        <view class="quick-item" @click="quickConsult('other')">
          <view class="quick-icon">❓</view>
          <text class="quick-text">其他问题</text>
        </view>
      </view>
    </view>
    
    <view class="faq-section">
      <view class="section-header">
        <text class="section-title">常见问题</text>
      </view>
      <view class="faq-list">
        <view class="faq-item" v-for="(faq, index) in faqList" :key="index">
          <view class="faq-question" @click="toggleFaq(index)">
            <text class="question-text">{{ faq.question }}</text>
            <text class="question-arrow" :class="{ expanded: expandedIndex === index }">›</text>
          </view>
          <view class="faq-answer" v-if="expandedIndex === index">
            <text class="answer-text">{{ faq.answer }}</text>
          </view>
        </view>
      </view>
    </view>
    
    <view class="session-section" v-if="sessions.length > 0">
      <view class="section-header">
        <text class="section-title">历史会话</text>
      </view>
      <view class="session-list">
        <view class="session-item" v-for="(session, index) in sessions" :key="index" @click="goChat(session)">
          <view class="session-avatar">
            <image :src="session.avatar || '/static/images/robot-avatar.png'" class="avatar-image"></image>
            <view class="unread-badge" v-if="session.unread_count > 0">
              {{ session.unread_count }}
            </view>
          </view>
          <view class="session-info">
            <view class="session-header">
              <text class="session-name">{{ session.name || '智能客服' }}</text>
              <text class="session-time">{{ formatTime(session.updated_at) }}</text>
            </view>
            <text class="session-last" v-if="session.last_message">
              {{ session.last_message }}
            </text>
          </view>
        </view>
      </view>
    </view>
    
    <view class="contact-section">
      <view class="section-header">
        <text class="section-title">联系方式</text>
      </view>
      <view class="contact-list">
        <view class="contact-item" @click="makePhoneCall">
          <view class="contact-icon">📞</view>
          <view class="contact-info">
            <text class="contact-name">客服电话</text>
            <text class="contact-value">400-123-4567</text>
          </view>
          <text class="contact-arrow">›</text>
        </view>
        <view class="contact-item">
          <view class="contact-icon">🕐</view>
          <view class="contact-info">
            <text class="contact-name">服务时间</text>
            <text class="contact-value">周一至周日 9:00-21:00</text>
          </view>
        </view>
        <view class="contact-item">
          <view class="contact-icon">💬</view>
          <view class="contact-info">
            <text class="contact-name">在线客服</text>
            <text class="contact-value">24小时在线</text>
          </view>
        </view>
      </view>
    </view>
    
    <view class="bottom-section">
      <view class="online-btn" @click="goOnlineChat">
        <text class="btn-icon">💬</text>
        <text class="btn-text">在线咨询</text>
      </view>
    </view>
  </view>
</template>

<script>
import api from '@/common/api.js'
import utils from '@/common/utils.js'

export default {
  data() {
    return {
      sessions: [],
      expandedIndex: -1,
      faqList: [
        {
          question: '如何预约旧衣回收？',
          answer: '点击首页的"预约回收"按钮，选择衣物类型、填写回收数量和具体地址，选择上门时间后提交即可。16:00前可预约当天服务。'
        },
        {
          question: '回收的衣物如何处理？',
          answer: '我们会将回收的衣物进行专业分类处理：1) 可再利用的衣物经过消毒清洗后，捐赠给有需要的人群或进行二次销售；2) 不可再利用的衣物会进行环保处理，加工成工业抹布、保温材料等。'
        },
        {
          question: '积分如何计算和使用？',
          answer: '积分根据衣物类型、数量及品质计算，不同类型的衣物积分不同。积分可用于：1) 在积分商城兑换商品；2) 参与公益捐赠活动；3) 兑换优惠券。'
        },
        {
          question: '如何邀请好友获得奖励？',
          answer: '在"邀请好友"页面分享您的邀请码，好友注册时填写邀请码，双方都能获得50积分奖励。好友完成第一笔旧衣回收订单后，您还能再获得50积分奖励。'
        },
        {
          question: '订单可以取消或修改吗？',
          answer: '订单在"待接单"状态可以直接取消。"待上门"状态可以联系回收员调整时间或取消订单。订单完成后无法取消，但可以评价服务。'
        }
      ]
    }
  },
  
  onShow() {
    this.loadSessions()
  },
  
  methods: {
    formatTime(time) {
      return utils.relativeTime(time)
    },
    
    async loadSessions() {
      const token = uni.getStorageSync('token')
      if (!token) return
      
      try {
        const res = await api.get('/chat/sessions')
        if (res.code === 200) {
          this.sessions = res.data.list || []
        }
      } catch (e) {
        console.error('加载会话列表失败:', e)
      }
    },
    
    toggleFaq(index) {
      this.expandedIndex = this.expandedIndex === index ? -1 : index
    },
    
    quickConsult(type) {
      let message = ''
      switch (type) {
        case 'order':
          message = '我有订单相关的问题'
          break
        case 'points':
          message = '我有积分相关的问题'
          break
        case 'exchange':
          message = '我有兑换相关的问题'
          break
        default:
          message = '我有其他问题'
      }
      
      uni.navigateTo({
        url: '/pages/chat/detail'
      })
    },
    
    goChat(session) {
      uni.navigateTo({
        url: `/pages/chat/detail?session_id=${session.id}`
      })
    },
    
    goOnlineChat() {
      uni.navigateTo({
        url: '/pages/chat/detail'
      })
    },
    
    makePhoneCall() {
      uni.makePhoneCall({
        phoneNumber: '400-123-4567'
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: $bg-color;
  padding-bottom: 180rpx;
}

.header-section {
  background: linear-gradient(135deg, $primary-color, #66BB6A);
  padding: 60rpx 40rpx;
  padding-top: calc(60rpx + env(safe-area-inset-top));
}

.header-title {
  font-size: $font-size-xl;
  font-weight: bold;
  color: $white;
}

.header-subtitle {
  font-size: $font-size-sm;
  color: rgba($white, 0.8);
  margin-top: 10rpx;
  display: block;
}

.quick-section,
.faq-section,
.session-section,
.contact-section {
  background-color: $white;
  margin: 20rpx;
  border-radius: $border-radius-md;
  padding: 0 30rpx;
}

.section-header {
  padding: 30rpx 0;
  border-bottom: 1rpx solid $border-color;
}

.section-title {
  font-size: $font-size-base;
  font-weight: bold;
  color: $text-color;
}

.quick-list {
  display: flex;
  flex-wrap: wrap;
  padding: 30rpx 0;
  gap: 40rpx;
}

.quick-item {
  width: calc(50% - 20rpx);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30rpx 0;
  background-color: $bg-color;
  border-radius: $border-radius-md;
}

.quick-icon {
  font-size: 48rpx;
  margin-bottom: 16rpx;
}

.quick-text {
  font-size: $font-size-base;
  color: $text-color;
}

.faq-list {
  padding: 10rpx 0;
}

.faq-item {
  border-bottom: 1rpx solid $border-color;
  
  &:last-child {
    border-bottom: none;
  }
}

.faq-question {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx 0;
}

.question-text {
  flex: 1;
  font-size: $font-size-base;
  color: $text-color;
  margin-right: 20rpx;
}

.question-arrow {
  font-size: $font-size-lg;
  color: $text-muted;
  transition: transform 0.3s;
  
  &.expanded {
    transform: rotate(90deg);
  }
}

.faq-answer {
  padding: 0 0 30rpx 0;
}

.answer-text {
  font-size: $font-size-sm;
  color: $text-secondary;
  line-height: 1.8;
}

.session-list {
  padding: 10rpx 0;
}

.session-item {
  display: flex;
  padding: 20rpx 0;
  border-bottom: 1rpx solid $border-color;
  
  &:last-child {
    border-bottom: none;
  }
}

.session-avatar {
  position: relative;
  margin-right: 20rpx;
}

.avatar-image {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
}

.unread-badge {
  position: absolute;
  top: -8rpx;
  right: -8rpx;
  min-width: 36rpx;
  height: 36rpx;
  line-height: 36rpx;
  padding: 0 10rpx;
  background-color: $danger-color;
  color: $white;
  font-size: $font-size-xs;
  border-radius: 18rpx;
  text-align: center;
}

.session-info {
  flex: 1;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10rpx;
}

.session-name {
  font-size: $font-size-base;
  color: $text-color;
  font-weight: 500;
}

.session-time {
  font-size: $font-size-xs;
  color: $text-muted;
}

.session-last {
  font-size: $font-size-sm;
  color: $text-secondary;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.contact-list {
  padding: 10rpx 0;
}

.contact-item {
  display: flex;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 1rpx solid $border-color;
  
  &:last-child {
    border-bottom: none;
  }
}

.contact-icon {
  font-size: 40rpx;
  margin-right: 20rpx;
}

.contact-info {
  flex: 1;
}

.contact-name {
  font-size: $font-size-base;
  color: $text-color;
}

.contact-value {
  font-size: $font-size-sm;
  color: $text-secondary;
  margin-top: 6rpx;
  display: block;
}

.contact-arrow {
  font-size: $font-size-lg;
  color: $text-muted;
}

.bottom-section {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  background-color: $white;
  box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.online-btn {
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: $primary-color;
  color: $white;
  border-radius: 44rpx;
}

.btn-icon {
  font-size: 36rpx;
  margin-right: 10rpx;
}

.btn-text {
  font-size: $font-size-lg;
  font-weight: bold;
}
</style>
