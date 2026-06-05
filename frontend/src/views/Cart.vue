<template>
  <div class="cart-page" v-loading="cartStore.loading">
    <div class="cart-header">
      <h1>购物车</h1>
      <div class="cart-actions">
        <el-button
          v-if="cartStore.hasInvalidItems"
          type="danger"
          @click="handleClearInvalid"
        >
          <el-icon><Delete /></el-icon>
          清理失效商品
        </el-button>
        <el-button @click="handleClearCart">
          <el-icon><Delete /></el-icon>
          清空购物车
        </el-button>
      </div>
    </div>

    <el-alert
      v-if="cartStore.hasLowStockItems"
      type="warning"
      :title="`有 ${cartStore.lowStockItems.length} 件商品库存不足，请调整数量`"
      show-icon
      class="stock-alert"
    />

    <el-alert
      v-if="cartStore.hasInvalidItems"
      type="error"
      :title="`有 ${cartStore.invalidItems.length} 件商品已失效，请清理`"
      show-icon
      class="stock-alert"
    />

    <div class="cart-content">
      <div class="cart-main">
        <div class="cart-table-header">
          <el-checkbox
            :model-value="cartStore.isAllSelected"
            :indeterminate="!cartStore.isAllSelected && cartStore.items.length > 0 && cartStore.items.some(i => i.selected)"
            @change="cartStore.toggleAllSelected"
          >
            全选
          </el-checkbox>
          <span class="header-info">商品信息</span>
          <span class="header-price">单价</span>
          <span class="header-quantity">数量</span>
          <span class="header-subtotal">小计</span>
          <span class="header-action">操作</span>
        </div>

        <div class="cart-items">
          <div
            v-for="item in cartStore.items"
            :key="item.id"
            class="cart-item"
            :class="{ 'low-stock': isLowStock(item) }"
          >
            <div class="item-checkbox">
              <el-checkbox
                :model-value="item.selected"
                @change="(val: boolean) => cartStore.updateSelected(item.id, val)"
              />
            </div>

            <div class="item-cover" @click="router.push(`/books/${item.book_id}`)">
              <img
                :src="item.book.cover_image || defaultCover"
                :alt="item.book.title"
                @error="handleImageError"
              />
            </div>

            <div class="item-info" @click="router.push(`/books/${item.book_id}`)">
              <h3 class="item-title" :title="item.book.title">{{ item.book.title }}</h3>
              <p class="item-author">{{ item.book.author }}</p>
              <div class="item-stock">
                <el-tag
                  v-if="isLowStock(item)"
                  type="warning"
                  size="small"
                  effect="light"
                >
                  库存仅 {{ item.book.stock }} 本
                </el-tag>
                <el-tag
                  v-else
                  type="success"
                  size="small"
                  effect="light"
                >
                  库存 {{ item.book.stock }} 本
                </el-tag>
              </div>
            </div>

            <div class="item-price">
              <span class="price-value">¥{{ item.book.price.toFixed(2) }}</span>
              <span v-if="memberLevelInfo?.current_level && memberLevelInfo.current_level.discount_rate < 1" class="member-price">
                会员价 ¥{{ (item.book.price * memberLevelInfo.current_level.discount_rate).toFixed(2) }}
              </span>
            </div>

            <div class="item-quantity">
              <el-input-number
              :model-value="item.quantity"
              :min="1"
              :max="item.book.stock"
              size="small"
              @change="(val: number) => handleQuantityChange(item, val)"
              />
            </div>

            <div class="item-subtotal">
              <div v-if="memberLevelInfo?.current_level && memberLevelInfo.current_level.discount_rate < 1">
                <span class="subtotal-value member">¥{{ (item.quantity * item.book.price * memberLevelInfo.current_level.discount_rate).toFixed(2) }}</span>
                <span class="original-subtotal">¥{{ (item.quantity * item.book.price).toFixed(2) }}</span>
              </div>
              <span v-else class="subtotal-value">¥{{ (item.quantity * item.book.price).toFixed(2) }}</span>
            </div>

            <div class="item-action">
              <el-button
                type="danger"
                text
                @click="handleDeleteItem(item)"
              >
                删除
              </el-button>
            </div>
          </div>

          <el-empty
            v-if="cartStore.items.length === 0 && cartStore.invalidItems.length === 0"
            description="购物车是空的"
            class="cart-empty"
          >
            <el-button type="primary" @click="router.push('/books')">
              去逛逛
            </el-button>
          </el-empty>
        </div>

        <div v-if="cartStore.invalidItems.length > 0" class="invalid-section">
          <h3 class="invalid-title">
            <el-icon><WarningFilled /></el-icon>
            失效商品 ({{ cartStore.invalidItems.length }})
          </h3>
          <div
            v-for="item in cartStore.invalidItems"
            :key="item.id"
            class="cart-item invalid-item"
          >
            <div class="item-checkbox">
              <el-checkbox disabled />
            </div>

            <div class="item-cover">
              <img
                :src="item.book?.cover_image || defaultCover"
                :alt="item.book?.title || '已下架'"
                @error="handleImageError"
              />
            </div>

            <div class="item-info">
              <h3 class="item-title" :title="item.book?.title || '已下架'">
                {{ item.book?.title || '商品已下架' }}
              </h3>
              <p class="item-author">{{ item.book?.author || '-' }}</p>
              <div class="item-stock">
                <el-tag type="danger" size="small" effect="light">
                  {{ item.book?.stock === 0 ? '已缺货' : '已失效' }}
                </el-tag>
              </div>
            </div>

            <div class="item-price">
              <span class="price-value invalid">
                ¥{{ item.book?.price.toFixed(2) || '--' }}
              </span>
            </div>

            <div class="item-quantity">
              <el-input-number
                :model-value="item.quantity"
                :min="1"
                disabled
                size="small"
              />
            </div>

            <div class="item-subtotal">
              <span class="subtotal-value invalid">
                ¥{{ item.book ? (item.quantity * item.book.price).toFixed(2) : '--' }}
              </span>
            </div>

            <div class="item-action">
              <el-button
                type="danger"
                text
                @click="handleDeleteItem(item)"
              >
                删除
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <div class="cart-sidebar">
        <div class="cart-summary">
          <h3>订单汇总</h3>
          
          <div class="summary-row">
            <span>商品件数：</span>
            <span>{{ cartStore.totalCount }} 件</span>
          </div>
          
          <div class="summary-row">
            <span>已选件数：</span>
            <span>{{ cartStore.selectedCount }} 件</span>
          </div>
          
          <div class="summary-row total-row">
            <span>商品总价：</span>
            <span class="total-price">¥{{ cartStore.selectedPrice.toFixed(2) }}</span>
          </div>
          
          <div v-if="memberDiscount > 0" class="summary-row member-discount-row">
            <span>会员优惠：</span>
            <span class="member-discount">-¥{{ memberDiscount.toFixed(2) }}</span>
          </div>

          <el-divider />

          <div class="summary-footer">
            <div class="footer-total">
              <span>合计：</span>
              <span class="footer-price">¥{{ finalPrice.toFixed(2) }}</span>
            </div>
            <div v-if="memberDiscount > 0" class="saved-info">
              已优惠 ¥{{ memberDiscount.toFixed(2) }}
            </div>
            
            <el-button
              type="primary"
              size="large"
              class="checkout-btn"
              :disabled="cartStore.selectedCount === 0"
              @click="handleCheckout"
            >
              结算 ({{ cartStore.selectedCount }})
            </el-button>
            
            <el-button
              type="danger"
              text
              class="delete-selected-btn"
              :disabled="cartStore.selectedCount === 0"
              @click="handleDeleteSelected"
            >
              删除选中
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useUserStore } from '@/stores/user'
import type { CartItem, UserMemberLevelInfo } from '@/types'
import { api } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Delete,
  WarningFilled
} from '@element-plus/icons-vue'

