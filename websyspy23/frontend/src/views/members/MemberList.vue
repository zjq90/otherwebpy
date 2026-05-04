<template>
  <div class="member-list-page">
    <div class="page-header">
      <h2 class="page-title">会员管理</h2>
      <p class="page-desc">管理系统会员信息及会员卡绑定</p>
    </div>

    <div class="search-bar">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="姓名/手机号/会员号"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable>
            <el-option label="活跃" value="active" />
            <el-option label="停用" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button type="success" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增会员
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-container">
      <el-table :data="tableData" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="会员号" width="150">
          <template #default="scope">
            <span class="member-code">{{ scope.row.member_code }}</span>
          </template>
        </el-table-column>
        <el-table-column label="头像" width="100">
          <template #default="scope">
            <el-avatar :size="40">
              <img v-if="scope.row.avatar" :src="scope.row.avatar" />
              <span v-else>{{ scope.row.name?.charAt(0) || '会' }}</span>
            </el-avatar>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column label="性别" width="80">
          <template #default="scope">
            <el-tag v-if="scope.row.gender === 'male'" type="primary" size="small">男</el-tag>
            <el-tag v-else-if="scope.row.gender === 'female'" type="danger" size="small">女</el-tag>
            <span v-else>未知</span>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="120" />
        <el-table-column label="会员卡数量" width="100">
          <template #default="scope">
            <el-badge :value="scope.row.card_count || 0" class="item" />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'" size="small">
              {{ scope.row.status === 'active' ? '活跃' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleEdit(scope.row)">
              编辑
            </el-button>
            <el-button type="warning" link @click="handleView(scope.row)">
              详情
            </el-button>
            <el-button type="success" link @click="handleBindCard(scope.row)">
              绑卡
            </el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="formData.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="formData.phone" placeholder="请输入手机号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="性别">
              <el-radio-group v-model="formData.gender">
                <el-radio value="male">男</el-radio>
                <el-radio value="female">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出生日期">
              <el-date-picker
                v-model="formData.birth_date"
                type="date"
                placeholder="选择出生日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="邮箱">
              <el-input v-model="formData.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="formData.status" style="width: 100%">
                <el-option label="活跃" value="active" />
                <el-option label="停用" value="inactive" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider>其他信息</el-divider>
        <el-form-item label="地址">
          <el-input v-model="formData.address" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="紧急联系人">
          <el-input v-model="formData.emergency_contact" placeholder="请输入紧急联系人" />
        </el-form-item>
        <el-form-item label="紧急联系电话">
          <el-input v-model="formData.emergency_phone" placeholder="请输入紧急联系电话" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="formData.notes"
            type="textarea"
            :rows="2"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog
      v-model="detailDialogVisible"
      title="会员详情"
      width="600px"
    >
      <el-descriptions :column="2" border v-if="currentMember">
        <el-descriptions-item label="会员号" :span="2">
          <span class="member-code">{{ currentMember.member_code }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="姓名">
          {{ currentMember.name }}
        </el-descriptions-item>
        <el-descriptions-item label="性别">
          <el-tag v-if="currentMember.gender === 'male'" type="primary" size="small">男</el-tag>
          <el-tag v-else-if="currentMember.gender === 'female'" type="danger" size="small">女</el-tag>
          <span v-else>未知</span>
        </el-descriptions-item>
        <el-descriptions-item label="手机号">
          {{ currentMember.phone }}
        </el-descriptions-item>
        <el-descriptions-item label="邮箱">
          {{ currentMember.email || '未填写' }}
        </el-descriptions-item>
        <el-descriptions-item label="出生日期">
          {{ currentMember.birth_date || '未填写' }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentMember.status === 'active' ? 'success' : 'danger'">
            {{ currentMember.status === 'active' ? '活跃' : '停用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="地址" :span="2">
          {{ currentMember.address || '未填写' }}
        </el-descriptions-item>
        <el-descriptions-item label="紧急联系人">
          {{ currentMember.emergency_contact || '未填写' }}
        </el-descriptions-item>
        <el-descriptions-item label="紧急联系电话">
          {{ currentMember.emergency_phone || '未填写' }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          {{ currentMember.notes || '无' }}
        </el-descriptions-item>
      </el-descriptions>

      <el-divider>会员卡信息</el-divider>
      <el-table :data="currentMemberCards" style="width: 100%" size="small">
        <el-table-column prop="card_name" label="卡名称" />
        <el-table-column label="卡类型">
          <template #default="scope">
            <el-tag size="small">{{ scope.row.card_type_name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="开始日期" prop="start_date" />
        <el-table-column label="结束日期" prop="end_date" />
        <el-table-column label="剩余次数">
          <template #default="scope">
            {{ scope.row.remaining_count ?? '不限' }}
          </template>
        </el-table-column>
        <el-table-column label="余额">
          <template #default="scope">
            {{ scope.row.balance ?? '不限' }}
          </template>
        </el-table-column>
        <el-table-column label="状态">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'" size="small">
              {{ scope.row.status === 'active' ? '有效' : '无效' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <el-dialog
      v-model="cardDialogVisible"
      title="绑定会员卡"
      width="500px"
    >
      <el-form
        ref="cardFormRef"
        :model="cardFormData"
        :rules="cardFormRules"
        label-width="100px"
      >
        <el-form-item label="选择卡项" prop="card_id">
          <el-select
            v-model="cardFormData.card_id"
            placeholder="请选择要绑定的卡项"
            style="width: 100%"
          >
            <el-option
              v-for="item in activeCards"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-divider>高级设置（可选）</el-divider>
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="cardFormData.start_date"
            type="date"
            placeholder="选择开始日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="cardFormData.end_date"
            type="date"
            placeholder="选择结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="剩余次数">
          <el-input-number
            v-model="cardFormData.remaining_count"
            :min="0"
            placeholder="不填则使用卡项默认值"
          />
        </el-form-item>
        <el-form-item label="余额">
          <el-input-number
            v-model="cardFormData.balance"
            :min="0"
            :precision="2"
            placeholder="不填则使用卡项默认值"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cardDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleCardSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { memberApi, cardApi, memberCardApi } from '@/api'

const loading = ref(false)
const tableData = ref([])
const activeCards = ref([])
const currentMemberCards = ref([])
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const cardDialogVisible = ref(false)
const dialogTitle = ref('新增会员')
const isEdit = ref(false)
const formRef = ref(null)
const cardFormRef = ref(null)
const currentMember = ref(null)
const currentMemberId = ref(null)

const searchForm = reactive({
  keyword: '',
  status: null
})

const formData = reactive({
  name: '',
  phone: '',
  gender: null,
  birth_date: null,
  email: '',
  address: '',
  emergency_contact: '',
  emergency_phone: '',
  status: 'active',
  notes: ''
})

const cardFormData = reactive({
  card_id: null,
  start_date: null,
  end_date: null,
  remaining_count: null,
  balance: null
})

const formRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

const cardFormRules = {
  card_id: [
    { required: true, message: '请选择卡项', trigger: 'change' }
  ]
}

const fetchActiveCards = async () => {
  try {
    const data = await cardApi.getList({ is_active: true })
    activeCards.value = data
  } catch (error) {
    console.error('获取卡项列表失败:', error)
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchForm.keyword) {
      params.keyword = searchForm.keyword
    }
    if (searchForm.status) {
      params.status = searchForm.status
    }
    const data = await memberApi.getList(params)
    tableData.value = data
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchMemberCards = async (memberId) => {
  try {
    const data = await memberCardApi.getList({ member_id: memberId })
    currentMemberCards.value = data
  } catch (error) {
    console.error('获取会员卡列表失败:', error)
    currentMemberCards.value = []
  }
}

const handleSearch = () => {
  fetchData()
}

const handleReset = () => {
  searchForm.keyword = ''
  searchForm.status = null
  fetchData()
}

const resetForm = () => {
  formData.name = ''
  formData.phone = ''
  formData.gender = null
  formData.birth_date = null
  formData.email = ''
  formData.address = ''
  formData.emergency_contact = ''
  formData.emergency_phone = ''
  formData.status = 'active'
  formData.notes = ''
}

const resetCardForm = () => {
  cardFormData.card_id = null
  cardFormData.start_date = null
  cardFormData.end_date = null
  cardFormData.remaining_count = null
  cardFormData.balance = null
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增会员'
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑会员'
  formData.id = row.id
  formData.name = row.name
  formData.phone = row.phone
  formData.gender = row.gender
  formData.birth_date = row.birth_date
  formData.email = row.email || ''
  formData.address = row.address || ''
  formData.emergency_contact = row.emergency_contact || ''
  formData.emergency_phone = row.emergency_phone || ''
  formData.status = row.status
  formData.notes = row.notes || ''
  dialogVisible.value = true
}

const handleView = async (row) => {
  currentMember.value = row
  currentMemberId.value = row.id
  await fetchMemberCards(row.id)
  detailDialogVisible.value = true
}

const handleBindCard = (row) => {
  currentMemberId.value = row.id
  resetCardForm()
  cardDialogVisible.value = true
}

const handleSubmit = async () => {
  await formRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await memberApi.update(formData.id, formData)
          ElMessage.success('更新成功')
        } else {
          await memberApi.create(formData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        console.error('提交失败:', error)
      }
    }
  })
}

const handleCardSubmit = async () => {
  await cardFormRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        const submitData = {
          member_id: currentMemberId.value,
          card_id: cardFormData.card_id
        }
        if (cardFormData.start_date) {
          submitData.start_date = cardFormData.start_date
        }
        if (cardFormData.end_date) {
          submitData.end_date = cardFormData.end_date
        }
        if (cardFormData.remaining_count !== null) {
          submitData.remaining_count = cardFormData.remaining_count
        }
        if (cardFormData.balance !== null) {
          submitData.balance = cardFormData.balance
        }
        await memberCardApi.create(submitData)
        ElMessage.success('绑卡成功')
        cardDialogVisible.value = false
        fetchData()
      } catch (error) {
        console.error('绑卡失败:', error)
      }
    }
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除会员"${row.name}"吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await memberApi.delete(row.id)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchActiveCards()
  fetchData()
})
</script>

<style scoped>
.member-list-page {
  height: 100%;
}

.member-code {
  color: #409eff;
  font-weight: bold;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
