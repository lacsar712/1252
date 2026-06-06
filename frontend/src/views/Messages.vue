<template>
  <div class="messages-page">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon :size="28"><Bell /></el-icon>
        消息中心
      </h2>
      <div class="header-actions">
        <el-button 
          type="primary" 
          :disabled="messageStore.unreadCount.total_unread === 0"
          @click="handleMarkAllRead"
        >
          <el-icon><Check /></el-icon>
          全部已读
        </el-button>
        <el-button 
          type="danger" 
          :disabled="messageStore.selectedMessages.length === 0"
          @click="handleBatchDelete"
        >
          <el-icon><Delete /></el-icon>
          批量删除
        </el-button>
      </div>
    </div>

    <div class="unread-summary">
      <el-row :gutter="16">
        <el-col :span="4" v-for="item in unreadStats" :key="item.type">
          <div class="stat-card" :class="{ active: activeTypeFilter === item.type }" @click="handleTypeFilter(item.type)">
            <div class="stat-icon" :class="`icon-${item.type}`">
              <el-icon :size="24"><component :is="item.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">{{ item.label }}</div>
              <div class="stat-value">{{ item.count }}</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <div class="filter-bar">
      <div class="filter-left">
        <el-radio-group v-model="messageStore.currentStatusFilter" @change="handleStatusFilter">
          <el-radio-button value="all">全部</el-radio-button>
          <el-radio-button value="unread">未读</el-radio-button>
          <el-radio-button value="read">已读</el-radio-button>
        </el-radio-group>
      </div>
      <div class="filter-right">
        <el-checkbox 
          v-model="isAllSelected" 
          :indeterminate="isIndeterminate"
          @change="messageStore.selectAll"
        >
          全选
        </el-checkbox>
      </div>
    </div>

    <div class="message-list" v-loading="messageStore.loading">
      <el-empty 
        v-if="messageStore.messages.length === 0 && !messageStore.loading" 
        description="暂无消息"
        :image-size="100"
      />
      
      <div 
        v-for="message in messageStore.messages" 
        :key="message.id" 
        class="message-item"
        :class="{ 'is-read': message.is_read, 'is-selected': messageStore.selectedMessages.includes(message.id) }"
      >
        <div class="message-checkbox">
          <el-checkbox 
            :model-value="messageStore.selectedMessages.includes(message.id)"
            @change="messageStore.toggleSelect(message.id)"
          />
        </div>
        
        <div class="message-icon" :class="`icon-${message.type}`">
          <el-icon :size="24">
            <component :is="getMessageIcon(message.type)" />
          </el-icon>
        </div>

        <div class="message-content" @click="handleViewMessage(message)">
          <div class="message-header">
            <span class="message-type-tag" :class="`tag-${message.type}`">
              {{ getMessageTypeLabel(message.type) }}
            </span>
            <span class="message-title" :class="{ 'unread-title': !message.is_read }">
              {{ message.title }}
            </span>
            <span class="message-time">{{ formatTime(message.created_at) }}</span>
          </div>
          <div class="message-preview">{{ message.content }}</div>
          <div class="message-meta" v-if="message.order_no && message.order_id">
            <span>关联订单：</span>
            <el-link type="primary" @click.stop="goToOrderDetail(message.order_id)">
              {{ message.order_no }}
            </el-link>
          </div>
        </div>

        <div class="message-actions">
          <el-button 
            v-if="!message.is_read"
            type="primary" 
            text 
            size="small"
            @click.stop="messageStore.markAsRead(message.id)"
          >
            标记已读
          </el-button>
          <el-button 
            type="danger" 
            text 
            size="small"
            @click.stop="handleDelete(message.id)"
          >
            删除
          </el-button>
        </div>
      </div>
    </div>

    <div class="pagination" v-if="messageStore.total > messageStore.pageSize">
      <el-pagination
        v-model:current-page="messageStore.currentPage"
        v-model:page-size="messageStore.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="messageStore.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handlePageSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <el-dialog 
      v-model="detailDialogVisible" 
      title="消息详情" 
      width="600px"
      class="message-detail-dialog"
    >
      <div v-if="currentMessage" class="message-detail">
        <div class="detail-header">
          <span class="detail-type-tag" :class="`tag-${currentMessage.type}`">
            {{ getMessageTypeLabel(currentMessage.type) }}
          </span>
          <h3 class="detail-title">{{ currentMessage.title }}</h3>
          <div class="detail-meta">
            <span v-if="currentMessage.sender_name">发送者：{{ currentMessage.sender_name }}</span>
            <span>发送时间：{{ formatTime(currentMessage.created_at) }}</span>
            <span v-if="currentMessage.order_no && currentMessage.order_id">
              订单号：
              <el-link type="primary" @click="goToOrderDetail(currentMessage.order_id)">
                {{ currentMessage.order_no }}
              </el-link>
            </span>
          </div>
        </div>
        <div class="detail-content">
          {{ currentMessage.content }}
        </div>
        <div class="detail-footer" v-if="currentMessage.valid_to">
          <el-tag type="info">有效期至：{{ formatTime(currentMessage.valid_to) }}</el-tag>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useMessageStore } from '@/stores/message'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Bell, 
  Check, 
  Delete, 
  ShoppingCart, 
  Box, 
  BellFilled, 
  UserFilled,
  List
} from '@element-plus/icons-vue'
import type { Message, MessageType, MessageStatusFilter } from '@/types'

const router = useRouter()
const messageStore = useMessageStore()

const detailDialogVisible = ref(false)
const currentMessage = ref<Message | null>(null)
const activeTypeFilter = ref<MessageType | 'all'>('all')