const router = useRouter()
const cartStore = useCartStore()
const userStore = useUserStore()

const defaultCover = 'https://via.placeholder.com/120x160/6366f1/ffffff?text=Book'
const memberLevelInfo = ref<UserMemberLevelInfo | null>(null)

const memberDiscount = computed(() => {
  if (!memberLevelInfo.value?.current_level || memberLevelInfo.value.current_level.discount_rate >= 1) {
    return 0
  }
  const discountRate = memberLevelInfo.value.current_level.discount_rate
  return cartStore.selectedPrice * (1 - discountRate)
})

const finalPrice = computed(() => {
  return cartStore.selectedPrice - memberDiscount.value
})

onMounted(async () => {
  await checkLoginAndFetch()
})

async function checkLoginAndFetch() {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后查看购物车')
    router.push({ name: 'Login', query: { redirect: '/cart' } })
    return
  }
  await Promise.all([
    cartStore.fetchCart(),
    fetchMemberLevel()
  ])
}

async function fetchMemberLevel() {
  try {
    memberLevelInfo.value = await api.getMyMemberLevel()
  } catch (error) {
    console.error('获取会员等级信息失败:', error)
    memberLevelInfo.value = null
  }
}

function isLowStock(item: CartItem): boolean {
  return cartStore.lowStockItems.some(i => i.id === item.id)
}

