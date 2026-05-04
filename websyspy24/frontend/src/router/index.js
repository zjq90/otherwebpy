/**
 * Vue Router 路由配置
 * 定义应用的路由结构和导航规则
 */
import { createRouter, createWebHistory } from 'vue-router'

// 路由配置
const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '工作台', icon: 'Odometer' }
  },
  {
    path: '/members',
    name: 'Members',
    component: () => import('@/views/members/MemberList.vue'),
    meta: { title: '会员管理', icon: 'User' }
  },
  {
    path: '/checkin',
    name: 'CheckIn',
    component: () => import('@/views/checkin/CheckIn.vue'),
    meta: { title: '签到管理', icon: 'Timer' }
  },
  {
    path: '/checkin/records',
    name: 'CheckInRecords',
    component: () => import('@/views/checkin/CheckInRecords.vue'),
    meta: { title: '签到记录', icon: 'Document' }
  },
  {
    path: '/lockers',
    name: 'Lockers',
    component: () => import('@/views/lockers/LockerList.vue'),
    meta: { title: '储物柜管理', icon: 'Box' }
  },
  {
    path: '/lockers/usage',
    name: 'LockerUsage',
    component: () => import('@/views/lockers/LockerUsage.vue'),
    meta: { title: '使用记录', icon: 'List' }
  },
  {
    path: '/cashier',
    name: 'Cashier',
    component: () => import('@/views/cashier/Cashier.vue'),
    meta: { title: '收银台', icon: 'Money' }
  },
  {
    path: '/cashier/products',
    name: 'Products',
    component: () => import('@/views/cashier/ProductList.vue'),
    meta: { title: '商品管理', icon: 'Goods' }
  },
  {
    path: '/cashier/coupons',
    name: 'Coupons',
    component: () => import('@/views/cashier/CouponList.vue'),
    meta: { title: '优惠券管理', icon: 'Ticket' }
  },
  {
    path: '/cashier/orders',
    name: 'Orders',
    component: () => import('@/views/cashier/OrderList.vue'),
    meta: { title: '订单管理', icon: 'Order' }
  },
  {
    path: '/cashier/reconcile',
    name: 'Reconcile',
    component: () => import('@/views/cashier/Reconcile.vue'),
    meta: { title: '流水对账', icon: 'DataAnalysis' }
  },
  {
    path: '/test',
    name: 'Test',
    component: () => import('@/views/test/TestCenter.vue'),
    meta: { title: '测试中心', icon: 'Tools' }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 健身房管理系统`
  }
  next()
})

export default router
