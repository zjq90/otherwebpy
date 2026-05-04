<script setup lang="ts">
import { onLaunch, onShow, onHide } from "@dcloudio/uni-app";
import { ref } from "vue";

const appLaunchTime = ref("");

onLaunch(() => {
  console.log("App Launch");
  appLaunchTime.value = new Date().toISOString();
  
  // 检查登录状态
  const token = uni.getStorageSync("token");
  const userInfo = uni.getStorageSync("userInfo");
  if (token && userInfo) {
    console.log("用户已登录");
  }
});

onShow(() => {
  console.log("App Show");
});

onHide(() => {
  console.log("App Hide");
});
</script>

<style>
/* 全局样式 */
page {
  background-color: #f5f5f5;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  font-size: 28rpx;
  color: #333;
}

/* 容器样式 */
.container {
  padding: 20rpx;
  box-sizing: border-box;
}

/* 卡片样式 */
.card {
  background-color: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

/* 按钮样式 */
.btn-primary {
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
  color: #fff;
  border: none;
  border-radius: 40rpx;
  padding: 20rpx 40rpx;
  font-size: 30rpx;
  font-weight: 500;
}

.btn-primary:active {
  opacity: 0.8;
}

.btn-outline {
  background-color: #fff;
  color: #4A90D9;
  border: 2rpx solid #4A90D9;
  border-radius: 40rpx;
  padding: 18rpx 38rpx;
  font-size: 30rpx;
  font-weight: 500;
}

/* 文本样式 */
.text-primary {
  color: #4A90D9;
}

.text-success {
  color: #52c41a;
}

.text-warning {
  color: #faad14;
}

.text-danger {
  color: #ff4d4f;
}

.text-secondary {
  color: #999;
}

/* 间距 */
.mt-10 {
  margin-top: 20rpx;
}

.mt-20 {
  margin-top: 40rpx;
}

.mb-10 {
  margin-bottom: 20rpx;
}

.mb-20 {
  margin-bottom: 40rpx;
}

/* 分割线 */
.divider {
  height: 1rpx;
  background-color: #f0f0f0;
  margin: 20rpx 0;
}

/* 弹性布局 */
.flex {
  display: flex;
}

.flex-col {
  flex-direction: column;
}

.flex-center {
  justify-content: center;
  align-items: center;
}

.flex-between {
  justify-content: space-between;
}

.flex-1 {
  flex: 1;
}

/* 图标占位样式 */
.icon-placeholder {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  color: #fff;
  font-size: 36rpx;
}
</style>
