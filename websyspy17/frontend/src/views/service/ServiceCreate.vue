<template>
  <div class="service-create">
    <el-card>
      <template #header>
        <span>提交服务请求</span>
      </template>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        style="max-width: 600px;"
      >
        <el-form-item label="服务类型" prop="service_type">
          <el-radio-group v-model="form.service_type">
            <el-radio value="repair">
              <el-icon><Tools /></el-icon>
              报修
            </el-radio>
            <el-radio value="complaint">
              <el-icon><Warning /></el-icon>
              投诉
            </el-radio>
            <el-radio value="consult">
              <el-icon><QuestionFilled /></el-icon>
              咨询
            </el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="请求标题" prop="title">
          <el-input
            v-model="form.title"
            placeholder="请输入请求标题"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="详细描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="5"
            placeholder="请详细描述您的问题或需求"
          />
        </el-form-item>
        
        <el-form-item label="优先级" prop="priority">
          <el-radio-group v-model="form.priority">
            <el-radio :value="1">普通</el-radio>
            <el-radio :value="2">紧急</el-radio>
            <el-radio :value="3">非常紧急</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="房间号" prop="room_number">
          <el-input
            v-model="form.room_number"
            placeholder="请输入您的房间号，如：1栋101室"
          />
        </el-form-item>
        
        <el-form-item label="具体位置" prop="location">
          <el-input
            v-model="form.location"
            placeholder="请输入具体位置描述"
          />
        </el-form-item>
        
        <el-form-item label="联系人" prop="contact_name">
          <el-input
            v-model="form.contact_name"
            placeholder="请输入联系人姓名"
          />
        </el-form-item>
        
        <el-form-item label="联系电话" prop="contact_phone">
          <el-input
            v-model="form.contact_phone"
            placeholder="请输入联系电话"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">
            提交申请
          </el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button @click="handleCancel">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { serviceApi } from '@/api/service'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  service_type: 'repair',
  title: '',
  description: '',
  priority: 1,
  room_number: '',
  location: '',
  contact_name: '',
  contact_phone: ''
})

const rules = {
  service_type: [
    { required: true, message: '请选择服务类型', trigger: 'change' }
  ],
  title: [
    { required: true, message: '请输入请求标题', trigger: 'blur' },
    { min: 2, max: 200, message: '标题长度在2-200个字符之间', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入详细描述', trigger: 'blur' }
  ],
  contact_name: [
    { required: true, message: '请输入联系人姓名', trigger: 'blur' }
  ],
  contact_phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' }
  ]
}

onMounted(() => {
  if (userStore.user) {
    form.room_number = userStore.user.room_number || ''
    form.contact_name = userStore.user.real_name || ''
    form.contact_phone = userStore.user.phone || ''
  }
})

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await serviceApi.createServiceRequest(form)
        ElMessage.success('提交成功！')
        router.push('/services')
      } catch (error) {
        console.error('提交失败:', error)
      } finally {
        loading.value = false
      }
    }
  })
}

const handleReset = () => {
  if (!formRef.value) return
  formRef.value.resetFields()
}

const handleCancel = () => {
  router.back()
}
</script>

<style scoped>
.service-create {
  padding: 0;
}
</style>
