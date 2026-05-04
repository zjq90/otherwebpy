<template>
  <div class="member-form">
    <div class="page-container">
      <div class="page-header">
        <span class="page-title">{{ isEdit ? '编辑会员' : '新增会员' }}</span>
        <el-button :icon="ArrowLeft" @click="$router.back()">返回</el-button>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="member-form-content"
      >
        <el-tabs v-model="activeTab">
          <el-tab-pane label="基本信息" name="basic">
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="姓名" prop="name">
                  <el-input v-model="form.name" placeholder="请输入姓名" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="手机号" prop="phone">
                  <el-input v-model="form.phone" placeholder="请输入手机号" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="性别" prop="gender">
                  <el-radio-group v-model="form.gender">
                  <el-radio value="male">男</el-radio>
                  <el-radio value="female">女</el-radio>
                </el-radio-group>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="出生日期">
                  <el-date-picker
                    v-model="form.birth_date"
                    type="date"
                    placeholder="请选择出生日期"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="身份证号">
                  <el-input v-model="form.id_card" placeholder="请输入身份证号" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="邮箱">
                  <el-input v-model="form.email" placeholder="请输入邮箱" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="注册渠道" prop="registration_channel">
                  <el-radio-group v-model="form.registration_channel">
                  <el-radio value="online">线上（官网）</el-radio>
                  <el-radio value="offline">线下（前台录入）</el-radio>
                </el-radio-group>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="紧急联系人">
                  <el-input v-model="form.emergency_contact" placeholder="请输入紧急联系人" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="紧急联系电话">
                  <el-input v-model="form.emergency_phone" placeholder="请输入紧急联系电话" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="注册日期">
                  <el-date-picker
                    v-model="form.registration_date"
                    type="date"
                    placeholder="请选择注册日期"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="24">
                <el-form-item label="联系地址">
                  <el-input
                    v-model="form.address"
                    type="textarea"
                    :rows="2"
                    placeholder="请输入联系地址"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-tab-pane>

          <el-tab-pane label="健康状况" name="health">
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="身高(cm)">
                  <el-input-number
                    v-model="form.height"
                    :min="0"
                    :max="300"
                    :precision="1"
                    placeholder="请输入身高"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="体重(kg)">
                  <el-input-number
                    v-model="form.weight"
                    :min="0"
                    :max="500"
                    :precision="1"
                    placeholder="请输入体重"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="血型">
                  <el-select v-model="form.blood_type" placeholder="请选择血型" clearable style="width: 100%">
                    <el-option label="A型" value="A" />
                    <el-option label="B型" value="B" />
                    <el-option label="AB型" value="AB" />
                    <el-option label="O型" value="O" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="是否有过敏史">
                  <el-radio-group v-model="form.has_allergies">
                  <el-radio :value="true">是</el-radio>
                  <el-radio :value="false">否</el-radio>
                </el-radio-group>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="24">
                <el-form-item label="过敏史详情">
                  <el-input
                    v-model="form.allergy_details"
                    type="textarea"
                    :rows="3"
                    placeholder="请输入过敏史详情"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="24">
                <el-form-item label="既往病史">
                  <el-input
                v-model="form.medical_history"
                type="textarea"
                :rows="3"
                placeholder="请输入既往病史"
              />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="24">
                <el-form-item label="健康状况备注">
                  <el-input
                v-model="form.health_remarks"
                type="textarea"
                :rows="3"
                placeholder="请输入健康状况备注"
              />
                </el-form-item>
              </el-col>
            </el-row>
          </el-tab-pane>

          <el-tab-pane label="实名认证" name="verify">
            <el-alert
              title="实名认证说明"
              type="info"
              :closable="false"
              style="margin-bottom: 20px;"
            >
              <template #default>
                支持两种实名认证方式：
                1. 手机号验证码验证：输入手机号后点击发送验证码进行验证
                2. 人脸识别验证：上传人脸照片进行验证（测试环境支持模拟验证
              </template>
            </el-alert>

            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="验证方式">
                  <el-radio-group v-model="verifyMethod">
                  <el-radio value="sms">手机号验证码</el-radio>
                  <el-radio value="face">人脸识别</el-radio>
                </el-radio-group>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24" v-if="verifyMethod === 'sms'">
              <el-col :span="12">
                <el-form-item label="验证码">
                  <el-row :gutter="10">
                    <el-col :span="16">
                      <el-input
                        v-model="verifyCode"
                        placeholder="请输入验证码"
                        maxlength="6"
                      />
                    </el-col>
                    <el-col :span="8">
                      <el-button
                        type="primary"
                        :loading="sendingCode"
                        :disabled="countdown > 0"
                        @click="handleSendCode"
                      >
                        {{ countdown > 0 ? `${countdown}s` : '发送验证码' }}
                      </el-button>
                    </el-col>
                  </el-row>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24" v-if="verifyMethod === 'face'">
              <el-col :span="12">
                <el-form-item label="人脸照片">
                  <el-upload
                    class="avatar-uploader"
                    action="#"
                    :show-file-list="false"
                    :before-upload="beforeUpload"
                  >
                    <img v-if="faceImage" :src="faceImage" class="avatar" />
                    <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
                  </el-upload>
                  <div class="el-upload__tip">支持上传人脸照片进行验证</div>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="24">
                <el-form-item>
                  <el-button type="success" @click="handleVerify" :loading="verifying">
                    完成认证
                  </el-button>
                </el-form-item>
              </el-col>
            </el-row>
          </el-tab-pane>
        </el-tabs>

        <el-divider />

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            保存
          </el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Plus } from '@element-plus/icons-vue'
