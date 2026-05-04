<template>
  <div class="error-page-container">
    <div class="error-page">
      <div class="error-code">{{ code }}</div>
      <div class="error-message">{{ message }}</div>
      <div class="error-description">{{ description }}</div>
      <el-button type="primary" @click="goHome">返回首页</el-button>
    </div>
  </div>
</template>

<script>
/**
 * 错误页面组件
 * 支持 403（权限不足）和 404（页面不存在）
 */
export default {
  name: 'ErrorPage',
  data() {
    return {
      // 错误码
      code: 404,
      // 错误消息
      message: '页面不存在',
      // 错误描述
      description: '抱歉，您访问的页面不存在'
    }
  },
  created() {
    // 从路由元信息获取错误码
    if (this.$route.meta.code === 403) {
      this.code = 403
      this.message = '权限不足'
      this.description = '抱歉，您没有权限访问此页面'
    } else {
      this.code = 404
      this.message = '页面不存在'
      this.description = '抱歉，您访问的页面不存在'
    }
    
    // 设置页面标题
    document.title = `${this.message} - ${process.env.VUE_APP_TITLE || '权限管理系统'}`
  },
  methods: {
    // 返回首页
    goHome() {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
/**
 * 错误页面样式
 */
.error-page-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.error-page {
  text-align: center;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.error-code {
  font-size: 120px;
  font-weight: bold;
  color: #409eff;
  line-height: 1;
  margin-bottom: 20px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.error-message {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 10px;
}

.error-description {
  font-size: 16px;
  color: #606266;
  margin-bottom: 30px;
}

.error-page /deep/ .el-button {
  padding: 12px 40px;
  font-size: 16px;
  border-radius: 25px;
}
</style>
