<template>
  <div class="publisher-detail-page" v-loading="loading">
    <template v-if="publisher">
      <div class="publisher-header">
        <el-button text @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
      </div>

      <div class="publisher-profile" v-if="publisher.is_active">
        <div class="publisher-logo-section">
          <div class="publisher-logo-wrapper">
            <img
              :src="publisher.logo || defaultLogo"
              :alt="publisher.name"
              class="publisher-logo"
              @error="handleLogoError"
            >
          </div>
        </div>

        <div class="publisher-info-section">
          <h1 class="publisher-name">{{ publisher.name }}</h1>
          
          <div class="publisher-meta">
            <div class="meta-item" v-if="publisher.location">
              <el-icon><Location /></el-icon>
              <span>{{ publisher.location }}</span>
            </div>
            <div class="meta-item" v-if="publisher.founded_year">
              <el-icon><Calendar /></el-icon>
              <span>{{ publisher.founded_year }} 年成立</span>
            </div>
            <div class="meta-item" v-if="publisher.website">
              <el-icon><Link /></el-icon>
              <a :href="publisher.website" target="_blank" class="website-link">
                {{ publisher.website }}
              </a>
            </div>
            <div class="meta-item">
              <el-icon><Collection /></el-icon>
              <span>共 {{ publisher.book_count }} 部作品</span>
            </div>
          </div>

          <div class="publisher-description" v-if="publisher.description">
            <h3>出版社简介</h3>
            <p>{{ publisher.description }}</p>
          </div>

          <div class="publisher-stats" v-if="publisher.category_distribution && publisher.category_distribution.length > 0">
            <h3>分类占比</h3>
            <div class="category-tags">
              <el-tag
                v-for="item in publisher.category_distribution"
                :key="item.category"
                size="large"
                type="info"
                effect="light"
              >
                {{ item.category }} ({{ item.count }}本)
              </el-tag>
            </div>
          </div>
        </div>
      </div>

      <el-empty
        v-else
        description="该出版社已暂停展示"
        :image-size="100"
      >
        <template #description>
          <p class="disabled-text">该出版社已暂停展示</p>
        </template>
      </el-empty>

      <div class="publisher-recent-section" v-if="publisher.is_active && publisher.recent_books && publisher.recent_books.length > 0">
        <h2>最近上架</h2>
        <div class="books-list">
          <el-row :gutter="24">
            <el-col v-for="book in publisher.recent_books" :key="book.id" :xs="12" :sm="8" :md="6" :lg="4">
              <div class="book-card" @click="router.push(`/books/${book.id}`)">
                <div class="book-cover">
                  <img
                    :src="book.cover_image || defaultBookCover"
                    :alt="book.title"
                    @error="handleBookCoverError"
                  >
                </div>
                <div class="book-info">
                  <h4 class="book-title" :title="book.title">{{ book.title }}</h4>
                  <p class="book-category" v-if="book.category">
                    <el-tag size="small" type="info">{{ book.category }}</el-tag>
                  </p>
                  <div class="book-price">
                    <span>¥{{ book.price.toFixed(2) }}</span>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>

      <div class="publisher-books-section" v-if="publisher.is_active && filteredBooks && filteredBooks.length > 0">
        <h2>旗下图书</h2>
        <div class="books-list">
          <el-row :gutter="24">
            <el-col v-for="book in filteredBooks" :key="book.id" :xs="12" :sm="8" :md="6" :lg="4">
              <div class="book-card" @click="router.push(`/books/${book.id}`)">
                <div class="book-cover">
                  <img
                    :src="book.cover_image || defaultBookCover"
                    :alt="book.title"
                    @error="handleBookCoverError"
                  >
                </div>
                <div class="book-info">
                  <h4 class="book-title" :title="book.title">{{ book.title }}</h4>
                  <p class="book-category" v-if="book.category">
                    <el-tag size="small" type="info">{{ book.category }}</el-tag>
                  </p>
                  <div class="book-price">
                    <span>¥{{ book.price.toFixed(2) }}</span>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>

      <el-empty v-if="publisher.is_active && (!filteredBooks || filteredBooks.length === 0) && (!publisher.recent_books || publisher.recent_books.length === 0)" description="暂无相关图书" />
    </template>

    <el-empty v-else-if="!loading" description="出版社不存在" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '@/api'
