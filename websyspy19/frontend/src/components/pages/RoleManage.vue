<template>
  <div class="role-manage-container">
    <!-- 搜索区域 -->
    <div class="search-box">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="角色名称">
          <el-input
            v-model="searchForm.name"
            placeholder="请输入角色名称"
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
        <i class="el-icon-plus"></i> 新增角色
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
      <el-table-column prop="name" label="角色名称" min-width="120" />
      <el-table-column prop="code" label="角色代码" min-width="120">
        <template slot-scope="scope">
          <el-tag size="small" type="info">{{ scope.row.code }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="200">
        <template slot-scope="scope">
          {{ scope.row.description || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="permissions" label="权限数" width="100">
        <template slot-scope="scope">
          <el-tag size="small" type="primary">
            {{ scope.row.permissions ? scope.row.permissions.length : 0 }} 个权限
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_system" label="系统内置" width="100">
        <template slot-scope="scope">
          <el-tag v-if="scope.row.is_system" size="small" type="danger">
            是
          </el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160">
        <template slot-scope="scope">
          {{ formatTime(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template slot-scope="scope">
          <el-button type="text" size="small" @click="handleEdit(scope.row)">
            <i class="el-icon-edit"></i> 编辑
          </el-button>
          <el-button type="text" size="small" @click="handleAssignPermissions(scope.row)">
            <i class="el-icon-key"></i> 分配权限
          </el-button>
          <el-button
            type="text"
            size="small"
            class="danger"
            :disabled="scope.row.is_system"
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
      width="450px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="dataForm"
        :model="dataForm"
        :rules="dataRules"
        label-width="80px"
      >
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="dataForm.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色代码" prop="code">
          <el-input
            v-model="dataForm.code"
            placeholder="请输入角色代码（英文，如：admin）"
            :disabled="isEdit"
          />
          <span style="color: #909399; font-size: 12px;">
            角色代码为英文标识，创建后不可修改
          </span>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="dataForm.description"
            type="textarea"
            placeholder="请输入角色描述"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </span>
    </el-dialog>
    
    <!-- 分配权限对话框 -->
    <el-dialog
      title="分配权限"
      :visible.sync="assignDialogVisible"
      width="600px"
    >
      <div class="permission-tree-container">
        <el-tree
          ref="permissionTree"
          :data="permissionTree"
          show-checkbox
          node-key="id"
          default-expand-all
          :props="{
            label: 'name',
            children: 'children'
          }"
        />
      </div>
      <div style="margin-top: 20px;">
        <el-alert
          title="提示"
          type="info"
          :closable="false"
          show-icon
        >
          <p>权限代码格式：<code>模块:操作</code>，如：<code>user:create</code></p>
          <p>勾选权限后，该角色下的所有用户将拥有这些权限</p>
        </el-alert>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="assignDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAssignSubmit">确定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
/**
 * 角色管理页面组件
 * 实现角色的增删改查、权限分配等功能
 */
import { getRoleList, getRoleDetail, createRole, updateRole, deleteRole, assignPermissions, getPermissionList } from '@/utils/auth'

export default {
  name: 'RoleManage',
  data() {
    return {
      // 加载状态
      loading: false,
      // 搜索表单
      searchForm: {
        name: ''
      },
      // 表格数据
      tableData: [],
      // 对话框
      dialogVisible: false,
      dialogTitle: '新增角色',
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
          { required: true, message: '请输入角色名称', trigger: 'blur' },
          { min: 2, max: 50, message: '角色名称长度在 2 到 50 个字符', trigger: 'blur' }
        ],
        code: [
          { required: true, message: '请输入角色代码', trigger: 'blur' },
          { min: 2, max: 50, message: '角色代码长度在 2 到 50 个字符', trigger: 'blur' },
          { pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/, message: '角色代码只能包含英文、数字和下划线，且必须以英文或下划线开头', trigger: 'blur' }
        ]
      },
      // 分配权限对话框
      assignDialogVisible: false,
      currentRole: null,
      // 权限列表
      permissionList: [],
      // 权限树形结构
      permissionTree: []
    }
  },
  created() {
    // 加载数据
    this.loadData()
    this.loadPermissionList()
  },
  methods: {
    // 加载数据
    async loadData() {
      this.loading = true
      try {
        const res = await getRoleList()
        let data = res.data || []
        
        // 搜索过滤
        if (this.searchForm.name) {
          data = data.filter(item => 
            item.name.includes(this.searchForm.name)
          )
        }
        
        this.tableData = data
      } catch (error) {
        console.error('加载数据失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    // 加载权限列表
    async loadPermissionList() {
      try {
        const res = await getPermissionList()
        this.permissionList = res.data || []
        // 构建树形结构
        this.buildPermissionTree()
      } catch (error) {
        console.error('加载权限列表失败:', error)
      }
    },
    
    // 构建权限树形结构（按模块分组）
    buildPermissionTree() {
      const moduleMap = {}
      
      this.permissionList.forEach(permission => {
        // 从权限代码中提取模块名（如 user:create -> user）
        const codeParts = permission.code.split(':')
        const moduleName = codeParts[0] || '其他'
        
        if (!moduleMap[moduleName]) {
          moduleMap[moduleName] = {
            id: `module_${moduleName}`,
            name: this.getModuleName(moduleName),
            children: []
          }
        }
        
        moduleMap[moduleName].children.push({
          id: permission.id,
          name: `${permission.name} (${permission.code})`,
          code: permission.code,
          description: permission.description
        })
      })
      
      this.permissionTree = Object.values(moduleMap)
    },
    
    // 获取模块中文名称
    getModuleName(module) {
      const moduleNames = {
        'user': '用户管理',
        'role': '角色管理',
        'permission': '权限管理',
        'log': '日志管理',
        'system': '系统管理'
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
        name: ''
      }
      this.loadData()
    },
    
    // 新增
    handleAdd() {
      this.isEdit = false
      this.dialogTitle = '新增角色'
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
      this.dialogTitle = '编辑角色'
      
      try {
        const res = await getRoleDetail(row.id)
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
        console.error('获取角色详情失败:', error)
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
    
    // 创建角色
    async doCreate() {
      try {
        await createRole(this.dataForm)
        this.$message.success('创建成功')
        this.dialogVisible = false
        this.loadData()
      } catch (error) {
        console.error('创建失败:', error)
      }
    },
    
    // 更新角色
    async doUpdate() {
      try {
        await updateRole(this.dataForm.id, {
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
      if (row.is_system) {
        this.$message.warning('系统内置角色不可删除')
        return
      }
      
      this.$confirm(`确定要删除角色 "${row.name}" 吗？`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.doDelete(row.id)
      }).catch(() => {})
    },
    
    // 执行删除
    async doDelete(roleId) {
      try {
        await deleteRole(roleId)
        this.$message.success('删除成功')
        this.loadData()
      } catch (error) {
        console.error('删除失败:', error)
      }
    },
    
    // 分配权限
    handleAssignPermissions(row) {
      this.currentRole = row
      this.assignDialogVisible = true
      
      // 等待对话框打开后设置选中状态
      this.$nextTick(() => {
        // 获取当前角色已有的权限ID
        const checkedIds = row.permissions ? row.permissions.map(p => p.id) : []
        
        // 设置树形组件的选中状态
        if (this.$refs.permissionTree) {
          this.$refs.permissionTree.setCheckedKeys(checkedIds)
        }
      })
    },
    
    // 提交分配权限
    async handleAssignSubmit() {
      if (!this.$refs.permissionTree) return
      
      // 获取所有选中的权限ID
      const checkedIds = this.$refs.permissionTree.getCheckedKeys()
      // 过滤掉模块节点（只保留实际的权限ID）
      const permissionIds = checkedIds.filter(id => typeof id === 'number')
      
      try {
        await assignPermissions(this.currentRole.id, permissionIds)
        this.$message.success('权限分配成功')
        this.assignDialogVisible = false
        this.loadData()
      } catch (error) {
        console.error('权限分配失败:', error)
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
 * 角色管理页面样式
 */
.role-manage-container {
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

.permission-tree-container {
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.danger {
  color: #f56c6c !important;
}

.dialog-footer {
  text-align: right;
}
</style>
