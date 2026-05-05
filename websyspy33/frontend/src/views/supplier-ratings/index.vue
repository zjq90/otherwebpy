<template>
  <div class="supplier-ratings-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>供应商评级</span>
          <div class="header-buttons">
            <el-button type="primary" @click="handleCalculate">
              <el-icon><RefreshRight /></el-icon>
              计算评级
            </el-button>
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              新增评级
            </el-button>
          </div>
        </div>
      </template>
      
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon icon-green">
                <el-icon size="28"><Star /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.aLevel }}</div>
                <div class="stat-label">A级供应商</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon icon-orange">
                <el-icon size="28"><Star /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.bLevel }}</div>
                <div class="stat-label">B级供应商</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon icon-red">
                <el-icon size="28"><Star /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.cLevel }}</div>
                <div class="stat-label">C级供应商</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon icon-blue">
                <el-icon size="28"><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.avgScore }}分</div>
                <div class="stat-label">平均评分</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="评级编号">
          <el-input
            v-model="searchForm.rating_no"
            placeholder="请输入评级编号"
            clearable
          />
        </el-form-item>
        <el-form-item label="供应商">
          <el-input
            v-model="searchForm.supplier_name"
            placeholder="请输入供应商名称"
            clearable
          />
        </el-form-item>
        <el-form-item label="评级周期">
          <el-select v-model="searchForm.rating_period" placeholder="请选择" clearable>
            <el-option label="2024年第一季度" value="2024年第一季度" />
            <el-option label="2024年第二季度" value="2024年第二季度" />
            <el-option label="2024年第三季度" value="2024年第三季度" />
            <el-option label="2024年第四季度" value="2024年第四季度" />
          </el-select>
        </el-form-item>
        <el-form-item label="评级等级">
          <el-select v-model="searchForm.rating_level" placeholder="请选择" clearable>
            <el-option label="A级" value="A级">
              <span style="color: #67C23A;">A级（≥90分）</span>
            </el-option>
            <el-option label="B级" value="B级">
              <span style="color: #E6A23C;">B级（75-89分）</span>
            </el-option>
            <el-option label="C级" value="C级">
              <span style="color: #F56C6C;">C级（60-74分）</span>
            </el-option>
            <el-option label="D级" value="D级">
              <span style="color: #909399;">D级（<60分）</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="tableData" style="width: 100%" v-loading="loading" stripe>
        <el-table-column prop="rating_no" label="评级编号" width="140" />
        <el-table-column prop="supplier_name" label="供应商名称" min-width="180" />
        <el-table-column prop="rating_period" label="评级周期" width="130" />
        <el-table-column prop="rating_date" label="评级日期" width="110" />
        <el-table-column prop="quality_score" label="质量评分" width="100">
          <template #default="scope">
            <span :class="getScoreClass(scope.row.quality_score, 40)">
              {{ scope.row.quality_score }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="delivery_score" label="交付评分" width="100">
          <template #default="scope">
            <span :class="getScoreClass(scope.row.delivery_score, 30)">
              {{ scope.row.delivery_score }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="price_score" label="价格评分" width="100">
          <template #default="scope">
            <span :class="getScoreClass(scope.row.price_score, 20)">
              {{ scope.row.price_score }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="service_score" label="服务评分" width="100">
          <template #default="scope">
            <span :class="getScoreClass(scope.row.service_score, 10)">
              {{ scope.row.service_score }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="total_score" label="总分" width="100">
          <template #default="scope">
            <span :class="getTotalScoreClass(scope.row.total_score)">
              <strong>{{ scope.row.total_score }}</strong>
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="rating_level" label="评级等级" width="100">
          <template #default="scope">
            <el-tag :type="getRatingTagType(scope.row.rating_level)" effect="dark">
              {{ scope.row.rating_level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="inspection_count" label="检验批次" width="100" />
        <el-table-column prop="pass_rate" label="合格率(%)" width="110">
          <template #default="scope">
            <el-progress 
              :percentage="scope.row.pass_rate" 
              :status="scope.row.pass_rate >= 95 ? 'success' : scope.row.pass_rate >= 85 ? '' : 'exception'"
              :stroke-width="12"
              :text-inside="true"
            />
          </template>
        </el-table-column>
        <el-table-column prop="delivery_count" label="交付批次" width="100" />
        <el-table-column prop="on_time_rate" label="及时率(%)" width="110">
          <template #default="scope">
            <el-progress 
              :percentage="scope.row.on_time_rate" 
              :status="scope.row.on_time_rate >= 95 ? 'success' : scope.row.on_time_rate >= 85 ? '' : 'exception'"
              :stroke-width="12"
              :text-inside="true"
            />
          </template>
        </el-table-column>
        <el-table-column prop="rater" label="评级人" width="90" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.status === '已生效' ? 'success' : 'info'" size="small">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleView(scope.row)">
              查看
            </el-button>
            <el-button type="primary" link v-if="scope.row.status === '草稿'" @click="handleEdit(scope.row)">
              编辑
            </el-button>
            <el-button type="success" link v-if="scope.row.status === '草稿'" @click="handleActivate(scope.row)">
              生效
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>
    
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
    >
      <el-descriptions :column="3" border v-if="isView">
        <el-descriptions-item label="评级编号">{{ currentRating.rating_no }}</el-descriptions-item>
        <el-descriptions-item label="供应商">{{ currentRating.supplier_name }}</el-descriptions-item>
        <el-descriptions-item label="评级周期">{{ currentRating.rating_period }}</el-descriptions-item>
        <el-descriptions-item label="质量评分">{{ currentRating.quality_score }}/40</el-descriptions-item>
        <el-descriptions-item label="交付评分">{{ currentRating.delivery_score }}/30</el-descriptions-item>
        <el-descriptions-item label="价格评分">{{ currentRating.price_score }}/20</el-descriptions-item>
        <el-descriptions-item label="服务评分">{{ currentRating.service_score }}/10</el-descriptions-item>
        <el-descriptions-item label="总分">
          <span :class="getTotalScoreClass(currentRating.total_score)">
            <strong>{{ currentRating.total_score }}</strong>
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="评级等级">
          <el-tag :type="getRatingTagType(currentRating.rating_level)" effect="dark">
            {{ currentRating.rating_level }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
      
      <el-divider v-if="isView">详细数据</el-divider>
      
      <el-row :gutter="20" v-if="isView">
        <el-col :span="12">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="检验批次">{{ currentRating.inspection_count }}批</el-descriptions-item>
            <el-descriptions-item label="合格率">{{ currentRating.pass_rate }}%</el-descriptions-item>
          </el-descriptions>
        </el-col>
        <el-col :span="12">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="交付批次">{{ currentRating.delivery_count }}批</el-descriptions-item>
            <el-descriptions-item label="及时率">{{ currentRating.on_time_rate }}%</el-descriptions-item>
          </el-descriptions>
        </el-col>
      </el-row>
      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const isView = ref(false)
const currentRating = ref({})

const stats = reactive({
  aLevel: 5,
  bLevel: 7,
  cLevel: 3,
  avgScore: 82.5
})

const searchForm = reactive({
  rating_no: '',
  supplier_name: '',
  rating_period: '',
  rating_level: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const dialogTitle = computed(() => {
  return '查看供应商评级'
})

const getScoreClass = (score, maxScore) => {
  const percentage = score / maxScore * 100
  if (percentage >= 90) return 'text-green font-bold'
  if (percentage >= 75) return 'text-orange font-bold'
  return 'text-red font-bold'
}

const getTotalScoreClass = (score) => {
  if (score >= 90) return 'text-green font-bold'
  if (score >= 75) return 'text-orange font-bold'
  if (score >= 60) return 'text-red font-bold'
  return 'text-gray font-bold'
}

const getRatingTagType = (level) => {
  const typeMap = {
    'A级': 'success',
    'B级': 'warning',
    'C级': 'danger',
    'D级': 'info'
  }
  return typeMap[level] || 'info'
}

const fetchData = async () => {
  loading.value = true
  try {
    tableData.value = [
      {
        id: 1,
        rating_no: 'SR2024Q1001',
        supplier_id: 1,
        supplier_name: '山水水泥有限公司',
        rating_period: '2024年第一季度',
        rating_date: '2024-04-01',
        quality_score: 38.5,
        delivery_score: 28.0,
        price_score: 18.0,
        service_score: 9.5,
        total_score: 94.0,
        rating_level: 'A级',
        inspection_count: 25,
        pass_rate: 98.5,
        delivery_count: 30,
        on_time_rate: 96.7,
        rater: '评级员A',
        status: '已生效'
      },
      {
        id: 2,
        rating_no: 'SR2024Q1002',
        supplier_id: 2,
        supplier_name: '海螺水泥集团',
        rating_period: '2024年第一季度',
        rating_date: '2024-04-01',
        quality_score: 32.0,
        delivery_score: 25.5,
        price_score: 16.5,
        service_score: 8.0,
        total_score: 82.0,
        rating_level: 'B级',
        inspection_count: 20,
        pass_rate: 92.0,
        delivery_count: 25,
        on_time_rate: 88.0,
        rater: '评级员B',
        status: '已生效'
      },
      {
        id: 3,
        rating_no: 'SR2024Q1003',
        supplier_id: 3,
        supplier_name: '华新水泥股份',
        rating_period: '2024年第一季度',
        rating_date: '2024-04-01',
        quality_score: 28.0,
        delivery_score: 22.0,
        price_score: 14.0,
        service_score: 7.0,
        total_score: 71.0,
        rating_level: 'C级',
        inspection_count: 15,
        pass_rate: 85.0,
        delivery_count: 18,
        on_time_rate: 78.0,
        rater: '评级员C',
        status: '草稿'
      }
    ]
    pagination.total = 3
  } catch (error) {
    console.error('获取供应商评级数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.rating_no = ''
  searchForm.supplier_name = ''
  searchForm.rating_period = ''
  searchForm.rating_level = ''
  handleSearch()
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchData()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchData()
}

const handleCalculate = () => {
  ElMessageBox.confirm(
    '确定要重新计算所有供应商评级吗？计算完成后可以查看结果。',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    ElMessage.success('评级计算完成')
    fetchData()
  }).catch(() => {})
}

const handleAdd = () => {
  ElMessage.info('新增评级功能开发中...')
}

const handleView = (row) => {
  currentRating.value = { ...row }
  isView.value = true
  dialogVisible.value = true
}

const handleEdit = (row) => {
  ElMessage.info('编辑评级功能开发中...')
}

const handleActivate = (row) => {
  ElMessageBox.confirm(
    `确定要生效供应商"${row.supplier_name}"的评级吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'success'
    }
  ).then(() => {
    row.status = '已生效'
    ElMessage.success('评级已生效')
    fetchData()
  }).catch(() => {})
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.supplier-ratings-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-buttons {
  display: flex;
  gap: 10px;
}

.search-form {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.icon-green {
  background: linear-gradient(135deg, #67C23A, #85ce61);
}

.icon-orange {
  background: linear-gradient(135deg, #E6A23C, #ebb563);
}

.icon-red {
  background: linear-gradient(135deg, #F56C6C, #f78989);
}

.icon-blue {
  background: linear-gradient(135deg, #409EFF, #66b1ff);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.text-green {
  color: #67C23A;
}

.text-orange {
  color: #E6A23C;
}

.text-red {
  color: #F56C6C;
}

.text-gray {
  color: #909399;
}

.font-bold {
  font-weight: bold;
}
</style>
