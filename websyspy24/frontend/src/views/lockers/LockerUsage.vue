<template>
  <!-- 储物柜使用记录页面 -->
  <div class="locker-usage">
    <!-- 搜索和操作栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="会员ID">
          <el-input
            v-model="searchForm.member_id"
            placeholder="请输入会员ID"
            clearable
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="储物柜编号">
          <el-input
            v-model="searchForm.locker_no"
            placeholder="请输入储物柜编号"
            clearable
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="使用中" value="active" />
            <el-option label="已归还" value="returned" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="searchForm.start_date"
            type="date"
            placeholder="开始日期"
            value-format="YYYY-MM-DD"
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="searchForm.end_date"
            type="date"
            placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
      
      <el-divider />
      
      <div class="action-bar">
        <el-button type="success" @click="loadData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </el-card>
    
    <!-- 使用记录表格 -->
    <el-card class="table-card">
      <el-table
        :data="tableData"
        v-loading="loading"
        border
        stripe
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="locker_no" label="储物柜编号" width="120" />
        <el-table-column prop="member_name" label="会员姓名" width="100">
          <template #default="{ row }">
            {{ row.member_name || '未知' }}
          </template>
        </el-table-column>
        <el-table-column prop="member_no" label="会员编号" width="120">
          <template #default="{ row }">
            {{ row.member_no || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="assign_type" label="分配方式" width="100">
          <template #default="{ row }">
            <el-tag :type="row.assign_type === 'auto' ? 'primary' : 'success'" effect="light" size="small">
              {{ row.assign_type === 'auto' ? '自动分配' : '手动选择' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assign_time" label="分配时间" width="160">
          <template #default="{ row }">
            {{ row.assign_time ? formatDateTime(row.assign_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="return_time" label="归还时间" width="160">
          <template #default="{ row }">
            {{ row.return_time ? formatDateTime(row.return_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'warning' : 'success'" effect="light">
              {{ row.status === 'active' ? '使用中' : '已归还' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="operator" label="操作人" width="100">
          <template #default="{ row }">
            {{ row.operator || '系统' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="row.status === 'active'" 
              type="warning" 
              size="small" plain 
              @click="handleReturn(row)"
            >
              归还
            </el-button>
            <el-button type="primary" size="small" plain @click="handleView(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 归还弹窗 -->
    <el-dialog
      v-model="returnDialogVisible"
      title="归还储物柜"
      width="400px"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="储物柜编号">
          {{ currentUsage?.locker_no }}
        </el-descriptions-item>
        <el-descriptions-item label="会员姓名">
          {{ currentUsage?.member_name }}
        </el-descriptions-item>
        <el-descriptions-item label="分配时间">
          {{ currentUsage?.assign_time ? formatDateTime(currentUsage.assign_time) : '-' }}
        </el-descriptions-item>
      </el-descriptions>
      
      <el-divider />
      
      <el-form label-width="80px">
        <el-form-item label="归还人">
          <el-input v-model="returnForm.operator" placeholder="请输入操作人" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="returnForm.remarks"
            type="textarea"
            :rows="2"
            placeholder="请输入备注（可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="returnDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReturn" :loading="returnLoading">
          确认归还
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="使用详情"
      width="500px"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="使用记录ID">
          {{ currentUsage?.id }}
        </el-descriptions-item>
        <el-descriptions-item label="储物柜编号">
          {{ currentUsage?.locker_no }}
        </el-descriptions-item>
        <el-descriptions-item label="会员姓名">
          {{ currentUsage?.member_name || '未知' }}
        </el-descriptions-item>
        <el-descriptions-item label="会员编号">
          {{ currentUsage?.member_no || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="分配方式">
          <el-tag :type="currentUsage?.assign_type === 'auto' ? 'primary' : 'success'">
            {{ currentUsage?.assign_type === 'auto' ? '自动分配' : '手动选择' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="分配时间">
          {{ currentUsage?.assign_time ? formatDateTime(currentUsage.assign_time) : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="归还时间" v-if="currentUsage?.return_time">
          {{ formatDateTime(currentUsage.return_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentUsage?.status === 'active' ? 'warning' : 'success'">
            {{ currentUsage?.status === 'active' ? '使用中' : '已归还' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="操作人">
          {{ currentUsage?.operator || '系统' }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" v-if="currentUsage?.remarks">
          {{ currentUsage.remarks }}
        </el-descriptions-item>
      </el-descriptions>
      
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import api from '@/api'

// 表格数据
const tableData = ref([])
const loading = ref(false)

// 搜索表单
const searchForm = reactive({
  member_id: '',
  locker_no: '',
  status: '',
  start_date: '',
  end_date: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 归还相关
const returnDialogVisible = ref(false)
const currentUsage = ref(null)
const returnLoading = ref(false)
const returnForm = reactive({
  operator: '管理员',
  remarks: ''
})

// 详情相关
const detailDialogVisible = ref(false)

// 格式化日期时间
const formatDateTime = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      status: searchForm.status || undefined
    }
    
    const res = await api.getActiveUsages(params)
    
    tableData.value = res.items || []
    pagination.total = res.total || 0
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置
const handleReset = () => {
  searchForm.member_id = ''
  searchForm.locker_no = ''
  searchForm.status = ''
  searchForm.start_date = ''
  searchForm.end_date = ''
  pagination.page = 1
  loadData()
}

// 分页变更
const handleSizeChange = (size) => {
  pagination.pageSize = size
  loadData()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadData()
}

// 归还储物柜
const handleReturn = (row) => {
  currentUsage.value = row
  returnForm.operator = '管理员'
  returnForm.remarks = ''
  returnDialogVisible.value = true
}

// 提交归还
const submitReturn = async () => {
  if (!currentUsage.value) return
  
  try {
    await api.returnLocker({
      usage_id: currentUsage.value.id,
      operator: returnForm.operator,
      remarks: returnForm.remarks
    })
    
    ElMessage.success('归还成功')
    returnDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('归还失败:', error)
    ElMessage.error('归还失败')
  }
}

// 查看详情
const handleView = (row) => {
  currentUsage.value = row
  detailDialogVisible.value = true
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.locker-usage {
  padding: 0;
}

.search-card {
  margin-bottom: 20px;
}

.action-bar {
  display: flex;
  gap: 10px;
}

.table-card {
  padding: 0;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  padding: 20px;
}
</style>
