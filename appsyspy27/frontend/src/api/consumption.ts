/**
 * 消费记录相关API
 */

import { get } from "@/utils/request";

const API_PREFIX = "/api/v1/consumptions";

/**
 * 获取我的消费记录
 */
export function getMyConsumptions(params?: {
  record_type?: string;
  start_date?: string;
  end_date?: string;
  page?: number;
  page_size?: number;
}) {
  return get(`${API_PREFIX}/my`, params, {
    loadingText: "加载中..."
  });
}

/**
 * 获取消费记录详情
 */
export function getConsumptionDetail(recordId: number) {
  return get(`${API_PREFIX}/my/${recordId}`, {}, {
    loadingText: "加载中..."
  });
}

/**
 * 获取月度账单
 */
export function getMonthlyBill(year: number, month: number) {
  return get(`${API_PREFIX}/monthly-bill`, { year, month }, {
    loadingText: "加载中..."
  });
}

/**
 * 获取消费统计
 */
export function getConsumptionStatistics(period: string = "month") {
  return get(`${API_PREFIX}/statistics`, { period }, {
    loadingText: "加载中..."
  });
}

export default {
  getMyConsumptions,
  getConsumptionDetail,
  getMonthlyBill,
  getConsumptionStatistics
};
