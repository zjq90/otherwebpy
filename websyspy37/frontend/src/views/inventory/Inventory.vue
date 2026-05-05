<template>
  <div class="page-content">
    <el-card class="content-card">
      <template #header>
        <span style="font-weight: bold; font-size: 16px;">库存管理</span>
      </template>
      <el-empty description="库存管理页面">
        <el-button type="primary" @click="$router.push('/inventory/warehouse')">查看仓库管理</el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup>
</script>
