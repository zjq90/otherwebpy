import { get, post } from './request'

export interface Order {
  id: number
  order_no: string
  user_name: string
  user_phone: string
  address: string
  province?: string
  city?: string
  district?: string
  latitude?: number
  longitude?: number
  clothing_types?: string
  estimated_weight?: number
  estimated_quantity?: number
  description?: string
  collector_id?: number
  actual_weight?: number
  actual_quantity?: number
  recycle_photos?: string
  unit_price: number
  total_amount?: number
  status: string
  reject_reason?: string
  cancel_reason?: string
  appointment_time?: string
  accepted_at?: string
  completed_at?: string
  created_at: string
  updated_at: string
}

export interface OrderListResponse {
  total: number
  orders: Order[]
}

export interface OrderAcceptParams {
  order_id: number
}

export interface OrderRejectParams {
  order_id: number
  reject_reason: string
}

export interface OrderCompleteParams {
  order_id: number
  actual_weight: number
  actual_quantity?: number
  recycle_photos?: string
  unit_price?: number
}

export const getPendingOrders = async (page: number = 1, pageSize: number = 10): Promise<OrderListResponse> => {
  return get<OrderListResponse>(`/orders/pending?page=${page}&page_size=${pageSize}`)
}

export const getAcceptedOrders = async (page: number = 1, pageSize: number = 10): Promise<OrderListResponse> => {
  return get<OrderListResponse>(`/orders/accepted?page=${page}&page_size=${pageSize}`)
}

export const getCompletedOrders = async (page: number = 1, pageSize: number = 10): Promise<OrderListResponse> => {
  return get<OrderListResponse>(`/orders/completed?page=${page}&page_size=${pageSize}`)
}

export const getOrderDetail = async (orderId: number): Promise<Order> => {
  return get<Order>(`/orders/${orderId}`)
}

export const acceptOrder = async (params: OrderAcceptParams): Promise<Order> => {
  return post<Order>('/orders/accept', params)
}

export const rejectOrder = async (params: OrderRejectParams): Promise<Order> => {
  return post<Order>('/orders/reject', params)
}

export const completeOrder = async (params: OrderCompleteParams): Promise<Order> => {
  return post<Order>('/orders/complete', params)
}

export const createOrder = async (params: any): Promise<Order> => {
  return post<Order>('/orders/create', params, false)
}

export const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    pending: '待接单',
    accepted: '已接单',
    rejected: '已拒绝',
    processing: '回收中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

export const getStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    pending: '#ff976a',
    accepted: '#2979ff',
    rejected: '#909399',
    processing: '#07c160',
    completed: '#f56c6c',
    cancelled: '#c0c4cc'
  }
  return colorMap[status] || '#909399'
}

export default {
  getPendingOrders,
  getAcceptedOrders,
  getCompletedOrders,
  getOrderDetail,
  acceptOrder,
  rejectOrder,
  completeOrder,
  createOrder,
  getStatusText,
  getStatusColor
}
