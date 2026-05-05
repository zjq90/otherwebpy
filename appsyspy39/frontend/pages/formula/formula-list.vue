<template>
	<view class="formula-list-container">
		<!-- 搜索框 -->
		<view class="search-section">
			<view class="search-box">
				<text class="iconfont icon-search"></text>
				<input 
					class="search-input" 
					type="text" 
					v-model="searchKeyword" 
					placeholder="搜索配方名称、编号、混凝土标号"
					placeholder-class="input-placeholder"
					@confirm="handleSearch"
				/>
			</view>
		</view>
		
		<!-- 筛选标签 -->
		<view class="filter-tabs">
			<view 
				class="tab-item" 
				:class="{ active: currentGrade === '' }"
				@click="handleGradeFilter('')"
			>
				全部
			</view>
			<view 
				class="tab-item" 
				v-for="grade in gradeList" 
				:key="grade"
				:class="{ active: currentGrade === grade }"
				@click="handleGradeFilter(grade)"
			>
				{{ grade }}
			</view>
		</view>
		
		<!-- 配方列表 -->
		<scroll-view 
			class="formula-scroll" 
			scroll-y
			@scrolltolower="loadMore"
			refresher-enabled
			:refresher-triggered="refreshing"
			@refresherrefresh="onRefresh"
		>
			<view class="formula-list" v-if="formulaList.length > 0">
				<view 
					class="formula-card" 
					v-for="(formula, index) in formulaList" 
					:key="formula.id"
					@click="goToDetail(formula.id)"
				>
					<!-- 头部 -->
					<view class="card-header">
						<view class="grade-tag">
							<text class="grade-text">{{ formula.concrete_grade }}</text>
						</view>
						<view class="formula-name">
							<text class="name-text line-1">{{ formula.formula_name }}</text>
							<text class="code-text">{{ formula.formula_code }}</text>
						</view>
						<view class="status-badge" :class="{ active: formula.is_active }">
							{{ formula.is_active ? '启用' : '禁用' }}
						</view>
					</view>
					
					<!-- 主要参数 -->
					<view class="card-body">
						<view class="param-grid">
							<view class="param-item">
								<text class="param-label">水灰比</text>
								<text class="param-value">{{ formula.water_cement_ratio }}</text>
							</view>
							<view class="param-item">
								<text class="param-label">坍落度</text>
								<text class="param-value">{{ formula.slump || '-' }} mm</text>
							</view>
							<view class="param-item">
								<text class="param-label">类型</text>
								<text class="param-value">{{ formula.is_standard ? '标准' : '自定义' }}</text>
							</view>
						</view>
					</view>
					
					<!-- 材料用量预览 -->
					<view class="card-footer">
						<view class="material-preview">
							<view class="material-item" v-for="(m in getMaterialPreview(formula)" :key="m.name">
								<text class="material-name">{{ m.name }}</text>
								<text class="material-qty">{{ m.value }}kg</text>
							</view>
						</view>
					</view>
				</view>
			</view>
			
			<!-- 空状态 -->
			<view class="empty-state" v-else-if="!loading && formulaList.length === 0">
				<text class="empty-icon">📋</text>
				<text class="empty-text">暂无配方数据</text>
			</view>
			
			<!-- 加载更多 -->
			<view class="load-more" v-if="loading && page > 1">
				<text>加载中...</text>
			</view>
			
			<!-- 没有更多 -->
			<view class="no-more" v-if="!hasMore && formulaList.length > 0">
				<text>没有更多了</text>
			</view>
		</scroll-view>
	</view>
</template>

<script>
/**
 * 配方列表页面
 * 功能：
 * - 配方搜索
 * - 标号筛选
 * - 配方列表展示
 * - 快速调用配方
 */
import api from '@/utils/api.js'

export default {
	data() {
		return {
			// 搜索关键词
			searchKeyword: '',
			// 当前筛选的标号
			currentGrade: '',
			// 标号列表
			gradeList: ['C15', 'C20', 'C25', 'C30', 'C35', 'C40'],
			// 配方列表
			formulaList: [],
			// 分页
			page: 1,
			pageSize: 10,
			hasMore: true,
			// 加载状态
			loading: false,
			refreshing: false
		}
	},
	
	onLoad() {
		this.loadData()
	},
	
	onShow() {
		if (!this.loading) {
			this.onRefresh()
		}
	},
	
	methods: {
		/**
		 * 加载数据
		 */
		async loadData(isRefresh = false) {
			if (this.loading) return
			
			this.loading = true
			
			try {
				const params = {
					page: this.page,
					page_size: this.pageSize,
					is_active: true
				}
				
				// 标号筛选
				if (this.currentGrade) {
					params.concrete_grade = this.currentGrade
				}
				
				// 搜索关键词
				if (this.searchKeyword.trim()) {
					params.keyword = this.searchKeyword.trim()
				}
				
				const res = await api.formulas.getList(params)
				
				if (res && res.formulas) {
					const newFormulas = res.formulas
					
					if (isRefresh) {
						this.formulaList = newFormulas
					} else {
						this.formulaList = [...this.formulaList, ...newFormulas]
					}
					
					this.hasMore = newFormulas.length >= this.pageSize
				}
			} catch (error) {
				console.log('加载配方列表失败:', error)
			} finally {
				this.loading = false
				this.refreshing = false
			}
		},
		
		/**
		 * 下拉刷新
		 */
		async onRefresh() {
			this.refreshing = true
			this.page = 1
			this.hasMore = true
			await this.loadData(true)
		},
		
		/**
		 * 上拉加载更多
		 */
		loadMore() {
			if (this.hasMore && !this.loading) {
				this.page++
				this.loadData()
			}
		},
		
		/**
		 * 搜索
		 */
		handleSearch() {
			this.onRefresh()
		},
		
		/**
		 * 标号筛选
		 */
		handleGradeFilter(grade) {
			if (this.currentGrade === grade) return
			this.currentGrade = grade
			this.onRefresh()
		},
		
		/**
		 * 获取材料预览
		 */
		getMaterialPreview(formula) {
			const materials = [
				{ name: '水泥', value: formula.cement },
				{ name: '水', value: formula.water },
				{ name: '砂', value: formula.sand },
				{ name: '石', value: formula.stone }
			]
			
			if (formula.admixture) {
				materials.push({ name: '外加剂', value: formula.admixture })
			}
			
			return materials
		},
		
		// ========== 页面跳转 ==========
		
		goToDetail(formulaId) {
			uni.navigateTo({
				url: `/pages/formula/formula-detail?id=${formulaId}`
			})
		}
	}
}
</script>

