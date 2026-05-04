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
    meta: { title: '工作台' }
  },
  {
    path: '/members',
    redirect: '/members/list'
  },
  {
    path: '/members/list',
    name: 'MemberList',
    component: () => import('@/views/members/MemberList.vue'),
    meta: { title: '会员列表' }
  },
  {
    path: '/members/add',
    name: 'MemberAdd',
    component: () => import('@/views/members/MemberForm.vue'),
    meta: { title: '新增会员' }
  },
  {
    path: '/members/edit/:id',
    name: 'MemberEdit',
    component: () => import('@/views/members/MemberForm.vue'),
    meta: { title: '编辑会员' }
  },
  {
    path: '/members/detail/:id',
    name: 'MemberDetail',
    component: () => import('@/views/members/MemberDetail.vue'),
    meta: { title: '会员详情' }
  },
  {
    path: '/archive/physical-tests',
    name: 'PhysicalTests',
    component: () => import('@/views/archive/PhysicalTests.vue'),
    meta: { title: '体测数据' }
  },
  {
    path: '/archive/fitness-goals',
    name: 'FitnessGoals',
    component: () => import('@/views/archive/FitnessGoals.vue'),
    meta: { title: '运动目标' }
  },
  {
    path: '/archive/consumptions',
    name: 'Consumptions',
    component: () => import('@/views/archive/Consumptions.vue'),
    meta: { title: '消费记录' }
  },
  {
    path: '/archive/courses',
    name: 'Courses',
    component: () => import('@/views/archive/Courses.vue'),
    meta: { title: '课程参与' }
  },
  {
    path: '/levels',
    name: 'Levels',
    component: () => import('@/views/Levels.vue'),
    meta: { title: '等级权益' }
  },
  {
    path: '/status-logs',
    name: 'StatusLogs',
    component: () => import('@/views/StatusLogs.vue'),
    meta: { title: '状态日志' }
  },
  {
    path: '/test/generate',
    name: 'TestGenerate',
    component: () => import('@/views/test/TestGenerate.vue'),
    meta: { title: '生成测试数据' }
  },
  {
    path: '/test/helper',
    name: 'TestHelper',
    component: () => import('@/views/test/TestHelper.vue'),
    meta: { title: '测试助手' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
