<template>
  <div class="book-detail-page" v-loading="loading">
    <template v-if="book">
      <div class="book-header">
        <el-button text @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
      </div>
      
      <div class="book-content">
        <div class="book-cover">
          <img :src="book.cover_image || defaultCover" :alt="book.title" @error="handleImageError">
        </div>
        
        <div class="book-info">
          <div class="book-category" v-if="book.category">
            <el-tag type="info">{{ book.category }}</el-tag>
          </div>
          
          <h1 class="book-title">{{ book.title }}</h1>
          
          <div class="book-meta">
            <div class="meta-item">
              <el-icon><User /></el-icon>
              <span>作者：</span>
              <template v-if="book.authors && book.authors.length > 0">
                <span class="authors-list">
                  <router-link
                    v-for="(author, index) in book.authors"
                    :key="author.id"
                    :to="`/authors/${author.id}`"
                    class="author-link"
                  >
                    {{ author.name }}
                    <span v-if="index < book.authors.length - 1">、</span>
                  </router-link>
                </span>
              </template>
              <span v-else class="no-author">暂无作者信息</span>
            </div>
            <div class="meta-item" v-if="book.publisher">
              <el-icon><OfficeBuilding /></el-icon>
              <span>出版社：</span>
              <template v-if="book.publisher_info && book.publisher_info.is_active">
                <router-link :to="`/publishers/${book.publisher_info.id}`" class="publisher-link">
                  {{ book.publisher }}
                </router-link>
              </template>
              <span v-else>{{ book.publisher }}</span>
            </div>
            <div class="meta-item" v-if="book.isbn">
              <el-icon><Document /></el-icon>
              <span>ISBN：{{ book.isbn }}</span>
            </div>
          </div>
          
          <div class="book-price-section">
            <span class="price-label">价格</span>
            <div class="price-info">
              <span class="price-value">¥{{ book.price.toFixed(2)}}</span>
              <div v-if="memberPriceInfo && userStore.isLoggedIn" class="member-price-box">
                <div class="member-price-row">
                  <span class="member-label">会员价</span>
                  <span class="member-price">¥{{ memberPriceInfo.price_info.member_price.toFixed(2) }}</span>
                </div>
                <el-tag
                  v-if="memberPriceInfo.price_info.level_name"
                  size="small"
                  type="warning"
                  effect="light"
                  class="level-tag"
                >
                  {{ memberPriceInfo.price_info.level_name }}
                  {{ (memberPriceInfo.price_info.discount_rate * 10).toFixed(1) }}折
                </el-tag>
              </div>
            </div>
          </div>
          
          <div class="book-stock-section">
            <span class="stock-label">库存</span>
            <span class="stock-value" :class="{ 'out-of-stock': book.stock === 0 }">
              {{ book.stock > 0 ? `${book.stock} 本` : '暂时缺货' }}
            </span>
          </div>
          
          <div class="book-action-section" v-if="book">
            <div class="quantity-section">
              <span class="quantity-label">数量</span>
              <el-input-number
                v-model="quantity"
                :min="1"
                :max="book.stock"
                size="large"
                :disabled="book.stock === 0"
              />
            </div>
            
            <div class="action-buttons">
              <el-button
                type="primary"
                size="large"
                :disabled="book.stock === 0"
                @click="handleAddToCart"
              >
                <el-icon><ShoppingCart /></el-icon>
                加入购物车
              </el-button>
              <el-button
                size="large"
                :disabled="book.stock === 0"
                @click="handleBuyNow"
              >
                立即购买
              </el-button>
            </div>
          </div>
          
        </div>
      </div>
      
      <div class="book-description" v-if="book.description">
        <h2>图书简介</h2>
        <p>{{ book.description }}</p>
      </div>
    </template>
    
    <el-empty v-else-if="!loading" description="图书不存在" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '@/api'
import type { Book, BookMemberPriceResponse } from '@/types'
import { useCartStore } from '@/stores/cart'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { ArrowLeft, User, OfficeBuilding, Document, ShoppingCart } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const cartStore = useCartStore()
const userStore = useUserStore()

const loading = ref(false)
const book = ref<Book | null>(null)
const memberPriceInfo = ref<BookMemberPriceResponse | null>(null)
const quantity = ref(1)
const defaultCover = 'https://via.placeholder.com/300x400/6366f1/ffffff?text=Book'

