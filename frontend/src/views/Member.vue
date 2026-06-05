<template>
  <div class="member-page" v-loading="loading">
    <div class="member-header">
      <h1>会员中心</h1>
    </div>

    <div v-if="memberInfo" class="member-content">
      <div class="current-level-card">
        <div class="level-card-header" :style="{ background: levelGradient }">
          <div class="level-info">
            <div class="level-badge" :style="{ backgroundColor: memberInfo.current_level?.badge_color || '#409eff' }">
              <span class="level-name">{{ memberInfo.current_level?.name || '普通会员' }}</span>
              <el-tag v-if="memberInfo.is_manual" type="warning" size="small" effect="dark" class="manual-tag">
                手动设置
              </el-tag>
            </div>
            <div class="total-spent">
              <span class="spent-label">累计消费</span>
              <span class="spent-value">¥{{ memberInfo.total_spent.toFixed(2) }}</span>
            </div>
          </div>
          <div class="level-icon">
            <el-icon :size="64"><Medal /></el-icon>
          </div>
        </div>

        <div class="progress-section" v-if="memberInfo.next_level">
          <div class="progress-header">
            <span class="current-level-name">{{ memberInfo.current_level?.name || '普通会员' }}</span>
            <el-icon><Right /></el-icon>
            <span class="next-level-name">{{ memberInfo.next_level.name }}</span>
          </div>
          <el-progress
            :percentage="progressPercentage"
            :stroke-width="12"
            :color="progressColor"
            :show-text="false"
          />
          <div class="progress-info">
            <span>距离下一等级还差</span>
            <span class="amount-needed">¥{{ memberInfo.amount_to_next.toFixed(2) }}</span>
          </div>
        </div>
        <div v-else class="highest-level">
          <el-icon><Trophy /></el-icon>
          <span>您已达到最高等级！</span>
        </div>

        <div class="benefits-section" v-if="memberInfo.current_level?.benefits">
          <h3>当前等级权益</h3>
          <div class="benefits-content">
            <p>{{ memberInfo.current_level.benefits }}</p>
          </div>
        </div>

        <div class="discount-info">
          <div class="discount-item">
            <span class="discount-label">专属折扣</span>
            <span class="discount-value">{{ memberInfo.current_level ? (memberInfo.current_level.discount_rate * 10).toFixed(1) + '折' : '无' }}</span>
          </div>
        </div>
      </div>

      <div class="all-levels-section">
        <h2>全部等级</h2>
        <div class="levels-grid">
          <div
            v-for="level in allLevels"
            :key="level.id"
            class="level-card"
            :class="{ 'is-current': memberInfo.current_level?.id === level.id }"
          >
            <div class="level-card-badge" :style="{ backgroundColor: level.badge_color || '#409eff' }">
              <el-tag size="small" effect="dark" :color="level.badge_color || '#409eff'">
                {{ level.name }}
              </el-tag>
            </div>
            <div class="level-card-threshold">
              累计消费 ¥{{ level.threshold_amount.toFixed(2) }}
            </div>
            <div class="level-card-discount">
              <span class="discount-label">折扣</span>
              <span class="discount-value">{{ (level.discount_rate * 10).toFixed(1) }}折</span>
            </div>
            <div class="level-card-benefits" v-if="level.benefits">
              <p>{{ level.benefits }}</p>
            </div>
            <div v-if="memberInfo.current_level?.id === level.id" class="current-indicator">
              <el-icon><Check /></el-icon>
              <span>当前等级</span>
            </div>
          </div>
        </div>
        <el-empty v-if="allLevels.length === 0" description="暂无等级信息" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'
import type { UserMemberLevelInfo, MemberLevel } from '@/types'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { Medal, Right, Trophy, Check } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const memberInfo = ref<UserMemberLevelInfo | null>(null)
const allLevels = ref<MemberLevel[]>([])

const progressPercentage = computed(() => {
  if (!memberInfo.value?.current_level || !memberInfo.value?.next_level) return 100
  const currentThreshold = memberInfo.value.current_level.threshold_amount
  const nextThreshold = memberInfo.value.next_level.threshold_amount
  const total = nextThreshold - currentThreshold
  const achieved = memberInfo.value.total_spent - currentThreshold
  if (total <= 0) return 100
  return Math.min(Math.max(Math.round((achieved / total) * 100), 0), 100)
})

