import { post } from './request'

export interface LoginParams {
  username: string
  password: string
}

export interface LoginResult {
  access_token: string
  token_type: string
  expires_in: number
  user_id: number
  username: string
  real_name?: string
}

export interface RegisterParams {
  username: string
  password: string
  real_name?: string
  phone?: string
}

export interface RegisterResult {
  user_id: number
  username: string
  message: string
}

export const login = async (params: LoginParams): Promise<LoginResult> => {
  const formData = new FormData()
  formData.append('username', params.username)
  formData.append('password', params.password)
  
  return post<LoginResult>('/auth/login', formData, false)
}

export const register = async (params: RegisterParams): Promise<RegisterResult> => {
  return post<RegisterResult>('/auth/register', params, false)
}

export const saveLoginInfo = (result: LoginResult) => {
  uni.setStorageSync('token', result.access_token)
  uni.setStorageSync('userInfo', {
    user_id: result.user_id,
    username: result.username,
    real_name: result.real_name
  })
}

export const clearLoginInfo = () => {
  uni.removeStorageSync('token')
  uni.removeStorageSync('userInfo')
}

export const getToken = (): string | null => {
  return uni.getStorageSync('token')
}

export const getUserInfo = (): any => {
  return uni.getStorageSync('userInfo')
}

export const isLoggedIn = (): boolean => {
  const token = getToken()
  return !!token
}

export default {
  login,
  register,
  saveLoginInfo,
  clearLoginInfo,
  getToken,
  getUserInfo,
  isLoggedIn
}
