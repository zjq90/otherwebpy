/**
 * 路由配置文件
 * 定义应用的所有路由
 */
import { createRouter, createWebHistory } from 'vue-router'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' }
  },
  // 工程维保管理
  {
    path: '/equipment/list',
    name: 'EquipmentList',
    component: () => import('@/views/equipment/EquipmentList.vue'),
    meta: { title: '设备台账' }
  },
  {
    path: '/equipment/inspection',
    name: 'InspectionPlan',
    component: () => import('@/views/equipment/InspectionPlan.vue'),
    meta: { title: '巡检计划' }
  },
  {
    path: '/equipment/maintenance',
    name: 'MaintenancePlan',
    component: () => import('@/views/equipment/MaintenancePlan.vue'),
    meta: { title: '保养计划' }
  },
  {
    path: '/equipment/fault',
    name: 'FaultRecord',
    component: () => import('@/views/equipment/FaultRecord.vue'),
    meta: { title: '故障维修' }
  },
  {
    path: '/equipment/statistics',
    name: 'EquipmentStatistics',
    component: () => import('@/views/equipment/EquipmentStatistics.vue'),
    meta: { title: '费用统计' }
  },
  // 装修管理
  {
    path: '/decoration/application',
    name: 'DecorationApplication',
    component: () => import('@/views/decoration/DecorationApplication.vue'),
    meta: { title: '装修申请' }
  },
  {
    path: '/decoration/deposit',
    name: 'DecorationDeposit',
    component: () => import('@/views/decoration/DecorationDeposit.vue'),
    meta: { title: '押金管理' }
  },
  {
    path: '/decoration/inspection',
    name: 'DecorationInspection',
    component: () => import('@/views/decoration/DecorationInspection.vue'),
    meta: { title: '装修巡检' }
  },
  // 合同与供应商管理
  {
    path: '/contract/supplier',
    name: 'SupplierManagement',
    component: () => import('@/views/contract/SupplierManagement.vue'),
    meta: { title: '供应商管理' }
  },
  {
    path: '/contract/list',
    name: 'ContractManagement',
    component: () => import('@/views/contract/ContractManagement.vue'),
    meta: { title: '合同管理' }
  },
  {
    path: '/contract/payment',
    name: 'ContractPayment',
    component: () => import('@/views/contract/ContractPayment.vue'),
    meta: { title: '付款记录' }
  },
  {
    path: '/contract/evaluation',
    name: 'ServiceEvaluation',
    component: () => import('@/views/contract/ServiceEvaluation.vue'),
    meta: { title: '服务质量评估' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 物业综合管理系统`
  }
  next()
})

export default router
