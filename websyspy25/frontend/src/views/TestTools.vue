<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">测试工具</h2>
    </div>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>生成测试数据</span>
              <el-tag type="info">开发环境</el-tag>
            </div>
          </template>
          
          <el-form :model="generateForm" label-width="120px">
            <el-form-item label="教练数量">
              <el-input-number v-model="generateForm.coachCount" :min="1" :max="20" />
            </el-form-item>
            <el-form-item label="会员数量">
              <el-input-number v-model="generateForm.memberCount" :min="1" :max="50" />
            </el-form-item>
            <el-form-item label="课程包/会员">
              <el-input-number v-model="generateForm.packagePerMember" :min="1" :max="5" />
            </el-form-item>
            <el-form-item label="课时/课程包">
              <el-input-number v-model="generateForm.lessonsPerPackage" :min="1" :max="20" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="handleGenerateAll" :loading="generating">
                <el-icon><MagicStick /></el-icon>
                一键生成全部测试数据
              </el-button>
            </el-form-item>
          </el-form>
          
          <el-divider>单独生成</el-divider>
          
          <el-row :gutter="10">
            <el-col :span="8">
              <el-button type="primary" plain @click="handleGenerateCoaches" style="width: 100%;">
                生成教练数据
              </el-button>
            </el-col>
            <el-col :span="8">
              <el-button type="success" plain @click="handleGenerateMembers" style="width: 100%;">
                生成会员数据
              </el-button>
            </el-col>
          </el-row>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>数据管理</span>
              <el-tag type="warning">危险操作</el-tag>
            </div>
          </template>
          
          <el-alert
            title="警告：以下操作将删除数据"
            type="warning"
            :closable="false"
            style="margin-bottom: 20px;"
          >
            <template #default>
              清空操作将删除数据库中的所有数据，请谨慎使用！
            </template>
          </el-alert>
          
          <el-button type="danger" @click="handleClearAll" :loading="clearing" style="width: 100%; height: 50px;">
            <el-icon :size="20"><Delete /></el-icon>
            <span style="font-size: 16px; font-weight: bold;">清空所有测试数据</span>
          </el-button>
          
          <el-divider>API文档</el-divider>
          
          <el-card shadow="hover" style="margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <div>
                <strong>Swagger UI 文档</strong>
                <p style="margin: 5px 0; color: #909399; font-size: 12px;">交互式API文档，支持在线测试</p>
              </div>
              <el-button type="primary" @click="openApiDocs">
                打开文档
              </el-button>
            </div>
          </el-card>
          
          <el-card shadow="hover">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <div>
                <strong>ReDoc 文档</strong>
                <p style="margin: 5px 0; color: #909399; font-size: 12px;">美观的API文档展示</p>
              </div>
              <el-button type="success" @click="openRedoc">
                打开文档
              </el-button>
            </div>
          </el-card>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 20px;">
      <template #header>
        <span>快速操作指南</span>
      </template>
      
      <el-steps :active="3" finish-status="success" align-center>
        <el-step title="启动后端" description="运行后端服务 python main.py" />
        <el-step title="生成测试数据" description="点击一键生成按钮" />
        <el-step title="浏览功能" description="在各功能页面查看数据" />
        <el-step title="API测试" description="使用Swagger文档测试接口" />
      </el-steps>
      
      <el-row :gutter="20" style="margin-top: 30px;">
        <el-col :span="6">
          <el-card shadow="hover">
            <template #header>
              <div style="text-align: center;">
                <el-icon :size="30" color="#409EFF"><UserFilled /></el-icon>
                <div style="margin-top: 5px;">教练档案</div>
              </div>
            </template>
            <p style="font-size: 12px; color: #606266; text-align: center;">
              管理教练基本信息、擅长领域、排班时间
            </p>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <template #header>
              <div style="text-align: center;">
                <el-icon :size="30" color="#67C23A"><Team /></el-icon>
                <div style="margin-top: 5px;">会员管理</div>
              </div>
            </template>
            <p style="font-size: 12px; color: #606266; text-align: center;">
              管理会员信息、购买课程包
            </p>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <template #header>
              <div style="text-align: center;">
                <el-icon :size="30" color="#E6A23C"><Calendar /></el-icon>
                <div style="margin-top: 5px;">课时管理</div>
              </div>
            </template>
            <p style="font-size: 12px; color: #606266; text-align: center;">
              课时预约、核销、补课、冻结
            </p>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <template #header>
              <div style="text-align: center;">
                <el-icon :size="30" color="#F56C6C"><TrendCharts /></el-icon>
                <div style="margin-top: 5px;">业绩追踪</div>
              </div>
            </template>
            <p style="font-size: 12px; color: #606266; text-align: center;">
              按月/季度统计教练业绩
            </p>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/api'

const generating = ref(false)
const clearing = ref(false)

const generateForm = reactive({
  coachCount: 5,
  memberCount: 15,
  packagePerMember: 2,
  lessonsPerPackage: 8
})

// 一键生成全部测试数据
const handleGenerateAll = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要生成 ${generateForm.coachCount} 位教练、${generateForm.memberCount} 位会员的测试数据吗？`,
      '确认生成',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    generating.value = true
    
    const res = await api.test.generateAll({
      coach_count: generateForm.coachCount,
      member_count: generateForm.memberCount,
      package_per_member: generateForm.packagePerMember,
      lessons_per_package: generateForm.lessonsPerPackage
    })
    
    ElMessage.success(`测试数据生成成功！教练: ${res.counts.coaches} 位, 会员: ${res.counts.members} 位`)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('生成测试数据失败:', error)
      ElMessage.error('生成测试数据失败')
    }
  } finally {
    generating.value = false
  }
}

// 生成教练数据
const handleGenerateCoaches = async () => {
  try {
    generating.value = true
    const res = await api.test.generateCoaches({ count: generateForm.coachCount })
    ElMessage.success(`成功生成 ${res.count} 位教练`)
  } catch (error) {
    console.error('生成教练数据失败:', error)
    ElMessage.error('生成教练数据失败')
  } finally {
    generating.value = false
  }
}

// 生成会员数据
const handleGenerateMembers = async () => {
  try {
    generating.value = true
    const res = await api.test.generateMembers({ count: generateForm.memberCount })
    ElMessage.success(`成功生成 ${res.count} 位会员`)
  } catch (error) {
    console.error('生成会员数据失败:', error)
    ElMessage.error('生成会员数据失败')
  } finally {
    generating.value = false
  }
}

// 清空所有测试数据
const handleClearAll = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有测试数据吗？此操作不可恢复！',
      '警告',
      {
        confirmButtonText: '确定清空',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    clearing.value = true
    await api.test.clearAll()
    ElMessage.success('所有测试数据已清空')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空数据失败:', error)
      ElMessage.error('清空数据失败')
    }
  } finally {
    clearing.value = false
  }
}

// 打开API文档
const openApiDocs = () => {
  window.open('http://localhost:8000/api/docs', '_blank')
}

// 打开ReDoc文档
const openRedoc = () => {
  window.open('http://localhost:8000/api/redoc', '_blank')
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
