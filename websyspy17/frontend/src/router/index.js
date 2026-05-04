import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册', requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页' }
      },
      {
        path: 'services',
        name: 'Services',
        component: () => import('@/views/service/ServiceList.vue'),
        meta: { title: '服务请求' }
      },
      {
        path: 'services/create',
        name: 'ServiceCreate',
        component: () => import('@/views/service/ServiceCreate.vue'),
        meta: { title: '提交服务请求' }
      },
      {
        path: 'services/:id',
        name: 'ServiceDetail',
        component: () => import('@/views/service/ServiceDetail.vue'),
        meta: { title: '服务请求详情' }
      },
      {
        path: 'activities',
        name: 'Activities',
        component: () => import('@/views/activity/ActivityList.vue'),
        meta: { title: '社区活动' }
      },
      {
        path: 'activities/create',
        name: 'ActivityCreate',
        component: () => import('@/views/activity/ActivityCreate.vue'),
        meta: { title: '创建活动', requiresAdmin: true }
      },
      {
        path: 'activities/:id',
        name: 'ActivityDetail',
        component: () => import('@/views/activity/ActivityDetail.vue'),
        meta: { title: '活动详情' }
      },
      {
        path: 'my-activities',
        name: 'MyActivities',
        component: () => import('@/views/activity/MyActivities.vue'),
        meta: { title: '我的活动' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '社区管理系统'
  
  const userStore = useUserStore()
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth === false) {
    next()
  } else if (!token && !userStore.isLoggedIn) {
    next('/login')
  } else {
    if (to.meta.requiresAdmin && !userStore.isAdmin) {
      next('/dashboard')
    } else {
      next()
    }
  }
})

export default router
