<template>
  <div class="authors-page">
    <div class="page-header">
      <h1 class="page-title">作者列表</h1>
      <p class="page-subtitle">发现优秀作者，探索他们的作品世界</p>
    </div>

    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索作者姓名或国家..."
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
      <span v-if="total > 0">共找到 <strong>{{ total }}</strong> 位作者</span>
      <span v-else-if="!loading">暂无作者</span>
    </div>

    <div class="author-list" v-loading="loading">
      <el-row :gutter="24">
        <el-col v-for="author in authors" :key="author.id" :xs="12" :sm="8" :md="6" :lg="4">
          <div class="author-card" @click="router.push(`/authors/${author.id}`)">
            <div class="author-avatar-wrapper">
              <img
                :src="author.avatar || defaultAvatar"
                :alt="author.name"
                class="author-avatar"
                @error="handleAvatarError"
              >
              <div class="author-overlay">
                <el-button type="primary" circle>
                  <el-icon><View /></el-icon>
                </el-button>
              </div>
            </div>
            <div class="author-info">
              <h3 class="author-name">{{ author.name }}</h3>
              <p class="author-country" v-if="author.country">
                <el-icon><Location /></el-icon>
                {{ author.country }}
                <span v-if="author.birth_year"> · {{ author.birth_year }}</span>
              </p>
              <p class="author-bio" v-if="author.bio">{{ author.bio }}</p>
              <div class="author-footer">
                <el-tag size="small" :type="author.is_active ? 'success' : 'info'">
                  {{ author.is_active ? '活跃' : '已停用' }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <el-empty v-if="!loading && authors.length === 0" description="暂无作者数据" />
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
import type { Author } from '@/types'
import { Search, View, Location } from '@element-plus/icons-vue'

const router = useRouter()

const loading = ref(false)
const authors = ref<Author[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const searchQuery = ref('')
const defaultAvatar = 'https://via.placeholder.com/120x120/8b5cf6/ffffff?text=Author'

onMounted(() => {
  fetchAuthors()
})

async function fetchAuthors() {
  loading.value = true
  try {
    const response = await api.getAuthors({
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value || undefined,
      is_active: true
    })
    authors.value = response.items
    total.value = response.total
  } catch (error) {
    console.error('获取作者列表失败:', error)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  currentPage.value = 1
  fetchAuthors()
}

function handleAvatarError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultAvatar
}
</script>

<style scoped>
.authors-page {
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

.author-list {
  min-height: 400px;
}

.author-card {
  background: var(--bg-secondary);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  margin-bottom: 24px;
}

.author-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.author-card:hover .author-overlay {
  opacity: 1;
}

.author-avatar-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.author-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.author-card:hover .author-avatar {
  transform: scale(1.05);
}

.author-overlay {
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

.author-info {
  padding: 16px;
}

.author-name {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.author-country {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-secondary);
  margin: 0 0 8px 0;
}

.author-country .el-icon {
  color: var(--primary-color);
}

.author-bio {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 12px 0;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.5;
}

.author-footer {
  display: flex;
  justify-content: flex-end;
}

.pagination {
  display: flex;
  justify-content: center;
  padding: 24px 0;
}
</style>
