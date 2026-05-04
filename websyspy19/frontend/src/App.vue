<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
/**
 * 根组件
 */
export default {
  name: 'App'
}
</script>

<style>
/**
 * 全局样式
 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  width: 100%;
  height: 100%;
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB",
    "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
  font-size: 14px;
  color: #303133;
  background-color: #f0f2f5;
}

a {
  text-decoration: none;
  color: #409eff;
}

a:hover {
  color: #66b1ff;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-thumb {
  background-color: #c0c4cc;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background-color: #909399;
}

::-webkit-scrollbar-track {
  background-color: #f5f7fa;
}

/* 表格样式优化 */
.el-table {
  background-color: #fff;
  border-radius: 4px;
}

.el-table th {
  background-color: #f5f7fa !important;
  color: #606266;
  font-weight: 500;
}

/* 表单样式优化 */
.el-form-item__label {
  font-weight: 500;
}

/* 按钮样式优化 */
.el-button--primary {
  background-color: #409eff;
  border-color: #409eff;
}

.el-button--primary:hover {
  background-color: #66b1ff;
  border-color: #66b1ff;
}

/* 分页样式 */
.el-pagination {
  margin-top: 20px;
  justify-content: flex-end;
}

/* 对话框样式 */
.el-dialog__header {
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 20px;
}

.el-dialog__footer {
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}

/* 标签样式 */
.el-tag {
  margin-right: 8px;
}
</style>
