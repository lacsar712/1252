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
                  单价：
                  <template v-if="memberLevelInfo?.current_level && memberLevelInfo.current_level.discount_rate < 1">
                    <span class="original-price">¥{{ item.book.price.toFixed(2) }}</span>
                    <span class="member-price-tag">
                      会员价 ¥{{ (item.book.price * memberLevelInfo.current_level.discount_rate).toFixed(2) }}
                    </span>
                  </template>
                  <template v-else>
                    <span class="price">¥{{ item.book.price.toFixed(2) }}</span>
                  </template>
                  <span class="quantity">x {{ item.quantity }}</span>
                </p>
              </div>
              <div class="item-subtotal">
                <template v-if="memberLevelInfo?.current_level && memberLevelInfo.current_level.discount_rate < 1">
                  <span class="subtotal">¥{{ (item.quantity * item.book.price * memberLevelInfo.current_level.discount_rate).toFixed(2) }}</span>
                  <span class="original-subtotal">¥{{ (item.quantity * item.book.price).toFixed(2) }}</span>
                </template>
                <template v-else>
                  <span class="subtotal">¥{{ (item.quantity * item.book.price).toFixed(2) }}</span>
                </template>
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
            <span>商品原价：</span>
            <span>¥{{ originalPrice.toFixed(2) }}</span>
          </div>
          <div v-if="memberLevelInfo?.current_level" class="summary-row member-level-row">
            <span>会员等级：</span>
            <el-tag
              :color="memberLevelInfo.current_level.badge_color || '#409eff'"
              effect="dark"
              size="small"
            >
              {{ memberLevelInfo.current_level.name }}
              {{ (memberLevelInfo.current_level.discount_rate * 10).toFixed(1) }}折
            </el-tag>
          </div>
          <div v-if="memberDiscount > 0" class="summary-row member-discount-row">
            <span>会员优惠：</span>
            <span class="member-discount">-¥{{ memberDiscount.toFixed(2) }}</span>
          </div>
          <div class="summary-row">
            <span>运费：</span>
            <span class="free-shipping">免运费</span>
          </div>

          <div class="coupon-section">
            <div class="coupon-header">
              <span class="coupon-title">优惠券</span>
              <el-button type="primary" link @click="openCouponDialog" :disabled="selectedItems.length === 0">
                <template v-if="selectedCoupon">
                  已选：¥{{ selectedCoupon.coupon.discount_amount }}
                </template>
                <template v-else-if="availableCoupons.length > 0">
                  {{ availableCoupons.length }}张可用
                </template>
                <template v-else>
                  暂无可用
                </template>
              </el-button>
            </div>
            <div v-if="selectedCoupon" class="selected-coupon-info">
              <div class="coupon-badge">
                <span class="coupon-badge-amount">-¥{{ selectedCoupon.coupon.discount_amount }}</span>
              </div>
              <div class="coupon-badge-info">
                <div class="coupon-badge-name">{{ selectedCoupon.coupon.name }}</div>
                <div class="coupon-badge-desc">满{{ selectedCoupon.coupon.threshold_amount }}可用</div>
              </div>
              <el-button link type="danger" @click="clearCoupon">不使用</el-button>
            </div>
          </div>

          <el-divider />
          <div class="summary-footer">
            <div class="footer-total">
              <span>应付金额：</span>
              <span class="footer-price">¥{{ finalPrice.toFixed(2) }}</span>
            </div>
            <div v-if="totalDiscount > 0" class="discount-info">
              已优惠 ¥{{ totalDiscount.toFixed(2) }}
              <span v-if="memberDiscount > 0">（会员优惠 ¥{{ memberDiscount.toFixed(2) }}</span>
              <span v-if="discountAmount > 0">{{ memberDiscount > 0 ? '，' : '（' }}券优惠 ¥{{ discountAmount.toFixed(2) }}</span>
              <span v-if="totalDiscount > 0">）</span>
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

      <el-dialog
        v-model="couponDialogVisible"
        title="选择优惠券"
        width="600px"
        destroy-on-close
        @open="loadCoupons"
      >
        <div class="coupon-select-list">
          <div class="coupon-list-section">
            <div class="section-title">
              <span>可用优惠券 ({{ availableCoupons.length }})</span>
            </div>
            <div
              v-for="coupon in availableCoupons"
              :key="coupon.id"
              :class="['coupon-select-item', { 'selected': selectedCoupon?.id === coupon.id }]"
              @click="selectCoupon(coupon)"
            >
              <div class="coupon-select-left">
                <span class="coupon-select-amount">¥{{ coupon.coupon.discount_amount }}</span>
                <span class="coupon-select-threshold">满{{ coupon.coupon.threshold_amount }}可用</span>
              </div>
              <div class="coupon-select-right">
                <div class="coupon-select-name">{{ coupon.coupon.name }}</div>
                <div class="coupon-select-valid">
                  有效期：{{ formatDate(coupon.coupon.valid_from) }} - {{ formatDate(coupon.coupon.valid_to) }}
                </div>
                <div v-if="coupon.coupon.applicable_categories" class="coupon-select-cats">
                  适用：{{ coupon.coupon.applicable_categories }}
                </div>
              </div>
              <el-radio :model-value="selectedCoupon?.id === coupon.id" class="coupon-select-radio" />
            </div>
            <el-empty v-if="availableCoupons.length === 0" description="暂无可用优惠券" :image-size="80" />
          </div>

          <div v-if="unavailableCoupons.length > 0" class="coupon-list-section">
            <div class="section-title">
              <span>不可用优惠券 ({{ unavailableCoupons.length }})</span>
            </div>
            <div
              v-for="coupon in unavailableCoupons"
              :key="coupon.id"
              class="coupon-select-item unavailable"
            >
              <div class="coupon-select-left">
                <span class="coupon-select-amount">¥{{ coupon.coupon.discount_amount }}</span>
                <span class="coupon-select-threshold">满{{ coupon.coupon.threshold_amount }}可用</span>
              </div>
              <div class="coupon-select-right">
                <div class="coupon-select-name">{{ coupon.coupon.name }}</div>
                <div class="coupon-select-valid">
                  有效期：{{ formatDate(coupon.coupon.valid_from) }} - {{ formatDate(coupon.coupon.valid_to) }}
                </div>
                <div class="unavailable-reason">
                  <el-tag size="small" type="info">{{ coupon.unavailable_reason }}</el-tag>
                </div>
              </div>
            </div>
          </div>
        </div>

        <template #footer>
          <el-button @click="couponDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmCouponSelection">确定</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useUserStore } from '@/stores/user'
