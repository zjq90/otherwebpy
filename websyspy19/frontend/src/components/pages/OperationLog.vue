<template>
  <div class="operation-log-container">
    <!-- 搜索区域 -->
    <div class="search-box">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="操作用户">
          <el-input
            v-model="searchForm.username"
            placeholder="请输入用户名"
            clearable
            @keyup.enter.native="handleSearch"
          />
        </el-form-item>
        <el-form-item label="请求方法">
          <el-select v-model="searchForm.method" placeholder="全部方法" clearable>
            <el-option label="GET" value="GET" />
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="DELETE" value="DELETE" />
          </el-select>
        </el-form-item>
        <el-form-item label="响应状态">
          <el-select v-model="searchForm.status_code" placeholder="全部状态" clearable>
            <el-option label="成功 (2xx)" :value="200" />
            <el-option label="失败 (4xx/5xx)" :value="400" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间">
          <el-date-picker
            v-model="searchForm.start_time"
            type="datetime"
            placeholder="选择开始时间"
            value-format="yyyy-MM-dd HH:mm:ss"
            style="width: 180px;"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker
            v-model="searchForm.end_time"
            type="datetime"
            placeholder="选择结束时间"
            value-format="yyyy-MM-dd HH:mm:ss"
            style="width: 180px;"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <i class="el-icon-search"></i> 搜索
          </el-button>
          <el-button @click="handleReset">
            <i class="el-icon-refresh"></i> 重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 操作区域 -->
    <div class="action-box">
      <el-button type="success" @click="handleRefresh">
        <i class="el-icon-refresh"></i> 刷新
      </el-button>
      <el-button
        type="danger"
        :disabled="selectedCount === 0"
        @click="handleBatchDelete"
      >
        <i class="el-icon-delete"></i> 批量删除
      </el-button>
      <el-button type="warning" @click="handleCleanup">
        <i class="el-icon-delete-solid"></i> 清理旧日志
      </el-button>
    </div>
    
    <!-- 数据表格 -->
    <el-table
      ref="dataTable"
      :data="tableData"
      style="width: 100%;"
      v-loading="loading"
      stripe
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="操作用户" width="120">
        <template slot-scope="scope">
          <el-tag size="small" :type="scope.row.username ? '' : 'info'">
            {{ scope.row.username || '系统' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="method" label="请求方法" width="100">
        <template slot-scope="scope">
          <span :class="'method-tag ' + scope.row.method.toLowerCase()">
            {{ scope.row.method }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="path" label="请求路径" min-width="200" show-overflow-tooltip />
      <el-table-column prop="status_code" label="状态码" width="100">
        <template slot-scope="scope">
          <el-tag
            size="small"
            :type="scope.row.status_code >= 400 ? 'danger' : 'success'"
          >
            {{ scope.row.status_code }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="ip_address" label="IP地址" width="130">
        <template slot-scope="scope">
          {{ scope.row.ip_address || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="duration" label="耗时" width="100">
        <template slot-scope="scope">
          {{ scope.row.duration ? scope.row.duration.toFixed(2) + ' ms' : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="操作时间" width="160">
        <template slot-scope="scope">
          {{ formatTime(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template slot-scope="scope">
          <el-button type="text" size="small" @click="handleView(scope.row)">
            <i class="el-icon-view"></i> 详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <div class="pagination-box">
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="pagination.page"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="pagination.size"
        layout="total, sizes, prev, pager, next, jumper"
        :total="pagination.total"
      />
    </div>
    
    <!-- 详情对话框 -->
    <el-dialog
      title="操作日志详情"
      :visible.sync="detailDialogVisible"
      width="700px"
    >
      <el-descriptions :column="2" border v-if="currentLog">
        <el-descriptions-item label="日志ID">
          {{ currentLog.id }}
        </el-descriptions-item>
        <el-descriptions-item label="操作用户">
          {{ currentLog.username || '系统' }}
        </el-descriptions-item>
        <el-descriptions-item label="用户ID">
          {{ currentLog.user_id || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="请求方法">
          <el-tag size="small" :type="currentLog.method === 'GET' ? 'info' : 'primary'">
            {{ currentLog.method }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="请求路径">
          {{ currentLog.path }}
        </el-descriptions-item>
        <el-descriptions-item label="状态码">
          <el-tag
            size="small"
            :type="currentLog.status_code >= 400 ? 'danger' : 'success'"
          >
            {{ currentLog.status_code }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="IP地址">
          {{ currentLog.ip_address || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="用户代理">
          {{ currentLog.user_agent || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="耗时">
          {{ currentLog.duration ? currentLog.duration.toFixed(2) + ' ms' : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="操作时间">
          {{ formatTime(currentLog.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="请求参数" :span="2">
          <pre class="json-pre">{{ formatJson(currentLog.request_params) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="响应结果" :span="2">
          <pre class="json-pre">{{ formatJson(currentLog.response_body) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="错误信息" :span="2">
          <pre class="json-pre" style="color: #f56c6c;">{{ currentLog.error_message || '-' }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script>
/**
 * 操作日志页面组件
 * 实现操作日志的查询、查看详情、批量删除、清理旧日志等功能
 */
import { getOperationLogList, getOperationLogDetail, deleteOperationLogs, cleanupOperationLogs } from '@/utils/auth'

export default {
  name: 'OperationLog',
  data() {
    return {
      // 加载状态
      loading: false,
      // 搜索表单
      searchForm: {
        username: '',
        method: '',
        status_code: null,
        start_time: '',
        end_time: ''
      },
      // 表格数据
      tableData: [],
      // 选中的行
      selectedIds: [],
      selectedCount: 0,
      // 分页
      pagination: {
        page: 1,
        size: 10,
        total: 0
      },
      // 详情对话框
      detailDialogVisible: false,
      currentLog: null
    }
  },
  created() {
    // 加载数据
    this.loadData()
  },
  methods: {
    // 加载数据
    async loadData() {
      this.loading = true
      try {
        const params = {
          page: this.pagination.page,
          size: this.pagination.size,
          ...this.searchForm
        }
        // 移除空值的参数
        Object.keys(params).forEach(key => {
          if (params[key] === '' || params[key] === null || params[key] === undefined) {
            delete params[key]
          }
        })
        
        const res = await getOperationLogList(params)
        this.tableData = res.data || []
        this.pagination.total = res.total || 0
      } catch (error) {
        console.error('加载数据失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    // 搜索
    handleSearch() {
      this.pagination.page = 1
      this.loadData()
    },
    
    // 重置
    handleReset() {
      this.searchForm = {
        username: '',
        method: '',
        status_code: null,
        start_time: '',
        end_time: ''
      }
      this.pagination.page = 1
      this.loadData()
    },
    
    // 刷新
    handleRefresh() {
      this.loadData()
    },
    
    // 选中变化
    handleSelectionChange(selection) {
      this.selectedIds = selection.map(item => item.id)
      this.selectedCount = selection.length
    },
    
    // 页码变化
    handleCurrentChange(val) {
      this.pagination.page = val
      this.loadData()
    },
    
    // 每页条数变化
    handleSizeChange(val) {
      this.pagination.size = val
      this.pagination.page = 1
      this.loadData()
    },
    
    // 查看详情
    async handleView(row) {
      try {
        const res = await getOperationLogDetail(row.id)
        this.currentLog = res.data
        this.detailDialogVisible = true
      } catch (error) {
        console.error('获取日志详情失败:', error)
      }
    },
    
    // 批量删除
    handleBatchDelete() {
      this.$confirm(`确定要删除选中的 ${this.selectedCount} 条日志吗？`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.doBatchDelete()
      }).catch(() => {})
    },
    
    // 执行批量删除
    async doBatchDelete() {
      try {
        await deleteOperationLogs(this.selectedIds)
        this.$message.success('删除成功')
        this.loadData()
      } catch (error) {
        console.error('批量删除失败:', error)
      }
    },
    
    // 清理旧日志
    handleCleanup() {
      this.$prompt('请输入要清理多少天前的日志（如：30 表示清理30天前的日志）', '清理旧日志', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /^\d+$/,
        inputErrorMessage: '请输入有效的数字'
      }).then(({ value }) => {
        this.doCleanup(parseInt(value))
      }).catch(() => {})
    },
    
    // 执行清理
    async doCleanup(days) {
      try {
        await cleanupOperationLogs(days)
        this.$message.success(`成功清理 ${days} 天前的日志`)
        this.loadData()
      } catch (error) {
        console.error('清理日志失败:', error)
      }
    },
    
    // 格式化JSON
    formatJson(json) {
      if (!json) return '-'
      try {
        if (typeof json === 'string') {
          json = JSON.parse(json)
        }
        return JSON.stringify(json, null, 2)
      } catch (e) {
        return json
      }
    },
    
    // 格式化时间
    formatTime(time) {
      if (!time) return '-'
      const date = new Date(time)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      const seconds = String(date.getSeconds()).padStart(2, '0')
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
    }
  }
}
</script>

<style scoped>
/**
 * 操作日志页面样式
 */
.operation-log-container {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.search-box {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.action-box {
  margin-bottom: 15px;
}

.pagination-box {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 请求方法标签样式 */
.method-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.method-tag.get {
  background-color: #e6f7ff;
  color: #1890ff;
}

.method-tag.post {
  background-color: #f6ffed;
  color: #52c41a;
}

.method-tag.put {
  background-color: #fffbe6;
  color: #faad14;
}

.method-tag.delete {
  background-color: #fff2f0;
  color: #ff4d4f;
}

/* JSON 预览样式 */
.json-pre {
  margin: 0;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.5;
  overflow-x: auto;
  max-height: 300px;
  overflow-y: auto;
}
</style>
