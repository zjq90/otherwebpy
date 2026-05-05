import { get } from './request'

export interface RoutePoint {
  order_id: number
  order_no: string
  user_name: string
  address: string
  latitude?: number
  longitude?: number
  estimated_weight?: number
}

export interface RoutePlan {
  total_distance: number
  total_duration: number
  points: RoutePoint[]
  optimized_order: number[]
}

export const planRoute = async (startLat?: number, startLon?: number): Promise<RoutePlan> => {
  let url = '/route/plan'
  const params: string[] = []
  if (startLat !== undefined) {
    params.push(`start_lat=${startLat}`)
  }
  if (startLon !== undefined) {
    params.push(`start_lon=${startLon}`)
  }
  if (params.length > 0) {
    url += '?' + params.join('&')
  }
  return get<RoutePlan>(url)
}

export const getPendingRouteOrders = async (): Promise<RoutePoint[]> => {
  return get<RoutePoint[]>('/route/orders')
}

export default {
  planRoute,
  getPendingRouteOrders
}
