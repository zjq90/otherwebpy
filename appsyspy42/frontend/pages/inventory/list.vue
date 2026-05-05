<template>
    <view class="page-container">
        <view class="search-section">
            <view class="search-input">
                <text class="uni-icon uni-icon-search"></text>
                <input 
                    type="text" 
                    placeholder="搜索原材料名称" 
                    v-model="searchKeyword"
                    placeholder-class="placeholder"
                    @confirm="handleSearch"
                />
            </view>
        </view>
        
        <view class="filter-section">
            <scroll-view scroll-x class="filter-scroll">
                <view class="filter-list">
                    <view 
                        class="filter-item" 
                        :class="{ active: currentType === '' }"
                        @click="filterByType('')"
                    >
                        全部
                    </view>
                    <view 
                        class="filter-item" 
                        :class="{ active: currentType === '水泥' }"
                        @click="filterByType('水泥')"
                    >
                        水泥
                    </view>
                    <view 
                        class="filter-item" 
                        :class="{ active: currentType === '砂石' }"
                        @click="filterByType('砂石')"
                    >
                        砂石
                    </view>
                    <view 
                        class="filter-item" 
                        :class="{ active: currentType === '粉煤灰' }"
                        @click="filterByType('粉煤灰')"
                    >
                        粉煤灰
                    </view>
                    <view 
                        class="filter-item" 
                        :class="{ active: currentType === '外加剂' }"
                        @click="filterByType('外加剂')"
                    >
                        外加剂
                    </view>
                </view>
            </scroll-view>
        </view>
        
        <view class="inventory-list" v-if="inventoryList.length > 0">
            <view 
                class="inventory-item" 
                v-for="item in inventoryList" 
                :key="item.id"
                @click="goToDetail(item.id)"
            >
                <view class="item-header">
                    <view class="item-name">
                        <text class="name">{{ item.material_name }}</text>
                        <view class="type-tag" :class="getTypeClass(item.material_type)">
                            {{ item.material_type }}
                        </view>
                    </view>
                    <view class="item-status" v-if="item.is_low_stock === 1">
                        <text class="status-text">低库存</text>
                    </view>
                </view>
                
                <view class="item-content">
                    <view class="info-row">
                        <text class="info-label">料仓</text>
                        <text class="info-value">{{ item.warehouse_name }}</text>
                    </view>
                    <view class="info-row">
                        <text class="info-label">规格</text>
                        <text class="info-value">{{ item.specification || '-' }}</text>
                    </view>
                </view>
                
                <view class="item-quantity">
                    <view class="quantity-info">
                        <text class="quantity-label">当前库存</text>
                        <text class="quantity-value" :class="{ danger: item.is_low_stock === 1 }">
                            {{ item.quantity }} {{ item.unit }}
                        </text>
                    </view>
                    <view class="threshold-info">
                        <text class="threshold-label">安全阈值</text>
                        <text class="threshold-value">{{ item.safety_threshold }} {{ item.unit }}</text>
                    </view>
                </view>
                
                <view class="progress-section" v-if="item.expiry_date">
                    <view class="progress-info">
                        <text class="progress-label">保质期</text>
                        <text class="progress-value">{{ formatDate(item.expiry_date) }}</text>
                    </view>
                </view>
            </view>
        </view>
        
        <view class="empty-state" v-else-if="!loading">
            <text class="empty-text">暂无库存数据</text>
        </view>
        
        <view class="loading-state" v-if="loading">
            <text>加载中...</text>
        </view>
        
        <view class="load-more" v-if="!loading && hasMore" @click="loadMore">
            <text>加载更多</text>
        </view>
    </view>
</template>