onMounted(async () => {
  const bookId = Number(route.params.id)
  if (!bookId) {
    router.push('/books')
    return
  }
  
  await fetchBookData(bookId)
})

watch(
  () => route.params.id,
  async () => {
    const bookId = Number(route.params.id)
    if (bookId) {
      quantity.value = 1
      await fetchBookData(bookId)
    }
  }
)

async function fetchBookData(bookId: number) {
  loading.value = true
  try {
    const bookData = await api.getBook(bookId)
    book.value = bookData
    
    if (userStore.isLoggedIn) {
      try {
        memberPriceInfo.value = await api.getBookMemberPrice(bookId)
      } catch (e) {
        memberPriceInfo.value = null
      }
    } else {
      memberPriceInfo.value = null
    }
  } catch (error) {
    console.error('获取图书详情失败:', error)
  } finally {
    loading.value = false
  }
}

function handleImageError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultCover
}

async function handleAddToCart() {
  if (!book.value) return
  
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后加入购物车')
    router.push({ name: 'Login', query: { redirect: `/books/${book.value.id}` } })
    return
  }
  
  if (book.value.stock <= 0) {
    ElMessage.error('该图书已缺货')
    return
  }
  
  if (quantity.value > book.value.stock) {
    ElMessage.warning(`库存不足，当前库存 ${book.value.stock} 本`)
    return
  }
  
  const success = await cartStore.addToCart(book.value.id, quantity.value)
  if (success) {
    await cartStore.fetchCartCount()
  }
}

function handleBuyNow() {
  if (!book.value) return
  
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后购买')
    router.push({ name: 'Login', query: { redirect: `/books/${book.value.id}` } })
    return
  }
  
  if (book.value.stock <= 0) {
    ElMessage.error('该图书已缺货')
    return
  }
  
  ElMessage.info('购买功能开发中...')
}
</script>

<style scoped>
.book-detail-page {
  max-width: 1000px;
  margin: 0 auto;
}

.book-header {
  margin-bottom: 24px;
}

.book-content {
  display: flex;
  gap: 48px;
  padding: 32px;
  background: var(--bg-secondary);
  border-radius: 16px;
  box-shadow: var(--shadow);
}

.book-cover {
  flex-shrink: 0;
  width: 280px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}

.book-cover img {
  width: 100%;
  height: auto;
  display: block;
}

.book-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.book-category {
  margin-bottom: 8px;
}

.book-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.3;
}

.book-meta {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 14px;
}

.meta-item .el-icon {
  color: var(--primary-color);
}

.authors-list {
  display: inline;
}

.author-link {
  color: var(--primary-color);
  text-decoration: none;
  transition: color 0.2s;
}

.author-link:hover {
  color: var(--primary-dark);
  text-decoration: underline;
}

.no-author {
  color: var(--text-muted);
  font-style: italic;
}

.publisher-link {
  color: var(--primary-color);
  text-decoration: none;
  transition: color 0.2s;
}

.publisher-link:hover {
  color: var(--primary-dark);
  text-decoration: underline;
}

.book-price-section,
.book-stock-section {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-top: 8px;
}

.price-label,
.stock-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.price-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--secondary-color);
}

.price-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.member-price-box {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 8px;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.member-price-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.member-label {
  font-size: 13px;
  color: #92400e;
  font-weight: 500;
}

.member-price {
  font-size: 20px;
  font-weight: 700;
  color: #b45309;
}

.level-tag {
  margin-left: auto;
}

.stock-value {
  font-size: 16px;
  font-weight: 500;
  color: var(--success-color);
}

.stock-value.out-of-stock {
  color: var(--danger-color);
}

.book-action-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.quantity-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.quantity-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.action-buttons .el-button {
  padding: 12px 32px;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
}

.book-description {
  margin-top: 32px;
  padding: 32px;
  background: var(--bg-secondary);
  border-radius: 16px;
  box-shadow: var(--shadow);
}

.book-description h2 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text-primary);
}

.book-description p {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .book-content {
    flex-direction: column;
    gap: 24px;
  }
  
  .book-cover {
    width: 100%;
    max-width: 280px;
    margin: 0 auto;
  }
}
</style>
