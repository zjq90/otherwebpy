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
        meta: { title: '仪表盘', icon: 'Odometer' }
      },
      {
        path: 'equipment',
        name: 'Equipment',
        meta: { title: '设备档案管理', icon: 'Box' },
        children: [
          {
            path: '',
            name: 'EquipmentList',
            component: () => import('@/views/equipment/index.vue'),
            meta: { title: '设备列表' }
          },
          {
            path: 'sensor',
            name: 'SensorList',
            component: () => import('@/views/equipment/sensor.vue'),
            meta: { title: '传感器管理' }
          }
        ]
      },
      {
        path: 'monitoring',
        name: 'Monitoring',
        meta: { title: '设备运行状态监测', icon: 'Monitor' },
        children: [
          {
            path: 'realtime',
            name: 'RealtimeMonitoring',
            component: () => import('@/views/monitoring/realtime.vue'),
            meta: { title: '实时监测' }
          },
          {
            path: 'history',
            name: 'HistoryData',
            component: () => import('@/views/monitoring/history.vue'),
            meta: { title: '历史数据' }
          },
          {
            path: 'logs',
            name: 'OperationLogs',
            component: () => import('@/views/monitoring/logs.vue'),
            meta: { title: '运行日志' }
          }
        ]
      },
      {
        path: 'maintenance',
        name: 'Maintenance',
        meta: { title: '维护保养计划管理', icon: 'Tools' },
        children: [
          {
            path: 'plan',
            name: 'MaintenancePlan',
            component: () => import('@/views/maintenance/plan.vue'),
            meta: { title: '保养计划' }
          },
          {
            path: 'task',
            name: 'MaintenanceTask',
            component: () => import('@/views/maintenance/task.vue'),
            meta: { title: '保养任务' }
          },
          {
            path: 'record',
            name: 'MaintenanceRecord',
            component: () => import('@/views/maintenance/record.vue'),
            meta: { title: '保养记录' }
          }
        ]
      },
      {
        path: 'control-system',
        name: 'ControlSystem',
        meta: { title: '控制系统监控', icon: 'Connection' },
        children: [
          {
            path: '',
            name: 'ControlSystemList',
            component: () => import('@/views/control-system/index.vue'),
            meta: { title: '系统状态监控' }
          }
        ]
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
