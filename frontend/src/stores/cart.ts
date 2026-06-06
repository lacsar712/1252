import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api'
import { ElMessage } from 'element-plus'
import type { CartListResponse, CartItem } from '@/types'
import { useUserStore } from '@/stores/user'

const GUEST_CART_KEY = 'guest_cart'

interface GuestCartItem {
    book_id: number
    quantity: number
    selected: boolean
}

export const useCartStore = defineStore('cart', () => {
    const cartData = ref<CartListResponse | null>(null)
    const cartCount = ref(0)
    const loading = ref(false)

    const totalCount = computed(() => cartData.value?.total_count ?? 0)
    const selectedCount = computed(() => cartData.value?.selected_count ?? 0)
    const totalPrice = computed(() => cartData.value?.total_price ?? 0)
    const selectedPrice = computed(() => cartData.value?.selected_price ?? 0)
    const items = computed(() => cartData.value?.items ?? [])
    const invalidItems = computed(() => cartData.value?.invalid_items ?? [])
    const lowStockItems = computed(() => cartData.value?.low_stock_items ?? [])
    const adjustedItems = computed(() => cartData.value?.adjusted_items ?? [])
    const hasInvalidItems = computed(() => invalidItems.value.length > 0)
    const hasLowStockItems = computed(() => lowStockItems.value.length > 0)
    const hasAdjustedItems = computed(() => adjustedItems.value.length > 0)

    const isAllSelected = computed(() => {
        const validItems = items.value
        if (validItems.length === 0) return false
        return validItems.every(item => item.selected)
    })

    function _getGuestCart(): GuestCartItem[] {
        try {
            const data = localStorage.getItem(GUEST_CART_KEY)
            return data ? JSON.parse(data) : []
        } catch {
            return []
        }
    }

    function _saveGuestCart(cart: GuestCartItem[]) {
        localStorage.setItem(GUEST_CART_KEY, JSON.stringify(cart))
    }

    async function _mergeGuestCartToServer() {
        const guestCart = _getGuestCart()
        if (guestCart.length === 0) return

        for (const item of guestCart) {
            try {
                await api.addToCart({
                    book_id: item.book_id,
                    quantity: item.quantity
                })
            } catch (error) {
                console.error('合并购物车失败:', error)
            }
        }

        localStorage.removeItem(GUEST_CART_KEY)
    }

    async function fetchCart() {
        const userStore = useUserStore()
        if (!userStore.isLoggedIn) {
            await _loadGuestCart()
            return
        }

        loading.value = true
        try {
            cartData.value = await api.getCart()
            cartCount.value = cartData.value.total_count
            if (cartData.value.adjusted_items && cartData.value.adjusted_items.length > 0) {
                const titles = cartData.value.adjusted_items.map(i => i.book?.title || '商品').join('、')
                ElMessage.warning(`因库存变化，以下商品数量已自动调整：${titles}`)
            }
        } catch (error) {
            console.error('获取购物车失败:', error)
        } finally {
            loading.value = false
        }
    }

    async function _loadGuestCart() {
        const guestCart = _getGuestCart()
        
        const validItems: CartItem[] = []
        const invalidItems: CartItem[] = []
        const lowStockItems: CartItem[] = []
        const adjustedItems: CartItem[] = []
        const adjustedTitles: string[] = []
        let totalCount = 0
        let selectedCount = 0
        let totalPrice = 0
        let selectedPrice = 0
        let guestCartChanged = false

        for (let i = 0; i < guestCart.length; i++) {
            const guestItem = guestCart[i]
            try {
                const book = await api.getBook(guestItem.book_id)
                
                if (book.stock <= 0) {
                    const cartItem: CartItem = {
                        id: -guestItem.book_id,
                        user_id: 0,
                        book_id: guestItem.book_id,
                        quantity: guestItem.quantity,
                        selected: guestItem.selected,
                        created_at: new Date().toISOString(),
                        updated_at: new Date().toISOString(),
                        book: book
                    }
                    invalidItems.push(cartItem)
                } else {
                    let finalQuantity = guestItem.quantity
                    if (guestItem.quantity > book.stock) {
                        finalQuantity = book.stock
                        guestCart[i].quantity = finalQuantity
                        guestCartChanged = true
                        adjustedTitles.push(book.title || '商品')
                    }
                    
                    const cartItem: CartItem = {
                        id: -guestItem.book_id,
                        user_id: 0,
                        book_id: guestItem.book_id,
                        quantity: finalQuantity,
                        selected: guestItem.selected,
                        created_at: new Date().toISOString(),
                        updated_at: new Date().toISOString(),
                        book: book
                    }
                    
                    if (finalQuantity <= 3) {
                        lowStockItems.push(cartItem)
                    }
                    if (guestItem.quantity !== finalQuantity) {
                        adjustedItems.push(cartItem)
                    }
                    
                    validItems.push(cartItem)
                    totalCount += finalQuantity
                    totalPrice += finalQuantity * book.price
                    
                    if (guestItem.selected) {
                        selectedCount += finalQuantity
                        selectedPrice += finalQuantity * book.price
                    }
                }
            } catch (error) {
                console.error('加载购物车商品失败:', error)
            }
        }

        if (guestCartChanged) {
            _saveGuestCart(guestCart)
        }

        cartData.value = {
            items: validItems,
            total_count: totalCount,
            selected_count: selectedCount,
            total_price: Math.round(totalPrice * 100) / 100,
            selected_price: Math.round(selectedPrice * 100) / 100,
            invalid_items: invalidItems,
            low_stock_items: lowStockItems,
            adjusted_items: adjustedItems
        }
        cartCount.value = totalCount

        if (adjustedTitles.length > 0) {
            ElMessage.warning(`因库存变化，以下商品数量已自动调整：${adjustedTitles.join('、')}`)
        }
    }

    async function fetchCartCount() {
        const userStore = useUserStore()
        if (!userStore.isLoggedIn) {
            const guestCart = _getGuestCart()
            let count = 0
            for (const item of guestCart) {
                count += item.quantity
            }
            cartCount.value = count
            return
        }

        try {
            cartCount.value = await api.getCartCount()
        } catch (error) {
            console.error('获取购物车数量失败:', error)
        }
    }

    async function addToCart(bookId: number, quantity: number = 1) {
        const userStore = useUserStore()
        if (!userStore.isLoggedIn) {
            const guestCart = _getGuestCart()
            const existingItem = guestCart.find(item => item.book_id === bookId)
            
            try {
                const book = await api.getBook(bookId)
                
                if (book.stock <= 0) {
                    ElMessage.error('图书已缺货，无法加入购物车')
                    return false
                }

                if (existingItem) {
                    const newQuantity = existingItem.quantity + quantity
                    if (newQuantity > book.stock) {
                        ElMessage.error(`库存不足，购物车已有 ${existingItem.quantity} 本，当前库存 ${book.stock} 本`)
                        return false
                    }
                    existingItem.quantity = newQuantity
                    existingItem.selected = true
                } else {
                    if (quantity > book.stock) {
                        ElMessage.error(`库存不足，当前库存 ${book.stock} 本`)
                        return false
                    }
                    guestCart.push({
                        book_id: bookId,
                        quantity: quantity,
                        selected: true
                    })
                }

                _saveGuestCart(guestCart)
                await _loadGuestCart()
                ElMessage.success(`已加入购物车，共 ${existingItem ? existingItem.quantity : quantity} 本`)
                return true
            } catch (error) {
                console.error('加入购物车失败:', error)
                return false
            }
        }

        try {
            cartData.value = await api.addToCart({ book_id: bookId, quantity })
            cartCount.value = cartData.value.total_count
            ElMessage.success('已加入购物车')
            return true
        } catch (error) {
            return false
        }
    }

    async function updateQuantity(cartItemId: number, bookId: number, quantity: number) {
        const userStore = useUserStore()
        if (!userStore.isLoggedIn) {
            const guestCart = _getGuestCart()
            const item = guestCart.find(item => item.book_id === bookId)
            
            if (item) {
                try {
                    const book = await api.getBook(bookId)
                    if (quantity > book.stock) {
                        ElMessage.error(`库存不足，当前库存 ${book.stock} 本`)
                        return false
                    }
                    item.quantity = quantity
                    _saveGuestCart(guestCart)
                    await _loadGuestCart()
                    return true
                } catch (error) {
                    console.error('更新数量失败:', error)
                    return false
                }
            }
            return false
        }

        try {
            cartData.value = await api.updateCartItemQuantity(cartItemId, { quantity })
            cartCount.value = cartData.value.total_count
            return true
        } catch (error) {
            return false
        }
    }

    async function updateSelected(cartItemId: number, selected: boolean) {
        const userStore = useUserStore()
        if (!userStore.isLoggedIn) {
            const guestCart = _getGuestCart()
            const item = guestCart.find(item => -item.book_id === cartItemId)
            if (item) {
                item.selected = selected
                _saveGuestCart(guestCart)
                await _loadGuestCart()
            }
            return
        }

        try {
            cartData.value = await api.updateCartItemSelected(cartItemId, { selected })
        } catch (error) {
            console.error('更新选中状态失败:', error)
        }
    }

    async function toggleAllSelected() {
        const userStore = useUserStore()
        const newSelected = !isAllSelected.value

        if (!userStore.isLoggedIn) {
            const guestCart = _getGuestCart()
            for (const item of guestCart) {
                item.selected = newSelected
            }
            _saveGuestCart(guestCart)
            await _loadGuestCart()
            return
        }

        try {
            cartData.value = await api.updateAllCartItemsSelected({ selected: newSelected })
        } catch (error) {
            console.error('全选失败:', error)
        }
    }

    async function deleteItem(cartItemId: number, bookId: number) {
        const userStore = useUserStore()
        if (!userStore.isLoggedIn) {
            const guestCart = _getGuestCart().filter(item => item.book_id !== bookId)
            _saveGuestCart(guestCart)
            await _loadGuestCart()
            ElMessage.success('已删除')
            return
        }

        try {
            cartData.value = await api.deleteCartItem(cartItemId)
            cartCount.value = cartData.value.total_count
            ElMessage.success('已删除')
        } catch (error) {
            console.error('删除失败:', error)
        }
    }

    async function batchDelete(ids: number[]) {
        const userStore = useUserStore()
        if (!userStore.isLoggedIn) {
            const guestCart = _getGuestCart().filter(item => !ids.includes(-item.book_id))
            _saveGuestCart(guestCart)
            await _loadGuestCart()
            ElMessage.success(`已删除 ${ids.length} 项商品`)
            return
        }

        try {
            cartData.value = await api.batchDeleteCartItems({ cart_item_ids: ids })
            cartCount.value = cartData.value.total_count
            ElMessage.success(`已删除 ${ids.length} 项商品`)
        } catch (error) {
            console.error('批量删除失败:', error)
        }
    }

    async function deleteSelected() {
        const selectedIds = items.value
            .filter(item => item.selected)
            .map(item => item.id)
        
        if (selectedIds.length === 0) {
            ElMessage.warning('请先选择要删除的商品')
            return
        }

        await batchDelete(selectedIds)
    }

    async function clearInvalidItems() {
        const userStore = useUserStore()
        if (!userStore.isLoggedIn) {
            const validItems: GuestCartItem[] = []
            const guestCart = _getGuestCart()
            
            for (const item of guestCart) {
                try {
                    const book = await api.getBook(item.book_id)
                    if (book.stock > 0) {
                        validItems.push(item)
                    }
                } catch {
                    // 图书不存在，跳过
                }
            }
            
            _saveGuestCart(validItems)
            await _loadGuestCart()
            ElMessage.success('已清理失效商品')
            return
        }

        try {
            cartData.value = await api.clearInvalidItems()
            cartCount.value = cartData.value.total_count
            ElMessage.success('已清理失效商品')
        } catch (error) {
            console.error('清理失效商品失败:', error)
        }
    }

    async function clearCart() {
        const userStore = useUserStore()
        if (!userStore.isLoggedIn) {
            _saveGuestCart([])
            await _loadGuestCart()
            ElMessage.success('购物车已清空')
            return
        }

        try {
            cartData.value = await api.clearCart()
            cartCount.value = 0
            ElMessage.success('购物车已清空')
        } catch (error) {
            console.error('清空购物车失败:', error)
        }
    }

    async function onUserLogin() {
        await _mergeGuestCartToServer()
        await fetchCart()
    }

    function onUserLogout() {
        cartData.value = null
        cartCount.value = 0
    }

    return {
        cartData,
        cartCount,
        loading,
        totalCount,
        selectedCount,
        totalPrice,
        selectedPrice,
        items,
        invalidItems,
        lowStockItems,
        adjustedItems,
        hasInvalidItems,
        hasLowStockItems,
        hasAdjustedItems,
        isAllSelected,
        fetchCart,
        fetchCartCount,
        addToCart,
        updateQuantity,
        updateSelected,
        toggleAllSelected,
        deleteItem,
        batchDelete,
        deleteSelected,
        clearInvalidItems,
        clearCart,
        onUserLogin,
        onUserLogout
    }
})
