<template>
  <div class="booklist-detail-page" v-loading="loading">
    <div v-if="bookList" class="detail-container">
      <div class="back-button">
        <el-button @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回书单列表
        </el-button>
      </div>

      <div class="booklist-header">
        <div class="booklist-cover-wrapper">
          <img
            :src="bookList.cover_image || defaultCover"
            :alt="bookList.title"
            class="booklist-cover"
            @error="handleCoverError"
          >
        </div>
        <div class="booklist-info">
          <div class="booklist-meta">
            <el-tag v-if="bookList.category" type="success" size="large">
              {{ bookList.category }}
            </el-tag>
            <span class="booklist-date">{{ formatDate(bookList.created_at) }}</span>
          </div>
          <h1 class="booklist-title">{{ bookList.title }}</h1>
          <p v-if="bookList.description" class="booklist-description">
            {{ bookList.description }}
          </p>
          <div class="booklist-stats">
            <div class="stat-item">
              <span class="stat-value">{{ bookList.book_count }}</span>
              <span class="stat-label">本图书</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ bookList.categories.length }}</span>
              <span class="stat-label">个分类</span>
            </div>
          </div>
          <div v-if="bookList.categories.length > 0" class="related-categories">
            <span class="label">关联分类：</span>
            <el-tag
              v-for="cat in bookList.categories"
              :key="cat"
              size="small"
              type="info"
              class="category-tag"
            >
              {{ cat }}
            </el-tag>
          </div>
        </div>
      </div>

      <div class="books-section">
        <h2 class="section-title">
          书单图书
          <span class="book-count">({{ bookList.books.length }} 本)</span>
        </h2>

        <el-empty
          v-if="bookList.books.length === 0"
          description="这个书单还没有添加图书"
        />

        <div v-else class="books-list">
          <div
            v-for="(book, index) in bookList.books"
            :key="book.id"
            class="book-item"
          >
            <div class="book-rank">{{ index + 1 }}</div>
            <div class="book-cover-wrapper" @click="router.push(`/books/${book.id}`)">
              <img
                :src="book.cover_image || defaultBookCover"
                :alt="book.title"
                class="book-cover"
                @error="handleBookCoverError"
              >
            </div>
            <div class="book-info">
              <h3
                class="book-title"
                @click="router.push(`/books/${book.id}`)"
              >
                {{ book.title }}
              </h3>
              <p class="book-author">{{ book.author }}</p>
              <div v-if="book.recommendation" class="book-recommendation">
                <el-icon><ChatDotRound /></el-icon>
                <span>{{ book.recommendation }}</span>
              </div>
              <div class="book-footer">
                <span class="book-price">¥{{ book.price.toFixed(2) }}</span>
                <el-button
                  type="primary"
                  size="small"
                  @click="addToCart(book.id)"
                >
                  加入购物车
                </el-button>
                <el-button
                  size="small"
                  @click="router.push(`/books/${book.id}`)"
                >
                  查看详情
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api'
import type { BookListDetail } from '@/types'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ChatDotRound } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const bookList = ref<BookListDetail | null>(null)
const defaultCover = 'https://via.placeholder.com/300x420/10b981/ffffff?text=BookList'
const defaultBookCover = 'https://via.placeholder.com/120x168/6366f1/ffffff?text=Book'

onMounted(() => {
  const id = Number(route.params.id)
  if (id) {
    fetchBookListDetail(id)
  }
})

async function fetchBookListDetail(id: number) {
  loading.value = true
  try {
    bookList.value = await api.getBookList(id)
  } catch (error) {
    console.error('获取书单详情失败:', error)
    ElMessage.error('获取书单详情失败')
  } finally {
    loading.value = false
  }
}

async function addToCart(bookId: number) {
  try {
    await api.addToCart({ book_id: bookId, quantity: 1 })
    ElMessage.success('已加入购物车')
  } catch (error) {
    console.error('加入购物车失败:', error)
  }
}

function handleCoverError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultCover
}

function handleBookCoverError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultBookCover
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style scoped>
.booklist-detail-page {
  min-height: 600px;
}

.detail-container {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.back-button {
  margin-bottom: 8px;
}

.booklist-header {
  display: flex;
  gap: 32px;
  padding: 32px;
  background: var(--bg-secondary);
  border-radius: 16px;
  box-shadow: var(--shadow);
}

.booklist-cover-wrapper {
  flex-shrink: 0;
  width: 300px;
  height: 420px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.booklist-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.booklist-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.booklist-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.booklist-date {
  font-size: 14px;
  color: var(--text-secondary);
}

.booklist-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.booklist-description {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-secondary);
  margin: 0;
}

.booklist-stats {
  display: flex;
  gap: 32px;
  padding: 16px 0;
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--primary-color);
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.related-categories {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.related-categories .label {
  font-size: 14px;
  color: var(--text-secondary);
}

.category-tag {
  margin: 0;
}

.books-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-title {
  font-size: 22px;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
}

.book-count {
  font-size: 16px;
  color: var(--text-secondary);
  font-weight: normal;
  margin-left: 8px;
}

.books-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.book-item {
  display: flex;
  gap: 20px;
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: 12px;
  box-shadow: var(--shadow);
  transition: box-shadow 0.2s, transform 0.2s;
}

.book-item:hover {
  box-shadow: var(--shadow-lg);
  transform: translateX(4px);
}

.book-rank {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 700;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 4px;
}

.book-cover-wrapper {
  flex-shrink: 0;
  width: 120px;
  height: 168px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: var(--shadow);
}

.book-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.book-cover-wrapper:hover .book-cover {
  transform: scale(1.05);
}

.book-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.book-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
  cursor: pointer;
  transition: color 0.2s;
}

.book-title:hover {
  color: var(--primary-color);
}

.book-author {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.book-recommendation {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 8px;
  font-size: 14px;
  color: #92400e;
  line-height: 1.6;
}

.book-recommendation .el-icon {
  flex-shrink: 0;
  margin-top: 2px;
  color: #d97706;
}

.book-footer {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: auto;
  padding-top: 8px;
}

.book-price {
  font-size: 20px;
  font-weight: 700;
  color: var(--secondary-color);
}

@media (max-width: 768px) {
  .booklist-header {
    flex-direction: column;
    padding: 20px;
    gap: 20px;
  }

  .booklist-cover-wrapper {
    width: 100%;
    height: 300px;
  }

  .booklist-title {
    font-size: 24px;
  }

  .booklist-stats {
    gap: 20px;
  }

  .stat-value {
    font-size: 24px;
  }

  .book-item {
    flex-direction: column;
    padding: 16px;
  }

  .book-rank {
    position: absolute;
    width: 28px;
    height: 28px;
    font-size: 14px;
  }

  .book-cover-wrapper {
    width: 100px;
    height: 140px;
  }

  .book-title {
    font-size: 16px;
  }

  .book-footer {
    flex-wrap: wrap;
  }

  .book-price {
    font-size: 18px;
  }
}
</style>
