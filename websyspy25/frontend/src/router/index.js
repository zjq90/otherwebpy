import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '首页概览' }
  },
  {
    path: '/coach/list',
    name: 'CoachList',
    component: () => import('@/views/coach/CoachList.vue'),
    meta: { title: '教练列表' }
  },
  {
    path: '/coach/schedule',
    name: 'CoachSchedule',
    component: () => import('@/views/coach/CoachSchedule.vue'),
    meta: { title: '排班管理' }
  },
  {
    path: '/member/list',
    name: 'MemberList',
    component: () => import('@/views/member/MemberList.vue'),
    meta: { title: '会员列表' }
  },
  {
    path: '/member/packages',
    name: 'MemberPackages',
    component: () => import('@/views/member/MemberPackages.vue'),
    meta: { title: '课程包管理' }
  },
  {
    path: '/lesson/records',
    name: 'LessonRecords',
    component: () => import('@/views/lesson/LessonRecords.vue'),
    meta: { title: '课时记录' }
  },
  {
    path: '/lesson/makeup',
    name: 'MakeupLessons',
    component: () => import('@/views/lesson/MakeupLessons.vue'),
    meta: { title: '补课管理' }
  },
  {
    path: '/lesson/freeze',
    name: 'FreezeRecords',
    component: () => import('@/views/lesson/FreezeRecords.vue'),
    meta: { title: '冻结管理' }
  },
  {
    path: '/performance',
    name: 'Performance',
    component: () => import('@/views/performance/Performance.vue'),
    meta: { title: '业绩追踪' }
  },
  {
    path: '/test',
    name: 'TestTools',
    component: () => import('@/views/TestTools.vue'),
    meta: { title: '测试工具' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 健身私教管理系统` : '健身私教管理系统'
  next()
})

export default router