const progressColor = computed(() => {
  return memberInfo.value?.current_level?.badge_color || '#409eff'
})

const levelGradient = computed(() => {
  const color = memberInfo.value?.current_level?.badge_color || '#409eff'
  return `linear-gradient(135deg, ${color} 0%, ${adjustColor(color, -30)} 100%)`
})

function adjustColor(color: string, amount: number): string {
  const hex = color.replace('#', '')
  const num = parseInt(hex, 16)
  let r = (num >> 16) + amount
  let g = ((num >> 8) & 0x00FF) + amount
  let b = (num & 0x0000FF) + amount
  r = Math.max(Math.min(255, r), 0)
  g = Math.max(Math.min(255, g), 0)
  b = Math.max(Math.min(255, b), 0)
  return '#' + (0x1000000 + r * 0x10000 + g * 0x100 + b).toString(16).slice(1)
}

onMounted(async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push({ name: 'Login', query: { redirect: '/member' } })
    return
  }
  await fetchData()
})

async function fetchData() {
  loading.value = true
  try {
    const [info, levels] = await Promise.all([
      api.getMyMemberLevel(),
      api.getActiveMemberLevels()
    ])
    memberInfo.value = info
    allLevels.value = levels
  } catch (error) {
    console.error('获取会员信息失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.member-page {
  max-width: 1200px;
  margin: 0 auto;
}

.member-header {
  margin-bottom: 24px;
}

.member-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.member-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.current-level-card {
  background: var(--bg-secondary);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow);
}

.level-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32px;
  color: #fff;
}

.level-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.level-badge {
  display: flex;
  align-items: center;
  gap: 12px;
}

.level-name {
  font-size: 32px;
  font-weight: 700;
}

.manual-tag {
  margin-left: 8px;
}

.total-spent {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.spent-label {
  font-size: 14px;
  opacity: 0.9;
}

.spent-value {
  font-size: 24px;
  font-weight: 600;
}

.level-icon {
  opacity: 0.9;
}

.progress-section {
  padding: 24px 32px;
  background: var(--bg-primary);
}

.progress-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  font-weight: 500;
  color: var(--text-primary);
}

.current-level-name {
  color: var(--primary-color);
  font-weight: 600;
}

.next-level-name {
  color: var(--text-secondary);
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  font-size: 14px;
  color: var(--text-secondary);
}

.amount-needed {
  font-weight: 600;
  color: var(--danger-color);
}

.highest-level {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 24px 32px;
  background: var(--bg-primary);
  font-size: 16px;
  font-weight: 600;
  color: var(--warning-color);
}

.benefits-section {
  padding: 24px 32px;
  border-top: 1px solid var(--border-color);
}

.benefits-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.benefits-content p {
  margin: 0;
  line-height: 1.8;
  color: var(--text-secondary);
}

.discount-info {
  padding: 20px 32px;
  border-top: 1px solid var(--border-color);
  display: flex;
  background: var(--bg-primary);
}

.discount-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.discount-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.discount-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--danger-color);
}

.all-levels-section h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
}

.levels-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}

.level-card {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--shadow);
  transition: all 0.3s;
  position: relative;
  border: 2px solid transparent;
}

.level-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.level-card.is-current {
  border-color: var(--primary-color);
}

.level-card-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 6px;
  margin-bottom: 16px;
}

.level-card-threshold {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.level-card-discount {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 12px;
}

.level-card-discount .discount-label {
  font-size: 13px;
}

.level-card-discount .discount-value {
  font-size: 20px;
}

.level-card-benefits p {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.current-indicator {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  color: var(--primary-color);
  background: rgba(99, 102, 241, 0.1);
  padding: 4px 10px;
  border-radius: 12px;
}

@media (max-width: 768px) {
  .level-card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
    padding: 24px;
  }

  .level-name {
    font-size: 24px;
  }

  .progress-section,
  .highest-level,
  .benefits-section,
  .discount-info {
    padding: 20px 24px;
  }

  .levels-grid {
    grid-template-columns: 1fr;
  }
}
</style>
