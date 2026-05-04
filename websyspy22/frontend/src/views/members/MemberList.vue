<template>
  <div class="member-list">
    <div class="page-container">
      <div class="page-header">
        <span class="page-title">会员列表</span>
        <el-button type="primary" :icon="Plus" @click="$router.push('/members/add')">
          新增会员
        </el-button>
      </div>

      <!-- 搜索筛选 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="姓名">
          <el-input v-model="searchForm.name" placeholder="请输入姓名" clearable />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="searchForm.phone" placeholder="请输入手机号" clearable />
        </el-form-item>
        <el-form-item label="会员等级">
          <el-select v-model="searchForm.level" placeholder="请选择等级" clearable>
            <el-option label="铜卡" value="bronze" />
            <el-option label="银卡" value="silver" />
            <el-option label="金卡" value="gold" />
          </el-select>
        </el-form-item>
        <el-form-item label="账户状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="正常" value="active" />
            <el-option label="已冻结" value="frozen" />
            <el-option label="已注销" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 会员表格 -->
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="gender" label="性别" width="80" :formatter="formatGender" />
        <el-table-column prop="registration_channel" label="注册渠道" width="100" :formatter="formatChannel" />
        <el-table-column prop="current_level" label="会员等级" width="100">
          <template #default="{ row }">
            <el-tag :class="`level-tag ${row.current_level?.toLowerCase()}`" effect="plain">
              {{ formatLevel(row.current_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_consumption" label="消费金额" width="120">
          <template #default="{ row }">
            ¥{{ (row.total_consumption || 0).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :class="`status-tag ${row.status}`" effect="plain">
              {{ formatStatus(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button type="primary" link :icon="View" @click="handleView(row)">查看</el-button>
              <el-button type="primary" link :icon="Edit" @click="handleEdit(row)">编辑</el-button>
              <el-button
                v-if="row.status === 'active'"
                type="warning"
                link
                :icon="Lock"
                @click="handleFreeze(row)"
              >冻结</el-button>
              <el-button
                v-if="row.status === 'frozen'"
                type="success"
                link
                :icon="Unlock"
                @click="handleUnfreeze(row)"
              >解冻</el-button>
              <el-button
                v-if="row.status !== 'cancelled'"
                type="danger"
                link
                :icon="Delete"
                @click="handleDelete(row)"
              >注销</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Refresh, View, Edit, Lock, Unlock, Delete
} from '@element-plus/icons-vue'
import {
  getMemberList, deleteMember, freezeMember, unfreezeMember
} from '@/api/member'
import dayjs from 'dayjs'

const router = useRouter()

const loading = ref(false)

const searchForm = reactive({
  name: '',
  phone: '',
  level: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const tableData = ref([])

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const formatGender = (row, column, value) => {
  const genderMap = { 'male': '男', 'female': '女' }
  return genderMap[value] || '-'
}

const formatChannel = (row, column, value) => {
  const channelMap = { 'online': '线上', 'offline': '线下' }
  return channelMap[value] || '-'
}

const formatStatus = (status) => {
  const statusMap = { 'active': '正常', 'frozen': '已冻结', 'cancelled': '已注销' }
  return statusMap[status] || status
}

const formatLevel = (level) => {
  const levelMap = { 'bronze': '铜卡', 'silver': '银卡', 'gold': '金卡' }
  return levelMap[level] || level
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm
    }
    // 移除空值
    Object.keys(params).forEach(key => {
      if (!params[key]) delete params[key]
    })
    
    const res = await getMemberList(params)
    if (res.data) {
      tableData.value = res.data.items || []
      pagination.total = res.data.total || 0
    }
  } catch (error) {
    // 使用模拟数据
    tableData.value = [
      { id: 1, name: '张三', phone: '13800138001', gender: 'male', registration_channel: 'online', current_level: 'bronze', total_consumption: 500, status: 'active', created_at: '2024-01-15T10:30:00' },
      { id: 2, name: '李四', phone: '13800138002', gender: 'female', registration_channel: 'offline', current_level: 'silver', total_consumption: 8000, status: 'active', created_at: '2024-01-14T14:20:00' },
      { id: 3, name: '王五', phone: '13800138003', gender: 'male', registration_channel: 'online', current_level: 'gold', total_consumption: 35000, status: 'active', created_at: '2024-01-13T09:15:00' },
      { id: 4, name: '赵六', phone: '13800138004', gender: 'male', registration_channel: 'offline', current_level: 'bronze', total_consumption: 200, status: 'frozen', created_at: '2024-01-12T16:45:00' },
      { id: 5, name: '孙七', phone: '13800138005', gender: 'female', registration_channel: 'online', current_level: 'silver', total_consumption: 6500, status: 'active', created_at: '2024-01-11T11:30:00' },
    ]
    pagination.total = 5
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.name = ''
  searchForm.phone = ''
  searchForm.level = ''
  searchForm.status = ''
  handleSearch()
}

const handleView = (row) => {
  router.push(`/members/detail/${row.id}`)
}

const handleEdit = (row) => {
  router.push(`/members/edit/${row.id}`)
}

const handleFreeze = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要冻结会员「${row.name}」的账户吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await freezeMember(row.id, '管理员冻结')
    ElMessage.success('账户已冻结')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('冻结失败')
    }
  }
}

const handleUnfreeze = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要解冻会员「${row.name}」的账户吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    
    await unfreezeMember(row.id, '管理员解冻')
    ElMessage.success('账户已解冻')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('解冻失败')
    }
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要注销会员「${row.name}」的账户吗？此操作不可恢复。`, '警告', {
      confirmButtonText: '确定注销',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteMember(row.id)
    ElMessage.success('账户已注销')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('注销失败')
    }
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.member-list {
  .search-form {
    margin-bottom: 20px;
    padding: 20px;
    background-color: #f5f7fa;
    border-radius: 4px;
  }

  .pagination-wrapper {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
