<template>
  <div class="books-page">
    <!-- 搜索和筛选 -->
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索书名、作者或出版社..."
        size="large"
        clearable
        @keyup.enter="handleSearch"
        class="search-input"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-select
        v-model="selectedCategory"
        placeholder="选择分类"
        size="large"
        clearable
        @change="handleSearch"
        class="category-select"
      >
        <el-option
          v-for="cat in categories"
          :key="cat"
          :label="cat"
          :value="cat"
        />
      </el-select>
      <el-select
        v-model="selectedTagId"
        placeholder="选择标签"
        size="large"
        clearable
        @change="handleSearch"
        class="tag-select"
      >
        <el-option
          v-for="tag in activeTags"
          :key="tag.id"
          :value="tag.id"
        >
          <el-tag
            :style="{ backgroundColor: tag.color || '#409eff', borderColor: tag.color || '#409eff' }"
            effect="dark"
            size="small"
          >
            {{ tag.name }}
          </el-tag>
        </el-option>
      </el-select>
      <el-button type="primary" size="large" @click="handleSearch">
        <el-icon><Search /></el-icon>
        搜索
      </el-button>
    </div>
    
    <!-- 结果统计 -->
    <div class="results-info">
      <span v-if="total > 0">共找到 <strong>{{ total }}</strong> 本图书</span>
      <span v-else-if="!loading">暂无图书</span>
    </div>
    
    <!-- 图书列表 -->
    <div class="book-list" v-loading="loading">
      <el-row :gutter="24">
        <el-col v-for="book in books" :key="book.id" :xs="12" :sm="8" :md="6" :lg="4">
          <div class="book-card">
            <div class="book-cover" @click="router.push(`/books/${book.id}`)">
              <img :src="book.cover_image || defaultCover" :alt="book.title" @error="handleImageError">
              <div class="book-overlay">
                <el-button type="primary" circle>
                  <el-icon><View /></el-icon>
                </el-button>
              </div>
            </div>
            <div class="book-info">
              <h4 class="book-title" :title="book.title" @click="router.push(`/books/${book.id}`)">{{ book.title }}</h4>
              <p class="book-author" @click="router.push(`/books/${book.id}`)">
                <template v-if="book.authors && book.authors.length > 0">
                  {{ book.authors.map(a => a.name).join('、') }}
                </template>
                <template v-else-if="book.author">
                  {{ book.author }}
                </template>
                <span v-else class="no-author">暂无作者</span>
              </p>
              <p class="book-publisher" v-if="book.publisher" @click="router.push(`/books/${book.id}`)">{{ book.publisher }}</p>
              <div class="book-tags" v-if="book.tags && book.tags.length > 0" @click.stop>
                <el-tag
                  v-for="tag in book.tags.slice(0, 3)"
                  :key="tag.id"
                  :style="{ backgroundColor: tag.color || '#409eff', borderColor: tag.color || '#409eff' }"
                  effect="dark"
                  size="small"
                  class="book-tag"
                  @click.stop="handleTagClick(tag.id)"
                >
                  {{ tag.name }}
                </el-tag>
              </div>
              <div class="book-meta">
                <span class="book-price">¥{{ book.price.toFixed(2) }}</span>
                <span class="book-stock" :class="{ 'out-of-stock': book.stock === 0 }">
                  {{ book.stock > 0 ? `库存: ${book.stock}` : '缺货' }}
                </span>
              </div>
              <div class="book-actions">
                <el-button
                  type="primary"
                  size="small"
                  class="add-cart-btn"
                  :disabled="book.stock === 0"
                  @click.stop="handleAddToCart(book)"
                >
                  <el-icon><ShoppingCart /></el-icon>
                  {{ book.stock === 0 ? '缺货' : '加入购物车' }}
                </el-button>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
      
      <!-- 空状态 -->
      <el-empty v-if="!loading && books.length === 0" description="暂无图书数据" />
    </div>
    
    <!-- 分页 -->
    <div class="pagination" v-if="total > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 36, 48]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSearch"
        @current-change="handleSearch"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '@/api'
