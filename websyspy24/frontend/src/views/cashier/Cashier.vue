<template>
  <!-- 收银台页面 -->
  <div class="cashier-page">
    <!-- 顶部信息栏 -->
    <el-card class="info-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="info-item">
            <span class="info-label">收银员</span>
            <span class="info-value">管理员</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="info-item">
            <span class="info-label">当前时间</span>
            <span class="info-value">{{ currentTime }}</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="info-item">
            <span class="info-label">今日订单</span>
            <span class="info-value highlight">{{ todayStats.totalOrders }}</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="info-item">
            <span class="info-label">今日营业额</span>
            <span class="info-value highlight">¥{{ todayStats.totalAmount.toFixed(2) }}</span>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="20">
      <!-- 左侧：商品选择区 -->
      <el-col :span="10">
        <el-card class="products-card">
          <template #header>
            <div class="card-header">
              <span>商品列表</span>
              <el-input
                v-model="productSearch"
                placeholder="搜索商品"
                clearable
                @clear="searchProducts"
                @keyup.enter="searchProducts"
                style="width: 200px"
              >
                <template #append>
                  <el-button :icon="Search" @click="searchProducts" />
                </template>
              </el-input>
            </div>
          </template>

          <!-- 商品分类 -->
          <div class="category-tabs">
            <el-button
              v-for="cat in categories"
              :key="cat"
              :type="currentCategory === cat ? 'primary' : 'default'"
              @click="filterByCategory(cat)"
              size="small"
            >
              {{ cat === 'all' ? '全部' : cat }}
            </el-button>
          </div>

          <!-- 商品列表 -->
          <div class="product-list" v-loading="productsLoading">
            <el-empty v-if="products.length === 0" description="暂无商品" />
            <el-row :gutter="10">
              <el-col :span="8" v-for="product in products" :key="product.id">
                <div
                  class="product-item"
                  :class="{ 'selected': isProductSelected(product.id) }"
                  @click="addProductToCart(product)"
                >
                  <div class="product-name">{{ product.name }}</div>
                  <div class="product-price">¥{{ product.price.toFixed(2) }}</div>
                  <div class="product-stock" :class="{ 'low-stock': product.stock_quantity < 10 }">
                    库存: {{ product.stock_quantity }}
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>

          <div class="pagination-container">
            <el-pagination
              v-model:current-page="productPage"
              v-model:page-size="productPageSize"
              :page-sizes="[12, 24, 48]"
              :total="productTotal"
              layout="total, prev, next"
              @size-change="loadProducts"
              @current-change="loadProducts"
            />
          </div>
        </el-card>
      </el-col>

      <!-- 中间：购物车 -->
      <el-col :span="8">
        <el-card class="cart-card">
          <template #header>
            <div class="card-header">
              <span>购物车</span>
              <el-button type="danger" size="small" plain @click="clearCart" :disabled="cartItems.length === 0">
                清空
              </el-button>
            </div>
          </template>

          <div class="cart-list" v-if="cartItems.length > 0">
            <div v-for="(item, index) in cartItems" :key="item.product_id" class="cart-item">
              <div class="item-info">
                <div class="item-name">{{ item.product_name }}</div>
                <div class="item-price">¥{{ item.unit_price.toFixed(2) }} × {{ item.quantity }}</div>
              </div>
              <div class="item-actions">
                <el-button-group size="small">
                  <el-button @click="decreaseQty(index)">-</el-button>
                  <el-button disabled>{{ item.quantity }}</el-button>
                  <el-button @click="increaseQty(index)">+</el-button>
                </el-button-group>
              </div>
              <div class="item-subtotal">¥{{ (item.unit_price * item.quantity).toFixed(2) }}</div>
              <el-button type="danger" size="small" link @click="removeFromCart(index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
          <el-empty v-else description="购物车为空，请选择商品" />

          <el-divider />

          <!-- 会员选择 -->
          <div class="member-section">
            <el-form label-width="80px">
              <el-form-item label="会员">
                <el-select
                  v-model="selectedMember"
                  placeholder="选择会员（可选）"
                  filterable
                  clearable
                  style="width: 100%"
                  @change="onMemberChange"
                >
                  <el-option
                    v-for="member in members"
                    :key="member.id"
                    :label="`${member.name} (${member.member_no})`"
                    :value="member"
                  />
                </el-select>
              </el-form-item>
            </el-form>
          </div>

          <!-- 优惠券 -->
          <div class="coupon-section">
            <el-form label-width="80px">
              <el-form-item label="优惠券">
                <el-input
                  v-model="couponCode"
                  placeholder="输入优惠券码"
                  clearable
                  style="width: 70%"
                >
                  <template #append>
                    <el-button @click="validateCoupon" :loading="couponLoading">验证</el-button>
                  </template>
                </el-input>
              </el-form-item>
            </el-form>
            <div v-if="validCoupon" class="coupon-info">
              <el-tag type="success">{{ validCoupon.coupon_name }}</el-tag>
              <span class="discount">优惠: ¥{{ validCoupon.discount_amount.toFixed(2) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：结算 -->
      <el-col :span="6">
        <el-card class="payment-card">
          <template #header>
            <span>结算</span>
          </template>

          <div class="payment-summary">
            <div class="summary-row">
              <span class="label">商品金额</span>
              <span class="value">¥{{ totalAmount.toFixed(2) }}</span>
            </div>
            <div class="summary-row" v-if="discountAmount > 0">
              <span class="label">优惠金额</span>
              <span class="value discount">-¥{{ discountAmount.toFixed(2) }}</span>
            </div>
            <el-divider />
            <div class="summary-row total">
              <span class="label">应收金额</span>
              <span class="value">¥{{ actualAmount.toFixed(2) }}</span>
            </div>
          </div>

          <!-- 支付方式 -->
          <div class="payment-methods">
            <div class="section-title">支付方式</div>
            <el-radio-group v-model="paymentMethod">
              <el-radio label="cash">
                <el-icon :size="20"><Money /></el-icon>
                <span>现金</span>
              </el-radio>
              <el-radio label="wechat">
                <el-icon :size="20"><ChatDotRound /></el-icon>
                <span>微信支付</span>
              </el-radio>
              <el-radio label="alipay">
                <el-icon :size="20"><Goods /></el-icon>
                <span>支付宝</span>
              </el-radio>
              <el-radio label="card" v-if="selectedMember">
                <el-icon :size="20"><CreditCard /></el-icon>
                <span>会员卡</span>
              </el-radio>
            </el-radio-group>
          </div>

          <!-- 会员卡余额 -->
          <div v-if="selectedMember" class="member-balance">
            <el-divider />
            <div class="balance-info">
              <span>会员卡余额</span>
              <span class="text-primary">¥{{ selectedMember.balance?.toFixed(2) || '0.00' }}</span>
            </div>
            <div v-if="paymentMethod === 'card' && selectedMember.balance < actualAmount" class="balance-warning">
              <el-alert type="warning" :closable="false" show-icon>
                余额不足，请选择其他支付方式
              </el-alert>
            </div>
          </div>

          <el-divider />

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <el-button
              type="primary"
              size="large"
              :loading="submitLoading"
              :disabled="cartItems.length === 0 || !paymentMethod"
              @click="handleSubmit"
              style="width: 100%"
            >
              <el-icon><Check /></el-icon>
              确认支付
            </el-button>
          </div>

          <!-- 订单结果 -->
          <div v-if="orderResult" class="order-result">
            <el-divider />
            <el-alert :type="orderResult.success ? 'success' : 'error'" show-icon>
              <template #title>
                {{ orderResult.success ? '订单创建成功' : '订单创建失败' }}
              </template>
              <template #default v-if="orderResult.success">
                <p>订单号: {{ orderResult.order_no }}</p>
                <p>支付金额: ¥{{ orderResult.actual_amount?.toFixed(2) }}</p>
              </template>
            </el-alert>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import api from '@/api'

// 当前时间
const currentTime = ref('')
let timeInterval = null

// 今日统计
const todayStats = reactive({
  totalOrders: 0,
  totalAmount: 0
})

// 商品相关
const products = ref([])
const productsLoading = ref(false)
const productSearch = ref('')
const productPage = ref(1)
const productPageSize = ref(12)
const productTotal = ref(0)
const categories = ref(['all'])
const currentCategory = ref('all')

// 购物车
const cartItems = ref([])

// 会员
const members = ref([])
const selectedMember = ref(null)

// 优惠券
const couponCode = ref('')
const couponLoading = ref(false)
const validCoupon = ref(null)

// 支付
const paymentMethod = ref('cash')
const submitLoading = ref(false)
const orderResult = ref(null)

// 计算金额
const totalAmount = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + (item.unit_price * item.quantity), 0)
})

