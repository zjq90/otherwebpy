<template>
  <div class="user-manage-container">
    <!-- 搜索区域 -->
    <div class="search-box">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="用户名">
          <el-input
            v-model="searchForm.username"
            placeholder="请输入用户名"
            clearable
            @keyup.enter.native="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="全部状态" clearable>
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
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
        <i class="el-icon-plus"></i> 新增用户
      </el-button>
      <el-button type="danger" :disabled="selectedCount === 0" @click="handleBatchDelete">
        <i class="el-icon-delete"></i> 批量删除
      </el-button>
    </div>
    
    <!-- 数据表格 -->
    <el-table
      ref="dataTable"
      :data="tableData"
      style="width: 100%;"
      v-loading="loading"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" min-width="120" />
      <el-table-column prop="email" label="邮箱" min-width="180" />
      <el-table-column prop="real_name" label="真实姓名" width="100">
        <template slot-scope="scope">
          {{ scope.row.real_name || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="phone" label="手机号" width="130">
        <template slot-scope="scope">
          {{ scope.row.phone || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="roles" label="角色" min-width="180">
        <template slot-scope="scope">
          <el-tag
            v-for="role in scope.row.roles"
            :key="role.id"
            size="small"
            style="margin-right: 5px; margin-bottom: 2px;"
          >
            {{ role.name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态" width="100">
        <template slot-scope="scope">
          <el-switch
            v-model="scope.row.is_active"
            :active-text="'启用'"
            :inactive-text="'禁用'"
            @change="handleStatusChange(scope.row)"
          />
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160">
        <template slot-scope="scope">
          {{ formatTime(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template slot-scope="scope">
          <el-button type="text" size="small" @click="handleEdit(scope.row)">
            <i class="el-icon-edit"></i> 编辑
          </el-button>
          <el-button type="text" size="small" @click="handleAssignRoles(scope.row)">
            <i class="el-icon-s-custom"></i> 分配角色
          </el-button>
          <el-button type="text" size="small" class="danger" @click="handleDelete(scope.row)">
            <i class="el-icon-delete"></i> 删除
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
    
    <!-- 新增/编辑对话框 -->
    <el-dialog
      :title="dialogTitle"
      :visible.sync="dialogVisible"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="dataForm"
        :model="dataForm"
        :rules="dataRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="dataForm.username" placeholder="请输入用户名" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="密码" :prop="isEdit ? '' : 'password'">
          <el-input
            v-model="dataForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
          <span style="color: #909399; font-size: 12px;">
            {{ isEdit ? '留空则不修改密码' : '新建用户时必填' }}
          </span>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="dataForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="真实姓名">
          <el-input v-model="dataForm.real_name" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="dataForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="dataForm.is_active"
            :active-text="'启用'"
            :inactive-text="'禁用'"
          />
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </span>
    </el-dialog>
    
    <!-- 分配角色对话框 -->
    <el-dialog
      title="分配角色"
      :visible.sync="assignDialogVisible"
      width="400px"
    >
      <el-transfer
        v-model="selectedRoleIds"
        :data="roleList"
        :props="{
          key: 'id',
          label: 'name'
        }"
        filterable
        filter-placeholder="搜索角色"
        :titles="['可选角色', '已选角色']"
      />
      <span slot="footer" class="dialog-footer">
        <el-button @click="assignDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAssignSubmit">确定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
/**
 * 用户管理页面组件
 * 实现用户的增删改查、角色分配、状态切换等功能
 */
import { getUserList, getUserDetail, createUser, updateUser, deleteUser, assignRoles, getRoleList } from '@/utils/auth'

export default {
  name: 'UserManage',
  data() {
    // 验证邮箱
    const validateEmail = (rule, value, callback) => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (value && !emailRegex.test(value)) {
        callback(new Error('请输入有效的邮箱地址'))
      } else {
        callback()
      }
    }
    
    return {
      // 加载状态
      loading: false,
      // 搜索表单
      searchForm: {
        username: '',
        is_active: null
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
      // 对话框
      dialogVisible: false,
      dialogTitle: '新增用户',
      isEdit: false,
      // 表单数据
      dataForm: {
        id: null,
        username: '',
        password: '',
        email: '',
        real_name: '',
        phone: '',
        is_active: true
      },
      // 表单验证规则
      dataRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 2, max: 50, message: '用户名长度在 2 到 50 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 100, message: '密码长度不能少于6位', trigger: 'blur' }
        ],
        email: [
          { validator: validateEmail, trigger: 'blur' }
        ]
      },
      // 分配角色对话框
      assignDialogVisible: false,
      currentUser: null,
      selectedRoleIds: [],
      roleList: []
    }
  },
  created() {
    // 加载数据
    this.loadData()
    this.loadRoleList()
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
        // 移除 null 值的参数
        Object.keys(params).forEach(key => {
          if (params[key] === null || params[key] === undefined) {
            delete params[key]
          }
        })
        
        const res = await getUserList(params)
        this.tableData = res.data || []
        this.pagination.total = res.total || 0
      } catch (error) {
        console.error('加载数据失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    // 加载角色列表
    async loadRoleList() {
      try {
        const res = await getRoleList()
        this.roleList = res.data || []
      } catch (error) {
        console.error('加载角色列表失败:', error)
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
        is_active: null
      }
      this.pagination.page = 1
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
    
    // 新增
    handleAdd() {
      this.isEdit = false
      this.dialogTitle = '新增用户'
      this.dataForm = {
        id: null,
        username: '',
        password: '',
        email: '',
        real_name: '',
        phone: '',
        is_active: true
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
      this.dialogTitle = '编辑用户'
      
      try {
        const res = await getUserDetail(row.id)
        this.dataForm = {
          id: res.data.id,
          username: res.data.username,
          password: '',
          email: res.data.email || '',
          real_name: res.data.real_name || '',
          phone: res.data.phone || '',
          is_active: res.data.is_active
        }
        this.dialogVisible = true
        // 重置表单验证
        this.$nextTick(() => {
          this.$refs.dataForm?.resetFields()
        })
      } catch (error) {
        console.error('获取用户详情失败:', error)
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
    
    // 创建用户
    async doCreate() {
      try {
        await createUser(this.dataForm)
        this.$message.success('创建成功')
        this.dialogVisible = false
        this.loadData()
      } catch (error) {
        console.error('创建失败:', error)
      }
    },
    
    // 更新用户
    async doUpdate() {
      try {
        // 只传递有值的字段
        const updateData = {}
        Object.keys(this.dataForm).forEach(key => {
          if (key !== 'id' && this.dataForm[key] !== '') {
            updateData[key] = this.dataForm[key]
          }
        })
        // 密码为空时不修改密码
        if (updateData.password === '') {
          delete updateData.password
        }
        
        await updateUser(this.dataForm.id, updateData)
        this.$message.success('更新成功')
        this.dialogVisible = false
        this.loadData()
      } catch (error) {
        console.error('更新失败:', error)
      }
    },
    
    // 删除
    handleDelete(row) {
      this.$confirm(`确定要删除用户 "${row.username}" 吗？`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.doDelete(row.id)
      }).catch(() => {})
    },
    
    // 执行删除
    async doDelete(userId) {
      try {
        await deleteUser(userId)
        this.$message.success('删除成功')
        this.loadData()
      } catch (error) {
        console.error('删除失败:', error)
      }
    },
    
    // 批量删除
    handleBatchDelete() {
      this.$confirm(`确定要删除选中的 ${this.selectedCount} 个用户吗？`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 批量删除 - 逐个删除
        const promises = this.selectedIds.map(id => deleteUser(id))
        Promise.all(promises).then(() => {
          this.$message.success('删除成功')
          this.loadData()
        }).catch(error => {
          console.error('批量删除失败:', error)
        })
      }).catch(() => {})
    },
    
    // 状态变更
    async handleStatusChange(row) {
      try {
        await updateUser(row.id, { is_active: row.is_active })
        this.$message.success('状态更新成功')
      } catch (error) {
        console.error('状态更新失败:', error)
        // 回滚状态
        row.is_active = !row.is_active
      }
    },
    
    // 分配角色
    handleAssignRoles(row) {
      this.currentUser = row
      this.selectedRoleIds = row.roles ? row.roles.map(r => r.id) : []
      this.assignDialogVisible = true
    },
    
    // 提交分配角色
    async handleAssignSubmit() {
      try {
        await assignRoles(this.currentUser.id, this.selectedRoleIds)
        this.$message.success('角色分配成功')
        this.assignDialogVisible = false
        this.loadData()
      } catch (error) {
        console.error('角色分配失败:', error)
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
 * 用户管理页面样式
 */
.user-manage-container {
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

.danger {
  color: #f56c6c !important;
}

.dialog-footer {
  text-align: right;
}
</style>
