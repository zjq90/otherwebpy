<template>
  <div class="quality-reports-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>质量报告</span>
          <div class="header-buttons">
            <el-button type="primary" @click="handleGenerate">
              <el-icon><DocumentAdd /></el-icon>
              生成报告
            </el-button>
          </div>
        </div>
      </template>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="报告编号">
          <el-input
            v-model="searchForm.report_no"
            placeholder="请输入报告编号"
            clearable
          />
        </el-form-item>
        <el-form-item label="报告类型">
          <el-select v-model="searchForm.report_type" placeholder="请选择" clearable>
            <el-option label="出厂合格证" value="出厂合格证" />
            <el-option label="质量追溯报告" value="质量追溯报告" />
            <el-option label="强度检测报告" value="强度检测报告" />
          </el-select>
        </el-form-item>
        <el-form-item label="检测结果">
          <el-select v-model="searchForm.overall_result" placeholder="请选择" clearable>
            <el-option label="合格" value="合格" />
            <el-option label="不合格" value="不合格" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable>
            <el-option label="草稿" value="草稿" />
            <el-option label="已发布" value="已发布" />
            <el-option label="已作废" value="已作废" />
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
        <el-table-column prop="report_no" label="报告编号" width="140" />
        <el-table-column prop="report_type" label="报告类型" width="130">
          <template #default="scope">
            <el-tag :type="getReportTypeTagType(scope.row.report_type)" size="small">
              {{ scope.row.report_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="batch_no" label="关联批次" width="130" />
        <el-table-column prop="project_name" label="工程项目" min-width="150" show-overflow-tooltip />
        <el-table-column prop="strength_grade" label="强度等级" width="100">
          <template #default="scope">
            <el-tag type="primary">{{ scope.row.strength_grade }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="report_date" label="报告日期" width="110" />
        <el-table-column prop="generated_by" label="生成人" width="90" />
        <el-table-column prop="overall_result" label="检测结果" width="90">
          <template #default="scope">
            <el-tag :type="scope.row.is_qualified ? 'success' : 'danger'" effect="dark">
              {{ scope.row.overall_result }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleView(scope.row)">
              查看
            </el-button>
            <el-button type="primary" link @click="handlePreview(scope.row)">
              预览
            </el-button>
            <el-button type="primary" link v-if="scope.row.status === '草稿'" @click="handleEdit(scope.row)">
              编辑
            </el-button>
            <el-button type="success" link v-if="scope.row.status === '草稿'" @click="handlePublish(scope.row)">
              发布
            </el-button>
            <el-button type="warning" link v-if="scope.row.status === '已发布'" @click="handleVoid(scope.row)">
              作废
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
      width="900px"
    >
      <el-descriptions :column="3" border>
        <el-descriptions-item label="报告编号">{{ currentReport.report_no }}</el-descriptions-item>
        <el-descriptions-item label="报告类型">{{ currentReport.report_type }}</el-descriptions-item>
        <el-descriptions-item label="报告日期">{{ currentReport.report_date }}</el-descriptions-item>
        <el-descriptions-item label="关联批次">{{ currentReport.batch_no }}</el-descriptions-item>
        <el-descriptions-item label="工程项目">{{ currentReport.project_name }}</el-descriptions-item>
        <el-descriptions-item label="强度等级">{{ currentReport.strength_grade }}</el-descriptions-item>
        <el-descriptions-item label="生成人">{{ currentReport.generated_by }}</el-descriptions-item>
        <el-descriptions-item label="检测结果">
          <el-tag :type="currentReport.is_qualified ? 'success' : 'danger'" effect="dark">
            {{ currentReport.overall_result }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentReport.status)">
            {{ currentReport.status }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
      
      <el-divider>报告摘要</el-divider>
      
      <el-card class="report-card">
        <div class="report-summary">
          <h4>质量报告摘要</h4>
          <p>{{ currentReport.summary }}</p>
        </div>
      </el-card>
      
      <el-divider>检测结论</el-divider>
      
      <el-card class="report-card">
        <div class="report-conclusion">
          <h4>检测结论</h4>
          <p :style="{ color: currentReport.is_qualified ? '#67C23A' : '#F56C6C', fontWeight: 'bold' }">
            {{ currentReport.conclusion }}
          </p>
        </div>
      </el-card>
      
      <el-divider>详细数据</el-divider>
      
      <el-table :data="reportDetails" style="width: 100%">
        <el-table-column label="检测项目" prop="item" width="150" />
        <el-table-column label="设计值/标准值" prop="design" min-width="150" />
        <el-table-column label="实际检测值" prop="actual" min-width="150" />
        <el-table-column label="偏差" prop="deviation" width="100">
          <template #default="scope">
            <span :class="scope.row.deviation === '合格' ? 'text-green' : 'text-red'">
              {{ scope.row.deviation }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="结果" prop="result" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.result === '合格' ? 'success' : 'danger'" size="small">
              {{ scope.row.result }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
    
    <el-dialog
      v-model="generateDialogVisible"
      title="生成质量报告"
      width="600px"
    >
      <el-form ref="generateFormRef" :model="generateForm" :rules="generateRules" label-width="120px">
        <el-form-item label="选择批次" prop="batch_id">
          <el-select v-model="generateForm.batch_id" placeholder="请选择生产批次" style="width: 100%">
            <el-option v-for="batch in batches" :key="batch.id" :label="batch.batch_no + ' - ' + batch.project_name" :value="batch.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="报告类型" prop="report_type">
          <el-select v-model="generateForm.report_type" placeholder="请选择报告类型" style="width: 100%">
            <el-option label="出厂合格证" value="出厂合格证" />
            <el-option label="质量追溯报告" value="质量追溯报告" />
            <el-option label="强度检测报告" value="强度检测报告" />
          </el-select>
        </el-form-item>
        <el-form-item label="报告日期" prop="report_date">
          <el-date-picker
            v-model="generateForm.report_date"
            type="date"
            placeholder="请选择报告日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleGenerateConfirm">生成报告</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const generateDialogVisible = ref(false)
const isView = ref(false)
const formRef = ref(null)
const generateFormRef = ref(null)
const currentReport = ref({})
const reportDetails = ref([])
const batches = ref([])

const searchForm = reactive({
  report_no: '',
  report_type: '',
  overall_result: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const generateForm = reactive({
  batch_id: null,
  report_type: '出厂合格证',
  report_date: dayjs().format('YYYY-MM-DD')
})

const generateRules = {
  batch_id: [{ required: true, message: '请选择生产批次', trigger: 'change' }],
  report_type: [{ required: true, message: '请选择报告类型', trigger: 'change' }]
}

const dialogTitle = computed(() => {
  return '查看质量报告'
})

const getReportTypeTagType = (type) => {
  const typeMap = {
    '出厂合格证': 'primary',
    '质量追溯报告': 'success',
    '强度检测报告': 'warning'
  }
  return typeMap[type] || ''
}

const getStatusType = (status) => {
  const typeMap = {
    '草稿': 'info',
    '已发布': 'success',
    '已作废': 'danger'
  }
  return typeMap[status] || 'info'
}

const fetchData = async () => {
  loading.value = true
  try {
    tableData.value = [
      {
        id: 1,
        report_no: 'QR20241201001',
        report_type: '出厂合格证',
        batch_id: 1,
        batch_no: 'PB20241201001',
        project_name: '市民中心建设项目',
        strength_grade: 'C30',
        report_date: '2024-12-01',
        generated_by: '技术员A',
        summary: '本批次混凝土配合比设计合理，生产过程控制良好，各项性能指标符合设计要求。',
        conclusion: '本批次混凝土合格，各项性能指标满足设计及规范要求。',
        overall_result: '合格',
        is_qualified: true,
        status: '已发布'
      },
      {
        id: 2,
        report_no: 'QR20241201002',
        report_type: '质量追溯报告',
        batch_id: 2,
        batch_no: 'PB20241201002',
        project_name: '地铁一号线工程',
        strength_grade: 'C35',
        report_date: '2024-12-01',
        generated_by: '技术员B',
        summary: '本批次混凝土原材料检验合格，生产过程中水胶比有轻微偏差，经调整后恢复正常。',
        conclusion: '本批次混凝土合格，生产过程中存在轻微波动，已及时调整。',
        overall_result: '合格',
        is_qualified: true,
        status: '已发布'
      },
      {
        id: 3,
        report_no: 'QR20241201003',
        report_type: '强度检测报告',
        batch_id: 3,
        batch_no: 'PB20241201003',
        project_name: '商业综合体项目',
        strength_grade: 'C40',
        report_date: '2024-11-30',
        generated_by: '技术员C',
        summary: '本批次混凝土试块强度检测结果未达到设计要求。',
        conclusion: '本批次混凝土不合格，强度检测结果低于设计值。',
        overall_result: '不合格',
        is_qualified: false,
        status: '草稿'
      }
    ]
    pagination.total = 3
    
    batches.value = [
      { id: 1, batch_no: 'PB20241201001', project_name: '市民中心建设项目' },
      { id: 2, batch_no: 'PB20241201002', project_name: '地铁一号线工程' },
      { id: 3, batch_no: 'PB20241201003', project_name: '商业综合体项目' }
    ]
  } catch (error) {
    console.error('获取质量报告数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.report_no = ''
  searchForm.report_type = ''
  searchForm.overall_result = ''
  searchForm.status = ''
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
  currentReport.value = { ...row }
  
  reportDetails.value = [
    { item: '水泥用量', design: '360kg/m³', actual: row.batch_no === 'PB20241201001' ? '360.5kg/m³' : '358kg/m³', deviation: row.is_qualified ? '合格' : '-0.5%', result: row.is_qualified ? '合格' : '不合格' },
    { item: '水胶比', design: '0.500', actual: row.batch_no === 'PB20241201001' ? '0.495' : '0.508', deviation: row.is_qualified ? '-1.0%' : '+1.6%', result: row.is_qualified ? '合格' : '不合格' },
    { item: '坍落度', design: '150±30mm', actual: row.batch_no === 'PB20241201001' ? '155mm' : '190mm', deviation: row.is_qualified ? '合格' : '+40mm', result: row.is_qualified ? '合格' : '不合格' },
    { item: '7天强度', design: '≥21MPa', actual: row.batch_no === 'PB20241201001' ? '25.0MPa' : '22.0MPa', deviation: row.is_qualified ? '合格' : '合格', result: '合格' },
    { item: '28天强度', design: '≥30MPa', actual: row.batch_no === 'PB20241201001' ? '35.0MPa' : '28.5MPa', deviation: row.is_qualified ? '+16.7%' : '-5.0%', result: row.is_qualified ? '合格' : '不合格' }
  ]
  
  dialogVisible.value = true
}

const handlePreview = (row) => {
  ElMessage.info('报告预览功能开发中...')
}

const handleEdit = (row) => {
  ElMessage.info('编辑功能开发中...')
}

const handlePublish = (row) => {
  ElMessageBox.confirm(
    `确定要发布报告"${row.report_no}"吗？发布后将不可修改。`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'success'
    }
  ).then(() => {
    row.status = '已发布'
    ElMessage.success('发布成功')
    fetchData()
  }).catch(() => {})
}

const handleVoid = (row) => {
  ElMessageBox.confirm(
    `确定要作废报告"${row.report_no}"吗？作废后该报告将失效。`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    row.status = '已作废'
    ElMessage.success('作废成功')
    fetchData()
  }).catch(() => {})
}

const handleGenerate = () => {
  generateForm.batch_id = null
  generateForm.report_type = '出厂合格证'
  generateForm.report_date = dayjs().format('YYYY-MM-DD')
  generateDialogVisible.value = true
}

const handleGenerateConfirm = async () => {
  if (!generateFormRef.value) return
  
  await generateFormRef.value.validate(async (valid) => {
    if (valid) {
      ElMessage.success('报告生成成功')
      generateDialogVisible.value = false
      fetchData()
    }
  })
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.quality-reports-container {
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

.report-card {
  margin-bottom: 0;
}

.report-summary h4,
.report-conclusion h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.report-summary p,
.report-conclusion p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.text-red {
  color: #F56C6C;
  font-weight: bold;
}

.text-green {
  color: #67C23A;
  font-weight: bold;
}
</style>
