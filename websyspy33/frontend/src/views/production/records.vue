<template>
  <div class="records-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>生产记录</span>
          <div class="header-buttons">
            <el-button type="primary" @click="handleExport">
              <el-icon><Download /></el-icon>
              导出数据
            </el-button>
          </div>
        </div>
      </template>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="批次号">
          <el-input
            v-model="searchForm.batch_no"
            placeholder="请输入批次号"
            clearable
          />
        </el-form-item>
        <el-form-item label="强度等级">
          <el-select v-model="searchForm.strength_grade" placeholder="请选择" clearable>
            <el-option label="C15" value="C15" />
            <el-option label="C20" value="C20" />
            <el-option label="C25" value="C25" />
            <el-option label="C30" value="C30" />
            <el-option label="C35" value="C35" />
            <el-option label="C40" value="C40" />
            <el-option label="C45" value="C45" />
            <el-option label="C50" value="C50" />
          </el-select>
        </el-form-item>
        <el-form-item label="是否正常">
          <el-select v-model="searchForm.is_normal" placeholder="请选择" clearable>
            <el-option label="正常" :value="true" />
            <el-option label="异常" :value="false" />
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
        <el-table-column prop="record_no" label="记录编号" width="160" />
        <el-table-column prop="batch_no" label="批次号" width="140" />
        <el-table-column prop="mix_no" label="盘号" width="80" />
        <el-table-column prop="mixing_time" label="搅拌时间(秒)" width="120" />
        <el-table-column prop="actual_cement" label="实际水泥(kg)" width="120" />
        <el-table-column prop="actual_sand" label="实际砂(kg)" width="110" />
        <el-table-column prop="actual_stone" label="实际石(kg)" width="110" />
        <el-table-column prop="actual_water" label="实际水(kg)" width="110" />
        <el-table-column prop="actual_water_cement_ratio" label="实际水胶比" width="110">
          <template #default="scope">
            <span :class="getWcrClass(scope.row)">
              {{ scope.row.actual_water_cement_ratio }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="design_water_cement_ratio" label="设计水胶比" width="100" />
        <el-table-column prop="deviation_rate" label="偏差率(%)" width="100">
          <template #default="scope">
            <el-tag :type="getDeviationTagType(scope.row.deviation_rate)" size="small">
              {{ scope.row.deviation_rate > 0 ? '+' : '' }}{{ scope.row.deviation_rate }}%
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="slump_actual" label="坍落度(mm)" width="100" />
        <el-table-column prop="temperature" label="温度(℃)" width="100" />
        <el-table-column prop="is_normal" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_normal ? 'success' : 'danger'" effect="dark">
              {{ scope.row.is_normal ? '正常' : '异常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="anomaly_reason" label="异常原因" min-width="150" show-overflow-tooltip>
          <template #default="scope">
            {{ scope.row.anomaly_reason || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleView(scope.row)">
              详情
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
      title="生产记录详情"
      width="900px"
    >
      <el-descriptions :column="3" border>
        <el-descriptions-item label="记录编号">{{ currentRecord.record_no }}</el-descriptions-item>
        <el-descriptions-item label="批次号">{{ currentRecord.batch_no }}</el-descriptions-item>
        <el-descriptions-item label="盘号">{{ currentRecord.mix_no }}</el-descriptions-item>
        <el-descriptions-item label="搅拌时间">{{ currentRecord.mixing_time }} 秒</el-descriptions-item>
        <el-descriptions-item label="坍落度">{{ currentRecord.slump_actual }} mm</el-descriptions-item>
        <el-descriptions-item label="温度">{{ currentRecord.temperature }} ℃</el-descriptions-item>
        <el-descriptions-item label="状态" :span="3">
          <el-tag :type="currentRecord.is_normal ? 'success' : 'danger'" effect="dark">
            {{ currentRecord.is_normal ? '正常' : '异常' }}
          </el-tag>
          <span v-if="currentRecord.anomaly_reason" style="margin-left: 10px; color: #F56C6C;">
            异常原因：{{ currentRecord.anomaly_reason }}
          </span>
        </el-descriptions-item>
      </el-descriptions>
      
      <el-divider>投料记录</el-divider>
      
      <el-table :data="feedingData" style="width: 100%">
        <el-table-column label="材料名称" width="120">
          <template #default="scope">
            <span style="font-weight: bold;">{{ scope.row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="设计用量(kg)" prop="design" width="130" />
        <el-table-column label="实际用量(kg)" prop="actual" width="130" />
        <el-table-column label="偏差量(kg)" width="120">
          <template #default="scope">
            <span :class="scope.row.deviation >= 0 ? 'text-red' : 'text-green'">
              {{ scope.row.deviation > 0 ? '+' : '' }}{{ scope.row.deviation }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="偏差率(%)" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.deviationRate > 2 ? 'danger' : scope.row.deviationRate < -2 ? 'warning' : 'success'" size="small">
              {{ scope.row.deviationRate > 0 ? '+' : '' }}{{ scope.row.deviationRate }}%
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="投料顺序" prop="sequence" width="100" />
      </el-table>
      
      <el-divider>水胶比对比</el-divider>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-statistic title="设计水胶比" :value="currentRecord.design_water_cement_ratio" :precision="3">
            <template #suffix>
              <span class="stat-unit">（允许偏差±2%）</span>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="12">
          <el-statistic 
            title="实际水胶比" 
            :value="currentRecord.actual_water_cement_ratio" 
            :precision="3"
            :value-style="currentRecord.is_normal ? { color: '#67C23A' } : { color: '#F56C6C' }"
          >
            <template #suffix>
              <el-tag :type="currentRecord.is_normal ? 'success' : 'danger'" effect="dark" style="margin-left: 10px;">
                {{ currentRecord.is_normal ? '合格' : '不合格' }}
              </el-tag>
            </template>
          </el-statistic>
        </el-col>
      </el-row>
      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const currentRecord = ref({})
const feedingData = ref([])

const searchForm = reactive({
  batch_no: '',
  strength_grade: '',
  is_normal: null
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const getWcrClass = (row) => {
  if (!row.is_normal) return 'text-red font-bold'
  return ''
}

const getDeviationTagType = (deviation) => {
  if (Math.abs(deviation) > 2) return 'danger'
  if (Math.abs(deviation) > 1) return 'warning'
  return 'success'
}

const fetchData = async () => {
  loading.value = true
  try {
    tableData.value = [
      {
        id: 1,
        record_no: 'PR202412010001',
        batch_id: 1,
        batch_no: 'PB20241201001',
        mix_no: 1,
        mixing_time: 120,
        actual_cement: 360.5,
        actual_sand: 748.0,
        actual_stone: 1102.0,
        actual_water: 178.0,
        actual_admixture: 5.35,
        actual_fly_ash: 72.0,
        actual_water_cement_ratio: 0.495,
        design_water_cement_ratio: 0.500,
        deviation_rate: -1.0,
        slump_actual: 155,
        temperature: 22.5,
        is_normal: true,
        anomaly_reason: null,
        operator: '操作员甲'
      },
      {
        id: 2,
        record_no: 'PR202412010002',
        batch_id: 1,
        batch_no: 'PB20241201001',
        mix_no: 2,
        mixing_time: 115,
        actual_cement: 358.0,
        actual_sand: 752.0,
        actual_stone: 1098.0,
        actual_water: 182.0,
        actual_admixture: 5.40,
        actual_fly_ash: 70.0,
        actual_water_cement_ratio: 0.508,
        design_water_cement_ratio: 0.500,
        deviation_rate: 1.6,
        slump_actual: 160,
        temperature: 23.0,
        is_normal: true,
        anomaly_reason: null,
        operator: '操作员甲'
      },
      {
        id: 3,
        record_no: 'PR202412010003',
        batch_id: 2,
        batch_no: 'PB20241201002',
        mix_no: 1,
        mixing_time: 130,
        actual_cement: 395.0,
        actual_sand: 715.0,
        actual_stone: 1085.0,
        actual_water: 180.0,
        actual_admixture: 6.10,
        actual_fly_ash: 82.0,
        actual_water_cement_ratio: 0.452,
        design_water_cement_ratio: 0.425,
        deviation_rate: 6.35,
        slump_actual: 190,
        temperature: 21.5,
        is_normal: false,
        anomaly_reason: '水胶比偏差超过允许范围',
        operator: '操作员乙'
      }
    ]
    pagination.total = 3
  } catch (error) {
    console.error('获取生产记录数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.batch_no = ''
  searchForm.strength_grade = ''
  searchForm.is_normal = null
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

const handleView = (row) => {
  currentRecord.value = { ...row }
  
  feedingData.value = [
    { 
      name: '水泥', 
      design: 360.0, 
      actual: row.actual_cement, 
      deviation: round(row.actual_cement - 360.0, 1), 
      deviationRate: round((row.actual_cement - 360.0) / 360.0 * 100, 2),
      sequence: '第2步'
    },
    { 
      name: '砂', 
      design: 750.0, 
      actual: row.actual_sand, 
      deviation: round(row.actual_sand - 750.0, 1), 
      deviationRate: round((row.actual_sand - 750.0) / 750.0 * 100, 2),
      sequence: '第1步'
    },
    { 
      name: '石', 
      design: 1100.0, 
      actual: row.actual_stone, 
      deviation: round(row.actual_stone - 1100.0, 1), 
      deviationRate: round((row.actual_stone - 1100.0) / 1100.0 * 100, 2),
      sequence: '第1步'
    },
    { 
      name: '水', 
      design: 180.0, 
      actual: row.actual_water, 
      deviation: round(row.actual_water - 180.0, 1), 
      deviationRate: round((row.actual_water - 180.0) / 180.0 * 100, 2),
      sequence: '第4步'
    },
    { 
      name: '外加剂', 
      design: 5.4, 
      actual: row.actual_admixture || 5.4, 
      deviation: round((row.actual_admixture || 5.4) - 5.4, 2), 
      deviationRate: round(((row.actual_admixture || 5.4) - 5.4) / 5.4 * 100, 2),
      sequence: '第3步'
    },
    { 
      name: '粉煤灰', 
      design: 70.0, 
      actual: row.actual_fly_ash || 0, 
      deviation: round((row.actual_fly_ash || 0) - 70.0, 1), 
      deviationRate: round(((row.actual_fly_ash || 0) - 70.0) / 70.0 * 100, 2),
      sequence: '第2步'
    }
  ]
  
  dialogVisible.value = true
}

const round = (num, precision) => {
  return Number(num.toFixed(precision))
}

const handleExport = () => {
  ElMessage.info('导出功能开发中...')
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.records-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.text-red {
  color: #F56C6C;
  font-weight: bold;
}

.text-green {
  color: #67C23A;
  font-weight: bold;
}

.stat-unit {
  font-size: 14px;
  color: #909399;
  font-weight: normal;
}
</style>