import { createMember, updateMember, getMemberDetail, sendVerificationCode, verifyMember } from '@/api/member'

const route = useRoute()
const router = useRouter()

const formRef = ref(null)
const submitting = ref(false)
const sendingCode = ref(false)
const verifying = ref(false)
const countdown = ref(0)
const activeTab = ref('basic')
const verifyMethod = ref('sms')
const verifyCode = ref('')
const faceImage = ref('')

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  name: '',
  phone: '',
  gender: 'male',
  birth_date: '',
  id_card: '',
  email: '',
  registration_channel: 'offline',
  emergency_contact: '',
  emergency_phone: '',
  registration_date: '',
  address: '',
  height: null,
  weight: null,
  blood_type: '',
  has_allergies: false,
  allergy_details: '',
  medical_history: '',
  health_remarks: ''
})

const rules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ],
  registration_channel: [
    { required: true, message: '请选择注册渠道', trigger: 'change' }
  ]
}

const fetchMember = async () => {
  if (!isEdit.value) return
  try {
    const res = await getMemberDetail(route.params.id)
    if (res.data) {
      Object.assign(form, res.data)
    }
  } catch (error) {
    ElMessage.error('获取会员信息失败')
  }
}

const handleSendCode = async () => {
  if (!form.phone) {
    ElMessage.warning('请先输入手机号')
    return
  }
  
  sendingCode.value = true
  try {
    await sendVerificationCode(form.phone)
    ElMessage.success('验证码已发送（测试环境请查看控制台）')
    
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
  } catch (error) {
    ElMessage.error('发送失败')
  } finally {
    sendingCode.value = false
  }
}

const handleVerify = async () => {
  if (!isEdit.value) {
    ElMessage.warning('请先保存会员信息')
    return
  }
  
  verifying.value = true
  try {
    const data = {
      verification_type: verifyMethod.value
    }
    if (verifyMethod.value === 'sms') {
      data.verification_code = verifyCode.value
    }
    
    await verifyMember(route.params.id, data)
    ElMessage.success('认证成功')
  } catch (error) {
    ElMessage.error('认证失败')
  } finally {
    verifying.value = false
  }
}

const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  
  const reader = new FileReader()
  reader.onload = (e) => {
    faceImage.value = e.target.result
  }
  reader.readAsDataURL(file)
  return false
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateMember(route.params.id, form)
      ElMessage.success('更新成功')
    } else {
      const res = await createMember(form)
      ElMessage.success('创建成功')
      if (res.data?.id) {
        router.push(`/members/detail/${res.data.id}`)
        return
      }
    }
    router.back()
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchMember()
})
</script>

<style lang="scss" scoped>
.member-form {
  .member-form-content {
    max-width: 800px;
  }

  :deep(.el-tabs__content) {
    padding: 20px 0;
  }

  .avatar-uploader {
    :deep(.el-upload) {
      border: 1px dashed var(--el-border-color);
      border-radius: 6px;
      cursor: pointer;
      position: relative;
      overflow: hidden;
      transition: var(--el-transition-duration-fast);
  
      &:hover {
        border-color: var(--el-color-primary);
      }
    }

    .avatar-uploader-icon {
      font-size: 28px;
      color: #8c939d;
      width: 178px;
      height: 178px;
      text-align: center;
      line-height: 178px;
    }

    .avatar {
      width: 178px;
      height: 178px;
      display: block;
    }
  }
}
</style>
