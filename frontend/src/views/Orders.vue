<template>
  <div class="orders-page" v-loading="loading">
    <div class="orders-header">
      <h1>我的订单</h1>
    </div>

    <el-card class="orders-card">
      <el-tabs
        v-model="activeTab"
        class="status-tabs"
        @tab-change="handleTabChange"
      >
        <el-tab-pane label="全部" name="" />
        <el-tab-pane label="待处理" name="pending" />
        <el-tab-pane label="已确认" name="confirmed" />
        <el-tab-pane label="已发货" name="shipped" />
        <el-tab-pane label="已完成" name="delivered" />
        <el-tab-pane label="已取消" name="cancelled" />
      </el-tabs>

      <div class="orders-list">
        <div
          v-for="order in orders"
          :key="order.id"
          class="order-card"
        >
          <div class="order-header">
            <div class="order-info">
              <span class="order-no">订单编号：{{ order.order_no }}</span>
              <span class="order-time">下单时间：{{ formatDate(order.created_at) }}</span>
            </div>
            <el-tag
              :type="getStatusType(order.status)"
              effect="light"
              size="large"
              class="order-status"
            >
              {{ getStatusText(order.status) }}
            </el-tag>
          </div>

          <div class="order-items">
            <div
              v-for="(item, index) in order.items"
              :key="index"
              class="order-item"
              @click="router.push(`/orders/${order.id}`)"
            >
              <div class="item-cover">
                <img
                  :src="item.book_cover || defaultCover"
                  :alt="item.book_title"
                  @error="handleImageError"
                />
              </div>
              <div class="item-info">
                <h3 class="item-title" :title="item.book_title">
                  {{ item.book_title }}
                </h3>
                <p class="item-author">{{ item.book_author }}</p>
                <p class="item-price">
                  <span class="price">¥{{ item.book_price.toFixed(2) }}</span>
                  <span class="quantity">x {{ item.quantity }}</span>
                </p>
              </div>
              <div class="item-subtotal">
                <span class="subtotal">¥{{ item.subtotal.toFixed(2) }}</span>
              </div>
            </div>
          </div>

          <div class="order-footer">
            <div class="order-total">
              共 {{ order.items.length }} 件商品，实付：
              <span class="total-amount">¥{{ order.total_amount.toFixed(2) }}</span>
            </div>
            <div class="order-actions">
              <el-button
                type="primary"
                size="small"
                @click="router.push(`/orders/${order.id}`)"
              >
                查看详情
              </el-button>
              <el-button
                v-if="order.status === 'pending'"
                type="danger"
                size="small"
                @click="handleCancelOrder(order)"
              >
                取消订单
              </el-button>
            </div>
          </div>
        </div>

        <el-empty
          v-if="orders.length === 0 && !loading"
          description="暂无订单"
          class="empty-state"
        >
          <el-button type="primary" @click="router.push('/books')">
            去逛逛
          </el-button>
        </el-empty>
      </div>

      <el-pagination
        v-if="total > 0"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[5, 10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        background
        class="pagination"
        @size-change="fetchOrders"
        @current-change="fetchOrders"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { api } from '@/api'
import type { Order, OrderStatus } from '@/types'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const activeTab = ref<OrderStatus | ''>('')
const orders = ref<Order[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const defaultCover = 'https://via.placeholder.com/120x160/6366f1/ffffff?text=Book'

const statusMap: Record<OrderStatus, { text: string; type: 'warning' | 'primary' | 'purple' | 'success' | 'info' }> = {
  pending: { text: '待处理', type: 'warning' },
  confirmed: { text: '已确认', type: 'primary' },
  shipped: { text: '已发货', type: 'primary' },
  delivered: { text: '已完成', type: 'success' },
  cancelled: { text: '已取消', type: 'info' }
}

onMounted(async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push({ name: 'Login', query: { redirect: '/orders' } })
    return
  }
  await fetchOrders()
})

function getStatusText(status: OrderStatus): string {
  return statusMap[status]?.text || status
}

function getStatusType(status: OrderStatus): 'warning' | 'primary' | 'success' | 'info' {
  const type = statusMap[status]?.type
  if (type === 'purple') return 'primary'
  return type || 'info'
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function handleImageError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultCover
}

function handleTabChange() {
  currentPage.value = 1
  fetchOrders()
}

async function fetchOrders() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...(activeTab.value ? { status: activeTab.value as OrderStatus } : {})
    }
    const response = await api.getMyOrders(params)
    orders.value = response.items
    total.value = response.total
  } catch (error) {
    console.error('获取订单列表失败:', error)
  } finally {
    loading.value = false
  }
}

async function handleCancelOrder(order: Order) {
  try {
    await ElMessageBox.confirm(
      `确定要取消订单「${order.order_no}」吗？`,
      '取消订单',
      {
        confirmButtonText: '确定取消',
        cancelButtonText: '再想想',
        type: 'warning'
      }
    )

    await api.cancelOrder(order.id, { cancel_reason: '用户取消' })
    ElMessage.success('订单已取消')
    await fetchOrders()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消订单失败:', error)
    }
  }
}
</script>

<style scoped>
.orders-page {
  max-width: 1200px;
  margin: 0 auto;
}

.orders-header {
  margin-bottom: 24px;
}

.orders-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.orders-card {
  border-radius: 16px;
  box-shadow: var(--shadow);
  border: none;
}

.status-tabs {
  margin-bottom: 24px;
}

.status-tabs :deep(.el-tabs__nav-wrap::after) {
  background-color: var(--border-color);
}

.orders-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.order-card {
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  transition: box-shadow 0.2s;
}

.order-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
}

.order-info {
  display: flex;
  gap: 24px;
  font-size: 14px;
  color: var(--text-secondary);
}

.order-no {
  font-weight: 500;
  color: var(--text-primary);
}

.order-status {
  font-weight: 500;
}

.order-items {
  padding: 16px 24px;
}

.order-item {
  display: flex;
  gap: 16px;
  align-items: center;
  padding: 12px 0;
  cursor: pointer;
  transition: background 0.2s;
  border-radius: 8px;
}

.order-item:hover {
  background: var(--bg-primary);
}

.order-item + .order-item {
  border-top: 1px dashed var(--border-color);
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
  margin: 0 0 6px 0;
}

.item-price {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
}

.price {
  color: var(--secondary-color);
}

.quantity {
  margin-left: 12px;
}

.item-subtotal {
  flex-shrink: 0;
  text-align: right;
}

.subtotal {
  font-size: 16px;
  font-weight: 600;
  color: var(--danger-color);
}

.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: var(--bg-primary);
  border-top: 1px solid var(--border-color);
}

.order-total {
  font-size: 14px;
  color: var(--text-secondary);
}

.total-amount {
  font-size: 20px;
  font-weight: 700;
  color: var(--danger-color);
  margin-left: 8px;
}

.order-actions {
  display: flex;
  gap: 12px;
}

.empty-state {
  padding: 60px 0;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

@media (max-width: 768px) {
  .order-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .order-info {
    flex-direction: column;
    gap: 4px;
  }

  .order-footer {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .order-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
