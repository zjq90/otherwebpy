/**
 * 路由配置文件
 * 定义应用的所有路由和页面组件映射
 */
import { createRouter, createWebHistory } from 'vue-router'

// 页面组件
const Dashboard = () => import('@/views/Dashboard.vue')
const PropertyProjects = () => import('@/views/PropertyProjects.vue')
const Properties = () => import('@/views/Properties.vue')
const Owners = () => import('@/views/Owners.vue')

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      title: '仪表盘',
      icon: 'DataBoard'
    }
  },
  {
    path: '/property-projects',
    name: 'PropertyProjects',
    component: PropertyProjects,
    meta: {
      title: '物业项目管理',
      icon: 'OfficeBuilding'
    }
  },
  {
    path: '/properties',
    name: 'Properties',
    component: Properties,
    meta: {
      title: '房产信息管理',
      icon: 'House'
    }
  },
  {
    path: '/owners',
    name: 'Owners',
    component: Owners,
    meta: {
      title: '业主/住户管理',
      icon: 'User'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - 物业信息管理系统`
  }
  next()
})

export default router
