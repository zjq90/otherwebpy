import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layout/index.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '首页', icon: 'HomeFilled' }
      },
      {
        path: 'suppliers',
        name: 'Suppliers',
        component: () => import('@/views/suppliers/index.vue'),
        meta: { title: '供应商管理', icon: 'OfficeBuilding' }
      },
      {
        path: 'raw-materials',
        name: 'RawMaterials',
        component: () => import('@/views/raw-materials/index.vue'),
        meta: { title: '原材料管理', icon: 'Box' }
      },
      {
        path: 'material-inspections',
        name: 'MaterialInspections',
        component: () => import('@/views/material-inspections/index.vue'),
        meta: { title: '原材料检验', icon: 'Search' }
      },
      {
        path: 'mix-designs',
        name: 'MixDesigns',
        component: () => import('@/views/mix-designs/index.vue'),
        meta: { title: '配比设计', icon: 'Document' }
      },
      {
        path: 'production',
        name: 'Production',
        component: () => import('@/views/production/index.vue'),
        meta: { title: '生产质量追踪', icon: 'Timer' },
        children: [
          {
            path: 'batches',
            name: 'ProductionBatches',
            component: () => import('@/views/production/batches.vue'),
            meta: { title: '生产批次', icon: 'List' }
          },
          {
            path: 'records',
            name: 'ProductionRecords',
            component: () => import('@/views/production/records.vue'),
            meta: { title: '生产记录', icon: 'Reading' }
          }
        ]
      },
      {
        path: 'test-blocks',
        name: 'TestBlocks',
        component: () => import('@/views/test-blocks/index.vue'),
        meta: { title: '试块管理', icon: 'Coin' }
      },
      {
        path: 'strength-tests',
        name: 'StrengthTests',
        component: () => import('@/views/strength-tests/index.vue'),
        meta: { title: '强度检测', icon: 'TrendCharts' }
      },
      {
        path: 'quality-reports',
        name: 'QualityReports',
        component: () => import('@/views/quality-reports/index.vue'),
        meta: { title: '质量报告', icon: 'Report' }
      },
      {
        path: 'supplier-ratings',
        name: 'SupplierRatings',
        component: () => import('@/views/supplier-ratings/index.vue'),
        meta: { title: '供应商评级', icon: 'Star' }
      },
      {
        path: 'settlement-orders',
        name: 'SettlementOrders',
        component: () => import('@/views/settlement-orders/index.vue'),
        meta: { title: '结算单管理', icon: 'Money' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
