import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api'
import type { UnreadCountResponse, Message, MessageListResponse, MessageStatusFilter, MessageType } from '@/types'

export const useMessageStore = defineStore('message', () => {
    const unreadCount = ref<UnreadCountResponse>({
        total_unread: 0,
        order_status_unread: 0,
        delivery_reminder_unread: 0,
        announcement_unread: 0,
        account_security_unread: 0
    })

    const messages = ref<Message[]>([])
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const currentStatusFilter = ref<MessageStatusFilter>('all')
    const currentTypeFilter = ref<MessageType | undefined>(undefined)
    const selectedMessages = ref<number[]>([])

    const loading = ref(false)

    async function fetchUnreadCount() {
        try {
            unreadCount.value = await api.getUnreadCount()
        } catch (error) {
            console.error('获取未读消息数量失败:', error)
        }
    }

    async function fetchMessages(
        status?: MessageStatusFilter,
        type?: MessageType,
        page?: number,
        page_size?: number
    ) {
        loading.value = true
        try {
            if (status !== undefined) currentStatusFilter.value = status
            if (type !== undefined) currentTypeFilter.value = type
            if (page !== undefined) currentPage.value = page
            if (page_size !== undefined) pageSize.value = page_size

            const response: MessageListResponse = await api.getMessages({
                status: currentStatusFilter.value,
                type: currentTypeFilter.value,
                page: currentPage.value,
                page_size: pageSize.value
            })

            messages.value = response.items
            total.value = response.total
        } finally {
            loading.value = false
        }
    }

    async function markAsRead(messageId: number) {
        try {
            await api.markMessageRead(messageId)
            const message = messages.value.find(m => m.id === messageId)
            if (message) {
                message.is_read = true
                message.read_at = new Date().toISOString()
            }
            unreadCount.value.total_unread = Math.max(0, unreadCount.value.total_unread - 1)
        } catch (error) {
            console.error('标记消息已读失败:', error)
        }
    }

    async function markAllAsRead(type?: MessageType) {
        try {
            const response = await api.markAllMessagesRead(type)
            messages.value.forEach(m => {
                if (!type || m.type === type) {
                    m.is_read = true
                    m.read_at = new Date().toISOString()
                }
            })
            if (!type) {
                unreadCount.value.total_unread = 0
                unreadCount.value.order_status_unread = 0
                unreadCount.value.delivery_reminder_unread = 0
                unreadCount.value.announcement_unread = 0
                unreadCount.value.account_security_unread = 0
            }
            return response
        } catch (error) {
            console.error('标记全部已读失败:', error)
            throw error
        }
    }

    async function deleteMessage(messageId: number) {
        try {
            await api.deleteMessage(messageId)
            const index = messages.value.findIndex(m => m.id === messageId)
            if (index > -1) {
                const message = messages.value[index]
                if (!message.is_read) {
                    unreadCount.value.total_unread = Math.max(0, unreadCount.value.total_unread - 1)
                }
                messages.value.splice(index, 1)
                total.value = Math.max(0, total.value - 1)
            }
        } catch (error) {
            console.error('删除消息失败:', error)
            throw error
        }
    }

    async function batchDelete(messageIds: number[]) {
        try {
            await api.batchDeleteMessages({ message_ids: messageIds })
            messageIds.forEach(id => {
                const index = messages.value.findIndex(m => m.id === id)
                if (index > -1) {
                    const message = messages.value[index]
                    if (!message.is_read) {
                        unreadCount.value.total_unread = Math.max(0, unreadCount.value.total_unread - 1)
                    }
                    messages.value.splice(index, 1)
                    total.value = Math.max(0, total.value - 1)
                }
            })
            selectedMessages.value = []
        } catch (error) {
            console.error('批量删除失败:', error)
            throw error
        }
    }

    function toggleSelect(messageId: number) {
        const index = selectedMessages.value.indexOf(messageId)
        if (index > -1) {
            selectedMessages.value.splice(index, 1)
        } else {
            selectedMessages.value.push(messageId)
        }
    }

    function selectAll() {
        if (selectedMessages.value.length === messages.value.length) {
            selectedMessages.value = []
        } else {
            selectedMessages.value = messages.value.map(m => m.id)
        }
    }

    function clearSelection() {
        selectedMessages.value = []
    }

    const isAllSelected = computed(() => {
        return messages.value.length > 0 && selectedMessages.value.length === messages.value.length
    })

    function onUserLogin() {
        fetchUnreadCount()
    }

    function onUserLogout() {
        unreadCount.value = {
            total_unread: 0,
            order_status_unread: 0,
            delivery_reminder_unread: 0,
            announcement_unread: 0,
            account_security_unread: 0
        }
        messages.value = []
        total.value = 0
        selectedMessages.value = []
    }

    return {
        unreadCount,
        messages,
        total,
        currentPage,
        pageSize,
        currentStatusFilter,
        currentTypeFilter,
        selectedMessages,
        loading,
        isAllSelected,
        fetchUnreadCount,
        fetchMessages,
        markAsRead,
        markAllAsRead,
        deleteMessage,
        batchDelete,
        toggleSelect,
        selectAll,
        clearSelection,
        onUserLogin,
        onUserLogout
    }
})