import type { Book, Tag } from '@/types'
import { useCartStore } from '@/stores/cart'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { Search, View, ShoppingCart } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const cartStore = useCartStore()
const userStore = useUserStore()

const loading = ref(false)
const books = ref<Book[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const searchQuery = ref('')
const selectedCategory = ref('')
const selectedTagId = ref<number | ''>('')
const categories = ref<string[]>([])
const activeTags = ref<Tag[]>([])
const defaultCover = 'https://via.placeholder.com/200x280/6366f1/ffffff?text=Book'

onMounted(async () => {
  const tagIdFromQuery = route.query.tag_id
  if (tagIdFromQuery && !isNaN(Number(tagIdFromQuery))) {
    selectedTagId.value = Number(tagIdFromQuery)
  }
  await Promise.all([fetchBooks(), fetchCategories(), fetchActiveTags()])
})

async function fetchBooks() {
  loading.value = true
  try {
    const response = await api.getBooks({
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value || undefined,
      category: selectedCategory.value || undefined,
      tag_id: selectedTagId.value || undefined
    })
    books.value = response.items
    total.value = response.total
  } catch (error) {
    console.error('获取图书列表失败:', error)
  } finally {
    loading.value = false
  }
}

async function fetchCategories() {
  try {
    categories.value = await api.getCategories()
  } catch (error) {
    console.error('获取分类失败:', error)
  }
}

async function fetchActiveTags() {
  try {
    activeTags.value = await api.getActiveTags()
  } catch (error) {
    console.error('获取标签失败:', error)
  }
}

function handleSearch() {
  currentPage.value = 1
  fetchBooks()
}

function handleTagClick(tagId: number) {
  selectedTagId.value = tagId
  selectedCategory.value = ''
  searchQuery.value = ''
  currentPage.value = 1
  fetchBooks()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function handleImageError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultCover
}

async function handleAddToCart(book: Book) {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后加入购物车')
    router.push({ name: 'Login', query: { redirect: `/books/${book.id}` } })
    return
  }
  
  if (book.stock <= 0) {
    ElMessage.error('该图书已缺货')
    return
  }
  
  const success = await cartStore.addToCart(book.id, 1)
  if (success) {
    await cartStore.fetchCartCount()
  }
}
</script>

<style scoped>
.books-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.search-bar {
  display: flex;
  gap: 16px;
  padding: 24px;
  background: var(--bg-secondary);
  border-radius: 16px;
  box-shadow: var(--shadow);
}

.search-input {
  flex: 1;
  max-width: 400px;
}

.category-select {
  width: 180px;
}

.tag-select {
  width: 180px;
}

.results-info {
  color: var(--text-secondary);
  font-size: 14px;
}

.results-info strong {
  color: var(--primary-color);
  font-weight: 600;
}

.book-list {
  min-height: 400px;
}

.book-card {
  background: var(--bg-secondary);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  margin-bottom: 24px;
}

.book-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.book-card:hover .book-overlay {
  opacity: 1;
}

.book-cover {
  position: relative;
  width: 100%;
  aspect-ratio: 3/4;
  overflow: hidden;
  background: #f1f5f9;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.book-card:hover .book-cover img {
  transform: scale(1.05);
}

.book-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.book-info {
  padding: 16px;
}

.book-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-author {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.book-author .no-author {
  color: var(--text-muted);
  font-style: italic;
}

.book-publisher {
  font-size: 11px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.book-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 8px;
}

.book-tag {
  cursor: pointer;
  transition: opacity 0.2s;
}

.book-tag:hover {
  opacity: 0.85;
}

.book-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.book-price {
  font-size: 16px;
  font-weight: 700;
  color: var(--secondary-color);
}

.book-stock {
  font-size: 11px;
  padding: 2px 8px;
  background: rgba(16, 185, 129, 0.1);
  color: var(--success-color);
  border-radius: 4px;
}

.book-stock.out-of-stock {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger-color);
}

.book-actions {
  margin-top: 8px;
}

.add-cart-btn {
  width: 100%;
}

.pagination {
  display: flex;
  justify-content: center;
  padding: 24px 0;
}
</style>
