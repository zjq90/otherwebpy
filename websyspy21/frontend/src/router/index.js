import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue')
  },
  {
    path: '/security/personnel',
    name: 'SecurityPersonnel',
    component: () => import('@/views/security/Personnel.vue')
  },
  {
    path: '/security/schedule',
    name: 'SecuritySchedule',
    component: () => import('@/views/security/Schedule.vue')
  },
  {
    path: '/security/patrol-route',
    name: 'PatrolRoute',
    component: () => import('@/views/security/PatrolRoute.vue')
  },
  {
    path: '/security/patrol-record',
    name: 'PatrolRecord',
    component: () => import('@/views/security/PatrolRecord.vue')
  },
  {
    path: '/security/monitor',
    name: 'MonitorDevice',
    component: () => import('@/views/security/Monitor.vue')
  },
  {
    path: '/security/vehicle',
    name: 'VehicleRecord',
    component: () => import('@/views/security/Vehicle.vue')
  },
  {
    path: '/security/visitor',
    name: 'VisitorRecord',
    component: () => import('@/views/security/Visitor.vue')
  },
  {
    path: '/security/emergency',
    name: 'EmergencyReport',
    component: () => import('@/views/security/Emergency.vue')
  },
  {
    path: '/environment/cleaning-area',
    name: 'CleaningArea',
    component: () => import('@/views/environment/CleaningArea.vue')
  },
  {
    path: '/environment/cleaning-record',
    name: 'CleaningRecord',
    component: () => import('@/views/environment/CleaningRecord.vue')
  },
  {
    path: '/environment/green-plant',
    name: 'GreenPlant',
    component: () => import('@/views/environment/GreenPlant.vue')
  },
  {
    path: '/environment/maintenance-plan',
    name: 'MaintenancePlan',
    component: () => import('@/views/environment/MaintenancePlan.vue')
  },
  {
    path: '/environment/maintenance-record',
    name: 'MaintenanceRecord',
    component: () => import('@/views/environment/MaintenanceRecord.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
