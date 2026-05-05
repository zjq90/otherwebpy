import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/views/Layout.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '数据概览', icon: 'DataLine' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/user/Users.vue'),
        meta: { title: '用户管理', icon: 'User' }
      },
      {
        path: 'feedbacks',
        name: 'Feedbacks',
        component: () => import('@/views/user/Feedbacks.vue'),
        meta: { title: '投诉反馈', icon: 'ChatDotRound' }
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('@/views/order/Orders.vue'),
        meta: { title: '订单管理', icon: 'Document' }
      },
      {
        path: 'order-stats',
        name: 'OrderStats',
        component: () => import('@/views/order/OrderStats.vue'),
        meta: { title: '订单统计', icon: 'TrendCharts' }
      },
      {
        path: 'recyclers',
        name: 'Recyclers',
        component: () => import('@/views/recycler/Recyclers.vue'),
        meta: { title: '回收人员', icon: 'Avatar' }
      },
      {
        path: 'performance',
        name: 'Performance',
        component: () => import('@/views/recycler/Performance.vue'),
        meta: { title: '绩效考核', icon: 'Trophy' }
      },
      {
        path: 'categories',
        name: 'Categories',
        component: () => import('@/views/category/Categories.vue'),
        meta: { title: '分类管理', icon: 'Collection' }
      },
      {
        path: 'pricing-rules',
        name: 'PricingRules',
        component: () => import('@/views/category/PricingRules.vue'),
        meta: { title: '价格规则', icon: 'Wallet' }
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('@/views/product/Products.vue'),
        meta: { title: '商品管理', icon: 'Goods' }
      },
      {
        path: 'points-rules',
        name: 'PointsRules',
        component: () => import('@/views/product/PointsRules.vue'),
        meta: { title: '积分规则', icon: 'Coin' }
      },
      {
        path: 'points-exchanges',
        name: 'PointsExchanges',
        component: () => import('@/views/product/PointsExchanges.vue'),
        meta: { title: '积分兑换', icon: 'Promotion' }
      },
      {
        path: 'announcements',
        name: 'Announcements',
        component: () => import('@/views/announcement/Announcements.vue'),
        meta: { title: '公告管理', icon: 'Bell' }
      },
      {
        path: 'cs-staffs',
        name: 'CsStaffs',
        component: () => import('@/views/customer-service/CsStaffs.vue'),
        meta: { title: '客服人员', icon: 'Service' }
      },
      {
        path: 'consultations',
        name: 'Consultations',
        component: () => import('@/views/customer-service/Consultations.vue'),
        meta: { title: '咨询记录', icon: 'ChatLineSquare' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
