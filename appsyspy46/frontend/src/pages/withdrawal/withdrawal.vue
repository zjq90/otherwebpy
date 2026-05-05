<template>
  <view class="withdrawal-container">
    <scroll-view class="withdrawal-scroll" scroll-y>
      <view class="balance-section">
        <text class="balance-label">可提现余额</text>
        <text class="balance-value">¥{{ availableBalance.toFixed(2) }}</text>
        <text class="balance-tip">最低提现金额：¥10.00</text>
      </view>

      <view class="form-section">
        <view class="section-header">
          <text class="section-title">提现信息</text>
        </view>

        <view class="form-item">
          <text class="form-label">提现金额 <text class="required">*</text></text>
          <view class="amount-input-wrapper">
            <text class="amount-prefix">¥</text>
            <input 
              class="amount-input"
              v-model="formData.amount"
              type="digit"
              placeholder="请输入提现金额"
              @blur="validateAmount"
            />
          </view>
          <view class="amount-actions">
            <text class="action-text" @click="setAmount(10)">¥10</text>
            <text class="action-text" @click="setAmount(50)">¥50</text>
            <text class="action-text" @click="setAmount(100)">¥100</text>
            <text class="action-text" @click="setAll">全部</text>
          </view>
          <text v-if="amountError" class="error-text">{{ amountError }}</text>
        </view>

        <view class="form-item">
          <text class="form-label">银行卡号 <text class="required">*</text></text>
          <input 
            class="form-input"
            v-model="formData.bank_card"
            type="number"
            placeholder="请输入银行卡号"
            maxlength="19"
          />
        </view>

        <view class="form-item">
          <text class="form-label">银行名称 <text class="required">*</text></text>
          <input 
            class="form-input"
            v-model="formData.bank_name"
            placeholder="请输入银行名称"
          />
        </view>

        <view class="form-item">
          <text class="form-label">账户姓名 <text class="required">*</text></text>
          <input 
            class="form-input"
            v-model="formData.account_name"
            placeholder="请输入银行卡开户姓名"
          />
        </view>
      </view>

      <view class="hint-section">
        <text class="hint-title">温馨提示</text>
        <view class="hint-list">
          <text class="hint-item">• 提现申请提交后，预计1-3个工作日到账</text>
          <text class="hint-item">• 单笔最低提现金额为10元</text>
          <text class="hint-item">• 请确保银行卡信息填写正确</text>
        </view>
      </view>
    </scroll-view>

    <view class="bottom-actions">
      <view class="preview-section">
        <text class="preview-label">预计到账</text>
        <text class="preview-value">¥{{ previewAmount.toFixed(2) }}</text>
      </view>
      <button 
        class="submit-btn" 
        :disabled="!canSubmit || submitting"
        :loading="submitting"
        @click="submitWithdrawal"
      >
        {{ submitting ? '提交中...' : '确认提现' }}
      </button>
    </view>
  </view>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { getProfile, createWithdrawal } from '@/api/user'
import { getUserInfo } from '@/api/auth'

interface UserProfile {
  id: number
  username: string
  real_name?: string
  total_income: number
}

export default defineComponent({
  setup() {
    const userProfile = ref<UserProfile | null>(null)
    const submitting = ref(false)
    const amountError = ref('')

    const formData = ref({
      amount: '',
      bank_card: '',
      bank_name: '',
      account_name: ''
    })

    const availableBalance = computed(() => {
      return userProfile.value?.total_income || 0
    })

    const previewAmount = computed(() => {
      const amount = parseFloat(formData.value.amount) || 0
      return amount
    })

    const canSubmit = computed(() => {
      const amount = parseFloat(formData.value.amount)
      return (
        amount && 
        amount >= 10 && 
        amount <= availableBalance.value &&
        formData.value.bank_card.trim() &&
        formData.value.bank_name.trim() &&
        formData.value.account_name.trim()
      )
    })

    const fetchProfile = async () => {
      try {
        const profile = await getProfile()
        userProfile.value = profile as UserProfile
      } catch (error) {
        console.error('获取用户信息失败:', error)
        const localInfo = getUserInfo()
        if (localInfo) {
          userProfile.value = {
            id: localInfo.id,
            username: localInfo.username,
            real_name: localInfo.real_name,
            total_income: localInfo.total_income || 0
          }
        }
      }
    }

    const validateAmount = () => {
      const amount = parseFloat(formData.value.amount)
      amountError.value = ''

      if (!formData.value.amount.trim()) {
        return
      }

      if (isNaN(amount) || amount <= 0) {
        amountError.value = '请输入有效的提现金额'
        return
      }

      if (amount < 10) {
        amountError.value = '最低提现金额为10元'
        return
      }

      if (amount > availableBalance.value) {
        amountError.value = '提现金额不能超过可提现余额'
        return
      }
    }

    const setAmount = (amount: number) => {
      if (amount > availableBalance.value) {
        uni.showToast({ title: '余额不足', icon: 'none' })
        return
      }
      formData.value.amount = amount.toString()
      amountError.value = ''
    }

    const setAll = () => {
      if (availableBalance.value < 10) {
        uni.showToast({ title: '余额不足10元，无法提现', icon: 'none' })
        return
      }
      formData.value.amount = availableBalance.value.toString()
      amountError.value = ''
    }

    const submitWithdrawal = async () => {
      if (!canSubmit.value) {
        if (!formData.value.amount.trim()) {
          uni.showToast({ title: '请输入提现金额', icon: 'none' })
        } else if (!formData.value.bank_card.trim()) {
          uni.showToast({ title: '请输入银行卡号', icon: 'none' })
        } else if (!formData.value.bank_name.trim()) {
          uni.showToast({ title: '请输入银行名称', icon: 'none' })
        } else if (!formData.value.account_name.trim()) {
          uni.showToast({ title: '请输入账户姓名', icon: 'none' })
        }
        return
      }

      uni.showModal({
        title: '确认提现',
        content: `确认提现 ¥${previewAmount.value.toFixed(2)} 到银行卡？`,
        success: async (res) => {
          if (res.confirm) {
            submitting.value = true
            try {
              await createWithdrawal({
                amount: parseFloat(formData.value.amount),
                bank_card: formData.value.bank_card,
                bank_name: formData.value.bank_name,
                account_name: formData.value.account_name
              })
              uni.showToast({ title: '提现申请已提交', icon: 'success' })
              setTimeout(() => {
                uni.navigateBack()
              }, 1500)
            } catch (error) {
              console.error('提交提现失败:', error)
              uni.showToast({ title: '提交失败，请重试', icon: 'none' })
            } finally {
              submitting.value = false
            }
          }
        }
      })
    }

    onMounted(() => {
      fetchProfile()
    })

    return {
      userProfile,
      formData,
      submitting,
      amountError,
      availableBalance,
      previewAmount,
      canSubmit,
      validateAmount,
      setAmount,
      setAll,
      submitWithdrawal
    }
  }
})
</script>

