/**
 * 会员卡相关API
 */

import { get } from "@/utils/request";

const API_PREFIX = "/api/v1/cards";

/**
 * 获取会员卡类型列表
 */
export function getCardTypes(params?: {
  category?: string;
  is_on_sale?: boolean;
}) {
  return get(`${API_PREFIX}/types`, params, {
    needAuth: false,
    loadingText: "加载中..."
  });
}

/**
 * 获取会员卡类型详情
 */
export function getCardTypeDetail(cardTypeId: number) {
  return get(`${API_PREFIX}/types/${cardTypeId}`, {}, {
    needAuth: false,
    loadingText: "加载中..."
  });
}

/**
 * 获取我的卡包
 */
export function getMyCards(params?: {
  status?: string;
  only_valid?: boolean;
}) {
  return get(`${API_PREFIX}/my`, params, {
    loadingText: "加载中..."
  });
}

/**
 * 获取我的会员卡详情
 */
export function getMyCardDetail(userCardId: number) {
  return get(`${API_PREFIX}/my/${userCardId}`, {}, {
    loadingText: "加载中..."
  });
}

/**
 * 获取会员卡使用记录
 */
export function getCardUsageRecords(
  userCardId: number,
  params?: {
    page?: number;
    page_size?: number;
  }
) {
  return get(`${API_PREFIX}/my/${userCardId}/usage-records`, params, {
    loadingText: "加载中..."
  });
}

export default {
  getCardTypes,
  getCardTypeDetail,
  getMyCards,
  getMyCardDetail,
  getCardUsageRecords
};
