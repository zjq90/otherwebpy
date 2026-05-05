<template>
  <div class="page-content">
    <el-card class="content-card">
      <template #header>
        <span style="font-weight: bold; font-size: 16px;">收入管理</span>
      </template>
      <el-empty description="收入管理页面">
        <el-button type="primary" @click="$router.push('/finance/account')">查看账户管理</el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup>
</script>
