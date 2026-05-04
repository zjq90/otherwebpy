<template>
  <div class="login-container">
    <div class="login-box">
      <!-- 标题 -->
      <div class="login-title">
        <i class="el-icon-s-tools"></i>
        <h2>{{ title }}</h2>
      </div>
      
      <!-- 登录表单 -->
      <el-form
        ref="loginForm"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        auto-complete="off"
      >
        <!-- 用户名 -->
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            prefix-icon="el-icon-user"
            size="large"
            @keyup.enter.native="handleLogin"
          />
        </el-form-item>
        
        <!-- 密码 -->
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="el-icon-lock"
            size="large"
            show-password
            @keyup.enter.native="handleLogin"
          />
        </el-form-item>
        
        <!-- 登录按钮 -->
        <el-form-item>
          <el-button
            :loading="loading"
            type="primary"
            size="large"
            style="width: 100%;"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      
      <!-- 默认账号提示 -->
      <div class="login-tips">
        <p>默认管理员账号：admin / admin123</p>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 登录页面组件
 */
export default {
  name: 'Login',
  data() {
    // 用户名验证规则
    const validateUsername = (rule, value, callback) => {
      if (value.trim() === '') {
        callback(new Error('请输入用户名'))
      } else {
        callback()
      }
    }
    
    // 密码验证规则
    const validatePassword = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入密码'))
      } else if (value.length < 6) {
        callback(new Error('密码长度不能少于6位'))
      } else {
        callback()
      }
    }
    
    return {
      // 系统标题
      title: process.env.VUE_APP_TITLE || '权限管理系统',
      // 加载状态
      loading: false,
      // 登录表单
      loginForm: {
        username: 'admin',
        password: 'admin123'
      },
      // 表单验证规则
      loginRules: {
        username: [
          { required: true, trigger: 'blur', validator: validateUsername }
        ],
        password: [
          { required: true, trigger: 'blur', validator: validatePassword }
        ]
      }
    }
  },
  created() {
    // 设置页面标题
    document.title = `登录 - ${process.env.VUE_APP_TITLE || '权限管理系统'}`
  },
  methods: {
    // 登录处理
    handleLogin() {
      this.$refs.loginForm.validate(valid => {
        if (valid) {
          this.loading = true
          // 调用登录接口
          this.$store.dispatch('user/login', this.loginForm)
            .then(() => {
              // 登录成功，跳转到首页
              this.$router.push({ path: this.$route.query.redirect || '/' })
            })
            .catch(() => {
              // 登录失败，重置表单
              this.loading = false
            })
        } else {
          console.log('表单验证失败')
          return false
        }
      })
    }
  }
}
</script>

<style scoped>
/**
 * 登录页面样式
 */
.login-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 400px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.login-title {
  text-align: center;
  margin-bottom: 30px;
}

.login-title i {
  font-size: 48px;
  color: #409eff;
  display: block;
  margin-bottom: 10px;
}

.login-title h2 {
  color: #303133;
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.login-form {
  margin-top: 20px;
}

.login-tips {
  margin-top: 20px;
  text-align: center;
  font-size: 12px;
  color: #909399;
}

.login-tips p {
  margin: 0;
}

/* 覆盖 Element UI 样式 */
.login-form /deep/ .el-input__inner {
  height: 44px;
  line-height: 44px;
}

.login-form /deep/ .el-form-item {
  margin-bottom: 25px;
}

.login-form /deep/ .el-input__prefix {
  left: 10px;
}

.login-form /deep/ .el-input__prefix i {
  color: #909399;
}
</style>
