<template>
  <div class="test-tool-container">
    <!-- 卡片区域 -->
    <el-row :gutter="20">
      <!-- 测试数据生成 -->
      <el-col :span="12">
        <div class="test-card">
          <div class="card-header">
            <i class="el-icon-database"></i>
            <span>测试数据生成</span>
          </div>
          <div class="card-body">
            <el-form label-width="100px">
              <el-form-item label="用户数量">
                <el-input-number
                  v-model="generateConfig.user_count"
                  :min="1"
                  :max="100"
                />
              </el-form-item>
              <el-form-item label="操作日志数量">
                <el-input-number
                  v-model="generateConfig.log_count"
                  :min="0"
                  :max="500"
                />
              </el-form-item>
              <el-form-item label="默认密码">
                <el-input
                  v-model="generateConfig.default_password"
                  placeholder="test123456"
                />
              </el-form-item>
            </el-form>
            <el-alert
              title="提示"
              type="info"
              :closable="false"
              style="margin-bottom: 15px;"
            >
              <p>生成的测试用户用户名为：test_user_001、test_user_002 等</p>
              <p>默认密码为：test123456</p>
            </el-alert>
            <el-button type="primary" :loading="generating" @click="handleGenerateData">
              <i class="el-icon-plus"></i> 生成测试数据
            </el-button>
            <el-button type="danger" @click="handleCleanupData">
              <i class="el-icon-delete"></i> 清理测试数据
            </el-button>
          </div>
        </div>
      </el-col>
      
      <!-- 权限测试 -->
      <el-col :span="12">
        <div class="test-card">
          <div class="card-header">
            <i class="el-icon-key"></i>
            <span>权限测试</span>
          </div>
          <div class="card-body">
            <el-form label-width="100px">
              <el-form-item label="权限代码">
                <el-select
                  v-model="testPermissionCode"
                  placeholder="请选择权限代码"
                  style="width: 100%;"
                  filterable
                  allow-create
                >
                  <el-option
                    v-for="permission in permissionList"
                    :key="permission.id"
                    :label="`${permission.name} (${permission.code})`"
                    :value="permission.code"
                  />
                </el-select>
              </el-form-item>
            </el-form>
            <el-alert
              title="说明"
              type="info"
              :closable="false"
              style="margin-bottom: 15px;"
            >
              <p>输入权限代码，测试当前用户是否拥有该权限</p>
              <p>也可以手动输入任意权限代码进行测试</p>
            </el-alert>
            <el-button type="primary" :loading="testingPermission" @click="handleTestPermission">
              <i class="el-icon-search"></i> 测试权限
            </el-button>
            
            <!-- 测试结果 -->
            <div v-if="permissionTestResult" class="test-result">
              <el-alert
                :title="permissionTestResult.title"
                :type="permissionTestResult.type"
                :closable="false"
                show-icon
              >
                <p v-for="(item, index) in permissionTestResult.messages" :key="index">
                  {{ item }}
                </p>
              </el-alert>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 系统信息 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <div class="test-card">
          <div class="card-header">
            <i class="el-icon-info"></i>
            <span>系统信息</span>
            <el-button type="text" @click="loadSystemInfo">
              <i class="el-icon-refresh"></i> 刷新
            </el-button>
          </div>
          <div class="card-body" v-loading="loadingSystemInfo">
            <el-descriptions :column="3" border v-if="systemInfo">
              <el-descriptions-item label="项目名称">
                {{ systemInfo.project_name || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="API版本">
                {{ systemInfo.api_version || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="调试模式">
                <el-tag :type="systemInfo.debug ? 'warning' : 'success'">
                  {{ systemInfo.debug ? '开启' : '关闭' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="Python版本">
                {{ systemInfo.python_version || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="FastAPI版本">
                {{ systemInfo.fastapi_version || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="SQLAlchemy版本">
                {{ systemInfo.sqlalchemy_version || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="数据库类型">
                {{ systemInfo.database || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="时区">
                {{ systemInfo.timezone || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="服务器时间">
                {{ formatTime(systemInfo.server_time) }}
              </el-descriptions-item>
            </el-descriptions>
            
            <!-- 文档链接 -->
            <div style="margin-top: 20px;">
              <el-divider content-position="left">API文档</el-divider>
              <div style="display: flex; gap: 20px;">
                <el-button type="primary" @click="openSwagger">
                  <i class="el-icon-link"></i> Swagger UI
                </el-button>
                <el-button type="success" @click="openRedoc">
                  <i class="el-icon-link"></i> ReDoc
                </el-button>
                <el-button type="warning" @click="openOpenAPI">
                  <i class="el-icon-link"></i> OpenAPI JSON
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 当前用户信息 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <div class="test-card">
          <div class="card-header">
            <i class="el-icon-user"></i>
            <span>当前用户信息</span>
          </div>
          <div class="card-body">
            <el-descriptions :column="3" border>
              <el-descriptions-item label="用户ID">
                {{ userInfo.id || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="用户名">
                <el-tag type="primary">{{ userInfo.username || '-' }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="邮箱">
                {{ userInfo.email || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="真实姓名">
                {{ userInfo.real_name || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="手机号">
                {{ userInfo.phone || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="userInfo.is_active ? 'success' : 'danger'">
                  {{ userInfo.is_active ? '启用' : '禁用' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="创建时间" :span="2">
                {{ formatTime(userInfo.created_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="是否超级管理员">
                <el-tag :type="isSuperAdmin ? 'danger' : 'info'">
                  {{ isSuperAdmin ? '是' : '否' }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
            
            <!-- 用户角色 -->
            <div style="margin-top: 20px;">
              <el-divider content-position="left">用户角色</el-divider>
              <div v-if="userInfo.roles && userInfo.roles.length > 0">
                <el-tag
                  v-for="role in userInfo.roles"
                  :key="role.id"
                  size="medium"
                  :type="role.is_system ? 'danger' : ''"
                  style="margin-right: 10px;"
                >
                  {{ role.name }}
                  <span v-if="role.is_system" style="margin-left: 5px; color: #f56c6c;">
                    (系统内置)
                  </span>
                </el-tag>
              </div>
              <span v-else style="color: #909399;">暂无角色</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
/**
 * 测试工具页面组件
 * 提供测试数据生成、权限测试、系统信息查看等功能
 */
import { mapGetters } from 'vuex'
import {
  generateTestData,
  cleanupTestData,
  testPermission,
  getSystemInfo,
  getPermissionList
} from '@/utils/auth'

export default {
  name: 'TestTool',
  data() {
    return {
      // 生成配置
      generateConfig: {
        user_count: 10,
        log_count: 50,
        default_password: 'test123456'
      },
      // 加载状态
      generating: false,
      testingPermission: false,
      loadingSystemInfo: false,
      // 权限测试
      testPermissionCode: '',
      permissionList: [],
      permissionTestResult: null,
      // 系统信息
      systemInfo: null
    }
  },
  computed: {
    // 映射 Vuex Getters
    ...mapGetters(['userInfo']),
    // 是否超级管理员
    isSuperAdmin() {
      if (!this.userInfo.roles) return false
      return this.userInfo.roles.some(role => role.code === 'super_admin')
    }
  },
  created() {
    // 加载数据
    this.loadSystemInfo()
    this.loadPermissionList()
  },
  methods: {
    // 加载权限列表
    async loadPermissionList() {
      try {
        const res = await getPermissionList()
        this.permissionList = res.data || []
      } catch (error) {
        console.error('加载权限列表失败:', error)
      }
    },
    
    // 加载系统信息
    async loadSystemInfo() {
      this.loadingSystemInfo = true
      try {
        const res = await getSystemInfo()
        this.systemInfo = res.data
      } catch (error) {
        console.error('加载系统信息失败:', error)
      } finally {
        this.loadingSystemInfo = false
      }
    },
    
    // 生成测试数据
    async handleGenerateData() {
      this.$confirm(
        `确定要生成 ${this.generateConfig.user_count} 个测试用户和 ${this.generateConfig.log_count} 条操作日志吗？`,
        '提示',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(async () => {
        this.generating = true
        try {
          await generateTestData(this.generateConfig)
          this.$message.success('测试数据生成成功')
        } catch (error) {
          console.error('生成测试数据失败:', error)
        } finally {
          this.generating = false
        }
      }).catch(() => {})
    },
    
    // 清理测试数据
    async handleCleanupData() {
      this.$confirm(
        '确定要清理所有测试数据吗？这将删除所有以 test_ 开头的用户和相关操作日志。',
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(async () => {
        try {
          await cleanupTestData()
          this.$message.success('测试数据清理成功')
        } catch (error) {
          console.error('清理测试数据失败:', error)
        }
      }).catch(() => {})
    },
    
    // 测试权限
    async handleTestPermission() {
      if (!this.testPermissionCode.trim()) {
        this.$message.warning('请输入权限代码')
        return
      }
      
      this.testingPermission = true
      this.permissionTestResult = null
      
      try {
        await testPermission(this.testPermissionCode)
        this.permissionTestResult = {
          title: '权限验证通过',
          type: 'success',
          messages: [
            `当前用户拥有权限：${this.testPermissionCode}`,
            '可以执行该权限对应的操作'
          ]
        }
      } catch (error) {
        this.permissionTestResult = {
          title: '权限验证失败',
          type: 'error',
          messages: [
            `当前用户不拥有权限：${this.testPermissionCode}`,
            '无法执行该权限对应的操作',
            '请联系管理员分配相应权限'
          ]
        }
      } finally {
        this.testingPermission = false
      }
    },
    
    // 打开 Swagger
    openSwagger() {
      window.open('/docs', '_blank')
    },
    
    // 打开 ReDoc
    openRedoc() {
      window.open('/redoc', '_blank')
    },
    
    // 打开 OpenAPI
    openOpenAPI() {
      window.open('/openapi.json', '_blank')
    },
    
    // 格式化时间
    formatTime(time) {
      if (!time) return '-'
      const date = new Date(time)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      const seconds = String(date.getSeconds()).padStart(2, '0')
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
    }
  }
}
</script>

<style scoped>
/**
 * 测试工具页面样式
 */
.test-tool-container {
  padding: 0;
}

/* 测试卡片样式 */
.test-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.test-card .card-header {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.test-card .card-header i {
  font-size: 20px;
  margin-right: 10px;
}

.test-card .card-header span {
  font-size: 16px;
  font-weight: 600;
}

.test-card .card-body {
  padding: 20px;
}

/* 测试结果样式 */
.test-result {
  margin-top: 15px;
}

/* 按钮间距 */
.test-card .el-button {
  margin-right: 10px;
}
</style>
