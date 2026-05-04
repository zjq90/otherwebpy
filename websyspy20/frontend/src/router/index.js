import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '首页', icon: 'HomeFilled' }
  },
  {
    path: '/fee-items',
    name: 'FeeItems',
    component: () => import('@/views/FeeItems.vue'),
    meta: { title: '费用项目设置', icon: 'Coin' }
  },
  {
    path: '/properties',
    name: 'Properties',
    component: () => import('@/views/Properties.vue'),
    meta: { title: '房产管理', icon: 'OfficeBuilding' }
  },
  {
    path: '/bills',
    name: 'Bills',
    component: () => import('@/views/Bills.vue'),
    meta: { title: '账单管理', icon: 'Document' }
  },
  {
    path: '/reminders',
    name: 'Reminders',
    component: () => import('@/views/Reminders.vue'),
    meta: { title: '催缴管理', icon: 'Bell' }
  },
  {
    path: '/invoices',
    name: 'Invoices',
    component: () => import('@/views/Invoices.vue'),
    meta: { title: '票据管理', icon: 'Ticket' }
  },
  {
    path: '/finance',
    name: 'Finance',
    component: () => import('@/views/Finance.vue'),
    meta: { title: '财务报表', icon: 'DataAnalysis' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title || '物业管理系统'}`
  next()
})

export default router