const discountAmount = computed(() => {
  return validCoupon.value ? validCoupon.value.discount_amount : 0
})

const actualAmount = computed(() => {
  return Math.max(totalAmount.value - discountAmount.value, 0)
})

// 检查商品是否已选中
const isProductSelected = (productId) => {
  return cartItems.value.some(item => item.product_id === productId)
}

// 更新时间
const updateTime = () => {
  currentTime.value = dayjs().format('YYYY-MM-DD HH:mm:ss')
}

// 加载商品
const loadProducts = async () => {
  productsLoading.value = true
  try {
    const params = {
      page: productPage.value,
      page_size: productPageSize.value,
      status: 'active'
    }
    if (productSearch.value) {
      params.keyword = productSearch.value
    }
    if (currentCategory.value !== 'all') {
      params.category = currentCategory.value
    }

    const res = await api.getProducts(params)
    products.value = res.items || []
    productTotal.value = res.total || 0

    // 提取分类
    const cats = new Set(['all'])
    products.value.forEach(p => {
      if (p.category) cats.add(p.category)
    })
    categories.value = Array.from(cats)
  } catch (error) {
    console.error('加载商品失败:', error)
  } finally {
    productsLoading.value = false
  }
}

// 搜索商品
const searchProducts = () => {
  productPage.value = 1
  loadProducts()
}

