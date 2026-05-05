<template>
  <div class="page-content">
    <el-card class="content-card">
      <template #header>
        <span style="font-weight: bold; font-size: 16px;">生产计划</span>
      </template>
      <el-empty description="生产计划管理页面">
        <el-button type="primary" @click="$router.push('/production/product')">查看产品管理</el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup>
</script>
