import { get, post } from './request'

export interface UserInfo {
  id: number
  username: string
  real_name?: string
  phone?: string
  avatar?: string
  id_card?: string
  total_orders: number
  total_weight: number
  total_income: number
  is_active: boolean
  is_verified: boolean
  created_at: string
}

export interface UserStats {
  total_orders: number
  total_weight: number
  total_income: number
  today_orders: number
  today_weight: number
  today_income: number
}

export interface WithdrawalRecord {
  id: number
  user_id: number
  amount: number
  bank_card: string
  bank_name: string
  account_name: string
  status: string
  reject_reason?: string
  processed_at?: string
  created_at: string
}

export interface WithdrawalParams {
  amount: number
  bank_card: string
  bank_name: string
  account_name: string
}

export const getProfile = async (): Promise<UserInfo> => {
  return get<UserInfo>('/users/profile')
}

export const getStats = async (): Promise<UserStats> => {
  return get<UserStats>('/users/stats')
}

export const updateProfile = async (data: Partial<UserInfo>): Promise<UserInfo> => {
  return get<UserInfo>('/users/profile', data)
}

export const createWithdrawal = async (params: WithdrawalParams): Promise<WithdrawalRecord> => {
  return post<WithdrawalRecord>('/users/withdrawal', params)
}

export const getWithdrawals = async (status?: string): Promise<WithdrawalRecord[]> => {
  const url = status ? `/users/withdrawals?status=${status}` : '/users/withdrawals'
  return get<WithdrawalRecord[]>(url)
}

export const getWithdrawalDetail = async (withdrawalId: number): Promise<WithdrawalRecord> => {
  return get<WithdrawalRecord>(`/users/withdrawals/${withdrawalId}`)
}

export default {
  getProfile,
  getStats,
  updateProfile,
  createWithdrawal,
  getWithdrawals,
  getWithdrawalDetail
}