// 按分类筛选
const filterByCategory = (cat) => {
  currentCategory.value = cat
  productPage.value = 1
  loadProducts()
}

// 添加商品到购物车
const addProductToCart = (product) => {
  const existingIndex = cartItems.value.findIndex(item => item.product_id === product.id)
  
  if (existingIndex >= 0) {
    // 已存在，增加数量
    if (cartItems.value[existingIndex].quantity < product.stock_quantity) {
      cartItems.value[existingIndex].quantity++
    } else {
      ElMessage.warning('库存不足')
    }
  } else {
    // 新增
    if (product.stock_quantity > 0) {
      cartItems.value.push({
        product_id: product.id,
        product_name: product.name,
        unit_price: product.price,
        quantity: 1
      })
    } else {
      ElMessage.warning('库存不足')
    }
  }
  
  // 重置订单结果
  orderResult.value = null
}

// 增加数量
const increaseQty = (index) => {
  const item = cartItems.value[index]
  // 简单检查，不查数据库
  item.quantity++
}

// 减少数量
const decreaseQty = (index) => {
  if (cartItems.value[index].quantity > 1) {
    cartItems.value[index].quantity--
  } else {
    removeFromCart(index)
  }
}

// 从购物车移除
const removeFromCart = (index) => {
  cartItems.value.splice(index, 1)
}

// 清空购物车
const clearCart = () => {
  cartItems.value = []
  couponCode.value = ''
  validCoupon.value = null
  orderResult.value = null
}

// 加载会员
const loadMembers = async () => {
  try {
    const res = await api.getMembers({ status: 'active', page_size: 100 })
    members.value = res.items || []
  } catch (error) {
    console.error('加载会员失败:', error)
  }
}

// 会员变更
const onMemberChange = (val) => {
  selectedMember.value = val
  // 如果之前选了会员卡支付但没有会员，重置支付方式
  if (!val && paymentMethod.value === 'card') {
    paymentMethod.value = 'cash'
  }
}

// 验证优惠券
const validateCoupon = async () => {
  if (!couponCode.value.trim()) {
    ElMessage.warning('请输入优惠券码')
    return
  }
  
  couponLoading.value = true
  try {
    const res = await api.validateCoupon(
      couponCode.value.trim(),
      totalAmount.value,
      selectedMember.value?.id
    )
    
    if (res.success && res.data.valid) {
      validCoupon.value = res.data
      ElMessage.success('优惠券有效')
    } else {
      validCoupon.value = null
      ElMessage.error(res.message || '优惠券无效')
    }
  } catch (error) {
    console.error('验证优惠券失败:', error)
    validCoupon.value = null
  } finally {
    couponLoading.value = false
  }
}