function handleImageError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultCover
}

async function handleQuantityChange(item: CartItem, newQuantity: number) {
  if (newQuantity > item.book.stock) {
    ElMessage.warning(`库存不足，当前库存 ${item.book.stock} 本`)
    return
  }
  await cartStore.updateQuantity(item.id, item.book_id, newQuantity)
}

async function handleDeleteItem(item: CartItem) {
  try {
    await ElMessageBox.confirm(
      `确定要删除「${item.book?.title || '该商品'}」吗？`,
      '删除确认',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await cartStore.deleteItem(item.id, item.book_id)
  } catch {
    // 用户取消
  }
}

async function handleDeleteSelected() {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${cartStore.selectedCount} 件商品吗？`,
      '批量删除确认',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await cartStore.deleteSelected()
  } catch {
    // 用户取消
  }
}

async function handleClearInvalid() {
  try {
    await ElMessageBox.confirm(
      '确定要清理所有失效商品吗？',
      '清理确认',
      {
        confirmButtonText: '清理',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await cartStore.clearInvalidItems()
  } catch {
    // 用户取消
  }
}

async function handleClearCart() {
  if (cartStore.items.length === 0 && cartStore.invalidItems.length === 0) {
    ElMessage.warning('购物车已经是空的了')
    return
  }
  try {
    await ElMessageBox.confirm(
      '确定要清空购物车吗？此操作不可恢复。',
      '清空确认',
      {
        confirmButtonText: '清空',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await cartStore.clearCart()
  } catch {
    // 用户取消
  }
}

function handleCheckout() {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push({ name: 'Login', query: { redirect: '/cart' } })
    return
  }
  if (cartStore.selectedCount === 0) {
    ElMessage.warning('请选择要结算的商品')
    return
  }
  router.push('/checkout')
}
</script>

<style scoped>
.cart-page {
  max-width: 1400px;
  margin: 0 auto;
}

.cart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.cart-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.cart-actions {
  display: flex;
  gap: 12px;
}

.stock-alert {
  margin-bottom: 16px;
}

.cart-content {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.cart-main {
  flex: 1;
  background: var(--bg-secondary);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow);
}

.cart-table-header {
  display: grid;
  grid-template-columns: 60px 1fr 120px 160px 120px 100px;
  gap: 16px;
  padding: 20px 24px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  font-weight: 500;
  color: var(--text-secondary);
  font-size: 14px;
}

.header-info {
  text-align: left;
}

.header-price,
.header-quantity,
.header-subtotal,
.header-action {
  text-align: center;
}

.cart-items {
  padding: 0 24px;
}

.cart-item {
  display: grid;
  grid-template-columns: 60px 120px 1fr 120px 160px 120px 100px;
  gap: 16px;
  align-items: center;
  padding: 20px 0;
  border-bottom: 1px solid var(--border-color);
  transition: background 0.2s;
}

.cart-item:last-child {
  border-bottom: none;
}

.cart-item.low-stock {
  background: rgba(251, 191, 36, 0.05);
}

.item-checkbox {
  display: flex;
  justify-content: center;
}

.item-cover {
  width: 100px;
  height: 130px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s;
}

.item-cover:hover {
  transform: scale(1.02);
}

.item-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-info {
  cursor: pointer;
}

.item-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.4;
}

.item-author {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.item-stock {
  display: flex;
  gap: 8px;
}

.item-price {
  text-align: center;
}

.price-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--secondary-color);
}

.price-value.invalid {
  color: var(--text-muted);
  text-decoration: line-through;
}

.item-quantity {
  display: flex;
  justify-content: center;
}

.item-subtotal {
  text-align: center;
}

.subtotal-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--danger-color);
}

.subtotal-value.invalid {
  color: var(--text-muted);
  text-decoration: line-through;
}

.item-action {
  display: flex;
  justify-content: center;
}

.cart-empty {
  padding: 60px 0;
}

.invalid-section {
  padding: 0 24px 24px;
}

.invalid-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--danger-color);
  margin-bottom: 16px;
  padding-top: 24px;
  border-top: 2px dashed var(--border-color);
}

.invalid-item {
  opacity: 0.7;
}

.cart-sidebar {
  width: 320px;
  flex-shrink: 0;
}

.cart-summary {
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--shadow);
  position: sticky;
  top: 88px;
}

.cart-summary h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 14px;
  color: var(--text-secondary);
}

.summary-row.total-row .total-price {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
}

.summary-row.selected-row .selected-price {
  font-size: 16px;
  font-weight: 600;
  color: var(--danger-color);
}

.summary-footer {
  margin-top: 8px;
}

.footer-total {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 16px;
}

.footer-total span:first-child {
  font-size: 14px;
  color: var(--text-secondary);
}

.footer-price {
  font-size: 24px;
  font-weight: 700;
  color: var(--danger-color);
}

.checkout-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
}

.delete-selected-btn {
  width: 100%;
  margin-top: 12px;
}

@media (max-width: 1024px) {
  .cart-content {
    flex-direction: column;
  }

  .cart-sidebar {
    width: 100%;
  }

  .cart-summary {
    position: static;
  }

  .cart-table-header {
    grid-template-columns: 50px 1fr 100px 140px 100px 80px;
    font-size: 12px;
    padding: 16px;
  }

  .cart-item {
    grid-template-columns: 50px 80px 1fr 100px 140px 100px 80px;
    padding: 16px 0;
  }

  .item-cover {
    width: 80px;
    height: 100px;
  }
}

@media (max-width: 640px) {
  .cart-table-header {
    display: none;
  }

  .cart-item {
    grid-template-columns: 40px 1fr;
    grid-template-rows: auto auto auto;
    gap: 12px;
    padding: 16px 0;
  }

  .item-checkbox {
    grid-row: span 2;
  }

  .item-cover {
    grid-column: 2;
    grid-row: 1 / span 2;
    width: 90px;
    height: 120px;
  }

  .item-info {
    grid-column: 2;
    grid-row: 3;
  }

  .item-price,
  .item-quantity,
  .item-subtotal,
  .item-action {
    grid-column: 2;
    grid-row: auto;
    justify-content: flex-start;
    text-align: left;
  }

  .invalid-item .item-checkbox {
    grid-row: span 2;
  }

  .invalid-item .item-cover {
    grid-column: 2;
    grid-row: 1 / span 2;
  }

  .invalid-item .item-info {
    grid-column: 2;
    grid-row: 3;
  }
}

.item-price {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.member-price {
  font-size: 13px;
  font-weight: 600;
  color: var(--warning-color);
}

.item-subtotal {
  text-align: center;
}

.original-subtotal {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  text-decoration: line-through;
}

.subtotal-value.member {
  color: var(--danger-color);
}

.member-discount-row {
  color: var(--warning-color);
}

.member-discount {
  font-weight: 600;
  color: var(--danger-color);
}

.saved-info {
  text-align: right;
  font-size: 13px;
  color: var(--danger-color);
  margin-bottom: 12px;
}
</style>
