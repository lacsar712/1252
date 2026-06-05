import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes: RouteRecordRaw[] = [
    {
        path: '/',
        component: () => import('@/layouts/MainLayout.vue'),
        children: [
            {
                path: '',
                name: 'Home',
                component: () => import('@/views/Home.vue'),
                meta: { title: '首页' }
            },
            {
                path: 'books',
                name: 'Books',
                component: () => import('@/views/Books.vue'),
                meta: { title: '图书列表' }
            },
            {
                path: 'books/:id',
                name: 'BookDetail',
                component: () => import('@/views/BookDetail.vue'),
                meta: { title: '图书详情' }
            },
            {
                path: 'admin',
                name: 'Admin',
                component: () => import('@/views/Admin.vue'),
                meta: { title: '后台管理', requiresAdmin: true }
            },
            {
                path: 'cart',
                name: 'Cart',
                component: () => import('@/views/Cart.vue'),
                meta: { title: '购物车', requiresAuth: true }
            },
            {
                path: 'orders',
                name: 'Orders',
                component: () => import('@/views/Orders.vue'),
                meta: { title: '我的订单', requiresAuth: true }
            },
            {
                path: 'orders/:id',
                name: 'OrderDetail',
                component: () => import('@/views/OrderDetail.vue'),
                meta: { title: '订单详情', requiresAuth: true }
            },
            {
                path: 'checkout',
                name: 'Checkout',
                component: () => import('@/views/Checkout.vue'),
                meta: { title: '确认订单', requiresAuth: true }
            },
            {
                path: 'coupons',
                name: 'Coupons',
                component: () => import('@/views/Coupons.vue'),
                meta: { title: '领券中心', requiresAuth: true }
            },
            {
                path: 'authors',
                name: 'Authors',
                component: () => import('@/views/Authors.vue'),
                meta: { title: '作者列表' }
            },
            {
                path: 'authors/:id',
                name: 'AuthorDetail',
                component: () => import('@/views/AuthorDetail.vue'),
                meta: { title: '作者详情' }
            },
            {
                path: 'publishers/:id',
                name: 'PublisherDetail',
                component: () => import('@/views/PublisherDetail.vue'),
                meta: { title: '出版社详情' }
            },
            {
                path: 'messages',
                name: 'Messages',
                component: () => import('@/views/Messages.vue'),
                meta: { title: '消息中心', requiresAuth: true }
            }
        ]
    },
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/Login.vue'),
        meta: { title: '登录' }
    },
    {
        path: '/register',
        name: 'Register',
        component: () => import('@/views/Register.vue'),
        meta: { title: '注册' }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 路由守卫
router.beforeEach((to, _from, next) => {
    // 更新页面标题
    document.title = `${to.meta.title || '在线书店'} - 现代化在线书店`

    const userStore = useUserStore()

    // 需要管理员权限的页面
    if (to.meta.requiresAdmin) {
        if (!userStore.isLoggedIn) {
            next({ name: 'Login', query: { redirect: to.fullPath } })
        } else if (!userStore.isAdmin) {
            next({ name: 'Home' })
        } else {
            next()
        }
    }
    // 需要登录的页面
    else if (to.meta.requiresAuth) {
        if (!userStore.isLoggedIn) {
            next({ name: 'Login', query: { redirect: to.fullPath } })
        } else {
            next()
        }
    } else {
        next()
    }
})

export default router
