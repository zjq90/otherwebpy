<template>
  <div class="levels-page">
    <div class="page-container">
      <div class="page-header">
        <span class="page-title">等级与权益</span>
      </div>

      <el-alert
        title="会员等级说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        <template #default>
          <p>会员等级根据消费金额自动升级，不同等级享有不同的权益：</p>
          <ul>
            <li>• 铜卡会员：消费0元起，无特殊折扣</li>
            <li>• 银卡会员：累计消费5000元，享受9折优惠</li>
            <li>• 金卡会员：累计消费20000元，享受8折优惠</li>
          </ul>
        </template>
      </el-alert>

      <!-- 等级卡片展示 -->
      <el-row :gutter="24">
        <el-col :span="8">
          <el-card class="level-card bronze-card">
            <template #header>
              <div class="level-header">
                <el-icon :size="40"><Medal /></el-icon>
                <span class="level-name">铜卡会员</span>
              </div>
            </template>
            <div class="level-content">
              <div class="level-amount">
                <span class="label">升级门槛</span>
                <span class="value">¥0</span>
              </div>
              <el-divider />
              <div class="level-benefits">
                <h4>权益列表</h4>
                <ul>
                  <li><el-icon><Check /></el-icon> 基础健身服务</li>
                  <li><el-icon><Check /></el-icon> 会员系统使用</li>
                  <li><el-icon><Check /></el-icon> 体测数据记录</li>
                  <li class="disabled"><el-icon><Close /></el-icon> 课程折扣</li>
                  <li class="disabled"><el-icon><Close /></el-icon> 免费体测</li>
                  <li class="disabled"><el-icon><Close /></el-icon> 优先预约</li>
                </ul>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="level-card silver-card">
            <template #header>
              <div class="level-header">
                <el-icon :size="40"><Medal /></el-icon>
                <span class="level-name">银卡会员</span>
                <el-tag type="success" effect="dark">推荐</el-tag>
              </div>
            </template>
            <div class="level-content">
              <div class="level-amount">
                <span class="label">升级门槛</span>
                <span class="value">¥5,000</span>
              </div>
              <el-divider />
              <div class="level-benefits">
                <h4>权益列表</h4>
                <ul>
                  <li><el-icon><Check /></el-icon> 基础健身服务</li>
                  <li><el-icon><Check /></el-icon> 会员系统使用</li>
                  <li><el-icon><Check /></el-icon> 体测数据记录</li>
                  <li><el-icon><Check /></el-icon> 课程9折优惠</li>
                  <li><el-icon><Check /></el-icon> 每月1次免费体测</li>
                  <li class="disabled"><el-icon><Close /></el-icon> 优先预约</li>
                </ul>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="level-card gold-card">
            <template #header>
              <div class="level-header">
                <el-icon :size="40"><Medal /></el-icon>
                <span class="level-name">金卡会员</span>
                <el-tag type="warning" effect="dark">尊享</el-tag>
              </div>
            </template>
            <div class="level-content">
              <div class="level-amount">
                <span class="label">升级门槛</span>
                <span class="value">¥20,000</span>
              </div>
              <el-divider />
              <div class="level-benefits">
                <h4>权益列表</h4>
                <ul>
                  <li><el-icon><Check /></el-icon> 基础健身服务</li>
                  <li><el-icon><Check /></el-icon> 会员系统使用</li>
                  <li><el-icon><Check /></el-icon> 体测数据记录</li>
                  <li><el-icon><Check /></el-icon> 课程8折优惠</li>
                  <li><el-icon><Check /></el-icon> 每月2次免费体测</li>
                  <li><el-icon><Check /></el-icon> 优先预约课程</li>
                </ul>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 等级规则说明 -->
      <el-card style="margin-top: 20px;">
        <template #header>
          <span>升级规则详情</span>
        </template>
        
        <el-descriptions :column="3" border>
          <el-descriptions-item label="铜卡会员">
            <p>• 入会即成为铜卡会员</p>
            <p>• 无消费门槛要求</p>
            <p>• 享受基础会员服务</p>
          </el-descriptions-item>
          <el-descriptions-item label="银卡会员">
            <p>• 累计消费满5000元自动升级</p>
            <p>• 消费享受9折优惠</p>
            <p>• 每月1次免费体测</p>
          </el-descriptions-item>
          <el-descriptions-item label="金卡会员">
            <p>• 累计消费满20000元自动升级</p>
            <p>• 消费享受8折优惠</p>
            <p>• 每月2次免费体测 + 优先预约</p>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 升级进度示例 -->
      <el-card style="margin-top: 20px;">
        <template #header>
          <span>升级进度示例</span>
        </template>
        
        <div class="upgrade-progress">
          <div class="progress-item">
            <div class="progress-header">
              <span class="member-name">张三</span>
              <span class="current-level">
                <el-tag class="level-tag bronze">铜卡</el-tag>
              </span>
            </div>
            <div class="progress-info">
              <span>当前消费: ¥3,500</span>
              <span>距银卡还需: ¥1,500</span>
            </div>
            <el-progress :percentage="70" :color="#cd7f32" />
          </div>

          <el-divider />

          <div class="progress-item">
            <div class="progress-header">
              <span class="member-name">李四</span>
              <span class="current-level">
                <el-tag class="level-tag silver">银卡</el-tag>
              </span>
            </div>
            <div class="progress-info">
              <span>当前消费: ¥12,000</span>
              <span>距金卡还需: ¥8,000</span>
            </div>
            <el-progress :percentage="60" :color="#c0c0c0" />
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { Medal, Check, Close } from '@element-plus/icons-vue'
</script>

<style lang="scss" scoped>
.levels-page {
  .level-card {
    transition: transform 0.3s, box-shadow 0.3s;
    border-top: 4px solid;

    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
    }

    .level-header {
      display: flex;
      align-items: center;
      gap: 12px;

      .level-name {
        font-size: 18px;
        font-weight: bold;
      }
    }

    .level-content {
      .level-amount {
        text-align: center;

        .label {
          display: block;
          font-size: 14px;
          color: #909399;
        }

        .value {
          display: block;
          font-size: 28px;
          font-weight: bold;
          margin-top: 8px;
        }
      }

      .level-benefits {
        h4 {
          font-size: 14px;
          color: #606266;
          margin-bottom: 12px;
        }

        ul {
          list-style: none;
          padding: 0;
          margin: 0;

          li {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 0;
            color: #606266;

            &.disabled {
              color: #c0c4cc;
            }
          }
        }
      }
    }

    &.bronze-card {
      border-top-color: #cd7f32;

      .level-header {
        color: #cd7f32;
      }

      .level-amount .value {
        color: #cd7f32;
      }
    }

    &.silver-card {
      border-top-color: #c0c0c0;

      .level-header {
        color: #606266;
      }

      .level-amount .value {
        color: #606266;
      }
    }

    &.gold-card {
      border-top-color: #ffd700;

      .level-header {
        color: #e6a23c;
      }

      .level-amount .value {
        color: #e6a23c;
      }
    }
  }

  .upgrade-progress {
    .progress-item {
      .progress-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;

        .member-name {
          font-size: 16px;
          font-weight: 600;
        }
      }

      .progress-info {
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
        color: #909399;
        font-size: 14px;
      }
    }
  }
}
</style>
