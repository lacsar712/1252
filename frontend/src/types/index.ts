export interface User {
    id: number
    username: string
    email: string
    is_active: boolean
    is_admin: boolean
    created_at: string
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
