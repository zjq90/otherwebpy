<template>
  <div class="card-list-page">
    <div class="page-header">
      <h2 class="page-title">卡项列表</h2>
      <p class="page-desc">管理各类会员卡产品，支持年卡、月卡、次卡、储值卡、私教包等</p>
    </div>

    <div class="search-bar">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="卡类型">
          <el-select v-model="searchForm.card_type_id" placeholder="全部类型" clearable>
            <el-option
              v-for="item in cardTypeList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="全部状态" clearable>
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
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
            新增卡项
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-container">
      <el-table :data="tableData" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="卡项名称" width="180" />
        <el-table-column label="卡类型" width="120">
          <template #default="scope">
            <el-tag :type="getCardTypeColor(scope.row.card_type_id)">
              {{ getCardTypeName(scope.row.card_type_id) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="价格信息" min-width="180">
          <template #default="scope">
            <div class="price-info">
              <span class="current-price">¥{{ scope.row.price }}</span>
              <span v-if="scope.row.original_price" class="original-price">
                ¥{{ scope.row.original_price }}
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="有效期/次数" width="150">
          <template #default="scope">
            <div v-if="scope.row.valid_days">
              <span>有效期: {{ scope.row.valid_days }}天</span>
            </div>
            <div v-if="scope.row.valid_count">
              <span>有效次数: {{ scope.row.valid_count }}次</span>
            </div>
            <div v-if="scope.row.stored_amount">
              <span>储值金额: ¥{{ scope.row.stored_amount }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'" size="small">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleEdit(scope.row)">
              编辑
            </el-button>
            <el-button type="warning" link @click="handleView(scope.row)">
              详情
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
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="卡项名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入卡项名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="卡类型" prop="card_type_id">
              <el-select v-model="formData.card_type_id" placeholder="请选择卡类型" style="width: 100%">
                <el-option
                  v-for="item in cardTypeList"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="价格" prop="price">
              <el-input-number
                v-model="formData.price"
                :min="0"
                :precision="2"
                style="width: 100%"
                placeholder="请输入价格"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="原价">
              <el-input-number
                v-model="formData.original_price"
                :min="0"
                :precision="2"
                :disabled="false"
                style="width: 100%"
                placeholder="请输入原价（可选）"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider>卡项属性（根据卡类型填写）</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="有效期天数">
              <el-input-number
                v-model="formData.valid_days"
                :min="0"
                style="width: 100%"
                placeholder="年卡、月卡使用"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="有效次数">
              <el-input-number
                v-model="formData.valid_count"
                :min="0"
                style="width: 100%"
                placeholder="次卡、私教包使用"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="储值金额">
              <el-input-number
                v-model="formData.stored_amount"
                :min="0"
                :precision="2"
                style="width: 100%"
                placeholder="储值卡使用"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="赠送金额">
              <el-input-number
                v-model="formData.bonus_amount"
                :min="0"
                :precision="2"
                style="width: 100%"
                placeholder="储值卡使用"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider>其他设置</el-divider>
        <el-form-item label="包含权益">
          <el-input
            v-model="formData.benefits"
            type="textarea"
            :rows="2"
            placeholder="JSON格式，如：{\"yoga\": true, \"spinning\": true}"
          />
        </el-form-item>
        <el-form-item label="续费规则">
          <el-input
            v-model="formData.renewal_rules"
            type="textarea"
            :rows="2"
            placeholder="JSON格式，如：{\"discount\": 0.9, \"extend_days\": 30}"
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入卡项描述"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="状态">
              <el-radio-group v-model="formData.is_active">
                <el-radio :value="true">启用</el-radio>
                <el-radio :value="false">禁用</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序权重">
              <el-input-number
                v-model="formData.sort_order"
                :min="0"
                style="width: 100%"
                placeholder="数字越小越靠前"
              />
            </el-form-item>
          </el-col>
        </el-row>
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
      title="卡项详情"
      width="500px"
    >
      <el-descriptions :column="1" border v-if="currentCard">
        <el-descriptions-item label="卡项名称">
          {{ currentCard.name }}
        </el-descriptions-item>
        <el-descriptions-item label="卡类型">
          {{ getCardTypeName(currentCard.card_type_id) }}
        </el-descriptions-item>
        <el-descriptions-item label="价格">
          <span class="current-price">¥{{ currentCard.price }}</span>
          <span v-if="currentCard.original_price" class="original-price ml-2">
            原价 ¥{{ currentCard.original_price }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="有效期天数" v-if="currentCard.valid_days">
          {{ currentCard.valid_days }}天
        </el-descriptions-item>
        <el-descriptions-item label="有效次数" v-if="currentCard.valid_count">
          {{ currentCard.valid_count }}次
        </el-descriptions-item>
        <el-descriptions-item label="储值金额" v-if="currentCard.stored_amount">
          ¥{{ currentCard.stored_amount }}
          <span v-if="currentCard.bonus_amount" class="ml-2">
            (赠送 ¥{{ currentCard.bonus_amount }})
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="包含权益" v-if="currentCard.benefits">
          {{ currentCard.benefits }}
        </el-descriptions-item>
        <el-descriptions-item label="描述" v-if="currentCard.description">
          {{ currentCard.description }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentCard.is_active ? 'success' : 'danger'">
            {{ currentCard.is_active ? '启用' : '禁用' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { cardApi, cardTypeApi } from '@/api'

const loading = ref(false)
const tableData = ref([])
const cardTypeList = ref([])
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const dialogTitle = ref('新增卡项')
const isEdit = ref(false)
const formRef = ref(null)
const currentCard = ref(null)

const searchForm = reactive({
  card_type_id: null,
  is_active: null
})

const formData = reactive({
  name: '',
  card_type_id: null,
  price: 0,
  original_price: null,
  valid_days: null,
  valid_count: null,
  stored_amount: null,
  bonus_amount: 0,
  benefits: '',
  renewal_rules: '',
  description: '',
  is_active: true,
  sort_order: 0
})

const formRules = {
  name: [
    { required: true, message: '请输入卡项名称', trigger: 'blur' }
  ],
  card_type_id: [
    { required: true, message: '请选择卡类型', trigger: 'change' }
  ],
  price: [
    { required: true, message: '请输入价格', trigger: 'blur' }
  ]
}

const formatDate = (date) => {
  if (!date) return ''
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const getCardTypeName = (id) => {
  const type = cardTypeList.value.find(item => item.id === id)
  return type ? type.name : '未知'
}

const getCardTypeColor = (id) => {
  const colors = {
    1: 'primary',
    2: 'success',
    3: 'warning',
    4: 'danger',
    5: 'info'
  }
  return colors[id] || 'info'
}

const fetchCardTypes = async () => {
  try {
    const data = await cardTypeApi.getList({ is_active: true })
    cardTypeList.value = data
  } catch (error) {
    console.error('获取卡类型失败:', error)
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchForm.card_type_id !== null) {
      params.card_type_id = searchForm.card_type_id
    }
    if (searchForm.is_active !== null) {
      params.is_active = searchForm.is_active
    }
    const data = await cardApi.getList(params)
    tableData.value = data
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  fetchData()
}

const handleReset = () => {
  searchForm.card_type_id = null
  searchForm.is_active = null
  fetchData()
}

const resetForm = () => {
  formData.name = ''
  formData.card_type_id = null
  formData.price = 0
  formData.original_price = null
  formData.valid_days = null
  formData.valid_count = null
  formData.stored_amount = null
  formData.bonus_amount = 0
  formData.benefits = ''
  formData.renewal_rules = ''
  formData.description = ''
  formData.is_active = true
  formData.sort_order = 0
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增卡项'
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑卡项'
  formData.id = row.id
  formData.name = row.name
  formData.card_type_id = row.card_type_id
  formData.price = row.price
  formData.original_price = row.original_price
  formData.valid_days = row.valid_days
  formData.valid_count = row.valid_count
  formData.stored_amount = row.stored_amount
  formData.bonus_amount = row.bonus_amount || 0
  formData.benefits = row.benefits || ''
  formData.renewal_rules = row.renewal_rules || ''
  formData.description = row.description || ''
  formData.is_active = row.is_active
  formData.sort_order = row.sort_order || 0
  dialogVisible.value = true
}

const handleView = (row) => {
  currentCard.value = row
  detailDialogVisible.value = true
}

const handleSubmit = async () => {
  await formRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await cardApi.update(formData.id, formData)
          ElMessage.success('更新成功')
        } else {
          await cardApi.create(formData)
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

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除卡项"${row.name}"吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await cardApi.delete(row.id)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchCardTypes()
  fetchData()
})
</script>

<style scoped>
.card-list-page {
  height: 100%;
}

.price-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.current-price {
  font-size: 16px;
  font-weight: bold;
  color: #f56c6c;
}

.original-price {
  font-size: 12px;
  color: #909399;
  text-decoration: line-through;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.ml-2 {
  margin-left: 8px;
}
</style>
