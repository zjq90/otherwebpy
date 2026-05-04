import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/cards/types',
    name: 'CardTypes',
    component: () => import('@/views/cards/CardTypes.vue'),
    meta: { title: '卡类型管理' }
  },
  {
    path: '/cards/list',
    name: 'CardList',
    component: () => import('@/views/cards/CardList.vue'),
    meta: { title: '卡项列表' }
  },
  {
    path: '/courses/types',
    name: 'CourseTypes',
    component: () => import('@/views/courses/CourseTypes.vue'),
    meta: { title: '课程类型管理' }
  },
  {
    path: '/courses/list',
    name: 'CourseList',
    component: () => import('@/views/courses/CourseList.vue'),
    meta: { title: '课程列表' }
  },
  {
    path: '/courses/schedules',
    name: 'CourseSchedules',
    component: () => import('@/views/courses/CourseSchedule.vue'),
    meta: { title: '课程排期' }
  },
  {
    path: '/venues',
    name: 'Venues',
    component: () => import('@/views/venues/VenueList.vue'),
    meta: { title: '场地管理' }
  },
  {
    path: '/members/list',
    name: 'MemberList',
    component: () => import('@/views/members/MemberList.vue'),
    meta: { title: '会员列表' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