import type { PublisherDetail } from '@/types'
import { ArrowLeft, Location, Calendar, Link, Collection } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const publisher = ref<PublisherDetail | null>(null)
const defaultLogo = 'https://via.placeholder.com/200x200/f59e0b/ffffff?text=Publisher'
const defaultBookCover = 'https://via.placeholder.com/150x200/6366f1/ffffff?text=Book'

const filteredBooks = computed(() => {
  if (!publisher.value || !publisher.value.books) return []
  const recentBookIds = new Set((publisher.value.recent_books || []).map(b => b.id))
  return publisher.value.books.filter(book => !recentBookIds.has(book.id))
})

onMounted(async () => {
  const publisherId = Number(route.params.id)
  if (!publisherId) {
    router.push('/')
    return
  }
  await fetchPublisher(publisherId)
})

async function fetchPublisher(publisherId: number) {
  loading.value = true
  try {
    publisher.value = await api.getPublisher(publisherId)
  } catch (error) {
    console.error('获取出版社详情失败:', error)
  } finally {
    loading.value = false
  }
}

function handleLogoError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultLogo
}

function handleBookCoverError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultBookCover
}
</script>

<style scoped>
.publisher-detail-page {
  max-width: 1200px;
  margin: 0 auto;
}

.publisher-header {
  margin-bottom: 24px;
}

.publisher-profile {
  display: flex;
  gap: 48px;
  padding: 40px;
  background: var(--bg-secondary);
  border-radius: 20px;
  box-shadow: var(--shadow);
  margin-bottom: 32px;
}

.publisher-logo-section {
  flex-shrink: 0;
}

.publisher-logo-wrapper {
  width: 200px;
  height: 200px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.publisher-logo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.publisher-info-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.publisher-name {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.publisher-meta {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary);
  font-size: 14px;
}

.meta-item .el-icon {
  color: var(--primary-color);
}

.website-link {
  color: var(--primary-color);
  text-decoration: none;
  transition: color 0.2s;
}

.website-link:hover {
  color: var(--primary-dark);
  text-decoration: underline;
}

.publisher-description,
.publisher-stats {
  margin-top: 8px;
}

.publisher-description h3,
.publisher-stats h3,
.publisher-recent-section h2,
.publisher-books-section h2 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.publisher-description p {
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-secondary);
  margin: 0;
}

.category-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.publisher-recent-section,
.publisher-books-section {
  padding: 32px;
  background: var(--bg-secondary);
  border-radius: 20px;
  box-shadow: var(--shadow);
  margin-bottom: 24px;
}

.publisher-recent-section h2,
.publisher-books-section h2 {
  font-size: 24px;
  margin: 0 0 24px 0;
}

.books-list {
  min-height: 200px;
}

.book-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  margin-bottom: 24px;
}

.book-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow);
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
}

.book-info {
  padding: 12px;
}

.book-title {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 6px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-primary);
}

.book-category {
  margin: 0 0 8px 0;
}

.book-price {
  color: var(--secondary-color);
  font-weight: 700;
  font-size: 16px;
}

.disabled-text {
  color: var(--text-muted);
  font-size: 16px;
  margin: 0;
}

@media (max-width: 768px) {
  .publisher-profile {
    flex-direction: column;
    gap: 24px;
    padding: 24px;
  }

  .publisher-logo-section {
    display: flex;
    justify-content: center;
  }

  .publisher-logo-wrapper {
    width: 150px;
    height: 150px;
  }

  .publisher-name {
    font-size: 24px;
    text-align: center;
  }

  .publisher-meta {
    justify-content: center;
  }
}
</style>
