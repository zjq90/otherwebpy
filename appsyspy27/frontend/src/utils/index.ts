/**
 * 工具函数模块
 * 包含通用的工具函数
 */

/**
 * 格式化日期
 * @param date 日期对象或时间戳
 * @param format 格式化模板，默认 'YYYY-MM-DD HH:mm:ss'
 */
export function formatDate(
  date: Date | string | number,
  format: string = "YYYY-MM-DD HH:mm:ss"
): string {
  let d: Date;
  
  if (typeof date === "string") {
    // 处理ISO字符串
    d = new Date(date.replace(/-/g, "/"));
  } else if (typeof date === "number") {
    d = new Date(date);
  } else {
    d = date;
  }

  const year = d.getFullYear();
  const month = d.getMonth() + 1;
  const day = d.getDate();
  const hour = d.getHours();
  const minute = d.getMinutes();
  const second = d.getSeconds();

  return format
    .replace("YYYY", String(year))
    .replace("MM", String(month).padStart(2, "0"))
    .replace("DD", String(day).padStart(2, "0"))
    .replace("HH", String(hour).padStart(2, "0"))
    .replace("mm", String(minute).padStart(2, "0"))
    .replace("ss", String(second).padStart(2, "0"));
}

/**
 * 格式化相对时间
 * @param date 日期
 */
export function formatRelativeTime(date: Date | string | number): string {
  const d = typeof date === "string" || typeof date === "number" 
    ? new Date(date) 
    : date;
  
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (seconds < 60) {
    return "刚刚";
  } else if (minutes < 60) {
    return `${minutes}分钟前`;
  } else if (hours < 24) {
    return `${hours}小时前`;
  } else if (days < 7) {
    return `${days}天前`;
  } else {
    return formatDate(d, "MM-DD");
  }
}

/**
 * 脱敏手机号
 * @param phone 手机号
 */
export function maskPhone(phone: string): string {
  if (!phone || phone.length < 11) {
    return phone || "";
  }
  return phone.slice(0, 3) + "****" + phone.slice(-4);
}

/**
 * 格式化金额
 * @param amount 金额
 * @param decimals 小数位数，默认2位
 */
export function formatAmount(amount: number | string, decimals: number = 2): string {
  const num = typeof amount === "string" ? parseFloat(amount) : amount;
  return num.toFixed(decimals);
}

/**
 * 格式化时长（分钟转小时分钟）
 * @param minutes 分钟数
 */
export function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${minutes}分钟`;
  }
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (mins === 0) {
    return `${hours}小时`;
  }
  return `${hours}小时${mins}分钟`;
}

/**
 * 防抖函数
 * @param fn 函数
 * @param delay 延迟时间（ms）
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout> | null = null;
  
  return (...args: Parameters<T>) => {
    if (timer) {
      clearTimeout(timer);
    }
    timer = setTimeout(() => {
      fn(...args);
    }, delay);
  };
}

/**
 * 节流函数
 * @param fn 函数
 * @param delay 间隔时间（ms）
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let lastTime = 0;
  
  return (...args: Parameters<T>) => {
    const now = Date.now();
    if (now - lastTime >= delay) {
      fn(...args);
      lastTime = now;
    }
  };
}

/**
 * 显示成功提示
 * @param title 提示内容
 */
export function showSuccess(title: string): void {
  uni.showToast({
    title,
    icon: "success",
    duration: 2000
  });
}

/**
 * 显示错误提示
 * @param title 提示内容
 */
export function showError(title: string): void {
  uni.showToast({
    title,
    icon: "none",
    duration: 2000
  });
}

/**
 * 显示加载提示
 * @param title 提示内容
 */
export function showLoading(title: string = "加载中..."): void {
  uni.showLoading({
    title,
    mask: true
  });
}

/**
 * 隐藏加载提示
 */
export function hideLoading(): void {
  uni.hideLoading();
}

/**
 * 确认对话框
 * @param title 标题
 * @param content 内容
 */
export function showConfirm(title: string, content: string): Promise<boolean> {
  return new Promise((resolve) => {
    uni.showModal({
      title,
      content,
      success: (res) => {
        resolve(res.confirm);
      },
      fail: () => {
        resolve(false);
      }
    });
  });
}

export default {
  formatDate,
  formatRelativeTime,
  maskPhone,
  formatAmount,
  formatDuration,
  debounce,
  throttle,
  showSuccess,
  showError,
  showLoading,
  hideLoading,
  showConfirm
};