// 提交订单
const handleSubmit = async () => {
  if (cartItems.value.length === 0) {
    ElMessage.warning('请选择商品')
    return
  }
  
  if (!paymentMethod.value) {
    ElMessage.warning('请选择支付方式')
    return
  }
  
  // 检查会员卡余额
  if (paymentMethod.value === 'card' && selectedMember.value) {
    if (selectedMember.value.balance < actualAmount.value) {
      ElMessage.error('会员卡余额不足')
      return
    }
  }
  
  submitLoading.value = true
  try {
    const orderData = {
      member_id: selectedMember.value?.id,
      order_type: 'sale',
      payment_method: paymentMethod.value,
      coupon_code: validCoupon.value?.coupon_code,
      cashier: '管理员',
      items: cartItems.value.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity
      }))
    }
    
    const res = await api.createOrder(orderData)
    
    if (res.success) {
      orderResult.value = {
        success: true,
        order_no: res.data.order_no,
        actual_amount: res.data.actual_amount
      }
      
      ElMessage.success('订单创建成功')
      
      // 清空购物车
      cartItems.value = []
      couponCode.value = ''
      validCoupon.value = null
      
      // 刷新今日统计
      loadTodayStats()
      
      // 刷新商品列表
      loadProducts()
    } else {
      orderResult.value = {
        success: false,
        message: res.message
      }
      ElMessage.error(res.message || '订单创建失败')
    }
  } catch (error) {
    console.error('创建订单失败:', error)
    orderResult.value = {
      success: false,
      message: '创建订单失败'
    }
  } finally {
    submitLoading.value = false
  }
}

// 加载今日统计
const loadTodayStats = async () => {
  try {
    const res = await api.getDailyReconcile()
    if (res.success) {
      todayStats.totalOrders = res.data.order_stats?.paid || 0
      todayStats.totalAmount = res.data.order_stats?.actual_amount || 0
    }
  } catch (error) {
    console.error('加载今日统计失败:', error)
  }
}

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  
  loadProducts()
  loadMembers()
  loadTodayStats()
})
</script>

<style scoped>
.cashier-page {
  padding: 0;
}

/* 信息卡 */
.info-card {
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
}

.info-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.info-value {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.info-value.highlight {
  color: #409EFF;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

/* 商品卡片 */
.products-card {
  min-height: 500px;
}

.category-tabs {
  margin-bottom: 15px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.product-list {
  min-height: 350px;
}

.product-item {
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
}

.product-item:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
}

.product-item.selected {
  border-color: #67C23A;
  background: #f0f9eb;
}

.product-name {
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
  font-size: 14px;
}

.product-price {
  color: #F56C6C;
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 5px;
}

.product-stock {
  font-size: 12px;
  color: #909399;
}

.product-stock.low-stock {
  color: #E6A23C;
}

.pagination-container {
  margin-top: 15px;
  display: flex;
  justify-content: center;
}

/* 购物车 */
.cart-card {
  min-height: 500px;
}

.cart-list {
  max-height: 300px;
  overflow-y: auto;
}

.cart-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #EBEEF5;
}

.item-info {
  flex: 1;
}

.item-name {
  font-weight: 500;
  color: #303133;
}

.item-price {
  font-size: 12px;
  color: #909399;
}

.item-actions {
  margin: 0 10px;
}

.item-subtotal {
  min-width: 80px;
  text-align: right;
  font-weight: bold;
  color: #F56C6C;
}

/* 会员和优惠券区域 */
.member-section,
.coupon-section {
  margin-top: 10px;
}

.coupon-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 5px;
}

.discount {
  color: #67C23A;
  font-weight: bold;
}

/* 结算卡片 */
.payment-card {
  min-height: 500px;
}

.payment-summary {
  padding: 10px 0;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

.summary-row.total {
  font-size: 18px;
  font-weight: bold;
}

.summary-row.total .value {
  color: #F56C6C;
}

.summary-row .discount {
  color: #67C23A;
}

.section-title {
  font-weight: bold;
  margin-bottom: 10px;
  color: #303133;
}

.payment-methods .el-radio-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.payment-methods .el-radio {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 15px;
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  margin: 0;
  transition: all 0.3s;
}

.payment-methods .el-radio:hover {
  border-color: #409EFF;
}

.payment-methods .el-radio.is-checked {
  border-color: #409EFF;
  background: #ECF5FF;
}

.member-balance {
  margin-top: 10px;
}

.balance-info {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
}

.text-primary {
  color: #409EFF;
  font-weight: bold;
}

.action-buttons {
  margin-top: 20px;
}

.order-result {
  margin-top: 15px;
}
</style>