const unreadStats = computed(() => [
  {
    type: 'all' as const,
    label: '全部未读',
    count: messageStore.unreadCount.total_unread,
    icon: Bell
  },
  {
    type: 'order_status' as const,
    label: '订单状态',
    count: messageStore.unreadCount.order_status_unread,
    icon: ShoppingCart
  },
  {
    type: 'delivery_reminder' as const,
    label: '到货提醒',
    count: messageStore.unreadCount.delivery_reminder_unread,
    icon: Box
  },
  {
    type: 'announcement' as const,
    label: '系统公告',
    count: messageStore.unreadCount.announcement_unread,
    icon: BellFilled
  },
  {
    type: 'account_security' as const,
    label: '账号安全',
    count: messageStore.unreadCount.account_security_unread,
    icon: UserFilled
  }
])

const isIndeterminate = computed(() => {
  return messageStore.selectedMessages.length > 0 && 
         messageStore.selectedMessages.length < messageStore.messages.length
})

const isAllSelected = computed({
  get: () => messageStore.isAllSelected,
  set: () => {}
})

function getMessageIcon(type: MessageType) {
  const iconMap: Record<MessageType, any> = {
    order_status: ShoppingCart,
    delivery_reminder: Box,
    announcement: BellFilled,
    account_security: UserFilled
  }
  return iconMap[type] || Bell
}

function getMessageTypeLabel(type: MessageType) {
  const labelMap: Record<MessageType, string> = {
    order_status: '订单状态',
    delivery_reminder: '到货提醒',
    announcement: '系统公告',
    account_security: '账号安全'
  }
  return labelMap[type] || '其他'
}

function formatTime(time: string | null) {
  if (!time) return '-'
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function handleStatusFilter(status: MessageStatusFilter) {
  messageStore.fetchMessages(status, activeTypeFilter.value === 'all' ? undefined : activeTypeFilter.value, 1)
  messageStore.clearSelection()
}

function handleTypeFilter(type: MessageType | 'all') {
  activeTypeFilter.value = type
  messageStore.fetchMessages(
    messageStore.currentStatusFilter,
    type === 'all' ? undefined : type,
    1
  )
  messageStore.clearSelection()
}

function handlePageChange(page: number) {
  messageStore.fetchMessages(undefined, undefined, page)
  messageStore.clearSelection()
}

function handlePageSizeChange(size: number) {
  messageStore.fetchMessages(undefined, undefined, 1, size)
  messageStore.clearSelection()
}

async function handleViewMessage(message: Message) {
  if (!message.is_read) {
    await messageStore.markAsRead(message.id)
  }
  currentMessage.value = message
  detailDialogVisible.value = true
}

async function handleMarkAllRead() {
  try {
    await ElMessageBox.confirm(
      '确定要将所有消息标记为已读吗？',
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    await messageStore.markAllAsRead(
      activeTypeFilter.value === 'all' ? undefined : activeTypeFilter.value
    )
    ElMessage.success('已全部标记为已读')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('标记全部已读失败:', error)
    }
  }
}

async function handleDelete(messageId: number) {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条消息吗？',
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await messageStore.deleteMessage(messageId)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

async function handleBatchDelete() {
  if (messageStore.selectedMessages.length === 0) {
    ElMessage.warning('请先选择要删除的消息')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${messageStore.selectedMessages.length} 条消息吗？`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await messageStore.batchDelete(messageStore.selectedMessages)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
    }
  }
}

function goToOrderDetail(orderId: number) {
  router.push({ name: 'OrderDetail', params: { id: orderId } })
}

onMounted(() => {
  messageStore.fetchMessages()
  messageStore.fetchUnreadCount()
})
</script>

<style scoped>
.messages-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.unread-summary {
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.stat-card.active {
  border-color: var(--primary-color);
  background: rgba(99, 102, 241, 0.05);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.icon-all {
  background: var(--gradient-primary);
}

.icon-order_status {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.icon-delivery_reminder {
  background: linear-gradient(135deg, #10b981, #059669);
}

.icon-announcement {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
}

.icon-account_security {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #fff;
  border-radius: 12px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.message-list {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.message-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
  transition: background 0.2s;
}

.message-item:last-child {
  border-bottom: none;
}

.message-item:hover {
  background: rgba(99, 102, 241, 0.02);
}

.message-item.is-read {
  opacity: 0.7;
}

.message-item.is-selected {
  background: rgba(99, 102, 241, 0.08);
}

.message-checkbox {
  padding-top: 4px;
}

.message-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  cursor: pointer;
  min-width: 0;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.message-type-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  color: #fff;
}

.tag-order_status {
  background: #f59e0b;
}

.tag-delivery_reminder {
  background: #10b981;
}

.tag-announcement {
  background: #6366f1;
}

.tag-account_security {
  background: #ef4444;
}

.message-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.unread-title {
  font-weight: 600;
}

.message-time {
  font-size: 13px;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.message-preview {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  margin-bottom: 8px;
}

.message-meta {
  font-size: 13px;
  color: var(--text-secondary);
}

.message-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
}

.pagination {
  display: flex;
  justify-content: center;
  padding: 24px 0;
}

.message-detail-dialog :deep(.el-dialog__body) {
  padding: 0 24px 24px;
}

.detail-header {
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 20px;
}

.detail-type-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  color: #fff;
  margin-bottom: 12px;
}

.detail-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 14px;
  color: var(--text-secondary);
}

.detail-content {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-primary);
  padding: 20px;
  background: #f8fafc;
  border-radius: 8px;
  white-space: pre-wrap;
}

.detail-footer {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}
</style>
