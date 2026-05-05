<template>
  <view class="page">
    <view class="chat-section" v-if="sessionId">
      <scroll-view 
        scroll-y 
        class="message-scroll" 
        :scroll-top="scrollTop"
        scroll-with-animation
      >
        <view class="message-list">
          <view 
            class="message-item" 
            v-for="(msg, index) in messages" 
            :key="index"
            :class="{ self: msg.is_self }"
          >
            <image 
              :src="msg.is_self ? (userInfo.avatar || '/static/images/default-avatar.png') : '/static/images/robot-avatar.png'" 
              class="message-avatar"
            ></image>
            <view class="message-content">
              <text class="message-text">{{ msg.content }}</text>
              <text class="message-time">{{ formatTime(msg.created_at) }}</text>
            </view>
          </view>
          
          <view class="loading-message" v-if="isSending">
            <text class="loading-text">正在输入...</text>
          </view>
        </view>
      </scroll-view>
    </view>
    
    <view class="empty-section" v-else>
      <view class="empty-content">
        <text class="empty-icon">💬</text>
        <text class="empty-text">选择一个会话开始聊天</text>
      </view>
      
      <view class="faq-section">
        <view class="section-header">
          <text class="section-title">常见问题</text>
        </view>
        <view class="faq-list">
          <view class="faq-item" v-for="(faq, index) in faqList" :key="index" @click="sendFaq(faq)">
            <text class="faq-question">{{ faq.question }}</text>
            <text class="faq-arrow">›</text>
          </view>
        </view>
      </view>
      
      <view class="quick-section">
        <view class="section-header">
          <text class="section-title">快捷咨询</text>
        </view>
        <view class="quick-list">
          <view class="quick-item" @click="quickConsult('order')">
            <text class="quick-icon">📋</text>
            <text class="quick-text">订单问题</text>
          </view>
          <view class="quick-item" @click="quickConsult('points')">
            <text class="quick-icon">💰</text>
            <text class="quick-text">积分问题</text>
          </view>
          <view class="quick-item" @click="quickConsult('exchange')">
            <text class="quick-icon">📦</text>
            <text class="quick-text">兑换问题</text>
          </view>
          <view class="quick-item" @click="quickConsult('other')">
            <text class="quick-icon">❓</text>
            <text class="quick-text">其他问题</text>
          </view>
        </view>
      </view>
    </view>
    
    <view class="input-section">
      <view class="input-bar">
        <input 
          v-model="inputMessage" 
          type="text" 
          placeholder="请输入消息..." 
          confirm-type="send"
          @confirm="sendMessage"
        />
        <view class="send-btn" :class="{ disabled: !inputMessage.trim() }" @click="sendMessage">
          发送
        </view>
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
      sessionId: null,
      messages: [],
      inputMessage: '',
      isSending: false,
      scrollTop: 0,
      userInfo: {},
      faqList: [],
      collectorId: null
    }
  },
  
  onLoad(options) {
    if (options.collector_id) {
      this.collectorId = parseInt(options.collector_id)
    }
    this.loadData()
  },
  
  onShow() {
    this.userInfo = uni.getStorageSync('userInfo') || {}
  },
  
  methods: {
    formatTime(time) {
      return utils.formatTime(time, 'HH:mm')
    },
    
    async loadData() {
      await this.loadFAQ()
    },
    
    async loadFAQ() {
      try {
        const res = await api.get('/chat/faq')
        if (res.code === 200) {
          this.faqList = res.data.list || []
        }
      } catch (e) {
        console.error('加载FAQ失败:', e)
        this.faqList = [
          { question: '如何预约旧衣回收？', answer: '点击首页的"预约回收"按钮，选择衣物类型和上门时间即可。' },
          { question: '回收的衣物如何处理？', answer: '我们会将回收的衣物进行分类处理，可再利用的衣物会进行消毒清洗后捐赠或二次销售，不可再利用的会进行环保处理。' },
          { question: '积分如何使用？', answer: '积分可以在积分商城兑换商品，也可以参与公益捐赠活动。' },
          { question: '如何邀请好友获得奖励？', answer: '在"邀请好友"页面分享您的邀请码，好友注册并完成回收后，双方都能获得积分奖励。' }
        ]
      }
    },
    
    async startSession() {
      const token = uni.getStorageSync('token')
      if (!token) {
        utils.showToast('请先登录')
        uni.navigateTo({
          url: '/pages/login/login'
        })
        return null
      }
      
      try {
        const res = await api.post('/chat/session', {
          collector_id: this.collectorId
        })
        if (res.code === 200) {
          return res.data.session_id
        }
      } catch (e) {
        console.error('创建会话失败:', e)
      }
      
      return null
    },
    
    async loadMessages() {
      if (!this.sessionId) return
      
      try {
        const res = await api.get(`/chat/messages/${this.sessionId}`)
        if (res.code === 200) {
          this.messages = res.data.list || []
          this.scrollToBottom()
        }
      } catch (e) {
        console.error('加载消息失败:', e)
      }
    },
    
    async sendMessage() {
      const content = this.inputMessage.trim()
      if (!content) return
      
      if (!this.sessionId) {
        this.sessionId = await this.startSession()
        if (!this.sessionId) return
      }
      
      const tempMsg = {
        id: Date.now(),
        content: content,
        is_self: true,
        created_at: new Date().toISOString()
      }
      
      this.messages.push(tempMsg)
      this.inputMessage = ''
      this.scrollToBottom()
      
      this.isSending = true
      
      try {
        const res = await api.post(`/chat/messages/${this.sessionId}/send`, {
          content: content
        })
        
        if (res.code === 200) {
          const index = this.messages.findIndex(m => m.id === tempMsg.id)
          if (index > -1) {
            this.messages[index] = res.data.user_message
          }
          
          if (res.data.reply) {
            setTimeout(() => {
              this.messages.push(res.data.reply)
              this.scrollToBottom()
            }, 500)
          }
        }
      } catch (e) {
        console.error('发送消息失败:', e)
        utils.showToast('发送失败')
      } finally {
        this.isSending = false
      }
    },
    
    async sendFaq(faq) {
      this.inputMessage = faq.question
      await this.sendMessage()
    },
    
    async quickConsult(type) {
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
      
      this.inputMessage = message
      await this.sendMessage()
    },
    
    scrollToBottom() {
      this.$nextTick(() => {
        const query = uni.createSelectorQuery().in(this)
        query.select('.message-list').boundingClientRect(rect => {
          if (rect) {
            this.scrollTop = rect.height
          }
        }).exec()
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: $bg-color;
  display: flex;
  flex-direction: column;
}

.chat-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: $bg-color;
}

.message-scroll {
  flex: 1;
  padding: 20rpx;
}

.message-list {
  padding-bottom: 20rpx;
}

.message-item {
  display: flex;
  margin-bottom: 30rpx;
  
  &.self {
    flex-direction: row-reverse;
  }
}

.message-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
  margin: 0 20rpx;
}

.message-text {
  display: inline-block;
  padding: 20rpx 24rpx;
  background-color: $white;
  border-radius: $border-radius-md;
  font-size: $font-size-base;
  color: $text-color;
  line-height: 1.6;
  
  .self & {
    background-color: $primary-color;
    color: $white;
  }
}

.message-time {
  display: block;
  font-size: $font-size-xs;
  color: $text-muted;
  margin-top: 10rpx;
  
  .self & {
    text-align: right;
  }
}

.loading-message {
  display: flex;
  align-items: center;
  margin-bottom: 30rpx;
  padding-left: 100rpx;
}

.loading-text {
  font-size: $font-size-sm;
  color: $text-muted;
}

.empty-section {
  flex: 1;
  padding: 20rpx;
  overflow-y: auto;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60rpx 0;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: $font-size-base;
  color: $text-secondary;
}

.faq-section,
.quick-section {
  background-color: $white;
  border-radius: $border-radius-lg;
  padding: 0 30rpx;
  margin-bottom: 20rpx;
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

.faq-list {
  padding: 10rpx 0;
}

.faq-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 1rpx solid $border-color;
  
  &:last-child {
    border-bottom: none;
  }
}

.faq-question {
  flex: 1;
  font-size: $font-size-base;
  color: $text-color;
  margin-right: 20rpx;
}

.faq-arrow {
  font-size: $font-size-lg;
  color: $text-muted;
}

.quick-list {
  display: flex;
  flex-wrap: wrap;
  padding: 20rpx 0;
  gap: 20rpx;
}

.quick-item {
  width: calc(50% - 10rpx);
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
  font-size: $font-size-sm;
  color: $text-color;
}

.input-section {
  background-color: $white;
  padding: 20rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  border-top: 1rpx solid $border-color;
}

.input-bar {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.input-bar input {
  flex: 1;
  height: 80rpx;
  padding: 0 24rpx;
  background-color: $bg-color;
  border-radius: 40rpx;
  font-size: $font-size-base;
}

.send-btn {
  padding: 16rpx 40rpx;
  background-color: $primary-color;
  color: $white;
  font-size: $font-size-base;
  border-radius: 40rpx;
  
  &.disabled {
    background-color: $border-color;
  }
}
</style>