import { api } from '@/api'
import type { UserCoupon, OrderCreateWithCoupon, UserMemberLevelInfo } from '@/types'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'

const router = useRouter()
const cartStore = useCartStore()
const userStore = useUserStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const submitting = ref(false)
const defaultCover = 'https://via.placeholder.com/120x160/6366f1/ffffff?text=Book'
const memberLevelInfo = ref<UserMemberLevelInfo | null>(null)

const couponDialogVisible = ref(false)
const couponsLoading = ref(false)
const availableCoupons = ref<UserCoupon[]>([])
const unavailableCoupons = ref<UserCoupon[]>([])
const selectedCoupon = ref<UserCoupon | null>(null)
const tempSelectedCoupon = ref<UserCoupon | null>(null)

const originalPrice = computed(() => {
  return cartStore.selectedPrice
})

const memberDiscount = computed(() => {
  if (!memberLevelInfo.value?.current_level || memberLevelInfo.value.current_level.discount_rate >= 1) {
    return 0
  }
  const discountRate = memberLevelInfo.value.current_level.discount_rate
  return cartStore.selectedPrice * (1 - discountRate)
})

const discountAmount = computed(() => {
  return selectedCoupon.value ? selectedCoupon.value.coupon.discount_amount : 0
})

const totalDiscount = computed(() => {
  return memberDiscount.value + discountAmount.value
})

const finalPrice = computed(() => {
  const priceAfterMember = cartStore.selectedPrice - memberDiscount.value
  const price = priceAfterMember - discountAmount.value
  return price > 0 ? price : 0
})

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
    await Promise.all([
      cartStore.fetchCart(),
      fetchMemberLevel()
    ])
    if (selectedItems.value.length === 0) {
      ElMessage.warning('请先选择要结算的商品')
      router.push('/cart')
    }
  } finally {
    loading.value = false
  }
}

async function fetchMemberLevel() {
  try {
    memberLevelInfo.value = await api.getMyMemberLevel()
  } catch (error) {
    console.error('获取会员等级信息失败:', error)
    memberLevelInfo.value = null
  }
}

function handleImageError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultCover
}

