/**
 * 路由配置文件
 */
import Vue from 'vue'
import VueRouter from 'vue-router'

// 使用 Vue Router
Vue.use(VueRouter)

// 路由配置
const routes = [
  // 登录页
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/components/pages/Login.vue'),
    meta: { title: '登录' }
  },
  
  // 主布局
  {
    path: '/',
    component: () => import('@/components/common/Layout.vue'),
    redirect: '/dashboard',
    children: [
      // 仪表盘
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/components/pages/Dashboard.vue'),
        meta: { title: '首页', icon: 'el-icon-s-home' }
      },
      
      // 用户管理
      {
        path: 'user-manage',
        name: 'UserManage',
        component: () => import('@/components/pages/UserManage.vue'),
        meta: { title: '用户管理', icon: 'el-icon-user' }
      },
      
      // 角色管理
      {
        path: 'role-manage',
        name: 'RoleManage',
        component: () => import('@/components/pages/RoleManage.vue'),
        meta: { title: '角色管理', icon: 'el-icon-s-custom' }
      },
      
      // 权限管理
      {
        path: 'permission-manage',
        name: 'PermissionManage',
        component: () => import('@/components/pages/PermissionManage.vue'),
        meta: { title: '权限管理', icon: 'el-icon-key' }
      },
      
      // 操作日志
      {
        path: 'operation-log',
        name: 'OperationLog',
        component: () => import('@/components/pages/OperationLog.vue'),
        meta: { title: '操作日志', icon: 'el-icon-document' }
      },
      
      // 测试功能
      {
        path: 'test-tool',
        name: 'TestTool',
        component: () => import('@/components/pages/TestTool.vue'),
        meta: { title: '测试工具', icon: 'el-icon-cpu' }
      }
    ]
  },
  
  // 403 权限不足
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/components/common/ErrorPage.vue'),
    meta: { title: '权限不足', code: 403 }
  },
  
  // 404 页面不存在
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/components/common/ErrorPage.vue'),
    meta: { title: '页面不存在', code: 404 }
  },
  
  // 重定向到 404
  {
    path: '*',
    redirect: '/404'
  }
]

// 创建路由实例
const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
