<template>
  <div class="page-content">
    <el-card class="content-card">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: bold; font-size: 16px;">测试数据管理</span>
          <el-button type="primary" @click="generateTestData" :loading="generating">
            <el-icon><Plus /></el-icon>
            生成测试数据
          </el-button>
        </div>
      </template>

      <el-alert
        title="提示"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        点击"生成测试数据"按钮，可以为各模块生成示例数据，方便进行功能测试。数据将包括客户、产品、仓库、部门、职位、员工、账户和库存等基础数据。
      </el-alert>

      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic title="客户数量" :value="dataStatus.customers" :value-style="{ color: '#409eff' }">
            <template #suffix>
              <span style="font-size: 16px;">个</span>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="产品数量" :value="dataStatus.products" :value-style="{ color: '#67c23a' }">
            <template #suffix>
              <span style="font-size: 16px;">个</span>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="员工数量" :value="dataStatus.employees" :value-style="{ color: '#f56c6c' }">
            <template #suffix>
              <span style="font-size: 16px;">人</span>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="是否有测试数据" :value="dataStatus.has_test_data ? '是' : '否'" :value-style="{ color: dataStatus.has_test_data ? '#67c23a' : '#f56c6c' }">
          </el-statistic>
        </el-col>
      </el-row>

      <el-divider />

      <h3 style="margin-bottom: 15px;">测试数据内容说明</h3>
      <el-table :data="testDataInfo" border stripe>
        <el-table-column prop="module" label="模块" width="150" />
        <el-table-column prop="item" label="数据项" width="150" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="count" label="数量" width="80" align="center" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
import { Plus } from '@element-plus/icons-vue'

const generating = ref(false)

const dataStatus = ref({
  customers: 0,
  products: 0,
  employees: 0,
  has_test_data: false
})

const testDataInfo = ref([
  { module: '销售模块', item: '客户数据', description: '包括阿里巴巴、腾讯、百度、京东、字节跳动等知名企业客户数据', count: 5 },
  { module: '生产模块', item: '产品数据', description: '包括智能笔记本电脑、无线蓝牙耳机、智能手表、机械键盘、4K显示器等产品', count: 5 },
  { module: '库存模块', item: '仓库数据', description: '包括北京中心仓库、上海分仓库、深圳保税仓等仓库数据', count: 3 },
  { module: '库存模块', item: '库存数据', description: '各产品在不同仓库的库存数据', count: 5 },
  { module: '财务模块', item: '账户数据', description: '包括工商银行基本账户、建设银行一般账户、现金账户等', count: 3 },
  { module: '人事模块', item: '部门数据', description: '包括总经办、销售部、生产部、财务部、人事部等部门', count: 5 },
  { module: '人事模块', item: '职位数据', description: '包括总经理、部门经理、销售代表、生产工人、会计等职位', count: 5 },
  { module: '人事模块', item: '员工数据', description: '示例员工数据，包含完整的人事信息', count: 5 }
])

const loadDataStatus = async () => {
  try {
    const result = await api.getTestDataStatus()
    dataStatus.value = {
      customers: result.customers || 0,
      products: result.products || 0,
      employees: result.employees || 0,
      has_test_data: result.has_test_data || false
    }
  } catch (error) {
    console.log('加载数据状态失败:', error)
  }
}

const generateTestData = async () => {
  generating.value = true
  try {
    await api.generateTestData()
    ElMessage.success('测试数据生成成功！')
    await loadDataStatus()
  } catch (error) {
    ElMessage.error('测试数据生成失败，请确保后端服务已启动')
  } finally {
    generating.value = false
  }
}

onMounted(() => {
  loadDataStatus()
})
</script>
