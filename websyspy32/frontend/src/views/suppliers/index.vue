<template>
  <div class="suppliers-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>供应商管理</span>
          <div class="header-actions">
            <el-button type="primary" @click="handleAddSupplier">
              <el-icon><Plus /></el-icon>新增供应商
            </el-button>
          </div>
        </div>
      </template>

      <el-tabs v-model="activeTab" type="border-card">
        <el-tab-pane label="供应商列表" name="list">
          <el-table :data="suppliersList" stripe v-loading="loading">
            <el-table-column prop="name" label="供应商名称" min-width="180" />
            <el-table-column prop="contact_person" label="联系人" width="100" />
            <el-table-column prop="contact_phone" label="联系电话" width="130" />
            <el-table-column prop="material_types" label="供应物料" min-width="150" />
            <el-table-column prop="overall_rating" label="综合评分" width="120">
              <template #default="{ row }">
                <el-rate
                  v-model="row.overall_rating"
                  disabled
                  show-score
                  text-color="#ff9900"
                  score-template="{value}分"
                  :max="10"
                />
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === '合作中' ? 'success' : 'info'">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="280" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleViewRatings(row)">
                  评级记录
                </el-button>
                <el-button type="success" link @click="handleAddRating(row)">
                  新增评级
                </el-button>
                <el-button type="primary" link @click="handleViewOrders(row)">
                  采购订单
                </el-button>
                <el-button type="primary" link @click="handleEditSupplier(row)">编辑</el-button>
                <el-button type="danger" link @click="handleDeleteSupplier(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="采购订单" name="orders">
          <div style="margin-bottom: 16px;">
            <el-form :inline="true">
              <el-form-item label="供应商">
                <el-select v-model="orderFilter.supplier_id" placeholder="全部" clearable style="width: 180px">
                  <el-option
                    v-for="s in suppliersList"
                    :key="s.id"
                    :label="s.name"
                    :value="s.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="状态">
                <el-select v-model="orderFilter.status" placeholder="全部" clearable style="width: 140px">
                  <el-option label="待发货" value="待发货" />
                  <el-option label="已发货" value="已发货" />
                  <el-option label="部分收货" value="部分收货" />
                  <el-option label="已完成" value="已完成" />
                  <el-option label="已取消" value="已取消" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="fetchOrders">
                  <el-icon><Search /></el-icon>搜索
                </el-button>
                <el-button type="primary" @click="handleAddOrder">
                  <el-icon><Plus /></el-icon>新增订单
                </el-button>
              </el-form-item>
            </el-form>
          </div>

          <el-table :data="ordersList" stripe v-loading="ordersLoading">
            <el-table-column prop="order_no" label="订单编号" width="180" />
            <el-table-column label="供应商" min-width="150">
              <template #default="{ row }">
                {{ getSupplierName(row.supplier_id) }}
              </template>
            </el-table-column>
            <el-table-column prop="material_type" label="物料类型" width="100" />
            <el-table-column prop="quantity" label="数量(吨)" width="100">
              <template #default="{ row }">
                {{ row.quantity.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="unit_price" label="单价(元/吨)" width="120">
              <template #default="{ row }">
                ¥{{ row.unit_price.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="total_amount" label="总金额(元)" width="120">
              <template #default="{ row }">
                <span class="amount-text">¥{{ row.total_amount.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="order_date" label="下单日期" width="100" />
            <el-table-column prop="delivery_date" label="约定交货" width="100" />
            <el-table-column prop="actual_delivery_date" label="实际交货" width="100" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getOrderStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="success" link @click="handleCreateSettlement(row)" 
                  :disabled="row.status !== '已完成' || hasSettlement(row.id)">
                  生成结算单
                </el-button>
                <el-button type="primary" link @click="handleEditOrder(row)">编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="supplierDialogVisible" :title="supplierDialogTitle" width="550px">
      <el-form :model="supplierForm" :rules="supplierRules" ref="supplierFormRef" label-width="100px">
        <el-form-item label="供应商名称" prop="name">
          <el-input v-model="supplierForm.name" placeholder="请输入供应商名称" />
        </el-form-item>
        <el-form-item label="联系人" prop="contact_person">
          <el-input v-model="supplierForm.contact_person" placeholder="请输入联系人" />
        </el-form-item>
        <el-form-item label="联系电话" prop="contact_phone">
          <el-input v-model="supplierForm.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="supplierForm.address" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="供应物料" prop="material_types">
          <el-select v-model="supplierForm.material_types" multiple placeholder="请选择供应物料" style="width: 100%">
            <el-option label="水泥" value="水泥" />
            <el-option label="砂石" value="砂石" />
            <el-option label="粉煤灰" value="粉煤灰" />
            <el-option label="外加剂" value="外加剂" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="supplierForm.status" style="width: 100%">
            <el-option label="合作中" value="合作中" />
            <el-option label="暂停合作" value="暂停合作" />
            <el-option label="已终止" value="已终止" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="supplierDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSupplierSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="ratingDialogVisible" title="新增供应商评级" width="500px">
      <el-form :model="ratingForm" :rules="ratingRules" ref="ratingFormRef" label-width="100px">
        <el-form-item label="供应商">
          <el-input :value="currentSupplier?.name" disabled />
        </el-form-item>
        <el-form-item label="评级日期" prop="rating_date">
          <el-date-picker
            v-model="ratingForm.rating_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="供货及时性" prop="delivery_score">
          <el-rate v-model="ratingForm.delivery_score" :max="10" show-score score-template="{value}分" />
        </el-form-item>
        <el-form-item label="材料质量" prop="quality_score">
          <el-rate v-model="ratingForm.quality_score" :max="10" show-score score-template="{value}分" />
        </el-form-item>
        <el-form-item label="价格合理性" prop="price_score">
          <el-rate v-model="ratingForm.price_score" :max="10" show-score score-template="{value}分" />
        </el-form-item>
        <el-form-item label="服务态度" prop="service_score">
          <el-rate v-model="ratingForm.service_score" :max="10" show-score score-template="{value}分" />
        </el-form-item>
        <el-form-item label="评价人" prop="evaluator">
          <el-input v-model="ratingForm.evaluator" placeholder="请输入评价人" />
        </el-form-item>
        <el-form-item label="评价备注" prop="comment">
          <el-input v-model="ratingForm.comment" type="textarea" :rows="3" placeholder="请输入评价备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ratingDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleRatingSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="ratingsDialogVisible" title="评级记录" width="700px">
      <el-table :data="currentSupplierRatings" stripe>
        <el-table-column prop="rating_date" label="评级日期" width="100" />
        <el-table-column prop="delivery_score" label="供货及时性" width="100" />
        <el-table-column prop="quality_score" label="材料质量" width="100" />
        <el-table-column prop="price_score" label="价格合理性" width="100" />
        <el-table-column prop="service_score" label="服务态度" width="100" />
        <el-table-column prop="total_score" label="综合评分" width="100">
          <template #default="{ row }">
            <el-tag :type="row.total_score >= 8 ? 'success' : row.total_score >= 6 ? 'warning' : 'danger'">
              {{ row.total_score }}分
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="evaluator" label="评价人" width="80" />
        <el-table-column prop="comment" label="备注" min-width="150" show-overflow-tooltip />
      </el-table>
    </el-dialog>

    <el-dialog v-model="orderDialogVisible" :title="orderDialogTitle" width="600px">
      <el-form :model="orderForm" :rules="orderRules" ref="orderFormRef" label-width="120px">
        <el-form-item label="供应商" prop="supplier_id">
          <el-select v-model="orderForm.supplier_id" placeholder="请选择供应商" style="width: 100%">
            <el-option
              v-for="s in suppliersList.filter(s => s.status === '合作中')"
              :key="s.id"
              :label="s.name"
              :value="s.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="物料类型" prop="material_type">
          <el-select v-model="orderForm.material_type" placeholder="请选择物料类型" style="width: 100%">
            <el-option label="水泥" value="水泥" />
            <el-option label="砂石" value="砂石" />
            <el-option label="粉煤灰" value="粉煤灰" />
            <el-option label="外加剂" value="外加剂" />
          </el-select>
        </el-form-item>
        <el-form-item label="数量(吨)" prop="quantity">
          <el-input-number v-model="orderForm.quantity" :min="0" :step="10" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="单价(元/吨)" prop="unit_price">
          <el-input-number v-model="orderForm.unit_price" :min="0" :step="10" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="下单日期" prop="order_date">
          <el-date-picker
            v-model="orderForm.order_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="约定交货日期" prop="delivery_date">
          <el-date-picker
            v-model="orderForm.delivery_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="实际交货日期" prop="actual_delivery_date">
          <el-date-picker
            v-model="orderForm.actual_delivery_date"
            type="date"
            placeholder="选择日期（选填）"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="orderForm.status" style="width: 100%">
            <el-option label="待发货" value="待发货" />
            <el-option label="已发货" value="已发货" />
            <el-option label="部分收货" value="部分收货" />
            <el-option label="已完成" value="已完成" />
            <el-option label="已取消" value="已取消" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="orderForm.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="orderDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleOrderSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { supplierApi, settlementApi } from '@/api'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const ordersLoading = ref(false)
const activeTab = ref('list')

const suppliersList = ref([])
const ordersList = ref([])
const currentSupplierRatings = ref([])

const supplierDialogVisible = ref(false)
const ratingDialogVisible = ref(false)
const ratingsDialogVisible = ref(false)
const orderDialogVisible = ref(false)

const currentSupplier = ref(null)
const isEditSupplier = ref(false)
const isEditOrder = ref(false)

const supplierFormRef = ref<FormInstance>()
const ratingFormRef = ref<FormInstance>()
const orderFormRef = ref<FormInstance>()

const orderFilter = reactive({
  supplier_id: null,
  status: ''
})

const supplierForm = reactive({
  id: null,
  name: '',
  contact_person: '',
  contact_phone: '',
  address: '',
  material_types: '',
  status: '合作中'
})

const ratingForm = reactive({
  supplier_id: null,
  rating_date: '',
  delivery_score: 7,
  quality_score: 7,
  price_score: 7,
  service_score: 7,
  comment: '',
  evaluator: ''
})

const orderForm = reactive({
  id: null,
  supplier_id: null,
  material_type: '',
  quantity: 0,
  unit_price: 0,
  order_date: '',
  delivery_date: '',
  actual_delivery_date: '',
  status: '待发货',
  remark: ''
})

const supplierRules: FormRules = {
  name: [{ required: true, message: '请输入供应商名称', trigger: 'blur' }]
}

const ratingRules: FormRules = {
  rating_date: [{ required: true, message: '请选择评级日期', trigger: 'change' }]
}

const orderRules: FormRules = {
  supplier_id: [{ required: true, message: '请选择供应商', trigger: 'change' }],
  material_type: [{ required: true, message: '请选择物料类型', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
  unit_price: [{ required: true, message: '请输入单价', trigger: 'blur' }],
  order_date: [{ required: true, message: '请选择下单日期', trigger: 'change' }]
}

const supplierDialogTitle = computed(() => isEditSupplier.value ? '编辑供应商' : '新增供应商')
const orderDialogTitle = computed(() => isEditOrder.value ? '编辑采购订单' : '新增采购订单')

const getOrderStatusType = (status) => {
  const types = {
    '待发货': 'warning',
    '已发货': 'primary',
    '部分收货': 'info',
    '已完成': 'success',
    '已取消': 'info'
  }
  return types[status] || 'info'
}

const getSupplierName = (supplierId) => {
  const supplier = suppliersList.value.find(s => s.id === supplierId)
  return supplier ? supplier.name : '未知供应商'
}

const hasSettlement = (orderId) => {
  return false
}

const fetchSuppliers = async () => {
  loading.value = true
  try {
    const res = await supplierApi.getList({ limit: 100 })
    suppliersList.value = res.data
  } catch (error) {
    ElMessage.error('获取供应商列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const fetchOrders = async () => {
  ordersLoading.value = true
  try {
    let res
    if (orderFilter.supplier_id) {
      res = await supplierApi.getOrdersBySupplier(orderFilter.supplier_id)
    } else if (orderFilter.status) {
      res = await supplierApi.getOrdersByStatus(orderFilter.status)
    } else {
      res = await supplierApi.getOrders({ limit: 100 })
    }
    ordersList.value = res.data
  } catch (error) {
    ElMessage.error('获取采购订单失败')
    console.error(error)
  } finally {
    ordersLoading.value = false
  }
}

const handleAddSupplier = () => {
  isEditSupplier.value = false
  Object.assign(supplierForm, {
    id: null,
    name: '',
    contact_person: '',
    contact_phone: '',
    address: '',
    material_types: '',
    status: '合作中'
  })
  supplierDialogVisible.value = true
}

const handleEditSupplier = (row) => {
  isEditSupplier.value = true
  Object.assign(supplierForm, { ...row })
  supplierDialogVisible.value = true
}

const handleDeleteSupplier = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除供应商"${row.name}"吗？`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await supplierApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchSuppliers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleViewRatings = async (row) => {
  currentSupplier.value = row
  try {
    const res = await supplierApi.getRatingsBySupplier(row.id)
    currentSupplierRatings.value = res.data
    ratingsDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取评级记录失败')
  }
}

const handleAddRating = (row) => {
  currentSupplier.value = row
  Object.assign(ratingForm, {
    supplier_id: row.id,
    rating_date: new Date().toISOString().split('T')[0],
    delivery_score: 7,
    quality_score: 7,
    price_score: 7,
    service_score: 7,
    comment: '',
    evaluator: ''
  })
  ratingDialogVisible.value = true
}

const handleViewOrders = (row) => {
  orderFilter.supplier_id = row.id
  activeTab.value = 'orders'
  fetchOrders()
}

const handleAddOrder = () => {
  isEditOrder.value = false
  const today = new Date().toISOString().split('T')[0]
  Object.assign(orderForm, {
    id: null,
    supplier_id: route.query.supplier_id ? parseInt(route.query.supplier_id) : null,
    material_type: route.query.materialType || '',
    quantity: route.query.quantity ? parseFloat(route.query.quantity) : 0,
    unit_price: 0,
    order_date: today,
    delivery_date: '',
    actual_delivery_date: '',
    status: '待发货',
    remark: ''
  })
  orderDialogVisible.value = true
}

const handleEditOrder = (row) => {
  isEditOrder.value = true
  Object.assign(orderForm, { ...row })
  orderDialogVisible.value = true
}

const handleCreateSettlement = async (row) => {
  try {
    const settlement = await settlementApi.create({
      purchase_order_id: row.id,
      settlement_date: new Date().toISOString().split('T')[0],
      quantity: row.quantity,
      unit_price: row.unit_price,
      tax_rate: 0.13
    })
    ElMessage.success('结算单已生成')
    router.push('/settlements')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '生成结算单失败')
  }
}

const handleSupplierSubmit = async () => {
  if (!supplierFormRef.value) return
  
  await supplierFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEditSupplier.value) {
          await supplierApi.update(supplierForm.id, supplierForm)
          ElMessage.success('更新成功')
        } else {
          await supplierApi.create(supplierForm)
          ElMessage.success('创建成功')
        }
        supplierDialogVisible.value = false
        fetchSuppliers()
      } catch (error) {
        ElMessage.error(isEditSupplier.value ? '更新失败' : '创建失败')
      }
    }
  })
}

const handleRatingSubmit = async () => {
  if (!ratingFormRef.value) return
  
  await ratingFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await supplierApi.createRating(ratingForm)
        ElMessage.success('评级成功')
        ratingDialogVisible.value = false
        fetchSuppliers()
      } catch (error) {
        ElMessage.error('评级失败')
      }
    }
  })
}

const handleOrderSubmit = async () => {
  if (!orderFormRef.value) return
  
  await orderFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEditOrder.value) {
          await supplierApi.updateOrder(orderForm.id, orderForm)
          ElMessage.success('更新成功')
        } else {
          await supplierApi.createOrder(orderForm)
          ElMessage.success('创建成功')
        }
        orderDialogVisible.value = false
        fetchOrders()
      } catch (error) {
        ElMessage.error(isEditOrder.value ? '更新失败' : '创建失败')
      }
    }
  })
}

onMounted(() => {
  fetchSuppliers()
  fetchOrders()
})
</script>

<style scoped>
.suppliers-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.amount-text {
  color: #F56C6C;
  font-weight: 600;
}
</style>
