<template>
  <div class="coupons-page">
    <div class="page-header">
      <h1>领券中心</h1>
      <p class="subtitle">精选优惠券，先到先得</p>
    </div>

    <el-tabs v-model="activeTab" class="coupons-tabs">
      <el-tab-pane label="可领取" name="available">
        <div class="coupon-grid" v-loading="availableLoading">
          <div
            v-for="coupon in availableCoupons"
            :key="coupon.id"
            class="coupon-card available"
          >
            <div class="coupon-left">
              <div class="coupon-amount">
                <span class="currency">¥</span>
                <span class="amount">{{ coupon.discount_amount }}</span>
              </div>
              <div class="coupon-threshold">
                满{{ coupon.threshold_amount }}可用
              </div>
            </div>
            <div class="coupon-right">
              <div class="coupon-name">{{ coupon.name }}</div>
              <div class="coupon-desc" v-if="coupon.description">
                {{ coupon.description }}
              </div>
              <div class="coupon-valid">
                有效期：{{ formatDate(coupon.valid_from) }} - {{ formatDate(coupon.valid_to) }}
              </div>
              <div class="coupon-stock">
                已领 {{ coupon.claimed_quantity }}/{{ coupon.total_quantity }} 张
              </div>
              <el-button
                type="primary"
                class="claim-btn"
                :loading="claimingId === coupon.id"
                :disabled="coupon.user_claimed_count >= coupon.limit_per_user"
                @click="handleClaim(coupon.id)"
              >
                {{ coupon.user_claimed_count >= coupon.limit_per_user ? '已领取' : '立即领取' }}
              </el-button>
            </div>
          </div>

          <el-empty
            v-if="availableCoupons.length === 0 && !availableLoading"
            description="暂无可用优惠券"
          />
        </div>

        <div class="pagination" v-if="availableTotal > 0">
          <el-pagination
            v-model:current-page="availablePage"
            v-model:page-size="availablePageSize"
            :total="availableTotal"
            layout="total, prev, pager, next"
            @current-change="fetchAvailableCoupons"
          />
        </div>
      </el-tab-pane>

      <el-tab-pane label="已领取" name="my">
        <div class="filter-bar">
          <el-radio-group v-model="myCouponStatus" @change="fetchMyCoupons">
            <el-radio-button value="">全部</el-radio-button>
            <el-radio-button value="unused">未使用</el-radio-button>
            <el-radio-button value="used">已使用</el-radio-button>
            <el-radio-button value="expired">已过期</el-radio-button>
          </el-radio-group>
        </div>

        <div class="coupon-grid" v-loading="myLoading">
          <div
            v-for="userCoupon in myCoupons"
            :key="userCoupon.id"
            :class="['coupon-card', 'my-coupon', userCoupon.status]"
          >
            <div class="coupon-left">
              <div class="coupon-amount">
                <span class="currency">¥</span>
                <span class="amount">{{ userCoupon.coupon.discount_amount }}</span>
              </div>
              <div class="coupon-threshold">
                满{{ userCoupon.coupon.threshold_amount }}可用
              </div>
            </div>
            <div class="coupon-right">
              <div class="coupon-name">{{ userCoupon.coupon.name }}</div>
              <div class="coupon-desc" v-if="userCoupon.coupon.description">
                {{ userCoupon.coupon.description }}
              </div>
              <div class="coupon-valid">
                有效期：{{ formatDate(userCoupon.coupon.valid_from) }} - {{ formatDate(userCoupon.coupon.valid_to) }}
              </div>
              <div class="coupon-categories" v-if="userCoupon.coupon.applicable_categories">
                适用分类：{{ userCoupon.coupon.applicable_categories }}
              </div>
              <div class="coupon-status">
                <el-tag :type="getUserCouponStatusType(userCoupon.status)" size="small">
                  {{ getUserCouponStatusText(userCoupon.status) }}
                </el-tag>
                <span class="claim-time">
                  领取时间：{{ formatDate(userCoupon.claimed_at) }}
                </span>
              </div>
              <div v-if="userCoupon.status === 'used'" class="used-info">
                使用时间：{{ formatDate(userCoupon.used_at!) }}
              </div>
            </div>
            <div v-if="userCoupon.status !== 'unused'" class="coupon-mask">
              <span v-if="userCoupon.status === 'used'">已使用</span>
              <span v-else-if="userCoupon.status === 'expired'">已过期</span>
            </div>
          </div>

          <el-empty
            v-if="myCoupons.length === 0 && !myLoading"
            description="暂无已领取的优惠券"
          />
        </div>

        <div class="pagination" v-if="myTotal > 0">
          <el-pagination
            v-model:current-page="myPage"
            v-model:page-size="myPageSize"
            :total="myTotal"
            layout="total, prev, pager, next"
            @current-change="fetchMyCoupons"
          />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'
