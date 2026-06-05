import axios from 'axios'
import type { Book, BookListResponse, BookCreate, LoginResponse, User, CartListResponse, CartItemAdd, CartItemUpdate, CartItemSelectedUpdate, CartItemBatchDelete, Order, OrderListResponse, OrderCancel, OrderShip, OrderAdminUpdate, OrderStatus, Coupon, CouponListResponse, CouponCreate, CouponUpdate, UserCouponListResponse, AvailableCouponResponse, CouponClaimResponse, OrderCreateWithCoupon } from '@/types'
import { ElMessage } from 'element-plus'

const instance = axios.create({
    baseURL: '/api',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json'
    }
})

instance.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

instance.interceptors.response.use(
    (response) => response.data,
    (error) => {
        const message = error.response?.data?.detail || '请求失败，请稍后重试'
        ElMessage.error(message)
        return Promise.reject(error)
    }
)

export const api = {
    login: (username: string, password: string): Promise<LoginResponse> =>
        instance.post('/auth/login', { username, password }),

    register: (username: string, email: string, password: string): Promise<User> =>
        instance.post('/auth/register', { username, email, password }),

    getCurrentUser: (): Promise<User> =>
        instance.get('/auth/me'),

    getBooks: (params?: { page?: number; page_size?: number; search?: string; category?: string }): Promise<BookListResponse> =>
        instance.get('/books', { params }),

    getBook: (id: number): Promise<Book> =>
        instance.get(`/books/${id}`),

    createBook: (book: BookCreate): Promise<Book> =>
        instance.post('/books', book),

    updateBook: (id: number, book: Partial<BookCreate>): Promise<Book> =>
        instance.put(`/books/${id}`, book),

    deleteBook: (id: number): Promise<void> =>
        instance.delete(`/books/${id}`),

    getCategories: (): Promise<string[]> =>
        instance.get('/books/categories/list'),

    getCart: (): Promise<CartListResponse> =>
        instance.get('/cart'),

    getCartCount: (): Promise<number> =>
        instance.get('/cart/count'),

    addToCart: (data: CartItemAdd): Promise<CartListResponse> =>
        instance.post('/cart', data),

    updateCartItemQuantity: (cartItemId: number, data: CartItemUpdate): Promise<CartListResponse> =>
        instance.put(`/cart/${cartItemId}`, data),

    updateCartItemSelected: (cartItemId: number, data: CartItemSelectedUpdate): Promise<CartListResponse> =>
        instance.patch(`/cart/${cartItemId}/selected`, data),

    updateAllCartItemsSelected: (data: CartItemSelectedUpdate): Promise<CartListResponse> =>
        instance.patch('/cart/selected/all', data),

    deleteCartItem: (cartItemId: number): Promise<CartListResponse> =>
        instance.delete(`/cart/${cartItemId}`),

    batchDeleteCartItems: (data: CartItemBatchDelete): Promise<CartListResponse> =>
        instance.post('/cart/batch-delete', data),

    clearInvalidItems: (): Promise<CartListResponse> =>
        instance.delete('/cart/clear/invalid'),

    clearCart: (): Promise<CartListResponse> =>
        instance.delete('/cart'),

    getMyOrders: (params?: { status?: OrderStatus; page?: number; page_size?: number }): Promise<OrderListResponse> =>
        instance.get('/orders/my', { params }),

    getOrderDetail: (orderId: number): Promise<Order> =>
        instance.get(`/orders/${orderId}`),

    cancelOrder: (orderId: number, data: OrderCancel): Promise<Order> =>
        instance.post(`/orders/${orderId}/cancel`, data),

    shipOrder: (orderId: number, data: OrderShip): Promise<Order> =>
        instance.post(`/orders/${orderId}/ship`, data),

    getAllOrders: (params?: { status?: OrderStatus; page?: number; page_size?: number }): Promise<OrderListResponse> =>
        instance.get('/orders', { params }),

    updateOrderAdmin: (orderId: number, data: OrderAdminUpdate): Promise<Order> =>
        instance.patch(`/orders/${orderId}/admin`, data),

    createOrder: (data: OrderCreateWithCoupon): Promise<Order> =>
        instance.post('/orders', data),

    getAdminCoupons: (params?: { status?: string; page?: number; page_size?: number }): Promise<CouponListResponse> =>
        instance.get('/coupons/admin', { params }),

    getAdminCoupon: (couponId: number): Promise<Coupon> =>
        instance.get(`/coupons/admin/${couponId}`),

    createCoupon: (coupon: CouponCreate): Promise<Coupon> =>
        instance.post('/coupons', coupon),

    updateCoupon: (couponId: number, coupon: CouponUpdate): Promise<Coupon> =>
        instance.put(`/coupons/${couponId}`, coupon),

    deleteCoupon: (couponId: number): Promise<void> =>
        instance.delete(`/coupons/${couponId}`),

    getAvailableCoupons: (params?: { page?: number; page_size?: number }): Promise<CouponListResponse> =>
        instance.get('/coupons/available', { params }),

    claimCoupon: (couponId: number): Promise<CouponClaimResponse> =>
        instance.post(`/coupons/${couponId}/claim`),

    getMyCoupons: (params?: { status?: string; page?: number; page_size?: number }): Promise<UserCouponListResponse> =>
        instance.get('/coupons/my', { params }),

    validateCouponsForOrder: (cartItemIds: number[]): Promise<AvailableCouponResponse> =>
        instance.post('/coupons/validate-for-order', { cart_item_ids: cartItemIds })
}
