<template>
  <div class="order-detail-page" v-loading="loading">
    <div class="detail-header">
      <el-button
        text
        @click="router.back()"
        class="back-btn"
      >
        <el-icon><ArrowLeft /></el-icon>
        返回订单列表
      </el-button>
      <h1>订单详情</h1>
    </div>

    <div v-if="order" class="detail-content">
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span class="card-title">订单信息</span>
            <el-tag
              :type="getStatusType(order.status)"
              effect="light"
              size="large"
              class="order-status"
            >
              {{ getStatusText(order.status) }}
            </el-tag>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单编号">
            <span class="order-no">{{ order.order_no }}</span>
            <el-button
              text
              type="primary"
              size="small"
              @click="copyOrderNo"
            >
              复制
            </el-button>
          </el-descriptions-item>
          <el-descriptions-item label="订单状态">
            <el-tag :type="getStatusType(order.status)" effect="light">
              {{ getStatusText(order.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="下单时间">
            {{ formatDate(order.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="支付时间">
            {{ order.paid_at ? formatDate(order.paid_at) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="发货时间">
            {{ order.shipped_at ? formatDate(order.shipped_at) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="完成时间">
            {{ order.delivered_at ? formatDate(order.delivered_at) : '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-card class="info-card">
        <template #header>
          <span class="card-title">收货信息</span>
        </template>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="收货人">
            {{ order.receiver_name }}
          </el-descriptions-item>
          <el-descriptions-item label="联系电话">
            {{ order.receiver_phone }}
          </el-descriptions-item>
          <el-descriptions-item label="收货地址">
            {{ order.receiver_address }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-card
        v-if="order.tracking_company && order.tracking_number"
        class="info-card"
      >
        <template #header>
          <span class="card-title">物流信息</span>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="物流公司">
            {{ order.tracking_company }}
          </el-descriptions-item>
          <el-descriptions-item label="物流单号">
            {{ order.tracking_number }}
            <el-button
              text
              type="primary"
              size="small"
              @click="copyTrackingNo"
            >
              复制
            </el-button>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-card class="items-card">
        <template #header>
          <span class="card-title">商品清单</span>
          <span class="item-count">共 {{ order.items.length }} 件商品</span>
        </template>
        <el-table :data="order.items" style="width: 100%">
          <el-table-column label="商品信息" min-width="300">
            <template #default="{ row }">
              <div class="table-item">
                <div class="item-cover">
                  <img
                    :src="row.book_cover || defaultCover"
                    :alt="row.book_title"
                    @error="handleImageError"
                  />
                </div>
                <div class="item-info">
                  <h3 class="item-title" :title="row.book_title">
                    {{ row.book_title }}
                  </h3>
                  <p class="item-author">{{ row.book_author }}</p>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="单价" width="120" align="center">
            <template #default="{ row }">
              <span class="price">¥{{ row.book_price.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="数量" width="100" align="center">
            <template #default="{ row }">
              {{ row.quantity }}
            </template>
          </el-table-column>
          <el-table-column label="小计" width="120" align="center">
            <template #default="{ row }">
              <span class="subtotal">¥{{ row.subtotal.toFixed(2) }}</span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <el-card
        v-if="order.used_coupon"
        class="info-card coupon-card"
      >
        <template #header>
          <span class="card-title">使用优惠券</span>
        </template>
        <div class="coupon-used-info">
          <div class="coupon-used-badge">
            <span class="coupon-used-amount">-¥{{ order.used_coupon.coupon.discount_amount }}</span>
            <span class="coupon-used-threshold">满{{ order.used_coupon.coupon.threshold_amount }}可用</span>
          </div>
          <div class="coupon-used-details">
            <div class="coupon-used-name">{{ order.used_coupon.coupon.name }}</div>
            <div class="coupon-used-time">使用时间：{{ formatDate(order.used_coupon.used_at!) }}</div>
          </div>
        </div>
      </el-card>

      <el-card class="summary-card">
        <template #header>
          <span class="card-title">订单汇总</span>
        </template>
        <div class="summary-content">
          <div class="summary-row">
            <span>商品总价：</span>
            <span>¥{{ order.original_amount.toFixed(2) }}</span>
          </div>
          <div v-if="order.member_level_name" class="summary-row member-level-row">
            <span>会员等级：</span>
            <el-tag
              :color="order.member_level_name ? '#e6a23c' : '#409eff'"
              effect="dark"
              size="small"
            >
              {{ order.member_level_name }}
              {{ order.member_discount_rate ? (order.member_discount_rate * 10).toFixed(1) + '折' : '' }}
            </el-tag>
          </div>
          <div v-if="order.member_discount_amount > 0" class="summary-row member-discount-row">
            <span>会员优惠：</span>
            <span class="member-discount">-¥{{ order.member_discount_amount.toFixed(2) }}</span>
          </div>
          <div v-if="order.used_coupon" class="summary-row discount-row">
            <span>优惠券抵扣：</span>
            <span class="discount-amount">-¥{{ order.used_coupon.coupon.discount_amount.toFixed(2) }}</span>
          </div>
          <div class="summary-row">
            <span>运费：</span>
            <span class="free-shipping">免运费</span>
          </div>
          <div v-if="order.remark" class="summary-row remark-row">
            <span>备注：</span>
            <span>{{ order.remark }}</span>
          </div>
          <el-divider />
          <div class="summary-total">
            <span>实付金额：</span>
            <span class="total-amount">¥{{ order.total_amount.toFixed(2) }}</span>
          </div>
        </div>
      </el-card>

      <div v-if="order.status === 'pending'" class="action-bar">
        <el-button
          type="danger"
          size="large"
          :loading="canceling"
          @click="handleCancelOrder"
        >
          取消订单
        </el-button>
      </div>
    </div>

    <el-empty
      v-if="!order && !loading"
      description="订单不存在或已被删除"
      class="empty-state"
    >
      <el-button type="primary" @click="router.push('/orders')">
        返回订单列表
      </el-button>
    </el-empty>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { api } from '@/api'
import type { Order, OrderStatus } from '@/types'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const canceling = ref(false)
const order = ref<Order | null>(null)
const defaultCover = 'https://via.placeholder.com/120x160/6366f1/ffffff?text=Book'

const statusMap: Record<OrderStatus, { text: string; type: 'warning' | 'primary' | 'success' | 'info' }> = {
  pending: { text: '待处理', type: 'warning' },
  confirmed: { text: '已确认', type: 'primary' },
  shipped: { text: '已发货', type: 'primary' },
  delivered: { text: '已完成', type: 'success' },
  cancelled: { text: '已取消', type: 'info' }
}

onMounted(async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push({ name: 'Login', query: { redirect: route.fullPath } })
    return
  }
  await fetchOrderDetail()
})

function getStatusText(status: OrderStatus): string {
  return statusMap[status]?.text || status
}

function getStatusType(status: OrderStatus): 'warning' | 'primary' | 'success' | 'info' {
  return statusMap[status]?.type || 'info'
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

function handleImageError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultCover
}

async function fetchOrderDetail() {
  const orderId = Number(route.params.id)
  if (!orderId) {
    ElMessage.error('订单ID无效')
    router.push('/orders')
    return
  }

  loading.value = true
  try {
    order.value = await api.getOrderDetail(orderId)
  } catch (error) {
    console.error('获取订单详情失败:', error)
    order.value = null
  } finally {
    loading.value = false
  }
}

function copyOrderNo() {
  if (!order.value) return
  navigator.clipboard.writeText(order.value.order_no)
  ElMessage.success('订单编号已复制')
}

function copyTrackingNo() {
  if (!order.value?.tracking_number) return
  navigator.clipboard.writeText(order.value.tracking_number)
  ElMessage.success('物流单号已复制')
}

async function handleCancelOrder() {
  if (!order.value) return

  try {
    await ElMessageBox.confirm(
      `确定要取消订单「${order.value.order_no}」吗？`,
      '取消订单',
      {
        confirmButtonText: '确定取消',
        cancelButtonText: '再想想',
        type: 'warning'
      }
    )

    canceling.value = true
    try {
      await api.cancelOrder(order.value.id, { cancel_reason: '用户取消' })
      ElMessage.success('订单已取消')
      await fetchOrderDetail()
    } finally {
      canceling.value = false
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消订单失败:', error)
    }
  }
}
</script>

<style scoped>
.order-detail-page {
  max-width: 1000px;
  margin: 0 auto;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.back-btn {
  font-size: 14px;
  color: var(--text-secondary);
}

.detail-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-card,
.items-card,
.summary-card {
  border-radius: 16px;
  box-shadow: var(--shadow);
  border: none;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.item-count {
  font-size: 14px;
  color: var(--text-secondary);
}

.order-status {
  font-weight: 500;
}

.order-no {
  font-weight: 500;
  color: var(--text-primary);
  margin-right: 8px;
}

.table-item {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 8px 0;
}

.item-cover {
  width: 60px;
  height: 80px;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
}

.item-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0 0 6px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-author {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
}

.price {
  color: var(--secondary-color);
  font-weight: 500;
}

.subtotal {
  color: var(--danger-color);
  font-weight: 600;
}

.summary-content {
  padding: 8px 0;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 14px;
  color: var(--text-secondary);
}

.remark-row {
  align-items: flex-start;
}

.remark-row span:last-child {
  flex: 1;
  margin-left: 16px;
  text-align: right;
}

.free-shipping {
  color: var(--success-color);
}

.member-level-row {
  display: flex;
  align-items: center;
}

.member-discount-row {
  color: var(--warning-color);
}

.member-discount {
  font-weight: 600;
  color: var(--danger-color);
}

.discount-row {
  color: var(--danger-color);
}

.discount-amount {
  color: var(--danger-color);
  font-weight: 600;
}

.coupon-used-info {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: #fff;
}

.coupon-used-badge {
  text-align: center;
  padding: 12px 24px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  flex-shrink: 0;
}

.coupon-used-amount {
  display: block;
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
}

.coupon-used-threshold {
  display: block;
  font-size: 12px;
  opacity: 0.9;
  margin-top: 4px;
}

.coupon-used-details {
  flex: 1;
}

.coupon-used-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.coupon-used-time {
  font-size: 13px;
  opacity: 0.9;
}

.coupon-card {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

.coupon-card :deep(.el-card__header) {
  padding: 0 0 16px 0;
  border-bottom: none;
}

.summary-total {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.summary-total span:first-child {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
}

.total-amount {
  font-size: 28px;
  font-weight: 700;
  color: var(--danger-color);
}

.action-bar {
  display: flex;
  justify-content: flex-end;
  padding: 16px 0;
}

.empty-state {
  padding: 80px 0;
}

:deep(.el-descriptions__label) {
  width: 120px;
  font-weight: 500;
}

:deep(.el-table th) {
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-weight: 500;
}

@media (max-width: 768px) {
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  :deep(.el-descriptions) {
    font-size: 13px;
  }

  :deep(.el-descriptions__label) {
    width: 100px;
  }

  .action-bar {
    justify-content: center;
  }

  .action-bar .el-button {
    width: 100%;
  }
}
</style>