<style lang="scss" scoped>
.withdrawal-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.withdrawal-scroll {
  flex: 1;
  padding-bottom: 160rpx;
}

.balance-section {
  background: linear-gradient(135deg, #2979ff 0%, #1976d2 100%);
  padding: 60rpx 40rpx;
  text-align: center;
}

.balance-label {
  display: block;
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.8);
}

.balance-value {
  display: block;
  font-size: 64rpx;
  font-weight: bold;
  color: #ffffff;
  margin-top: 16rpx;
}

.balance-tip {
  display: block;
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 12rpx;
}

.form-section {
  background-color: #ffffff;
  margin: 20rpx;
  border-radius: 16rpx;
  overflow: hidden;
}

.section-header {
  padding: 24rpx 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.section-title {
  font-size: 30rpx;
  font-weight: 500;
  color: #303133;
}

.form-item {
  padding: 24rpx 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.form-item:last-child {
  border-bottom: none;
}

.form-label {
  display: block;
  font-size: 28rpx;
  color: #606266;
  margin-bottom: 16rpx;
}

.required {
  color: #f56c6c;
}

.form-input {
  width: 100%;
  height: 80rpx;
  background-color: #f5f7fa;
  border-radius: 12rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  box-sizing: border-box;
}

.amount-input-wrapper {
  display: flex;
  align-items: center;
  background-color: #f5f7fa;
  border-radius: 12rpx;
  padding: 0 20rpx;
}

.amount-prefix {
  font-size: 32rpx;
  font-weight: 500;
  color: #303133;
  margin-right: 8rpx;
}

.amount-input {
  flex: 1;
  height: 80rpx;
  font-size: 32rpx;
  font-weight: 500;
  color: #303133;
  background: transparent;
}

.amount-actions {
  display: flex;
  justify-content: flex-start;
  gap: 20rpx;
  margin-top: 20rpx;
}

.action-text {
  font-size: 26rpx;
  color: #2979ff;
  padding: 8rpx 20rpx;
  background-color: rgba(41, 121, 255, 0.1);
  border-radius: 20rpx;
}

.error-text {
  display: block;
  font-size: 24rpx;
  color: #f56c6c;
  margin-top: 12rpx;
}

.hint-section {
  background-color: #ffffff;
  margin: 20rpx;
  border-radius: 16rpx;
  padding: 24rpx 30rpx;
}

.hint-title {
  display: block;
  font-size: 28rpx;
  font-weight: 500;
  color: #303133;
  margin-bottom: 16rpx;
}

.hint-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.hint-item {
  font-size: 24rpx;
  color: #909399;
  line-height: 1.6;
}

.bottom-actions {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: #ffffff;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  display: flex;
  align-items: center;
  gap: 30rpx;
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.preview-section {
  display: flex;
  flex-direction: column;
}

.preview-label {
  font-size: 22rpx;
  color: #909399;
}

.preview-value {
  font-size: 36rpx;
  font-weight: bold;
  color: #f56c6c;
}

.submit-btn {
  flex: 1;
  height: 88rpx;
  background: linear-gradient(90deg, #07c160 0%, #05a652 100%);
  border-radius: 44rpx;
  color: #ffffff;
  font-size: 30rpx;
  font-weight: 500;
  border: none;
}

.submit-btn[disabled] {
  background: #c0c4cc;
  color: #ffffff;
}
</style>
