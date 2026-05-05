/**
 * 表单验证规则工具
 * 提供Element Plus表单验证所需的常用规则
 */

// 手机号正则（中国大陆手机号）
const PHONE_REGEX = /^1[3-9]\d{9}$/

// 邮箱正则
const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/

// 身份证号正则（18位或15位）
const ID_CARD_REGEX = /(^\d{18}$)|(^\d{15}$)|(^\d{17}(\d|X|x)$)/

// 正整数正则
const POSITIVE_INT_REGEX = /^[1-9]\d*$/

// 非负整数正则
const NON_NEGATIVE_INT_REGEX = /^[0-9]\d*$/

// 金额正则（最多两位小数）
const AMOUNT_REGEX = /^\d+(\.\d{1,2})?$/


/**
 * 验证手机号
 * @param {string} phone - 手机号
 * @returns {boolean} - 是否有效
 */
export function isValidPhone(phone) {
  if (!phone) return false
  const p = String(phone).trim().replace(/-/g, '').replace(/\s/g, '')
  return PHONE_REGEX.test(p)
}

/**
 * 验证邮箱
 * @param {string} email - 邮箱
 * @returns {boolean} - 是否有效
 */
export function isValidEmail(email) {
  if (!email) return false
  const e = String(email).trim()
  if (e.length > 254) return false
  return EMAIL_REGEX.test(e)
}

/**
 * 验证身份证号
 * @param {string} idCard - 身份证号
 * @returns {boolean} - 是否有效
 */
export function isValidIdCard(idCard) {
  if (!idCard) return false
  const card = String(idCard).trim().toUpperCase()
  
  if (!ID_CARD_REGEX.test(card)) return false
  
  if (card.length === 15) return true
  
  if (card.length === 18) {
    const weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    const checkCodes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    
    let sum = 0
    for (let i = 0; i < 17; i++) {
      sum += parseInt(card[i]) * weights[i]
    }
    const checkCode = checkCodes[sum % 11]
    return card[17] === checkCode
  }
  
  return false
}

/**
 * 验证正整数
 * @param {number|string} value - 数值
 * @returns {boolean} - 是否有效
 */
export function isValidPositiveInt(value) {
  if (value === null || value === undefined || value === '') return false
  const v = String(value).trim()
  return POSITIVE_INT_REGEX.test(v)
}

/**
 * 验证非负整数
 * @param {number|string} value - 数值
 * @returns {boolean} - 是否有效
 */
export function isValidNonNegativeInt(value) {
  if (value === null || value === undefined || value === '') return false
  const v = String(value).trim()
  return NON_NEGATIVE_INT_REGEX.test(v)
}

/**
 * 验证金额格式
 * @param {number|string} value - 金额
 * @returns {boolean} - 是否有效
 */
export function isValidAmount(value) {
  if (value === null || value === undefined || value === '') return false
  const v = String(value).trim()
  if (parseFloat(v) < 0) return false
  return AMOUNT_REGEX.test(v)
}


/**
 * Element Plus 表单验证规则集合
 */

// 必填验证
export const requiredRule = (message = '此项为必填项', trigger = 'blur') => ({
  required: true,
  message,
  trigger
})

// 字符串长度验证
export const stringLengthRule = (min = 0, max = 255, message = null, trigger = 'blur') => {
  const msg = message || `长度应在 ${min} 到 ${max} 个字符之间`
  return {
    min,
    max,
    message: msg,
    trigger
  }
}

// 手机号验证
export const phoneRule = (message = '请输入正确的手机号', trigger = 'blur') => ({
  validator: (rule, value, callback) => {
    if (!value || value === '') {
      callback()
      return
    }
    if (!isValidPhone(value)) {
      callback(new Error(message))
      return
    }
    callback()
  },
  trigger
})

// 邮箱验证
export const emailRule = (message = '请输入正确的邮箱地址', trigger = 'blur') => ({
  validator: (rule, value, callback) => {
    if (!value || value === '') {
      callback()
      return
    }
    if (!isValidEmail(value)) {
      callback(new Error(message))
      return
    }
    callback()
  },
  trigger
})

// 身份证号验证
export const idCardRule = (message = '请输入正确的身份证号', trigger = 'blur') => ({
  validator: (rule, value, callback) => {
    if (!value || value === '') {
      callback()
      return
    }
    if (!isValidIdCard(value)) {
      callback(new Error(message))
      return
    }
    callback()
  },
  trigger
})

// 正整数验证
export const positiveIntRule = (message = '请输入正整数', trigger = 'blur') => ({
  validator: (rule, value, callback) => {
    if (value === null || value === undefined || value === '') {
      callback()
      return
    }
    if (!isValidPositiveInt(value)) {
      callback(new Error(message))
      return
    }
    callback()
  },
  trigger
})

// 非负整数验证
export const nonNegativeIntRule = (message = '请输入非负整数', trigger = 'blur') => ({
  validator: (rule, value, callback) => {
    if (value === null || value === undefined || value === '') {
      callback()
      return
    }
    if (!isValidNonNegativeInt(value)) {
      callback(new Error(message))
      return
    }
    callback()
  },
  trigger
})

// 金额验证
export const amountRule = (message = '请输入正确的金额（最多两位小数）', trigger = 'blur') => ({
  validator: (rule, value, callback) => {
    if (value === null || value === undefined || value === '') {
      callback()
      return
    }
    if (!isValidAmount(value)) {
      callback(new Error(message))
      return
    }
    callback()
  },
  trigger
})

