<template>
  <div class="app-wrapper">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-logo">
        <i class="el-icon-s-tools"></i>
        <span>{{ title }}</span>
      </div>
      <el-menu
        :default-active="$route.path"
        class="sidebar-menu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
        router
        unique-opened
      >
        <template v-for="item in menuItems">
          <el-menu-item :key="item.path" :index="item.path">
            <i :class="item.icon"></i>
            <span slot="title">{{ item.title }}</span>
          </el-menu-item>
        </template>
      </el-menu>
    </aside>

    <!-- 主内容区 -->
    <div class="main-container">
      <!-- 顶部导航栏 -->
      <header class="navbar">
        <div class="navbar-left">
          <span class="breadcrumb">
            <span>首页</span>
            <span v-if="$route.meta.title && $route.meta.title !== '首页'">
              <i class="el-icon-arrow-right"></i>
              <span>{{ $route.meta.title }}</span>
            </span>
          </span>
        </div>
        <div class="navbar-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <i class="el-icon-user"></i>
              <span>{{ userInfo.username || '用户' }}</span>
              <i class="el-icon-arrow-down el-icon--right"></i>
            </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="profile">
                <i class="el-icon-user"></i> 个人信息
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <i class="el-icon-switch-button"></i> 退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </div>
      </header>

      <!-- 页面内容 -->
      <main class="app-main">
        <transition name="fade-transform" mode="out-in">
          <router-view />
        </transition>
      </main>
    </div>
  </div>
</template>

<script>
/**
 * 布局组件
 * 包含侧边栏、顶部导航栏和页面内容区域
 */
import { mapGetters } from 'vuex'

export default {
  name: 'Layout',
  data() {
    return {
      // 系统标题
      title: process.env.VUE_APP_TITLE || '权限管理系统',
      // 菜单项
      menuItems: [
        { path: '/dashboard', title: '首页', icon: 'el-icon-s-home' },
        { path: '/user-manage', title: '用户管理', icon: 'el-icon-user' },
        { path: '/role-manage', title: '角色管理', icon: 'el-icon-s-custom' },
        { path: '/permission-manage', title: '权限管理', icon: 'el-icon-key' },
        { path: '/operation-log', title: '操作日志', icon: 'el-icon-document' },
        { path: '/test-tool', title: '测试工具', icon: 'el-icon-cpu' }
      ]
    }
  },
  computed: {
    // 映射 Vuex Getters
    ...mapGetters(['userInfo'])
  },
  methods: {
    // 处理下拉菜单命令
    handleCommand(command) {
      switch (command) {
        case 'profile':
          // 显示用户信息
          this.showUserProfile()
          break
        case 'logout':
          // 退出登录
          this.handleLogout()
          break
      }
    },
    
    // 显示用户信息
    showUserProfile() {
      const user = this.userInfo
      this.$alert(`
        <div style="padding: 10px;">
          <p><strong>用户名：</strong>${user.username || '-'}</p>
          <p><strong>邮箱：</strong>${user.email || '-'}</p>
          <p><strong>角色：</strong>${user.roles ? user.roles.map(r => r.name).join(', ') : '-'}</p>
          <p><strong>创建时间：</strong>${user.created_at || '-'}</p>
        </div>
      `, '个人信息', {
        dangerouslyUseHTMLString: true,
        confirmButtonText: '确定'
      })
    },
    
    // 退出登录
    handleLogout() {
      this.$confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$store.dispatch('user/logout')
          .then(() => {
            this.$message.success('已退出登录')
            this.$router.push('/login')
          })
          .catch(() => {
            this.$message.error('退出失败')
          })
      }).catch(() => {})
    }
  }
}
</script>

<style scoped>
/**
 * 布局组件样式
 */
.app-wrapper {
  display: flex;
  width: 100%;
  height: 100%;
}

/* 侧边栏 */
.sidebar {
  width: 210px;
  background-color: #304156;
  transition: width 0.3s;
  overflow: hidden;
}

.sidebar-logo {
  height: 50px;
  padding: 0 15px;
  display: flex;
  align-items: center;
  background-color: #2b3a4a;
  border-bottom: 1px solid #1f2d3d;
}

.sidebar-logo i {
  font-size: 24px;
  color: #409eff;
  margin-right: 10px;
}

.sidebar-logo span {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
}

.sidebar-menu {
  border-right: none;
}

.sidebar-menu.el-menu {
  border-radius: 0;
}

/* 主内容区 */
.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶部导航栏 */
.navbar {
  height: 50px;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  z-index: 100;
}

.navbar-left .breadcrumb {
  font-size: 14px;
  color: #606266;
}

.navbar-left .breadcrumb i {
  margin: 0 8px;
  color: #c0c4cc;
}

.navbar-right .user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.navbar-right .user-info:hover {
  background-color: #f5f7fa;
}

.navbar-right .user-info i {
  color: #606266;
  margin-right: 5px;
}

.navbar-right .user-info span {
  color: #606266;
}

/* 页面内容 */
.app-main {
  flex: 1;
  padding: 20px;
  background-color: #f0f2f5;
  overflow-y: auto;
}

/* 页面过渡动画 */
.fade-transform-leave-active,
.fade-transform-enter-active {
  transition: all 0.3s;
}

.fade-transform-enter {
  opacity: 0;
  transform: translateX(-30px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
