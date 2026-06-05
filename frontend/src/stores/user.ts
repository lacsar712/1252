import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api'
import type { User } from '@/types'
import { useCartStore } from '@/stores/cart'
import { useMessageStore } from '@/stores/message'

export const useUserStore = defineStore('user', () => {
    const token = ref<string | null>(localStorage.getItem('token'))
    const user = ref<User | null>(null)

    const isLoggedIn = computed(() => !!token.value)
    const isAdmin = computed(() => user.value?.is_admin ?? false)

    async function login(username: string, password: string) {
        const response = await api.login(username, password)
        token.value = response.access_token
        localStorage.setItem('token', response.access_token)
        await fetchUser()
        
        const cartStore = useCartStore()
        await cartStore.onUserLogin()

        const messageStore = useMessageStore()
        messageStore.onUserLogin()
    }

    async function register(username: string, email: string, password: string) {
        await api.register(username, email, password)
    }

    async function fetchUser() {
        if (!token.value) return
        try {
            user.value = await api.getCurrentUser()
        } catch (error) {
            logout()
        }
    }

    function logout() {
        token.value = null
        user.value = null
        localStorage.removeItem('token')
        
        const cartStore = useCartStore()
        cartStore.onUserLogout()

        const messageStore = useMessageStore()
        messageStore.onUserLogout()
    }

    // 初始化时获取用户信息
    if (token.value) {
        fetchUser()
        const messageStore = useMessageStore()
        messageStore.fetchUnreadCount()
    }

    return {
        token,
        user,
        isLoggedIn,
        isAdmin,
        login,
        register,
        fetchUser,
        logout
    }
})
