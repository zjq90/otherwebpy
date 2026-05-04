<template>
  <div class="dashboard-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20">
      <el-col :span="6" v-for="item in statistics" :key="item.title">
        <div class="stat-card" :class="item.type">
          <div class="stat-icon">
            <i :class="item.icon"></i>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ item.value }}</div>
            <div class="stat-title">{{ item.title }}</div>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 内容区域 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 最近操作日志 -->
      <el-col :span="12">
        <div class="dashboard-card">
          <div class="card-header">
            <span class="card-title">最近操作日志</span>
            <el-button type="text" @click="$router.push('/operation-log')">查看更多</el-button>
          </div>
          <div class="card-body">
            <el-table :data="recentLogs" style="width: 100%;">
              <el-table-column prop="username" label="操作用户" width="120">
                <template slot-scope="scope">
                  <el-tag size="small">{{ scope.row.username || '系统' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="action" label="操作类型" width="100">
                <template slot-scope="scope">
                  <span :class="'action-tag ' + scope.row.method.toLowerCase()">
                    {{ scope.row.method }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="path" label="请求路径" show-overflow-tooltip></el-table-column>
              <el-table-column prop="created_at" label="时间" width="160">
                <template slot-scope="scope">
                  {{ formatTime(scope.row.created_at) }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-col>
      
      <!-- 系统信息 -->
      <el-col :span="12">
        <div class="dashboard-card">
          <div class="card-header">
            <span class="card-title">系统信息</span>
          </div>
          <div class="card-body">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="系统名称">
                {{ systemInfo.project_name || '权限管理系统' }}
              </el-descriptions-item>
              <el-descriptions-item label="当前用户">
                {{ userInfo.username || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="用户角色">
                <template v-if="userInfo.roles && userInfo.roles.length > 0">
                  <el-tag v-for="role in userInfo.roles" :key="role.id" size="small" style="margin-right: 5px;">
                    {{ role.name }}
                  </el-tag>
                </template>
                <span v-else>-</span>
              </el-descriptions-item>
              <el-descriptions-item label="Python版本">
                {{ systemInfo.python_version || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="FastAPI版本">
                {{ systemInfo.fastapi_version || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="数据库">
                {{ systemInfo.database || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="服务器时间">
                {{ formatTime(new Date().toISOString()) }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 快速操作 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <div class="dashboard-card">
          <div class="card-header">
            <span class="card-title">快速操作</span>
          </div>
          <div class="card-body">
            <el-row :gutter="20">
              <el-col :span="4">
                <div class="quick-action" @click="$router.push('/user-manage')">
                  <i class="el-icon-user"></i>
                  <span>用户管理</span>
                </div>
              </el-col>
              <el-col :span="4">
                <div class="quick-action" @click="$router.push('/role-manage')">
                  <i class="el-icon-s-custom"></i>
                  <span>角色管理</span>
                </div>
              </el-col>
              <el-col :span="4">
                <div class="quick-action" @click="$router.push('/permission-manage')">
                  <i class="el-icon-key"></i>
                  <span>权限管理</span>
                </div>
              </el-col>
              <el-col :span="4">
                <div class="quick-action" @click="$router.push('/operation-log')">
                  <i class="el-icon-document"></i>
                  <span>操作日志</span>
                </div>
              </el-col>
              <el-col :span="4">
                <div class="quick-action" @click="$router.push('/test-tool')">
                  <i class="el-icon-cpu"></i>
                  <span>测试工具</span>
                </div>
              </el-col>
              <el-col :span="4">
                <div class="quick-action" @click="showHelp">
                  <i class="el-icon-question"></i>
                  <span>帮助</span>
                </div>
              </el-col>
            </el-row>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
/**
 * 仪表盘页面组件
 * 显示系统统计、最近操作日志、系统信息和快速操作
 */
import { mapGetters } from 'vuex'
import { getOperationLogList, getSystemInfo, getUserList, getRoleList } from '@/utils/auth'

export default {
  name: 'Dashboard',
  data() {
    return {
      // 统计数据
      statistics: [
        { title: '用户总数', value: 0, icon: 'el-icon-user', type: 'blue' },
        { title: '角色总数', value: 0, icon: 'el-icon-s-custom', type: 'green' },
        { title: '权限总数', value: 0, icon: 'el-icon-key', type: 'orange' },
        { title: '今日操作', value: 0, icon: 'el-icon-document', type: 'purple' }
      ],
      // 最近操作日志
      recentLogs: [],
      // 系统信息
      systemInfo: {}
    }
  },
  computed: {
    // 映射 Vuex Getters
    ...mapGetters(['userInfo'])
  },
  created() {
    // 加载数据
    this.loadStatistics()
    this.loadRecentLogs()
    this.loadSystemInfo()
  },
  methods: {
    // 加载统计数据
    async loadStatistics() {
      try {
        // 获取用户数量
        const userRes = await getUserList({ page: 1, size: 1 })
        this.statistics[0].value = userRes.total || 0
        
        // 获取角色数量
        const roleRes = await getRoleList()
        this.statistics[1].value = roleRes.data?.length || 0
        
        // 获取权限数量
        // 权限列表暂时通过角色推断，实际应该有权限列表接口
        this.statistics[2].value = 10
        
        // 获取今日操作数量
        const logRes = await getOperationLogList({ page: 1, size: 1 })
        this.statistics[3].value = logRes.total || 0
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    },
    
    // 加载最近操作日志
    async loadRecentLogs() {
      try {
        const res = await getOperationLogList({ page: 1, size: 5 })
        this.recentLogs = res.data || []
      } catch (error) {
        console.error('加载操作日志失败:', error)
      }
    },
    
    // 加载系统信息
    async loadSystemInfo() {
      try {
        const res = await getSystemInfo()
        this.systemInfo = res.data || {}
      } catch (error) {
        console.error('加载系统信息失败:', error)
      }
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
    },
    
    // 显示帮助
    showHelp() {
      this.$alert(`
        <div style="padding: 10px;">
          <p><strong>默认管理员账号：</strong>admin / admin123</p>
          <p><strong>系统角色：</strong></p>
          <ul style="margin: 10px 0; padding-left: 20px;">
            <li>超级管理员 - 拥有所有权限</li>
            <li>管理员 - 拥有大部分管理权限</li>
            <li>财务 - 拥有财务相关权限</li>
            <li>维修工 - 拥有维修相关权限</li>
            <li>前台 - 拥有前台相关权限</li>
          </ul>
          <p><strong>权限代码格式：</strong>模块:操作，如 user:create</p>
        </div>
      `, '系统帮助', {
        dangerouslyUseHTMLString: true,
        confirmButtonText: '确定'
      })
    }
  }
}
</script>

<style scoped>
/**
 * 仪表盘页面样式
 */
.dashboard-container {
  padding: 0;
}

/* 统计卡片 */
.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px 0 rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  margin-right: 15px;
}

.stat-icon i {
  font-size: 30px;
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-title {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

/* 不同类型的统计卡片 */
.stat-card.blue .stat-icon {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
}

.stat-card.green .stat-icon {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
}

.stat-card.orange .stat-icon {
  background: linear-gradient(135deg, #e6a23c 0%, #ebb563 100%);
}

.stat-card.purple .stat-icon {
  background: linear-gradient(135deg, #909399 0%, #b4bccc 100%);
}

/* 卡片样式 */
.dashboard-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  border-bottom: 1px solid #ebeef5;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.card-body {
  padding: 20px;
}

/* 操作类型标签 */
.action-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.action-tag.get {
  background-color: #ecf5ff;
  color: #409eff;
}

.action-tag.post {
  background-color: #f0f9eb;
  color: #67c23a;
}

.action-tag.put {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.action-tag.delete {
  background-color: #fef0f0;
  color: #f56c6c;
}

/* 快速操作 */
.quick-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 0;
  background-color: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-action:hover {
  background-color: #409eff;
  transform: translateY(-5px);
}

.quick-action i {
  font-size: 36px;
  color: #409eff;
  margin-bottom: 10px;
  transition: color 0.3s;
}

.quick-action:hover i {
  color: #fff;
}

.quick-action span {
  font-size: 14px;
  color: #606266;
  transition: color 0.3s;
}

.quick-action:hover span {
  color: #fff;
}
</style>
