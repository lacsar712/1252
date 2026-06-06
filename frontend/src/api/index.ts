import axios from 'axios'
import type { Book, BookListResponse, BookCreate, LoginResponse, User, CartListResponse, CartItemAdd, CartItemUpdate, CartItemSelectedUpdate, CartItemBatchDelete, Order, OrderListResponse, OrderCancel, OrderShip, OrderAdminUpdate, OrderStatus, Coupon, CouponListResponse, CouponCreate, CouponUpdate, UserCouponListResponse, AvailableCouponResponse, CouponClaimResponse, OrderCreateWithCoupon, Author, AuthorListResponse, AuthorCreate, AuthorUpdate, AuthorDetail, AuthorSearchResult, AuthorBookCheckResponse, Publisher, PublisherListResponse, PublisherCreate, PublisherUpdate, PublisherDetail, PublisherSearchResult, PublisherNameCheckResponse, PublisherBookCheckResponse, Message, MessageListResponse, UnreadCountResponse, AnnouncementCreate, MessageStatsResponse, MessageBatchDeleteRequest, MessageStatusFilter, MessageType, DashboardResponse, TimeRange, BookList, BookListListResponse, BookListCreate, BookListUpdate, BookListDetail, BookListAddBooksRequest, BookListUpdateBookRequest, BookListReorderRequest, MemberLevel, MemberLevelListResponse, MemberLevelCreate, MemberLevelUpdate, UserMemberLevelInfo, UserMemberLevelUpdate, BookMemberPriceResponse, Tag, TagListResponse, TagCreate, TagUpdate, TagNameCheckResponse, TagBookCheckResponse } from '@/types'
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

    getBooks: (params?: { page?: number; page_size?: number; search?: string; category?: string; tag_id?: number }): Promise<BookListResponse> =>
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
        instance.post('/coupons/validate-for-order', { cart_item_ids: cartItemIds }),

    getAuthors: (params?: { page?: number; page_size?: number; search?: string; is_active?: boolean }): Promise<AuthorListResponse> =>
        instance.get('/authors', { params }),

    getAuthor: (id: number): Promise<AuthorDetail> =>
        instance.get(`/authors/${id}`),

    getAuthorBooks: (authorId: number, params?: { page?: number; page_size?: number }): Promise<BookListResponse> =>
        instance.get(`/authors/${authorId}/books`, { params }),

    searchAuthors: (keyword: string, limit?: number): Promise<AuthorSearchResult[]> =>
        instance.get('/authors/search', { params: { keyword, limit } }),

    checkAuthorDelete: (authorId: number): Promise<AuthorBookCheckResponse> =>
        instance.get(`/authors/${authorId}/check-delete`),

    createAuthor: (author: AuthorCreate): Promise<Author> =>
        instance.post('/authors', author),

    updateAuthor: (id: number, author: AuthorUpdate): Promise<Author> =>
        instance.put(`/authors/${id}`, author),

    deleteAuthor: (id: number): Promise<void> =>
        instance.delete(`/authors/${id}`),

    getPublishers: (params?: { page?: number; page_size?: number; search?: string; is_active?: boolean }): Promise<PublisherListResponse> =>
        instance.get('/publishers', { params }),

    getPublisher: (id: number): Promise<PublisherDetail> =>
        instance.get(`/publishers/${id}`),

    getPublisherBooks: (publisherId: number, params?: { page?: number; page_size?: number }): Promise<BookListResponse> =>
        instance.get(`/publishers/${publisherId}/books`, { params }),

    searchPublishers: (keyword: string, limit?: number, include_inactive?: boolean): Promise<PublisherSearchResult[]> =>
        instance.get('/publishers/search', { params: { keyword, limit, include_inactive } }),

    checkPublisherName: (name: string, exclude_id?: number): Promise<PublisherNameCheckResponse> =>
        instance.get('/publishers/check-name', { params: { name, exclude_id } }),

    checkPublisherDelete: (publisherId: number): Promise<PublisherBookCheckResponse> =>
        instance.get(`/publishers/${publisherId}/check-delete`),

    createPublisher: (publisher: PublisherCreate): Promise<Publisher> =>
        instance.post('/publishers', publisher),

    updatePublisher: (id: number, publisher: PublisherUpdate): Promise<Publisher> =>
        instance.put(`/publishers/${id}`, publisher),

    deletePublisher: (id: number): Promise<void> =>
        instance.delete(`/publishers/${id}`),

    getUnreadCount: (): Promise<UnreadCountResponse> =>
        instance.get('/messages/unread-count'),

    getMessages: (params?: { status?: MessageStatusFilter; type?: MessageType; page?: number; page_size?: number }): Promise<MessageListResponse> =>
        instance.get('/messages', { params }),

    getMessageDetail: (messageId: number): Promise<Message> =>
        instance.get(`/messages/${messageId}`),

    markMessageRead: (messageId: number): Promise<{ message: string }> =>
        instance.post(`/messages/${messageId}/read`),

    markAllMessagesRead: (type?: MessageType): Promise<{ message: string }> =>
        instance.post('/messages/read-all', null, { params: { type } }),

    deleteMessage: (messageId: number): Promise<{ message: string }> =>
        instance.delete(`/messages/${messageId}`),

    batchDeleteMessages: (data: MessageBatchDeleteRequest): Promise<{ message: string }> =>
        instance.post('/messages/batch-delete', data),

    getAdminMessages: (params?: { type?: MessageType; page?: number; page_size?: number }): Promise<MessageListResponse> =>
        instance.get('/admin/messages', { params }),

    getAdminUsers: (search?: string): Promise<User[]> =>
        instance.get('/admin/messages/users', { params: { search } }),

    createAnnouncement: (data: AnnouncementCreate): Promise<Message> =>
        instance.post('/admin/messages/announcement', data),

    toggleAnnouncementActive: (messageId: number): Promise<{ message: string; is_active: boolean }> =>
        instance.put(`/admin/messages/${messageId}/toggle-active`),

    deleteAnnouncement: (messageId: number): Promise<{ message: string }> =>
        instance.delete(`/admin/messages/${messageId}`),

    getMessageStats: (): Promise<MessageStatsResponse> =>
        instance.get('/admin/messages/stats'),

    getDashboardStats: (days: TimeRange = 7): Promise<DashboardResponse> =>
        instance.get('/admin/dashboard/stats', { params: { days } }),

    getBookLists: (params?: { page?: number; page_size?: number; search?: string; is_active?: boolean; category?: string }): Promise<BookListListResponse> =>
        instance.get('/book-lists', { params }),

    getBookList: (id: number): Promise<BookListDetail> =>
        instance.get(`/book-lists/${id}`),

    getBookListCategories: (): Promise<string[]> =>
        instance.get('/book-lists/categories'),

    createBookList: (data: BookListCreate): Promise<BookList> =>
        instance.post('/book-lists', data),

    updateBookList: (id: number, data: BookListUpdate): Promise<BookList> =>
        instance.put(`/book-lists/${id}`, data),

    deleteBookList: (id: number): Promise<void> =>
        instance.delete(`/book-lists/${id}`),

    addBooksToBookList: (id: number, data: BookListAddBooksRequest): Promise<BookListDetail> =>
        instance.post(`/book-lists/${id}/books`, data),

    updateBookInBookList: (listId: number, bookId: number, data: BookListUpdateBookRequest): Promise<BookListDetail> =>
        instance.put(`/book-lists/${listId}/books/${bookId}`, data),

    removeBookFromBookList: (listId: number, bookId: number): Promise<BookListDetail> =>
        instance.delete(`/book-lists/${listId}/books/${bookId}`),

    reorderBooksInBookList: (id: number, data: BookListReorderRequest): Promise<BookListDetail> =>
        instance.put(`/book-lists/${id}/books/reorder`, data),

    getAdminMemberLevels: (params?: { is_active?: boolean; page?: number; page_size?: number }): Promise<MemberLevelListResponse> =>
        instance.get('/member-levels/admin', { params }),

    getAdminAllActiveMemberLevels: (): Promise<MemberLevel[]> =>
        instance.get('/member-levels/admin/all'),

    getAdminMemberLevel: (levelId: number): Promise<MemberLevel> =>
        instance.get(`/member-levels/admin/${levelId}`),

    createMemberLevel: (data: MemberLevelCreate): Promise<MemberLevel> =>
        instance.post('/member-levels', data),

    updateMemberLevel: (levelId: number, data: MemberLevelUpdate): Promise<MemberLevel> =>
        instance.put(`/member-levels/${levelId}`, data),

    deleteMemberLevel: (levelId: number): Promise<void> =>
        instance.delete(`/member-levels/${levelId}`),

    updateUserMemberLevel: (userId: number, data: UserMemberLevelUpdate): Promise<UserMemberLevelInfo> =>
        instance.patch(`/member-levels/users/${userId}/level`, data),

    recalculateUserSpent: (userId: number): Promise<UserMemberLevelInfo> =>
        instance.post(`/member-levels/users/${userId}/recalculate`),

    getActiveMemberLevels: (): Promise<MemberLevel[]> =>
        instance.get('/member-levels/active'),

    getMyMemberLevel: (): Promise<UserMemberLevelInfo> =>
        instance.get('/member-levels/my'),

    getBookMemberPrice: (bookId: number): Promise<BookMemberPriceResponse> =>
        instance.get(`/member-levels/my/price/${bookId}`),

    getTags: (params?: { page?: number; page_size?: number; search?: string; is_active?: boolean }): Promise<TagListResponse> =>
        instance.get('/tags', { params }),

    getActiveTags: (): Promise<Tag[]> =>
        instance.get('/tags/active'),

    getAllTags: (include_inactive?: boolean): Promise<Tag[]> =>
        instance.get('/tags/all', { params: { include_inactive } }),

    searchTags: (keyword: string, limit?: number, include_inactive?: boolean): Promise<Tag[]> =>
        instance.get('/tags/search', { params: { keyword, limit, include_inactive } }),

    checkTagName: (name: string, exclude_id?: number): Promise<TagNameCheckResponse> =>
        instance.get('/tags/check-name', { params: { name, exclude_id } }),

    getTag: (tagId: number): Promise<Tag> =>
        instance.get(`/tags/${tagId}`),

    getTagBooks: (tagId: number, params?: { page?: number; page_size?: number }): Promise<BookListResponse> =>
        instance.get(`/tags/${tagId}/books`, { params }),

    checkTagDelete: (tagId: number): Promise<TagBookCheckResponse> =>
        instance.get(`/tags/${tagId}/check-delete`),

    createTag: (tag: TagCreate): Promise<Tag> =>
        instance.post('/tags', tag),

    updateTag: (tagId: number, tag: TagUpdate): Promise<Tag> =>
        instance.put(`/tags/${tagId}`, tag),

    deleteTag: (tagId: number): Promise<void> =>
        instance.delete(`/tags/${tagId}`)
}