<style scoped>
/* 配方列表页面样式 */
.formula-list-container {
	height: 100vh;
	display: flex;
	flex-direction: column;
	background: #F5F7FA;
}

/* 搜索区域 */
.search-section {
	background: #FFFFFF;
	padding: 20rpx 30rpx;
	border-bottom: 2rpx solid #F0F0F0;
}

.search-box {
	display: flex;
	align-items: center;
	background: #F5F7FA;
	border-radius: 40rpx;
	padding: 16rpx 30rpx;
}

.icon-search {
	font-size: 32rpx;
	color: #999999;
	margin-right: 16rpx;
}

.search-input {
	flex: 1;
	font-size: 28rpx;
	color: #333333;
}

.input-placeholder {
	color: #CCCCCC;
}

/* 筛选标签 */
.filter-tabs {
	display: flex;
	background: #FFFFFF;
	padding: 20rpx 30rpx;
	gap: 20rpx;
	overflow-x: auto;
	border-bottom: 2rpx solid #F0F0F0;
	white-space: nowrap;
}

.tab-item {
	flex-shrink: 0;
	font-size: 26rpx;
	color: #666666;
	padding: 10rpx 24rpx;
	border-radius: 30rpx;
	background: #F5F7FA;
}

.tab-item.active {
	background: #E6F7FF;
	color: #1890FF;
	font-weight: 500;
}

/* 滚动区域 */
.formula-scroll {
	flex: 1;
}

.formula-list {
	padding: 20rpx 30rpx;
	display: flex;
	flex-direction: column;
	gap: 24rpx;
}

/* 配方卡片 */
.formula-card {
	background: #FFFFFF;
	border-radius: 20rpx;
	overflow: hidden;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.03);
}

.card-header {
	display: flex;
	align-items: center;
	padding: 24rpx 30rpx;
	background: linear-gradient(90deg, #FAFAFA 0%, #FFFFFF 100%);
	border-bottom: 2rpx solid #F5F5F5;
}

.grade-tag {
	background: linear-gradient(135deg, #1890FF 0%, #40A9FF 100%);
	padding: 12rpx 20rpx;
	border-radius: 12rpx;
	margin-right: 20rpx;
	flex-shrink: 0;
}

.grade-text {
	font-size: 28rpx;
	color: #FFFFFF;
	font-weight: bold;
}

.formula-name {
	flex: 1;
	min-width: 0;
	display: flex;
	flex-direction: column;
}

.name-text {
	font-size: 28rpx;
	color: #333333;
	font-weight: 500;
	margin-bottom: 6rpx;
}

.code-text {
	font-size: 22rpx;
	color: #999999;
}

.status-badge {
	font-size: 22rpx;
	padding: 6rpx 16rpx;
	border-radius: 8rpx;
	background: #F0F0F0;
	color: #999999;
	margin-left: 16rpx;
	flex-shrink: 0;
}

.status-badge.active {
	background: #F6FFED;
	color: #52C41A;
}

/* 卡片主体 */
.card-body {
	padding: 24rpx 30rpx;
	border-bottom: 2rpx dashed #F0F0F0;
}

.param-grid {
	display: flex;
	gap: 40rpx;
}

.param-item {
	flex: 1;
	display: flex;
	flex-direction: column;
}

.param-label {
	font-size: 22rpx;
	color: #999999;
	margin-bottom: 8rpx;
}

.param-value {
	font-size: 28rpx;
	color: #333333;
	font-weight: 500;
}

/* 卡片底部 */
.card-footer {
	padding: 20rpx 30rpx;
	background: #FAFAFA;
}

.material-preview {
	display: flex;
	flex-wrap: wrap;
	gap: 20rpx;
}

.material-item {
	display: flex;
	flex-direction: column;
	align-items: center;
	min-width: 100rpx;
	background: #FFFFFF;
	padding: 12rpx 16rpx;
	border-radius: 12rpx;
}

.material-name {
	font-size: 20rpx;
	color: #999999;
	margin-bottom: 4rpx;
}

.material-qty {
	font-size: 24rpx;
	color: #333333;
	font-weight: 500;
}

/* 空状态 */
.empty-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 120rpx 0;
}

.empty-icon {
	font-size: 100rpx;
	margin-bottom: 30rpx;
}

.empty-text {
	font-size: 30rpx;
	color: #666666;
}

/* 加载状态 */
.load-more,
.no-more {
	text-align: center;
	padding: 40rpx;
	font-size: 26rpx;
	color: #999999;
}
</style>
