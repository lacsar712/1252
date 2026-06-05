<template>
  <div class="author-detail-page" v-loading="loading">
    <template v-if="author">
      <div class="author-header">
        <el-button text @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回作者列表
        </el-button>
      </div>

      <div class="author-profile">
        <div class="author-avatar-section">
          <div class="author-avatar-wrapper">
            <img
              :src="author.avatar || defaultAvatar"
              :alt="author.name"
              class="author-avatar"
              @error="handleAvatarError"
            >
          </div>
        </div>

        <div class="author-info-section">
          <h1 class="author-name">{{ author.name }}</h1>
          
          <div class="author-meta">
            <div class="meta-item" v-if="author.country">
              <el-icon><Location /></el-icon>
              <span>{{ author.country }}</span>
            </div>
            <div class="meta-item" v-if="author.birth_year">
              <el-icon><Calendar /></el-icon>
              <span>{{ author.birth_year }} 年出生</span>
            </div>
            <div class="meta-item">
              <el-icon><Collection /></el-icon>
              <span>共 {{ author.book_count }} 部作品</span>
            </div>
          </div>

          <div class="author-bio" v-if="author.bio">
            <h3>作者简介</h3>
            <p>{{ author.bio }}</p>
          </div>

          <div class="author-masterpieces" v-if="author.masterpieces">
            <h3>代表作品</h3>
            <p>{{ author.masterpieces }}</p>
          </div>

          <div class="author-stats" v-if="author.category_distribution && author.category_distribution.length > 0">
            <h3>分类分布</h3>
            <div class="category-tags">
              <el-tag
                v-for="item in author.category_distribution"
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

      <div class="author-books-section" v-if="author.books && author.books.length > 0">
        <h2>相关作品</h2>
        <div class="books-list">
          <el-row :gutter="24">
            <el-col v-for="book in author.books" :key="book.id" :xs="12" :sm="8" :md="6" :lg="4">
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

      <el-empty v-if="(!author.books || author.books.length === 0)" description="暂无相关作品" />
    </template>

    <el-empty v-else-if="!loading" description="作者不存在" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '@/api'
import type { AuthorDetail } from '@/types'
import { ArrowLeft, Location, Calendar, Collection } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const author = ref<AuthorDetail | null>(null)
const defaultAvatar = 'https://via.placeholder.com/200x200/8b5cf6/ffffff?text=Author'
const defaultBookCover = 'https://via.placeholder.com/150x200/6366f1/ffffff?text=Book'

onMounted(async () => {
  const authorId = Number(route.params.id)
  if (!authorId) {
    router.push('/authors')
    return
  }
  await fetchAuthor(authorId)
})

async function fetchAuthor(authorId: number) {
  loading.value = true
  try {
    author.value = await api.getAuthor(authorId)
  } catch (error) {
    console.error('获取作者详情失败:', error)
  } finally {
    loading.value = false
  }
}

function handleAvatarError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultAvatar
}

function handleBookCoverError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultBookCover
}
</script>

<style scoped>
.author-detail-page {
  max-width: 1200px;
  margin: 0 auto;
}

.author-header {
  margin-bottom: 24px;
}

.author-profile {
  display: flex;
  gap: 48px;
  padding: 40px;
  background: var(--bg-secondary);
  border-radius: 20px;
  box-shadow: var(--shadow);
  margin-bottom: 32px;
}

.author-avatar-section {
  flex-shrink: 0;
}

.author-avatar-wrapper {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.author-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.author-info-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.author-name {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.author-meta {
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

.author-bio,
.author-masterpieces,
.author-stats {
  margin-top: 8px;
}

.author-bio h3,
.author-masterpieces h3,
.author-stats h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.author-bio p,
.author-masterpieces p {
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

.author-books-section {
  padding: 32px;
  background: var(--bg-secondary);
  border-radius: 20px;
  box-shadow: var(--shadow);
}

.author-books-section h2 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
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

@media (max-width: 768px) {
  .author-profile {
    flex-direction: column;
    gap: 24px;
    padding: 24px;
  }

  .author-avatar-section {
    display: flex;
    justify-content: center;
  }

  .author-avatar-wrapper {
    width: 150px;
    height: 150px;
  }

  .author-name {
    font-size: 24px;
    text-align: center;
  }

  .author-meta {
    justify-content: center;
  }
}
</style>