<script>
export default {
    data() {
        return {
            searchKeyword: '',
            currentType: '',
            inventoryList: [],
            page: 1,
            pageSize: 20,
            loading: false,
            hasMore: true
        }
    },
    
    onShow() {
        this.page = 1
        this.inventoryList = []
        this.loadData()
    },
    
    methods: {
        async loadData() {
            if (this.loading) return
            
            this.loading = true
            
            try {
                const params = {
                    page: this.page,
                    page_size: this.pageSize
                }
                
                if (this.currentType) {
                    params.material_type = this.currentType
                }
                
                if (this.searchKeyword) {
                    params.material_name = this.searchKeyword
                }
                
                const res = await this.$api.getInventoryList(params)
                
                if (res.list && res.list.length > 0) {
                    if (this.page === 1) {
                        this.inventoryList = res.list
                    } else {
                        this.inventoryList = [...this.inventoryList, ...res.list]
                    }
                    this.hasMore = this.page < res.total_pages
                } else {
                    this.hasMore = false
                }
                
            } catch (err) {
                console.error('加载库存列表失败:', err)
            } finally {
                this.loading = false
            }
        },
        
        filterByType(type) {
            this.currentType = type
            this.page = 1
            this.inventoryList = []
            this.loadData()
        },
        
        handleSearch() {
            this.page = 1
            this.inventoryList = []
            this.loadData()
        },
        
        loadMore() {
            if (!this.hasMore) return
            this.page++
            this.loadData()
        },
        
        getTypeClass(type) {
            const classMap = {
                '水泥': 'cement',
                '砂石': 'sand',
                '粉煤灰': 'flyash',
                '外加剂': 'additive'
            }
            return classMap[type] || ''
        },
        
        formatDate(dateStr) {
            if (!dateStr) return '-'
            const date = new Date(dateStr)
            return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
        },
        
        goToDetail(id) {
            uni.navigateTo({
                url: `/pages/inventory/detail?id=${id}`
            })
        }
    }
}
</script>

<style scoped>
.page-container {
    min-height: 100vh;
    background-color: #f5f5f5;
}

.search-section {
    padding: 20rpx;
    background: #fff;
}

.search-input {
    display: flex;
    align-items: center;
    background: #f5f5f5;
    border-radius: 40rpx;
    padding: 0 24rpx;
    height: 72rpx;
}

.search-input text {
    font-size: 32rpx;
    color: #999;
    margin-right: 16rpx;
}

.search-input input {
    flex: 1;
    font-size: 28rpx;
}

.placeholder {
    color: #999;
}

.filter-section {
    background: #fff;
    padding: 0 20rpx 20rpx;
}

.filter-scroll {
    white-space: nowrap;
}

.filter-list {
    display: flex;
    gap: 16rpx;
}

.filter-item {
    display: inline-block;
    padding: 12rpx 28rpx;
    background: #f5f5f5;
    border-radius: 32rpx;
    font-size: 26rpx;
    color: #666;
}

.filter-item.active {
    background: #e6f4ff;
    color: #1677ff;
}

.inventory-list {
    padding: 20rpx;
}

.inventory-item {
    background: #fff;
    border-radius: 16rpx;
    padding: 24rpx;
    margin-bottom: 20rpx;
    box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20rpx;
}

.item-name {
    display: flex;
    align-items: center;
}

.name {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    margin-right: 16rpx;
}

.type-tag {
    font-size: 22rpx;
    padding: 4rpx 12rpx;
    border-radius: 8rpx;
}

.type-tag.cement {
    background: #e6f4ff;
    color: #1677ff;
}

.type-tag.sand {
    background: #f6ffed;
    color: #52c41a;
}

.type-tag.flyash {
    background: #fff7e6;
    color: #fa8c16;
}

.type-tag.additive {
    background: #f9f0ff;
    color: #722ed1;
}

.item-status {
    background: #fff2f0;
    padding: 4rpx 16rpx;
    border-radius: 8rpx;
}

.status-text {
    font-size: 22rpx;
    color: #ff4d4f;
}

.item-content {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20rpx;
}

.info-row {
    display: flex;
    flex-direction: column;
}

.info-label {
    font-size: 24rpx;
    color: #999;
    margin-bottom: 8rpx;
}

.info-value {
    font-size: 28rpx;
    color: #333;
}

.item-quantity {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20rpx;
    background: #fafafa;
    border-radius: 12rpx;
    margin-bottom: 16rpx;
}

.quantity-info, .threshold-info {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.quantity-label, .threshold-label {
    font-size: 24rpx;
    color: #999;
    margin-bottom: 8rpx;
}

.quantity-value {
    font-size: 36rpx;
    font-weight: 600;
    color: #333;
}

.quantity-value.danger {
    color: #ff4d4f;
}

.threshold-value {
    font-size: 28rpx;
    color: #666;
}

.progress-section {
    padding-top: 16rpx;
    border-top: 1rpx solid #f0f0f0;
}

.progress-info {
    display: flex;
    justify-content: space-between;
}

.progress-label {
    font-size: 24rpx;
    color: #999;
}

.progress-value {
    font-size: 24rpx;
    color: #666;
}

.empty-state {
    padding: 100rpx 0;
    text-align: center;
}

.empty-text {
    font-size: 28rpx;
    color: #999;
}

.loading-state {
    padding: 60rpx 0;
    text-align: center;
    color: #999;
}

.load-more {
    padding: 30rpx;
    text-align: center;
    color: #1677ff;
    font-size: 28rpx;
}
</style>
