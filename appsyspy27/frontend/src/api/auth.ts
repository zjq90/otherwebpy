/**
 * 认证相关API
 */

import { post, get, put } from "@/utils/request";

const API_PREFIX = "/api/v1/auth";

/**
 * 用户注册
 */
export function register(data: {
  username: string;
  password: string;
  real_name?: string;
  phone?: string;
  email?: string;
}) {
  return post(`${API_PREFIX}/register`, data, {
    needAuth: false,
    loadingText: "注册中..."
  });
}

/**
 * 用户登录
 */
export function login(data: {
  username: string;
  password: string;
}) {
  return post(`${API_PREFIX}/login`, data, {
    needAuth: false,
    loadingText: "登录中..."
  });
}

/**
 * 微信登录
 */
export function wechatLogin(code: string) {
  return post(`${API_PREFIX}/wechat-login`, { code }, {
    needAuth: false,
    loadingText: "微信登录中..."
  });
}

/**
 * 获取当前用户信息
 */
export function getCurrentUser() {
  return get(`${API_PREFIX}/me`, {}, {
    loadingText: "加载中..."
  });
}

/**
 * 更新当前用户信息
 */
export function updateCurrentUser(data: {
  real_name?: string;
  avatar?: string;
  phone?: string;
  email?: string;
}) {
  return put(`${API_PREFIX}/me`, data, {
    loadingText: "更新中..."
  });
}

/**
 * 绑定手机号
 */
export function bindPhone(phone: string, verifyCode: string) {
  return post(`${API_PREFIX}/bind-phone`, { phone, verifyCode }, {
    loadingText: "绑定中..."
  });
}

/**
 * 绑定微信
 */
export function bindWechat(code: string) {
  return post(`${API_PREFIX}/bind-wechat`, { code }, {
    loadingText: "绑定中..."
  });
}

/**
 * 保存登录状态
 */
export function saveLoginState(token: string, userInfo: any) {
  uni.setStorageSync("token", token);
  uni.setStorageSync("userInfo", userInfo);
}

/**
 * 清除登录状态
 */
export function clearLoginState() {
  uni.removeStorageSync("token");
  uni.removeStorageSync("userInfo");
}

/**
 * 获取本地用户信息
 */
export function getLocalUserInfo() {
  return uni.getStorageSync("userInfo") || null;
}

/**
 * 检查是否已登录
 */
export function isLoggedIn(): boolean {
  const token = uni.getStorageSync("token");
  return !!token;
}

export default {
  register,
  login,
  wechatLogin,
  getCurrentUser,
  updateCurrentUser,
  bindPhone,
  bindWechat,
  saveLoginState,
  clearLoginState,
  getLocalUserInfo,
  isLoggedIn
};