import type { Coupon, UserCoupon, UserCouponStatus as UserCouponStatusType } from '@/types'
import { ElMessage } from 'element-plus'

const router = useRouter()

const activeTab = ref('available')
const claimingId = ref<number | null>(null)

const availableLoading = ref(false)
const availableCoupons = ref<Coupon[]>([])
const availableTotal = ref(0)
const availablePage = ref(1)
const availablePageSize = ref(10)

const myLoading = ref(false)
const myCoupons = ref<UserCoupon[]>([])
const myTotal = ref(0)
const myPage = ref(1)
const myPageSize = ref(10)
const myCouponStatus = ref('')

onMounted(() => {
  fetchAvailableCoupons()
  fetchMyCoupons()
})

async function fetchAvailableCoupons() {
  availableLoading.value = true
  try {
    const response = await api.getAvailableCoupons({
      page: availablePage.value,
      page_size: availablePageSize.value
    })
    availableCoupons.value = response.items
    availableTotal.value = response.total
  } catch (error) {
    console.error('获取可领取优惠券失败:', error)
  } finally {
    availableLoading.value = false
  }
}

async function fetchMyCoupons() {
  myLoading.value = true
  try {
    const response = await api.getMyCoupons({
      status: myCouponStatus.value || undefined,
      page: myPage.value,
      page_size: myPageSize.value
    })
    myCoupons.value = response.items
    myTotal.value = response.total
  } catch (error) {
    console.error('获取我的优惠券失败:', error)
  } finally {
    myLoading.value = false
  }
}

async function handleClaim(couponId: number) {
  claimingId.value = couponId
  try {
    await api.claimCoupon(couponId)
    ElMessage.success('领取成功！')
    fetchAvailableCoupons()
    fetchMyCoupons()
  } catch (error) {
    console.error('领取优惠券失败:', error)
  } finally {
    claimingId.value = null
  }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

function getUserCouponStatusType(status: UserCouponStatusType): string {
  const map: Record<UserCouponStatusType, string> = {
    unused: 'success',
    used: 'info',
    expired: 'danger',
    locked: 'warning'
  }
  return map[status] || 'info'
}

function getUserCouponStatusText(status: UserCouponStatusType): string {
  const map: Record<UserCouponStatusType, string> = {
    unused: '未使用',
    used: '已使用',
    expired: '已过期',
    locked: '已锁定'
  }
  return map[status] || status
}
</script>

<style scoped>
.coupons-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
  text-align: center;
}

.page-header h1 {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
}

.coupons-tabs {
  margin-bottom: 24px;
}

.filter-bar {
  margin-bottom: 24px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 12px;
}

.coupon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
}

.coupon-card {
  position: relative;
  display: flex;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow);
  transition: transform 0.2s, box-shadow 0.2s;
}

.coupon-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.coupon-card.my-coupon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.coupon-card.used {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.coupon-card.expired {
  background: linear-gradient(135deg, #e0e0e0 0%, #bdbdbd 100%);
}

.coupon-left {
  width: 140px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
  padding: 24px 16px;
  border-right: 2px dashed rgba(255, 255, 255, 0.5);
  position: relative;
}

.coupon-left::before,
.coupon-left::after {
  content: '';
  position: absolute;
  right: -10px;
  width: 20px;
  height: 20px;
  background: var(--bg-primary);
  border-radius: 50%;
}

.coupon-left::before {
  top: -10px;
}

.coupon-left::after {
  bottom: -10px;
}

.coupon-amount {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8px;
}

.currency {
  font-size: 20px;
  font-weight: 600;
  margin-top: 4px;
}

.amount {
  font-size: 48px;
  font-weight: 700;
  line-height: 1;
}

.coupon-threshold {
  font-size: 12px;
  opacity: 0.9;
}

.coupon-right {
  flex: 1;
  padding: 20px 24px;
  color: #fff;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 160px;
}

.coupon-name {
  font-size: 18px;
  font-weight: 600;
}

.coupon-desc {
  font-size: 13px;
  opacity: 0.9;
  line-height: 1.4;
}

.coupon-valid,
.coupon-stock,
.coupon-categories {
  font-size: 12px;
  opacity: 0.85;
}

.coupon-status {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: auto;
}

.claim-time {
  font-size: 12px;
  opacity: 0.8;
}

.used-info {
  font-size: 12px;
  opacity: 0.85;
}

.claim-btn {
  margin-top: 8px;
  width: 100%;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.5);
  color: #fff;
  transition: all 0.2s;
}

.claim-btn:hover {
  background: rgba(255, 255, 255, 0.3) !important;
  border-color: #fff !important;
  color: #fff !important;
}

.coupon-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 24px;
  font-weight: 700;
  z-index: 10;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

@media (max-width: 768px) {
  .coupon-grid {
    grid-template-columns: 1fr;
  }

  .coupon-left {
    width: 120px;
  }

  .amount {
    font-size: 36px;
  }
}
</style>
