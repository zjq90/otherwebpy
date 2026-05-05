import Vue from 'vue'
import App from './App'

/**
 * 主入口文件
 * 初始化Vue应用和全局配置
 */

// 全局配置
Vue.config.productionTip = false

// 全局混入
Vue.mixin({
	methods: {
		/**
		 * 页面跳转
		 * @param {String} url - 跳转路径
		 */
		navigateTo(url) {
			uni.navigateTo({ url })
		},
		
		/**
		 * 关闭当前页跳转
		 * @param {String} url - 跳转路径
		 */
		redirectTo(url) {
			uni.redirectTo({ url })
		},
		
		/**
		 * 返回上一页
		 * @param {Number} delta - 返回层数
		 */
		navigateBack(delta = 1) {
			uni.navigateBack({ delta })
		},
		
		/**
		 * 切换TabBar
		 * @param {String} url - 跳转路径
		 */
		switchTab(url) {
			uni.switchTab({ url })
		},
		
		/**
		 * 显示加载提示
		 * @param {String} title - 提示文字
		 */
		showLoading(title = '加载中...') {
			uni.showLoading({
				title,
				mask: true
			})
		},
		
		/**
		 * 隐藏加载提示
		 */
		hideLoading() {
			uni.hideLoading()
		},
		
		/**
		 * 显示Toast提示
		 * @param {String} title - 提示文字
		 * @param {String} icon - 图标类型
		 * @param {Number} duration - 显示时间
		 */
		showToast(title, icon = 'none', duration = 2000) {
			uni.showToast({
				title,
				icon,
				duration
			})
		},
		
		/**
		 * 显示确认对话框
		 * @param {String} title - 标题
		 * @param {String} content - 内容
		 * @returns {Promise}
		 */
		showModal(title, content) {
			return new Promise((resolve, reject) => {
				uni.showModal({
					title,
					content,
					success: (res) => {
						if (res.confirm) {
							resolve(true)
						} else {
							resolve(false)
						}
					},
					fail: (err) => {
						reject(err)
					}
				})
			})
		}
	}
})

App.mpType = 'app'

const app = new Vue({
	...App
})

app.$mount()
