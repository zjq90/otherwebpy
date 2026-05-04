/**
 * 路由配置
 */
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
        meta: { title: '系统首页' }
      },
      {
        path: 'members',
        name: 'Members',
        component: () => import('../views/member/MemberList.vue'),
        meta: { title: '会员管理' }
      },
      {
        path: 'members/:id',
        name: 'MemberDetail',
        component: () => import('../views/member/MemberDetail.vue'),
        meta: { title: '会员详情' },
        hidden: true
      },
      {
        path: 'promotions',
        name: 'Promotions',
        component: () => import('../views/promotion/PromotionList.vue'),
        meta: { title: '促销活动管理' }
      },
      {
        path: 'promotions/:id',
        name: 'PromotionDetail',
        component: () => import('../views/promotion/PromotionDetail.vue'),
        meta: { title: '活动详情' },
        hidden: true
      },
      {
        path: 'reminders',
        name: 'Reminders',
        component: () => import('../views/reminder/ReminderList.vue'),
        meta: { title: '续费提醒管理' }
      },
      {
        path: 'test',
        name: 'Test',
        component: () => import('../views/TestTools.vue'),
        meta: { title: '测试工具' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 会员管理系统` : '会员管理系统'
  next()
})

export default router
