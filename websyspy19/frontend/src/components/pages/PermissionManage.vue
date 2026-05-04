<template>
  <div class="permission-manage-container">
    <!-- 搜索区域 -->
    <div class="search-box">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="权限名称">
          <el-input
            v-model="searchForm.name"
            placeholder="请输入权限名称"
            clearable
            @keyup.enter.native="handleSearch"
          />
        </el-form-item>
        <el-form-item label="权限代码">
          <el-input
            v-model="searchForm.code"
            placeholder="请输入权限代码"
            clearable
            @keyup.enter.native="handleSearch"
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
      <el-button type="primary" @click="handleAdd">
        <i class="el-icon-plus"></i> 新增权限
      </el-button>
    </div>
    
    <!-- 数据表格 -->
    <el-table
      :data="tableData"
      style="width: 100%;"
      v-loading="loading"
      stripe
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="权限名称" min-width="150" />
      <el-table-column prop="code" label="权限代码" min-width="200">
        <template slot-scope="scope">
          <el-tag size="small" type="primary">{{ scope.row.code }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="module" label="模块" width="120">
        <template slot-scope="scope">
          {{ getModuleName(scope.row.code.split(':')[0]) }}
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="200">
        <template slot-scope="scope">
          {{ scope.row.description || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160">
        <template slot-scope="scope">
          {{ formatTime(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template slot-scope="scope">
          <el-button type="text" size="small" @click="handleEdit(scope.row)">
            <i class="el-icon-edit"></i> 编辑
          </el-button>
          <el-button
            type="text"
            size="small"
            class="danger"
            @click="handleDelete(scope.row)"
          >
            <i class="el-icon-delete"></i> 删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 新增/编辑对话框 -->
    <el-dialog
      :title="dialogTitle"
      :visible.sync="dialogVisible"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-alert
        title="权限代码格式说明"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      >
        <p>权限代码格式：<code>模块:操作</code></p>
        <p>示例：</p>
        <ul style="margin-top: 5px;">
          <li><code>user:create</code> - 创建用户</li>
          <li><code>user:read</code> - 查看用户</li>
          <li><code>user:update</code> - 更新用户</li>
          <li><code>user:delete</code> - 删除用户</li>
        </ul>
      </el-alert>
      
      <el-form
        ref="dataForm"
        :model="dataForm"
        :rules="dataRules"
        label-width="80px"
      >
        <el-form-item label="权限名称" prop="name">
          <el-input v-model="dataForm.name" placeholder="请输入权限名称" />
        </el-form-item>
        <el-form-item label="权限代码" prop="code">
          <el-input
            v-model="dataForm.code"
            placeholder="请输入权限代码，如：user:create"
            :disabled="isEdit"
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="dataForm.description"
            type="textarea"
            placeholder="请输入权限描述"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
/**
 * 权限管理页面组件
 * 实现权限的增删改查功能
 */
import { getPermissionList, getPermissionDetail, createPermission, updatePermission, deletePermission } from '@/utils/auth'

export default {
  name: 'PermissionManage',
  data() {
    return {
      // 加载状态
      loading: false,
      // 搜索表单
      searchForm: {
        name: '',
        code: ''
      },
      // 表格数据
      tableData: [],
      // 对话框
      dialogVisible: false,
      dialogTitle: '新增权限',
      isEdit: false,
      // 表单数据
      dataForm: {
        id: null,
        name: '',
        code: '',
        description: ''
      },
      // 表单验证规则
      dataRules: {
        name: [
          { required: true, message: '请输入权限名称', trigger: 'blur' },
          { min: 2, max: 100, message: '权限名称长度在 2 到 100 个字符', trigger: 'blur' }
        ],
        code: [
          { required: true, message: '请输入权限代码', trigger: 'blur' },
          { min: 2, max: 100, message: '权限代码长度在 2 到 100 个字符', trigger: 'blur' },
          { pattern: /^[a-zA-Z_][a-zA-Z0-9_]*:[a-zA-Z_][a-zA-Z0-9_]*$/, message: '权限代码格式错误，应为：模块:操作', trigger: 'blur' }
        ]
      }
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
        const res = await getPermissionList()
        let data = res.data || []
        
        // 搜索过滤
        if (this.searchForm.name) {
          data = data.filter(item => 
            item.name.includes(this.searchForm.name)
          )
        }
        if (this.searchForm.code) {
          data = data.filter(item => 
            item.code.includes(this.searchForm.code)
          )
        }
        
        this.tableData = data
      } catch (error) {
        console.error('加载数据失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    // 获取模块中文名称
    getModuleName(module) {
      const moduleNames = {
        'user': '用户管理',
        'role': '角色管理',
        'permission': '权限管理',
        'log': '日志管理',
        'system': '系统管理',
        'finance': '财务管理',
        'repair': '维修管理',
        'reception': '前台管理'
      }
      return moduleNames[module] || module
    },
    
    // 搜索
    handleSearch() {
      this.loadData()
    },
    
    // 重置
    handleReset() {
      this.searchForm = {
        name: '',
        code: ''
      }
      this.loadData()
    },
    
    // 新增
    handleAdd() {
      this.isEdit = false
      this.dialogTitle = '新增权限'
      this.dataForm = {
        id: null,
        name: '',
        code: '',
        description: ''
      }
      this.dialogVisible = true
      // 重置表单验证
      this.$nextTick(() => {
        this.$refs.dataForm?.resetFields()
      })
    },
    
    // 编辑
    async handleEdit(row) {
      this.isEdit = true
      this.dialogTitle = '编辑权限'
      
      try {
        const res = await getPermissionDetail(row.id)
        this.dataForm = {
          id: res.data.id,
          name: res.data.name,
          code: res.data.code,
          description: res.data.description || ''
        }
        this.dialogVisible = true
        // 重置表单验证
        this.$nextTick(() => {
          this.$refs.dataForm?.resetFields()
        })
      } catch (error) {
        console.error('获取权限详情失败:', error)
      }
    },
    
    // 提交
    handleSubmit() {
      this.$refs.dataForm.validate(valid => {
        if (valid) {
          if (this.isEdit) {
            this.doUpdate()
          } else {
            this.doCreate()
          }
        } else {
          return false
        }
      })
    },
    
    // 创建权限
    async doCreate() {
      try {
        await createPermission(this.dataForm)
        this.$message.success('创建成功')
        this.dialogVisible = false
        this.loadData()
      } catch (error) {
        console.error('创建失败:', error)
      }
    },
    
    // 更新权限
    async doUpdate() {
      try {
        await updatePermission(this.dataForm.id, {
          name: this.dataForm.name,
          description: this.dataForm.description
        })
        this.$message.success('更新成功')
        this.dialogVisible = false
        this.loadData()
      } catch (error) {
        console.error('更新失败:', error)
      }
    },
    
    // 删除
    handleDelete(row) {
      this.$confirm(`确定要删除权限 "${row.name}" (${row.code}) 吗？`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.doDelete(row.id)
      }).catch(() => {})
    },
    
    // 执行删除
    async doDelete(permissionId) {
      try {
        await deletePermission(permissionId)
        this.$message.success('删除成功')
        this.loadData()
      } catch (error) {
        console.error('删除失败:', error)
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
 * 权限管理页面样式
 */
.permission-manage-container {
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

.danger {
  color: #f56c6c !important;
}

.dialog-footer {
  text-align: right;
}
</style>
