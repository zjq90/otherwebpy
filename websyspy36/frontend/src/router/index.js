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
    meta: { title: '数据概览' }
  },
  {
    path: '/production',
    name: 'Production',
    component: () => import('@/views/production/index.vue'),
    meta: { title: '生产数据分析' },
    children: [
      {
        path: '',
        redirect: '/production/records'
      },
      {
        path: 'records',
        name: 'ProductionRecords',
        component: () => import('@/views/production/Records.vue'),
        meta: { title: '生产记录' }
      },
      {
        path: 'equipment',
        name: 'Equipment',
        component: () => import('@/views/production/Equipment.vue'),
        meta: { title: '设备管理' }
      },
      {
        path: 'utilization',
        name: 'Utilization',
        component: () => import('@/views/production/Utilization.vue'),
        meta: { title: '设备利用率' }
      },
      {
        path: 'energy',
        name: 'Energy',
        component: () => import('@/views/production/Energy.vue'),
        meta: { title: '能耗指标' }
      },
      {
        path: 'stats',
        name: 'ProductionStats',
        component: () => import('@/views/production/Stats.vue'),
        meta: { title: '统计分析' }
      }
    ]
  },
  {
    path: '/cost',
    name: 'Cost',
    component: () => import('@/views/cost/index.vue'),
    meta: { title: '成本核算与利润分析' },
    children: [
      {
        path: '',
        redirect: '/cost/materials'
      },
      {
        path: 'materials',
        name: 'Materials',
        component: () => import('@/views/cost/Materials.vue'),
        meta: { title: '原材料管理' }
      },
      {
        path: 'material-costs',
        name: 'MaterialCosts',
        component: () => import('@/views/cost/MaterialCosts.vue'),
        meta: { title: '原材料成本' }
      },
      {
        path: 'employees',
        name: 'Employees',
        component: () => import('@/views/cost/Employees.vue'),
        meta: { title: '员工管理' }
      },
      {
        path: 'labor-costs',
        name: 'LaborCosts',
        component: () => import('@/views/cost/LaborCosts.vue'),
        meta: { title: '人工成本' }
      },
      {
        path: 'sales',
        name: 'Sales',
        component: () => import('@/views/cost/Sales.vue'),
        meta: { title: '销售记录' }
      },
      {
        path: 'profit',
        name: 'Profit',
        component: () => import('@/views/cost/Profit.vue'),
        meta: { title: '利润分析' }
      }
    ]
  },
  {
    path: '/environment',
    name: 'Environment',
    component: () => import('@/views/environment/index.vue'),
    meta: { title: '环保合规监管' },
    children: [
      {
        path: '',
        redirect: '/environment/points'
      },
      {
        path: 'points',
        name: 'MonitoringPoints',
        component: () => import('@/views/environment/Points.vue'),
        meta: { title: '监测点位' }
      },
      {
        path: 'dust',
        name: 'DustMonitoring',
        component: () => import('@/views/environment/Dust.vue'),
        meta: { title: '粉尘监测' }
      },
      {
        path: 'noise',
        name: 'NoiseMonitoring',
        component: () => import('@/views/environment/Noise.vue'),
        meta: { title: '噪音监测' }
      },
      {
        path: 'wastewater',
        name: 'WastewaterMonitoring',
        component: () => import('@/views/environment/Wastewater.vue'),
        meta: { title: '废水监测' }
      },
      {
        path: 'alarms',
        name: 'Alarms',
        component: () => import('@/views/environment/Alarms.vue'),
        meta: { title: '报警记录' }
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
