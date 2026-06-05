export interface User {
    id: number
    username: string
    email: string
    is_active: boolean
    is_admin: boolean
    created_at: string
}

export interface Author {
    id: number
    name: string
    avatar: string | null
    bio: string | null
    country: string | null
    birth_year: number | null
    masterpieces: string | null
    is_active: boolean
    created_at: string
    updated_at: string
}

export interface AuthorDetail extends Author {
    book_count: number
    category_distribution: { category: string; count: number }[]
    books: Book[]
}

export interface AuthorListResponse {
    total: number
    page: number
    page_size: number
    items: Author[]
}

export interface AuthorCreate {
    name: string
    avatar?: string
    bio?: string
    country?: string
    birth_year?: number
    masterpieces?: string
    is_active: boolean
}

export interface AuthorUpdate {
    name?: string
    avatar?: string
    bio?: string
    country?: string
    birth_year?: number
    masterpieces?: string
    is_active?: boolean
}

export interface AuthorSearchResult {
    id: number
    name: string
    country: string | null
    avatar: string | null
}

export interface AuthorBookCheckResponse {
    can_delete: boolean
    linked_books: number
    message: string | null
}

export interface Book {
    id: number
    title: string
    author: string
    publisher: string | null
    isbn: string | null
    price: number
    stock: number
    description: string | null
    cover_image: string | null
    category: string | null
    created_at: string
    updated_at: string
    authors: Author[]
}

export interface BookListResponse {
    total: number
    page: number
    page_size: number
    items: Book[]
}

export interface BookCreate {
    title: string
    author: string
    publisher?: string
    isbn?: string
    price: number
    stock?: number
    description?: string
    cover_image?: string
    category?: string
    author_ids?: number[]
}

export interface LoginResponse {
    access_token: string
    token_type: string
}

export interface CartItem {
    id: number
    user_id: number
    book_id: number
    quantity: number
    selected: boolean
    created_at: string
    updated_at: string
    book: Book
}

export interface CartListResponse {
    items: CartItem[]
    total_count: number
    selected_count: number
    total_price: number
    selected_price: number
    invalid_items: CartItem[]
    low_stock_items: CartItem[]
}

export interface CartItemAdd {
    book_id: number
    quantity: number
}

export interface CartItemUpdate {
    quantity: number
}

export interface CartItemSelectedUpdate {
    selected: boolean
}

export interface CartItemBatchDelete {
    cart_item_ids: number[]
}

export type OrderStatus = 'pending' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled'

export interface OrderItemSnapshot {
    book_id: number
    book_title: string
    book_author: string
    book_price: number
    book_cover: string | null
    quantity: number
    subtotal: number
}

export interface Order {
    id: number
    order_no: string
    user_id: number
    total_amount: number
    original_amount: number
    discount_amount: number
    user_coupon_id: number | null
    status: OrderStatus
    receiver_name: string
    receiver_phone: string
    receiver_address: string
    remark: string | null
    cancel_reason: string | null
    admin_remark: string | null
    tracking_company: string | null
    tracking_number: string | null
    paid_at: string | null
    shipped_at: string | null
    delivered_at: string | null
    created_at: string
    updated_at: string
    items: OrderItemSnapshot[]
    used_coupon: UserCoupon | null
}

export interface OrderListResponse {
    total: number
    page: number
    page_size: number
    items: Order[]
}

export interface OrderCreate {
    receiver_name: string
    receiver_phone: string
    receiver_address: string
    remark?: string
    cart_item_ids?: number[]
}

export interface OrderCancel {
    cancel_reason: string
}

export interface OrderShip {
    tracking_company: string
    tracking_number: string
    admin_remark?: string
}

export interface OrderAdminUpdate {
    status?: OrderStatus
    admin_remark?: string
    tracking_company?: string
    tracking_number?: string
}

export type CouponStatus = 'active' | 'inactive' | 'expired' | 'sold_out'
export type UserCouponStatus = 'unused' | 'used' | 'expired' | 'locked'

export interface Coupon {
    id: number
    name: string
    description: string | null
    threshold_amount: number
    discount_amount: number
    valid_from: string
    valid_to: string
    total_quantity: number
    claimed_quantity: number
    limit_per_user: number
    applicable_categories: string | null
    status: CouponStatus
    created_at: string
    updated_at: string
}

export interface CouponListResponse {
    total: number
    page: number
    page_size: number
    items: Coupon[]
}

export interface CouponCreate {
    name: string
    description?: string
    threshold_amount: number
    discount_amount: number
    valid_from: string
    valid_to: string
    total_quantity: number
    limit_per_user: number
    applicable_categories?: string
    status: CouponStatus
}

export interface CouponUpdate {
    name?: string
    description?: string
    threshold_amount?: number
    discount_amount?: number
    valid_from?: string
    valid_to?: string
    total_quantity?: number
    limit_per_user?: number
    applicable_categories?: string
    status?: CouponStatus
}

export interface UserCoupon {
    id: number
    coupon_id: number
    user_id: number
    status: UserCouponStatus
    order_id: number | null
    used_at: string | null
    claimed_at: string
    coupon: Coupon
    unavailable_reason?: string
    is_available?: boolean
}

export interface UserCouponListResponse {
    total: number
    page: number
    page_size: number
    items: UserCoupon[]
}

export interface AvailableCouponResponse {
    available: UserCoupon[]
    unavailable: UserCoupon[]
}

export interface OrderCreateWithCoupon extends OrderCreate {
    user_coupon_id?: number
}

export interface CouponClaimResponse {
    message: string
    user_coupon: UserCoupon
}
