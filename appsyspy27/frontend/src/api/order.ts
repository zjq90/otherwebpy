/**
 * 订单相关API
 */

import { get, post } from "@/utils/request";

const API_PREFIX = "/api/v1/orders";

/**
 * 获取优惠活动列表
 */
export function getPromotions(isActive: boolean = true) {
  return get(`${API_PREFIX}/promotions`, { is_active: isActive }, {
    needAuth: false,
    loadingText: "加载中..."
  });
}

/**
 * 创建订单
 */
export function createOrder(data: {
  order_type: string;
  card_type_id?: number;
  goods_id?: number;
  quantity: number;
  promotion_id?: number;
}) {
  return post(`${API_PREFIX}/create`, data, {
    loadingText: "创建订单中..."
  });
}

/**
 * 支付订单
 */
export function payOrder(data: {
  order_id: number;
  pay_method: string;
}) {
  return post(`${API_PREFIX}/pay`, data, {
    loadingText: "支付中..."
  });
}

/**
 * 获取我的订单列表
 */
export function getMyOrders(params?: {
  status?: string;
  order_type?: string;
  page?: number;
  page_size?: number;
}) {
  return get(`${API_PREFIX}/my`, params, {
    loadingText: "加载中..."
  });
}

/**
 * 获取订单详情
 */
export function getOrderDetail(orderId: number) {
  return get(`${API_PREFIX}/my/${orderId}`, {}, {
    loadingText: "加载中..."
  });
}

/**
 * 取消订单
 */
export function cancelOrder(orderId: number) {
  return post(`${API_PREFIX}/my/${orderId}/cancel`, {}, {
    loadingText: "取消中..."
  });
}

export default {
  getPromotions,
  createOrder,
  payOrder,
  getMyOrders,
  getOrderDetail,
  cancelOrder
};