// 数字范围验证
export const numberRangeRule = (min = null, max = null, message = null, trigger = 'blur') => ({
  validator: (rule, value, callback) => {
    if (value === null || value === undefined || value === '') {
      callback()
      return
    }
    const num = parseFloat(value)
    if (isNaN(num)) {
      callback(new Error(message || '请输入数字'))
      return
    }
    if (min !== null && num < min) {
      callback(new Error(message || `数值不能小于 ${min}`))
      return
    }
    if (max !== null && num > max) {
      callback(new Error(message || `数值不能大于 ${max}`))
      return
    }
    callback()
  },
  trigger
})


/**
 * 常用组合规则
 */

// 客户名称验证
export const customerNameRules = [
  requiredRule('请输入客户名称'),
  stringLengthRule(1, 100, '客户名称长度不能超过100个字符')
]

// 联系人验证
export const contactPersonRules = [
  stringLengthRule(0, 50, '联系人姓名长度不能超过50个字符')
]

// 手机号验证（可选）
export const phoneRules = [
  phoneRule()
]

// 手机号验证（必填）
export const phoneRequiredRules = [
  requiredRule('请输入手机号'),
  phoneRule()
]

// 邮箱验证（可选）
export const emailRules = [
  emailRule()
]

// 邮箱验证（必填）
export const emailRequiredRules = [
  requiredRule('请输入邮箱'),
  emailRule()
]

// 员工姓名验证
export const employeeNameRules = [
  requiredRule('请输入员工姓名'),
  stringLengthRule(1, 50, '员工姓名长度不能超过50个字符')
]

// 身份证号验证
export const idCardRules = [
  idCardRule()
]

// 产品名称验证
export const productNameRules = [
  requiredRule('请输入产品名称'),
  stringLengthRule(1, 100, '产品名称长度不能超过100个字符')
]

// 数量验证（正整数）
export const quantityRules = [
  requiredRule('请输入数量'),
  positiveIntRule('数量必须为正整数'),
  numberRangeRule(1, 1000000, '数量应在1-1000000之间')
]

// 金额验证
export const amountRules = [
  requiredRule('请输入金额'),
  amountRule(),
  numberRangeRule(0, 100000000000, '金额不能超过100000000000')
]

// 金额验证（可选）
export const amountOptionalRules = [
  amountRule(),
  numberRangeRule(0, 100000000000, '金额不能超过100000000000')
]

// 库存数量验证
export const inventoryQuantityRules = [
  nonNegativeIntRule('库存数量必须为非负整数'),
  numberRangeRule(0, 10000000, '库存数量不能超过10000000')
]

// 地址验证
export const addressRules = [
  stringLengthRule(0, 500, '地址长度不能超过500个字符')
]

// 描述验证
export const descriptionRules = [
  stringLengthRule(0, 500, '描述长度不能超过500个字符')
]

// 部门名称验证
export const departmentNameRules = [
  requiredRule('请输入部门名称'),
  stringLengthRule(1, 100, '部门名称长度不能超过100个字符')
]

// 职位名称验证
export const positionNameRules = [
  requiredRule('请输入职位名称'),
  stringLengthRule(1, 100, '职位名称长度不能超过100个字符')
]

// 薪资验证
export const salaryRules = [
  amountRule(),
  numberRangeRule(0, 100000000, '薪资不能超过100000000')
]

// 账户名称验证
export const accountNameRules = [
  requiredRule('请输入账户名称'),
  stringLengthRule(1, 100, '账户名称长度不能超过100个字符')
]

// 银行账号验证
export const bankAccountRules = [
  {
    validator: (rule, value, callback) => {
      if (!value || value === '') {
        callback()
        return
      }
      const v = String(value).trim().replace(/\s/g, '')
      if (v.length > 50) {
        callback(new Error('银行账号长度不能超过50个字符'))
        return
      }
      if (!/^\d+$/.test(v)) {
        callback(new Error('银行账号只能包含数字'))
        return
      }
      callback()
    },
    trigger: 'blur'
  }
]

// 税号验证
export const taxNoRules = [
  {
    validator: (rule, value, callback) => {
      if (!value || value === '') {
        callback()
        return
      }
      const v = String(value).trim()
      if (v.length !== 15 && v.length !== 17 && v.length !== 18) {
        callback(new Error('税号长度必须为15、17或18位'))
        return
      }
      if (!/^[A-Z0-9-]+$/i.test(v)) {
        callback(new Error('税号格式不正确'))
        return
      }
      callback()
    },
    trigger: 'blur'
  }
]


// 导出所有规则
export default {
  // 验证函数
  isValidPhone,
  isValidEmail,
  isValidIdCard,
  isValidPositiveInt,
  isValidNonNegativeInt,
  isValidAmount,
  
  // 基础规则
  requiredRule,
  stringLengthRule,
  phoneRule,
  emailRule,
  idCardRule,
  positiveIntRule,
  nonNegativeIntRule,
  amountRule,
  numberRangeRule,
  
  // 组合规则
  customerNameRules,
  contactPersonRules,
  phoneRules,
  phoneRequiredRules,
  emailRules,
  emailRequiredRules,
  employeeNameRules,
  idCardRules,
  productNameRules,
  quantityRules,
  amountRules,
  amountOptionalRules,
  inventoryQuantityRules,
  addressRules,
  descriptionRules,
  departmentNameRules,
  positionNameRules,
  salaryRules,
  accountNameRules,
  bankAccountRules,
  taxNoRules
}
