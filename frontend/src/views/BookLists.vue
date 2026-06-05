<template>
  <div class="book-lists-page">
    <div class="page-header">
      <h1 class="page-title">主题书单</h1>
      <p class="page-subtitle">精选好书合集，发现更多精彩阅读</p>
    </div>

    <div class="filter-bar">
      <div class="category-filters">
        <el-tag
          v-for="cat in categories"
          :key="cat"
          :type="selectedCategory === cat ? 'primary' : 'info'"
          :effect="selectedCategory === cat ? 'dark' : 'plain'"
          class="category-tag"
          @click="selectCategory(cat)"
        >
          {{ cat }}
        </el-tag>
        <el-tag
          :type="selectedCategory === '' ? 'primary' : 'info'"
          :effect="selectedCategory === '' ? 'dark' : 'plain'"
          class="category-tag"
          @click="selectCategory('')"
        >
          全部
        </el-tag>
      </div>
    </div>

    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索书单标题或简介..."
        size="large"
        clearable
        @keyup.enter="handleSearch"
        class="search-input"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-button type="primary" size="large" @click="handleSearch">
        <el-icon><Search /></el-icon>
        搜索
      </el-button>
    </div>

    <div class="results-info">
      <span v-if="total > 0">共找到 <strong>{{ total }}</strong> 个书单</span>
      <span v-else-if="!loading">暂无书单</span>
    </div>

    <div class="book-list-grid" v-loading="loading">
      <el-row :gutter="24">
        <el-col v-for="list in bookLists" :key="list.id" :xs="12" :sm="8" :md="6" :lg="6">
          <div class="booklist-card" @click="router.push(`/book-lists/${list.id}`)">
            <div class="booklist-cover-wrapper">
              <img
                :src="list.cover_image || defaultCover"
                :alt="list.title"
                class="booklist-cover"
                @error="handleCoverError"
              >
              <div v-if="list.category" class="booklist-category-tag">
                {{ list.category }}
              </div>
              <div class="booklist-overlay">
                <el-button type="primary" circle>
                  <el-icon><View /></el-icon>
                </el-button>
              </div>
            </div>
            <div class="booklist-info">
              <h3 class="booklist-title">{{ list.title }}</h3>
              <p class="booklist-description" v-if="list.description">
                {{ list.description }}
              </p>
              <div class="booklist-footer">
                <span class="booklist-date">{{ formatDate(list.created_at) }}</span>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <el-empty v-if="!loading && bookLists.length === 0" description="暂无书单数据" />
    </div>

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
import { useRouter } from 'vue-router'
import { api } from '@/api'
import type { BookList } from '@/types'
import { Search, View } from '@element-plus/icons-vue'

const router = useRouter()

const loading = ref(false)
const bookLists = ref<BookList[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const searchQuery = ref('')
const selectedCategory = ref('')
const categories = ref<string[]>([])
const defaultCover = 'https://via.placeholder.com/200x280/10b981/ffffff?text=BookList'

onMounted(() => {
  fetchCategories()
  fetchBookLists()
})

async function fetchCategories() {
  try {
    categories.value = await api.getBookListCategories()
  } catch (error) {
    console.error('获取分类失败:', error)
  }
}

async function fetchBookLists() {
  loading.value = true
  try {
    const response = await api.getBookLists({
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value || undefined,
      is_active: true,
      category: selectedCategory.value || undefined
    })
    bookLists.value = response.items
    total.value = response.total
  } catch (error) {
    console.error('获取书单列表失败:', error)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  currentPage.value = 1
  fetchBookLists()
}

function selectCategory(category: string) {
  selectedCategory.value = category
  handleSearch()
}

function handleCoverError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultCover
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
.book-lists-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  text-align: center;
  padding: 32px 0;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
}

.filter-bar {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 8px;
}

.category-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.category-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.category-tag:hover {
  transform: translateY(-2px);
}

.search-bar {
  display: flex;
  gap: 16px;
  padding: 24px;
  background: var(--bg-secondary);
  border-radius: 16px;
  box-shadow: var(--shadow);
  justify-content: center;
}

.search-input {
  flex: 1;
  max-width: 500px;
}

.results-info {
  color: var(--text-secondary);
  font-size: 14px;
}

.results-info strong {
  color: var(--primary-color);
  font-weight: 600;
}

.book-list-grid {
  min-height: 400px;
}

.booklist-card {
  background: var(--bg-secondary);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.booklist-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.booklist-card:hover .booklist-overlay {
  opacity: 1;
}

.booklist-cover-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 3/4;
  overflow: hidden;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.booklist-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.booklist-card:hover .booklist-cover {
  transform: scale(1.05);
}

.booklist-category-tag {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(255, 255, 255, 0.95);
  color: var(--primary-color);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  backdrop-filter: blur(10px);
}

.booklist-overlay {
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

.booklist-info {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.booklist-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.booklist-description {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 12px 0;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.5;
  flex: 1;
}

.booklist-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border-color);
  padding-top: 12px;
  margin-top: auto;
}

.booklist-date {
  font-size: 12px;
  color: var(--text-muted);
}

.pagination {
  display: flex;
  justify-content: center;
  padding: 24px 0;
}

@media (max-width: 768px) {
  .page-header {
    padding: 20px 0;
  }

  .page-title {
    font-size: 24px;
  }

  .search-bar {
    flex-direction: column;
    padding: 16px;
  }

  .search-input {
    max-width: none;
  }

  .booklist-cover-wrapper {
    aspect-ratio: 4/5;
  }

  .booklist-title {
    font-size: 14px;
  }
}
</style>
