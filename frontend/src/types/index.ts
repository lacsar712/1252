export interface User {
    id: number
    username: string
    email: string
    is_active: boolean
    is_admin: boolean
    total_spent: number
    manual_level_id: number | null
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

export interface Publisher {
    id: number
    name: string
    logo: string | null
    website: string | null
    location: string | null
    description: string | null
    founded_year: number | null
    is_active: boolean
    created_at: string
    updated_at: string
}

export interface PublisherDetail extends Publisher {
    book_count: number
    category_distribution: { category: string; count: number }[]
    recent_books: Book[]
    books: Book[]
}

export interface PublisherListResponse {
    total: number
    page: number
    page_size: number
    items: Publisher[]
}

export interface PublisherCreate {
    name: string
    logo?: string
    website?: string
    location?: string
    description?: string
    founded_year?: number
    is_active: boolean
}

export interface PublisherUpdate {
    name?: string
    logo?: string
    website?: string
    location?: string
    description?: string
    founded_year?: number
    is_active?: boolean
}

export interface PublisherSearchResult {
    id: number
    name: string
    location: string | null
    logo: string | null
    is_active: boolean
}

export interface PublisherNameCheckResponse {
    available: boolean
    message: string | null
}

export interface PublisherBookCheckResponse {
    can_delete: boolean
    linked_books: number
    message: string | null
}

export interface Book {
    id: number
    title: string
    author: string
    publisher: string | null
    publisher_id: number | null
    isbn: string | null
    price: number
    stock: number
    description: string | null
    cover_image: string | null
    category: string | null
    created_at: string
    updated_at: string
    authors: Author[]
    publisher_info: Publisher | null
}

export interface BookCreate {
    title: string
    author: string
    publisher?: string
    publisher_id?: number | null
    isbn?: string
    price: number
    stock?: number
    description?: string
    cover_image?: string
    category?: string
    author_ids?: number[]
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
    book_member_price: number
    book_cover: string | null
    quantity: number
    subtotal: number
    member_subtotal: number
}

export interface Order {
    id: number
    order_no: string
    user_id: number
    total_amount: number
    original_amount: number
    discount_amount: number
    member_discount_amount: number
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
    member_level_id: number | null
    member_level_name: string | null
    member_discount_rate: number | null
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

export type MessageType = 'order_status' | 'delivery_reminder' | 'announcement' | 'account_security'
export type MessageRecipientType = 'all_users' | 'specific_users'
export type MessageStatusFilter = 'all' | 'unread' | 'read'

export interface Message {
    id: number
    type: MessageType
    title: string
    content: string
    sender_id: number | null
    sender_name: string | null
    recipient_type: MessageRecipientType
    order_id: number | null
    order_no: string | null
    valid_from: string | null
    valid_to: string | null
    is_active: boolean
    created_at: string
    is_read: boolean
    read_at: string | null
    is_deleted: boolean
}

export interface MessageListResponse {
    total: number
    page: number
    page_size: number
    items: Message[]
}

export interface UnreadCountResponse {
    total_unread: number
    order_status_unread: number
    delivery_reminder_unread: number
    announcement_unread: number
    account_security_unread: number
}

export interface AnnouncementCreate {
    title: string
    content: string
    recipient_type: MessageRecipientType
    user_ids?: number[]
    valid_from?: string
    valid_to?: string
}

export interface MessageBatchDeleteRequest {
    message_ids: number[]
}

export interface MessageStatsResponse {
    total_messages: number
    active_messages: number
    total_recipients: number
    read_recipients: number
    read_rate: number
}

export interface DashboardStats {
    total_books: number
    total_users: number
    total_orders: number
    low_stock_count: number
    total_inventory_value: number
    pending_orders: number
    today_orders: number
    today_revenue: number
}

export interface RecentBook {
    id: number
    title: string
    cover_image: string | null
    price: number
    stock: number
    category: string | null
    created_at: string
}

export interface RecentOrder {
    id: number
    order_no: string
    receiver_name: string
    total_amount: number
    status: OrderStatus
    created_at: string
}

export interface CategoryStock {
    category: string
    count: number
    value: number
    percentage: number
}

export interface SalesTrendItem {
    date: string
    order_count: number
    revenue: number
    book_count: number
}

export interface DashboardResponse {
    stats: DashboardStats
    recent_books: RecentBook[]
    recent_orders: RecentOrder[]
    category_stock: CategoryStock[]
    sales_trend: SalesTrendItem[]
}

export type TimeRange = 7 | 30 | 90

export interface BookList {
    id: number
    title: string
    description: string | null
    cover_image: string | null
    is_active: boolean
    sort_weight: number
    category: string | null
    created_at: string
    updated_at: string
}

export interface BookListBook {
    id: number
    title: string
    author: string
    cover_image: string | null
    price: number
    category: string | null
    sort_order: number
    recommendation: string | null
}

export interface BookListDetail extends BookList {
    book_count: number
    books: BookListBook[]
    categories: string[]
}

export interface BookListListResponse {
    total: number
    page: number
    page_size: number
    items: BookList[]
}

export interface BookListCreate {
    title: string
    description?: string
    cover_image?: string
    is_active: boolean
    sort_weight: number
    category?: string
    books?: { book_id: number; sort_order: number; recommendation?: string }[]
}

export interface BookListUpdate {
    title?: string
    description?: string
    cover_image?: string
    is_active?: boolean
    sort_weight?: number
    category?: string
}

export interface BookListAddBooksRequest {
    books: { book_id: number; sort_order: number; recommendation?: string }[]
}

export interface BookListUpdateBookRequest {
    sort_order?: number
    recommendation?: string
}

export interface BookListReorderRequest {
    book_ids: number[]
}

export interface MemberLevel {
    id: number
    name: string
    threshold_amount: number
    discount_rate: number
    benefits: string | null
    badge_color: string | null
    icon: string | null
    sort_order: number
    is_active: boolean
    created_at: string
    updated_at: string
}

export interface MemberLevelListResponse {
    total: number
    page: number
    page_size: number
    items: MemberLevel[]
}

export interface MemberLevelCreate {
    name: string
    threshold_amount: number
    discount_rate: number
    benefits?: string
    badge_color?: string
    icon?: string
    sort_order: number
    is_active: boolean
}

export interface MemberLevelUpdate {
    name?: string
    threshold_amount?: number
    discount_rate?: number
    benefits?: string
    badge_color?: string
    icon?: string
    sort_order?: number
    is_active?: boolean
}

export interface UserMemberLevelInfo {
    user_id: number
    total_spent: number
    current_level: MemberLevel | null
    next_level: MemberLevel | null
    amount_to_next: number
    manual_level: MemberLevel | null
    is_manual: boolean
}

export interface UserMemberLevelUpdate {
    manual_level_id?: number | null
}

export interface MemberPriceInfo {
    original_price: number
    member_price: number
    discount_rate: number
    level_name: string | null
}

export interface BookMemberPriceResponse {
    book_id: number
    price_info: MemberPriceInfo
}
