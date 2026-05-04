<template>
  <div class="activity-create">
    <el-card>
      <template #header>
        <span>创建活动</span>
      </template>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        style="max-width: 700px;"
      >
        <el-form-item label="活动标题" prop="title">
          <el-input
            v-model="form.title"
            placeholder="请输入活动标题"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="活动类型" prop="activity_type">
          <el-select v-model="form.activity_type" placeholder="请选择活动类型" style="width: 100%;">
            <el-option label="节日活动" value="festival" />
            <el-option label="邻里互动" value="neighbor_interaction" />
            <el-option label="体育活动" value="sports" />
            <el-option label="文化活动" value="cultural" />
            <el-option label="公益活动" value="charity" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="活动描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="5"
            placeholder="请输入活动详细描述"
          />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始时间" prop="start_time">
              <el-date-picker
                v-model="form.start_time"
                type="datetime"
                placeholder="选择开始时间"
                style="width: 100%;"
                value-format="YYYY-MM-DD HH:mm:ss"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间" prop="end_time">
              <el-date-picker
                v-model="form.end_time"
                type="datetime"
                placeholder="选择结束时间"
                style="width: 100%;"
                value-format="YYYY-MM-DD HH:mm:ss"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="报名截止时间" prop="registration_deadline">
          <el-date-picker
            v-model="form.registration_deadline"
            type="datetime"
            placeholder="选择报名截止时间"
            style="width: 100%;"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        
        <el-form-item label="活动地点" prop="location">
          <el-input
            v-model="form.location"
            placeholder="请输入活动地点"
          />
        </el-form-item>
        
        <el-form-item label="最大参与人数" prop="max_participants">
          <el-input-number
            v-model="form.max_participants"
            :min="0"
            placeholder="不填则表示不限人数"
            style="width: 100%;"
          />
        </el-form-item>
        
        <el-form-item label="活动图片" prop="image_url">
          <el-input
            v-model="form.image_url"
            placeholder="请输入活动图片URL（可选）"
          />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系人" prop="contact_name">
              <el-input
                v-model="form.contact_name"
                placeholder="请输入联系人姓名"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="contact_phone">
              <el-input
                v-model="form.contact_phone"
                placeholder="请输入联系电话"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="设为推荐">
          <el-switch v-model="form.is_featured" />
          <span style="margin-left: 10px; color: #909399;">开启后将在首页推荐展示</span>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">
            创建活动
          </el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button @click="handleCancel">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { activityApi } from '@/api/activity'

const router = useRouter()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  title: '',
  activity_type: 'other',
  description: '',
  start_time: null,
  end_time: null,
  registration_deadline: null,
  location: '',
  max_participants: null,
  image_url: '',
  contact_name: '',
  contact_phone: '',
  is_featured: false
})

const rules = {
  title: [
    { required: true, message: '请输入活动标题', trigger: 'blur' },
    { min: 2, max: 200, message: '标题长度在2-200个字符之间', trigger: 'blur' }
  ],
  activity_type: [
    { required: true, message: '请选择活动类型', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入活动描述', trigger: 'blur' }
  ],
  start_time: [
    { required: true, message: '请选择开始时间', trigger: 'change' }
  ],
  end_time: [
    { required: true, message: '请选择结束时间', trigger: 'change' }
  ],
  location: [
    { required: true, message: '请输入活动地点', trigger: 'blur' }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const submitData = { ...form }
        if (submitData.max_participants === 0) {
          submitData.max_participants = null
        }
        
        const res = await activityApi.createActivity(submitData)
        ElMessage.success('创建成功！')
        
        if (res.id) {
          await activityApi.publishActivity(res.id)
          ElMessage.success('活动已发布！')
        }
        
        router.push('/activities')
      } catch (error) {
        console.error('创建失败:', error)
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
.activity-create {
  padding: 0;
}
</style>
