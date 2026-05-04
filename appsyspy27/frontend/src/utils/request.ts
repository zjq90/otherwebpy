/**
 * HTTP请求封装
 * 统一处理请求拦截、响应拦截、错误处理
 */

// API基础地址
const BASE_URL = "http://localhost:8000";

// 请求配置类型
interface RequestConfig {
  url: string;
  method?: "GET" | "POST" | "PUT" | "DELETE";
  data?: any;
  header?: Record<string, string>;
  needAuth?: boolean;
  showLoading?: boolean;
  loadingText?: string;
  showError?: boolean;
}

// 响应数据类型
interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

/**
 * 获取认证Token
 */
function getToken(): string | null {
  return uni.getStorageSync("token") || null;
}

/**
 * 统一错误处理
 */
function handleError(statusCode: number, message: string, showError: boolean): void {
  console.error(`请求错误 [${statusCode}]:`, message);
  
  if (showError) {
    let errorMsg = "网络请求失败";
    
    switch (statusCode) {
      case 401:
        errorMsg = "登录已过期，请重新登录";
        // 清除登录状态
        uni.removeStorageSync("token");
        uni.removeStorageSync("userInfo");
        // 跳转到登录页
        uni.redirectTo({
          url: "/pages/login/index"
        });
        break;
      case 403:
        errorMsg = "无权限访问";
        break;
      case 404:
        errorMsg = "请求资源不存在";
        break;
      case 422:
        errorMsg = "参数验证失败";
        break;
      case 500:
        errorMsg = "服务器内部错误";
        break;
      default:
        errorMsg = message || "请求失败";
    }
    
    uni.showToast({
      title: errorMsg,
      icon: "none",
      duration: 2000
    });
  }
}

/**
 * 发起HTTP请求
 */
export function request<T = any>(config: RequestConfig): Promise<ApiResponse<T>> {
  const {
    url,
    method = "GET",
    data,
    header = {},
    needAuth = true,
    showLoading = true,
    loadingText = "加载中...",
    showError = true
  } = config;

  // 显示加载提示
  if (showLoading) {
    uni.showLoading({
      title: loadingText,
      mask: true
    });
  }

  // 构建请求头
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...header
  };

  // 添加认证Token
  if (needAuth) {
    const token = getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    } else {
      uni.hideLoading();
      handleError(401, "未登录", showError);
      return Promise.reject(new Error("未登录"));
    }
  }

  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + url,
      method,
      data,
      header: headers,
      success: (res) => {
        uni.hideLoading();

        const statusCode = res.statusCode;
        const responseData = res.data as ApiResponse<T>;

        if (statusCode === 200 || statusCode === 201) {
          // 请求成功
          resolve(responseData);
        } else {
          // HTTP错误状态码
          const message = responseData?.message || `HTTP Error ${statusCode}`;
          handleError(statusCode, message, showError);
          reject(new Error(message));
        }
      },
      fail: (err) => {
        uni.hideLoading();
        console.error("请求失败:", err);
        handleError(-1, err.errMsg || "网络请求失败", showError);
        reject(err);
      }
    });
  });
}

/**
 * 封装GET请求
 */
export function get<T = any>(
  url: string,
  data?: any,
  config?: Omit<RequestConfig, "url" | "method" | "data">
): Promise<ApiResponse<T>> {
  return request<T>({
    url,
    method: "GET",
    data,
    ...config
  });
}

/**
 * 封装POST请求
 */
export function post<T = any>(
  url: string,
  data?: any,
  config?: Omit<RequestConfig, "url" | "method" | "data">
): Promise<ApiResponse<T>> {
  return request<T>({
    url,
    method: "POST",
    data,
    ...config
  });
}

/**
 * 封装PUT请求
 */
export function put<T = any>(
  url: string,
  data?: any,
  config?: Omit<RequestConfig, "url" | "method" | "data">
): Promise<ApiResponse<T>> {
  return request<T>({
    url,
    method: "PUT",
    data,
    ...config
  });
}

/**
 * 封装DELETE请求
 */
export function del<T = any>(
  url: string,
  data?: any,
  config?: Omit<RequestConfig, "url" | "method" | "data">
): Promise<ApiResponse<T>> {
  return request<T>({
    url,
    method: "DELETE",
    data,
    ...config
  });
}

export default {
  request,
  get,
  post,
  put,
  del,
  getToken
};