async function loadCoupons() {
  if (selectedItems.value.length === 0) return

  couponsLoading.value = true
  try {
    const cartItemIds = selectedItems.value.map(item => item.id)
    const response = await api.validateCouponsForOrder(cartItemIds)
    availableCoupons.value = response.available
    unavailableCoupons.value = response.unavailable
  } catch (error) {
    console.error('加载优惠券失败:', error)
  } finally {
    couponsLoading.value = false
  }
}

function openCouponDialog() {
  tempSelectedCoupon.value = selectedCoupon.value
  couponDialogVisible.value = true
}

function selectCoupon(coupon: UserCoupon) {
  tempSelectedCoupon.value = coupon
}

function clearCoupon() {
  selectedCoupon.value = null
  ElMessage.success('已取消使用优惠券')
}

function confirmCouponSelection() {
  selectedCoupon.value = tempSelectedCoupon.value
  couponDialogVisible.value = false
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
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

  let confirmMessage = '确认提交订单吗？\n'
  confirmMessage += `商品原价：¥${originalPrice.value.toFixed(2)}\n`
  if (memberDiscount.value > 0) {
    confirmMessage += `会员优惠：-¥${memberDiscount.value.toFixed(2)}\n`
  }
  if (discountAmount.value > 0) {
    confirmMessage += `优惠券优惠：-¥${discountAmount.value.toFixed(2)}\n`
  }
  if (totalDiscount.value > 0) {
    confirmMessage += `已优惠：¥${totalDiscount.value.toFixed(2)}\n`
  }
  confirmMessage += `应付金额：¥${finalPrice.value.toFixed(2)}`

  try {
    await ElMessageBox.confirm(confirmMessage, '提交订单', {
      confirmButtonText: '确认提交',
      cancelButtonText: '再想想',
      type: 'warning'
    })
  } catch {
    return
  }

  submitting.value = true
  try {
    const cartItemIds = selectedItems.value.map(item => item.id)
    const orderData: OrderCreateWithCoupon = {
      ...formData.value,
      cart_item_ids: cartItemIds
    }

    if (selectedCoupon.value) {
      orderData.user_coupon_id = selectedCoupon.value.id
    }

    const response = await api.createOrder(orderData)

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

.coupon-section {
  padding: 16px 0;
  border-top: 1px dashed var(--border-color);
}

.coupon-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.coupon-title {
  font-size: 14px;
  color: var(--text-secondary);
}

.selected-coupon-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: #fff;
}

.coupon-badge {
  flex-shrink: 0;
}

.coupon-badge-amount {
  font-size: 18px;
  font-weight: 700;
}

.coupon-badge-info {
  flex: 1;
  min-width: 0;
}

.coupon-badge-name {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 2px;
}

.coupon-badge-desc {
  font-size: 12px;
  opacity: 0.9;
}

.selected-coupon-info .el-button {
  color: rgba(255, 255, 255, 0.9) !important;
}

.discount-info {
  text-align: right;
  font-size: 13px;
  color: var(--danger-color);
  margin-bottom: 12px;
}

.coupon-select-list {
  max-height: 500px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.coupon-list-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.coupon-select-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 2px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.coupon-select-item:hover {
  border-color: var(--primary-color);
}

.coupon-select-item.selected {
  border-color: var(--primary-color);
  background: rgba(99, 102, 241, 0.05);
}

.coupon-select-item.unavailable {
  opacity: 0.6;
  cursor: not-allowed;
}

.coupon-select-left {
  width: 100px;
  text-align: center;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: #fff;
  flex-shrink: 0;
}

.coupon-select-item.unavailable .coupon-select-left {
  background: linear-gradient(135deg, #e0e0e0 0%, #bdbdbd 100%);
}

.coupon-select-amount {
  display: block;
  font-size: 24px;
  font-weight: 700;
  line-height: 1.2;
}

.coupon-select-threshold {
  display: block;
  font-size: 11px;
  opacity: 0.9;
  margin-top: 4px;
}

.coupon-select-right {
  flex: 1;
  min-width: 0;
}

.coupon-select-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.coupon-select-valid {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.coupon-select-cats {
  font-size: 12px;
  color: var(--text-muted);
}

.unavailable-reason {
  margin-top: 6px;
}

.coupon-select-radio {
  flex-shrink: 0;
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

.original-price {
  color: var(--text-muted);
  text-decoration: line-through;
  margin-right: 8px;
}

.member-price-tag {
  font-weight: 600;
  color: var(--warning-color);
}

.item-subtotal {
  flex-shrink: 0;
  text-align: right;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.original-subtotal {
  font-size: 12px;
  color: var(--text-muted);
  text-decoration: line-through;
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
</style>
