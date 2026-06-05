import axios from 'axios'
import type { Book, BookListResponse, BookCreate, LoginResponse, User, CartListResponse, CartItemAdd, CartItemUpdate, CartItemSelectedUpdate, CartItemBatchDelete } from '@/types'
import { ElMessage } from 'element-plus'

const instance = axios.create({
    baseURL: '/api',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json'
    }
})

// 请求拦截器
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

// 响应拦截器
instance.interceptors.response.use(
    (response) => response.data,
    (error) => {
        const message = error.response?.data?.detail || '请求失败，请稍后重试'
        ElMessage.error(message)
        return Promise.reject(error)
    }
)

export const api = {
    // 认证相关
    login: (username: string, password: string): Promise<LoginResponse> =>
        instance.post('/auth/login', { username, password }),

    register: (username: string, email: string, password: string): Promise<User> =>
        instance.post('/auth/register', { username, email, password }),

    getCurrentUser: (): Promise<User> =>
        instance.get('/auth/me'),

    // 图书相关
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

    // 购物车相关
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
        instance.delete('/cart')
}
