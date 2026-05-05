<template>
  <div class="page-content">
    <el-row :gutter="20">
      <el-col :span="6">
        <div class="stat-card" style="border-left: 4px solid #409eff;">
          <el-icon class="stat-icon" style="color: #409eff;"><UserFilled /></el-icon>
          <div class="stat-value">{{ stats.customers }}</div>
          <div class="stat-label">客户总数</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="border-left: 4px solid #67c23a;">
          <el-icon class="stat-icon" style="color: #67c23a;"><Goods /></el-icon>
          <div class="stat-value">{{ stats.products }}</div>
          <div class="stat-label">产品总数</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="border-left: 4px solid #e6a23c;">
          <el-icon class="stat-icon" style="color: #e6a23c;"><Box /></el-icon>
          <div class="stat-value">{{ stats.inventories }}</div>
          <div class="stat-label">库存记录</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="border-left: 4px solid #f56c6c;">
          <el-icon class="stat-icon" style="color: #f56c6c;"><User /></el-icon>
          <div class="stat-value">{{ stats.employees }}</div>
          <div class="stat-label">员工总数</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="content-card">
          <template #header>
            <span style="font-weight: bold; font-size: 16px;">快速入口</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="8" v-for="menu in quickMenus" :key="menu.path">
              <el-card 
                shadow="hover" 
                style="text-align: center; cursor: pointer;"
                @click="$router.push(menu.path)"
              >
                <el-icon :size="40" :color="menu.color">{{ menu.icon }}</el-icon>
                <div style="margin-top: 10px; font-weight: 500;">{{ menu.name }}</div>
              </el-card>
            </el-col>
          </el-row>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="content-card">
          <template #header>
            <span style="font-weight: bold; font-size: 16px;">系统信息</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="系统名称">ERP企业资源管理系统</el-descriptions-item>
            <el-descriptions-item label="技术栈">Vue 3 + Element Plus + FastAPI + SQLite</el-descriptions-item>
            <el-descriptions-item label="功能模块">销售、生产、库存、财务、人事</el-descriptions-item>
            <el-descriptions-item label="当前时间">{{ currentTime }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <el-row style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="content-card">
          <template #header>
            <span style="font-weight: bold; font-size: 16px;">使用说明</span>
          </template>
          <el-steps :active="-1" align-center>
            <el-step title="安装依赖" description="后端: pip install -r requirements.txt&#10;前端: npm install"></el-step>
            <el-step title="启动服务" description="后端: uvicorn app.main:app --reload&#10;前端: npm run dev"></el-step>
            <el-step title="生成测试数据" description="访问测试数据页面，点击生成测试数据按钮"></el-step>
            <el-step title="开始使用" description="通过左侧菜单访问各功能模块"></el-step>
          </el-steps>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'
import { UserFilled, Goods, Box, User, ShoppingCart, Tools, Wallet, UserFilled as UserFilledIcon } from '@element-plus/icons-vue'

const router = useRouter()

const stats = ref({
  customers: 0,
  products: 0,
  inventories: 0,
  employees: 0
})

const currentTime = ref('')

const quickMenus = ref([
  { name: '客户管理', path: '/sales/customer', icon: 'User', color: '#409eff' },
  { name: '产品管理', path: '/production/product', icon: 'Goods', color: '#67c23a' },
  { name: '库存管理', path: '/inventory/inventory', icon: 'Box', color: '#e6a23c' },
  { name: '员工管理', path: '/hr/employee', icon: 'UserFilled', color: '#f56c6c' },
  { name: '订单管理', path: '/sales/order', icon: 'Document', color: '#909399' },
  { name: '账户管理', path: '/finance/account', icon: 'Wallet', color: '#06c0f0' }
])

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN')
}

const loadStats = async () => {
  try {
    // 获取客户数量
    const customers = await api.getCustomers()
    stats.value.customers = Array.isArray(customers) ? customers.length : 0

    // 获取产品数量
    const products = await api.getProducts()
    stats.value.products = Array.isArray(products) ? products.length : 0

    // 获取库存数量
    const inventories = await api.getInventories()
    stats.value.inventories = Array.isArray(inventories) ? inventories.length : 0

    // 获取员工数量
    const employees = await api.getEmployees()
    stats.value.employees = Array.isArray(employees) ? employees.length : 0
  } catch (error) {
    console.log('加载统计数据失败:', error)
  }
}

onMounted(() => {
  updateTime()
  setInterval(updateTime, 1000)
  loadStats()
})
</script>
