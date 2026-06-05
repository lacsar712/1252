<template>
  <div class="checkout-page" v-loading="loading">
    <div class="checkout-header">
      <h1>确认订单</h1>
    </div>

    <div class="checkout-content">
      <div class="checkout-main">
        <el-card class="form-card">
          <template #header>
            <span class="card-title">收货信息</span>
          </template>
          <el-form
            ref="formRef"
            :model="formData"
            :rules="formRules"
            label-width="100px"
            label-position="right"
          >
            <el-form-item label="收货人" prop="receiver_name">
              <el-input
                v-model="formData.receiver_name"
                placeholder="请输入收货人姓名"
                maxlength="50"
                show-word-limit
              />
            </el-form-item>
            <el-form-item label="联系电话" prop="receiver_phone">
              <el-input
                v-model="formData.receiver_phone"
                placeholder="请输入联系电话"
                maxlength="20"
              />
            </el-form-item>
            <el-form-item label="收货地址" prop="receiver_address">
              <el-input
                v-model="formData.receiver_address"
                type="textarea"
                :rows="3"
                placeholder="请输入详细收货地址"
                maxlength="200"
                show-word-limit
              />
            </el-form-item>
            <el-form-item label="备注" prop="remark">
              <el-input
                v-model="formData.remark"
                type="textarea"
                :rows="2"
                placeholder="选填，如有特殊要求请备注"
                maxlength="200"
                show-word-limit
              />
            </el-form-item>
          </el-form>
        </el-card>

        <el-card class="items-card">
          <template #header>
            <span class="card-title">商品清单</span>
            <span class="item-count">共 {{ selectedItems.length }} 件商品</span>
          </template>
          <div class="items-list">
            <div
              v-for="item in selectedItems"
              :key="item.id"
              class="order-item"
            >
              <div class="item-cover">
                <img
                  :src="item.book.cover_image || defaultCover"
                  :alt="item.book.title"
                  @error="handleImageError"
                />
              </div>
              <div class="item-info">
                <h3 class="item-title" :title="item.book.title">
                  {{ item.book.title }}
                </h3>
                <p class="item-author">{{ item.book.author }}</p>
                <p class="item-price">
                  单价：<span class="price">¥{{ item.book.price.toFixed(2) }}</span>
                  <span class="quantity">x {{ item.quantity }}</span>
                </p>
              </div>
              <div class="item-subtotal">
                <span class="subtotal">¥{{ (item.quantity * item.book.price).toFixed(2) }}</span>
              </div>
            </div>
          </div>
          <el-empty
            v-if="selectedItems.length === 0"
            description="没有选择商品"
            class="empty-state"
          >
            <el-button type="primary" @click="router.push('/cart')">
              返回购物车
            </el-button>
          </el-empty>
        </el-card>
      </div>

      <div class="checkout-sidebar">
        <div class="order-summary">
          <h3>订单汇总</h3>
          <div class="summary-row">
            <span>商品件数：</span>
            <span>{{ cartStore.selectedCount }} 件</span>
          </div>
          <div class="summary-row">
            <span>商品总价：</span>
            <span>¥{{ cartStore.selectedPrice.toFixed(2) }}</span>
          </div>
          <div class="summary-row">
            <span>运费：</span>
            <span class="free-shipping">免运费</span>
          </div>
          <el-divider />
          <div class="summary-footer">
            <div class="footer-total">
              <span>应付金额：</span>
              <span class="footer-price">¥{{ cartStore.selectedPrice.toFixed(2) }}</span>
            </div>
            <el-button
              type="primary"
              size="large"
              class="submit-btn"
              :disabled="selectedItems.length === 0 || submitting"
              :loading="submitting"
              @click="handleSubmit"
            >
              提交订单
            </el-button>
            <el-button
              class="back-btn"
              @click="router.push('/cart')"
            >
              返回购物车
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
import { api } from '@/api'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'

const router = useRouter()
const cartStore = useCartStore()
const userStore = useUserStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const submitting = ref(false)
const defaultCover = 'https://via.placeholder.com/120x160/6366f1/ffffff?text=Book'

const formData = ref({
  receiver_name: '',
  receiver_phone: '',
  receiver_address: '',
  remark: ''
})

const formRules: FormRules = {
  receiver_name: [
    { required: true, message: '请输入收货人姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '姓名长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  receiver_phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  receiver_address: [
    { required: true, message: '请输入收货地址', trigger: 'blur' },
    { min: 5, max: 200, message: '地址长度在 5 到 200 个字符', trigger: 'blur' }
  ]
}

const selectedItems = computed(() => {
  return cartStore.items.filter(item => item.selected)
})

onMounted(async () => {
  await checkLoginAndFetch()
})

async function checkLoginAndFetch() {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push({ name: 'Login', query: { redirect: '/checkout' } })
    return
  }
  loading.value = true
  try {
    await cartStore.fetchCart()
    if (selectedItems.value.length === 0) {
      ElMessage.warning('请先选择要结算的商品')
      router.push('/cart')
    }
  } finally {
    loading.value = false
  }
}

function handleImageError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultCover
}

async function handleSubmit() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    ElMessage.warning('请完善收货信息')
    return
  }

  if (selectedItems.value.length === 0) {
    ElMessage.warning('请先选择要结算的商品')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确认提交订单吗？应付金额 ¥${cartStore.selectedPrice.toFixed(2)}`,
      '提交订单',
      {
        confirmButtonText: '确认提交',
        cancelButtonText: '再想想',
        type: 'warning'
      }
    )
  } catch {
    return
  }

  submitting.value = true
  try {
    const cartItemIds = selectedItems.value.map(item => item.id)
    const response = await api.createOrder({
      ...formData.value,
      cart_item_ids: cartItemIds
    })

    ElMessage.success('订单提交成功！')
    await cartStore.fetchCart()
    router.push(`/orders/${response.id}`)
  } catch (error) {
    console.error('提交订单失败:', error)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.checkout-page {
  max-width: 1400px;
  margin: 0 auto;
}

.checkout-header {
  margin-bottom: 24px;
}

.checkout-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.checkout-content {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.checkout-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-card,
.items-card {
  border-radius: 16px;
  box-shadow: var(--shadow);
  border: none;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.item-count {
  font-size: 14px;
  color: var(--text-secondary);
  float: right;
}

.items-list {
  display: flex;
  flex-direction: column;
}

.order-item {
  display: flex;
  gap: 16px;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid var(--border-color);
}

.order-item:last-child {
  border-bottom: none;
}

.item-cover {
  width: 80px;
  height: 100px;
  border-radius: 8px;
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
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-author {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 8px 0;
}

.item-price {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.price {
  color: var(--secondary-color);
  font-weight: 500;
}

.quantity {
  margin-left: 16px;
  color: var(--text-muted);
}

.item-subtotal {
  flex-shrink: 0;
  text-align: right;
}

.subtotal {
  font-size: 18px;
  font-weight: 600;
  color: var(--danger-color);
}

.empty-state {
  padding: 40px 0;
}

.checkout-sidebar {
  width: 320px;
  flex-shrink: 0;
}

.order-summary {
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--shadow);
  position: sticky;
  top: 88px;
}

.order-summary h3 {
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

.free-shipping {
  color: var(--success-color);
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

.submit-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
}

.back-btn {
  width: 100%;
  margin-top: 12px;
}

@media (max-width: 1024px) {
  .checkout-content {
    flex-direction: column;
  }

  .checkout-sidebar {
    width: 100%;
  }

  .order-summary {
    position: static;
  }
}
</style>
