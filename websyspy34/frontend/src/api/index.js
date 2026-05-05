import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../layout/Layout.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '监控面板', icon: 'Monitor' }
      },
      {
        path: 'formulas',
        name: 'Formulas',
        component: () => import('../views/formulas/FormulaList.vue'),
        meta: { title: '配方管理', icon: 'Document' }
      },
      {
        path: 'formulas/:id',
        name: 'FormulaDetail',
        component: () => import('../views/formulas/FormulaDetail.vue'),
        meta: { title: '配方详情', hidden: true }
      },
      {
        path: 'plans',
        name: 'Plans',
        component: () => import('../views/production/PlanList.vue'),
        meta: { title: '生产计划', icon: 'Calendar' }
      },
      {
        path: 'plans/:id',
        name: 'PlanDetail',
        component: () => import('../views/production/PlanDetail.vue'),
        meta: { title: '计划详情', hidden: true }
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('../views/production/OrderList.vue'),
        meta: { title: '生产任务', icon: 'List' }
      },
      {
        path: 'orders/:id',
        name: 'OrderDetail',
        component: () => import('../views/production/OrderDetail.vue'),
        meta: { title: '任务详情', hidden: true }
      },
      {
        path: 'resources',
        name: 'Resources',
        component: () => import('../views/production/ResourceList.vue'),
        meta: { title: '资源管理', icon: 'Truck' }
      },
      {
        path: 'monitoring',
        name: 'Monitoring',
        component: () => import('../views/monitoring/RealtimeMonitoring.vue'),
        meta: { title: '实时监控', icon: 'View' }
      },
      {
        path: 'logs',
        name: 'Logs',
        component: () => import('../views/monitoring/LogList.vue'),
        meta: { title: '生产日志', icon: 'Reading' }
      },
      {
        path: 'alerts',
        name: 'Alerts',
        component: () => import('../views/monitoring/AlertList.vue'),
        meta: { title: '预警管理', icon: 'Warning' }
      },
      {
        path: 'test',
        name: 'Test',
        component: () => import('../views/TestPage.vue'),
        meta: { title: '测试功能', icon: 'Tools' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 混凝土生产管理系统` : '混凝土生产管理系统'
  next()
})

export default router
