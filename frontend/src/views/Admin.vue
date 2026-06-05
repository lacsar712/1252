<template>
  <div class="admin-page">
    <el-tabs v-model="activeTab" class="admin-tabs">
      <el-tab-pane label="图书管理" name="books">
        <div class="tab-content">
          <div class="admin-header">
            <h1>图书管理</h1>
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              添加图书
            </el-button>
          </div>
          
          <div class="search-bar">
            <el-input
              v-model="searchQuery"
              placeholder="搜索图书..."
              clearable
              @keyup.enter="fetchBooks"
              style="max-width: 300px"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button @click="fetchBooks">搜索</el-button>
          </div>
          
          <el-table
            :data="books"
            v-loading="loading"
            stripe
            style="width: 100%"
          >
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column label="封面" width="80">
              <template #default="{ row }">
                <img
                  :src="row.cover_image || defaultCover"
                  :alt="row.title"
                  class="book-thumbnail"
                  @error="handleImageError"
                >
              </template>
            </el-table-column>
            <el-table-column prop="title" label="书名" min-width="150">
              <template #default="{ row }">
                <span class="book-title">{{ row.title }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="author" label="作者" width="120" />
            <el-table-column prop="publisher" label="出版社" width="140">
              <template #default="{ row }">
                <span>{{ row.publisher || '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="category" label="分类" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.category" size="small">{{ row.category }}</el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="price" label="价格" width="100">
              <template #default="{ row }">
                <span class="price">¥{{ row.price.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="stock" label="库存" width="80">
              <template #default="{ row }">
                <el-tag :type="row.stock > 0 ? 'success' : 'danger'" size="small">
                  {{ row.stock }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleEdit(row)">
                  编辑
                </el-button>
                <el-popconfirm
                  title="确定要删除此图书吗？"
                  @confirm="handleDelete(row.id)"
                >
                  <template #reference>
                    <el-button type="danger" link>删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="pagination">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :total="total"
              layout="total, prev, pager, next"
              @current-change="fetchBooks"
            />
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="订单管理" name="orders">
        <div class="tab-content">
          <div class="admin-header">
            <h1>订单管理</h1>
          </div>
          
          <div class="search-bar">
            <el-select
              v-model="orderStatusFilter"
              placeholder="订单状态"
              clearable
              style="width: 150px"
              @change="fetchOrders"
            >
              <el-option label="待确认" value="pending" />
              <el-option label="已确认" value="confirmed" />
              <el-option label="已发货" value="shipped" />
              <el-option label="已完成" value="delivered" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
            <el-button @click="fetchOrders">搜索</el-button>
          </div>
          
          <el-table
            :data="orders"
            v-loading="ordersLoading"
            stripe
            style="width: 100%"
          >
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="order_no" label="订单号" min-width="180" />
            <el-table-column label="收货人" width="100">
              <template #default="{ row }">
                {{ row.receiver_name }}
              </template>
            </el-table-column>
            <el-table-column label="联系电话" width="130">
              <template #default="{ row }">
                {{ row.receiver_phone }}
              </template>
            </el-table-column>
            <el-table-column label="金额" width="120">
              <template #default="{ row }">
                <span class="price">¥{{ row.total_amount.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="下单时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="280" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="viewOrderDetail(row)">
                  详情
                </el-button>
                <el-button
                  v-if="row.status === 'pending'"
                  link
                  type="success"
                  @click="confirmOrder(row)"
                >
                  确认订单
                </el-button>
                <el-button
                  v-if="row.status === 'confirmed'"
                  link
                  type="warning"
                  @click="openShipDialog(row)"
                >
                  发货
                </el-button>
                <el-button
                  v-if="row.status === 'shipped'"
                  link
                  type="success"
                  @click="completeOrder(row)"
                >
                  完成
                </el-button>
                <el-button link type="info" @click="openRemarkDialog(row)">
                  备注
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="pagination">
            <el-pagination
              v-model:current-page="ordersCurrentPage"
              v-model:page-size="ordersPageSize"
              :total="ordersTotal"
              layout="total, prev, pager, next"
              @current-change="fetchOrders"
            />
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
    
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑图书' : '添加图书'"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="bookFormRef"
        :model="bookForm"
        :rules="bookRules"
        label-width="80px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="书名" prop="title">
              <el-input v-model="bookForm.title" placeholder="请输入书名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="作者" prop="author">
              <el-input v-model="bookForm.author" placeholder="请输入作者" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="出版社" prop="publisher">
              <el-input v-model="bookForm.publisher" placeholder="请输入出版社" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="ISBN" prop="isbn">
              <el-input v-model="bookForm.isbn" placeholder="请输入ISBN" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="价格" prop="price">
              <el-input-number
                v-model="bookForm.price"
                :min="0.01"
                :precision="2"
                controls-position="right"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="库存" prop="stock">
              <el-input-number
                v-model="bookForm.stock"
                :min="0"
                controls-position="right"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="分类" prop="category">
          <el-input v-model="bookForm.category" placeholder="请输入分类" />
        </el-form-item>
        
        <el-form-item label="封面" prop="cover_image">
          <el-input v-model="bookForm.cover_image" placeholder="请输入封面图片URL" />
        </el-form-item>
        
        <el-form-item label="简介" prop="description">
          <el-input
            v-model="bookForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入图书简介"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ isEdit ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="orderDetailVisible"
      title="订单详情"
      width="800px"
      destroy-on-close
    >
      <div v-if="currentOrder" class="order-detail">
        <div class="order-section">
          <h3>基本信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="订单号">
              {{ currentOrder.order_no }}
            </el-descriptions-item>
            <el-descriptions-item label="订单状态">
              <el-tag :type="getStatusType(currentOrder.status)">
                {{ getStatusText(currentOrder.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="订单金额">
              <span class="price">¥{{ currentOrder.total_amount.toFixed(2) }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="下单时间">
              {{ formatDate(currentOrder.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="收货人">
              {{ currentOrder.receiver_name }}
            </el-descriptions-item>
            <el-descriptions-item label="联系电话">
              {{ currentOrder.receiver_phone }}
            </el-descriptions-item>
            <el-descriptions-item label="收货地址" :span="2">
              {{ currentOrder.receiver_address }}
            </el-descriptions-item>
            <el-descriptions-item v-if="currentOrder.tracking_company" label="物流公司">
              {{ currentOrder.tracking_company }}
            </el-descriptions-item>
            <el-descriptions-item v-if="currentOrder.tracking_number" label="物流单号">
              {{ currentOrder.tracking_number }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="order-section">
          <h3>商品信息</h3>
          <el-table :data="currentOrder.items" border>
            <el-table-column label="商品" min-width="200">
              <template #default="{ row }">
                <div class="order-item">
                  <img
                    :src="row.book_cover || defaultCover"
                    :alt="row.book_title"
                    class="order-item-cover"
                  >
                  <div class="order-item-info">
                    <div class="order-item-title">{{ row.book_title }}</div>
                    <div class="order-item-author">{{ row.book_author }}</div>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="单价" width="100">
              <template #default="{ row }">
                ¥{{ row.book_price.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="数量" width="80">
              <template #default="{ row }">
                {{ row.quantity }}
              </template>
            </el-table-column>
            <el-table-column label="小计" width="120">
              <template #default="{ row }">
                <span class="price">¥{{ row.subtotal.toFixed(2) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div v-if="currentOrder.remark" class="order-section">
          <h3>用户备注</h3>
          <p>{{ currentOrder.remark }}</p>
        </div>

        <div v-if="currentOrder.admin_remark" class="order-section">
          <h3>管理员备注</h3>
          <p>{{ currentOrder.admin_remark }}</p>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="orderDetailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="shipDialogVisible"
      title="订单发货"
      width="500px"
      destroy-on-close
    >
      <el-form
        ref="shipFormRef"
        :model="shipForm"
        :rules="shipRules"
        label-width="100px"
      >
        <el-form-item label="物流公司" prop="tracking_company">
          <el-input v-model="shipForm.tracking_company" placeholder="请输入物流公司名称" />
        </el-form-item>
        <el-form-item label="物流单号" prop="tracking_number">
          <el-input v-model="shipForm.tracking_number" placeholder="请输入物流单号" />
        </el-form-item>
        <el-form-item label="管理员备注" prop="admin_remark">
          <el-input
            v-model="shipForm.admin_remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息（可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="shipDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="shipSubmitting" @click="handleShip">
          确认发货
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="remarkDialogVisible"
      title="编辑备注"
      width="500px"
      destroy-on-close
    >
      <el-form
        ref="remarkFormRef"
        :model="remarkForm"
        label-width="100px"
      >
        <el-form-item label="订单状态">
          <el-select v-model="remarkForm.status" placeholder="选择状态（可选）">
            <el-option label="待确认" value="pending" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="已发货" value="shipped" />
            <el-option label="已完成" value="delivered" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="管理员备注">
          <el-input
            v-model="remarkForm.admin_remark"
            type="textarea"
            :rows="4"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="remarkDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="remarkSubmitting" @click="handleRemarkSubmit">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { api } from '@/api'
import type { Book, BookCreate, Order, OrderStatus } from '@/types'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'

const activeTab = ref('books')

const loading = ref(false)
const submitting = ref(false)
const books = ref<Book[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchQuery = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref<number | null>(null)
const bookFormRef = ref<FormInstance>()
const defaultCover = 'https://via.placeholder.com/60x80/6366f1/ffffff?text=Book'

const ordersLoading = ref(false)
const orders = ref<Order[]>([])
const ordersTotal = ref(0)
const ordersCurrentPage = ref(1)
const ordersPageSize = ref(10)
const orderStatusFilter = ref<OrderStatus | ''>('')

const orderDetailVisible = ref(false)
const currentOrder = ref<Order | null>(null)

const shipDialogVisible = ref(false)
const shipSubmitting = ref(false)
const shippingOrderId = ref<number | null>(null)
const shipFormRef = ref<FormInstance>()
const shipForm = reactive({
  tracking_company: '',
  tracking_number: '',
  admin_remark: ''
})

const shipRules: FormRules = {
  tracking_company: [{ required: true, message: '请输入物流公司', trigger: 'blur' }],
  tracking_number: [{ required: true, message: '请输入物流单号', trigger: 'blur' }]
}

const remarkDialogVisible = ref(false)
const remarkSubmitting = ref(false)
const remarkOrderId = ref<number | null>(null)
const remarkFormRef = ref<FormInstance>()
const remarkForm = reactive({
  status: '' as OrderStatus | '',
  admin_remark: ''
})

const bookForm = reactive<BookCreate>({
  title: '',
  author: '',
  publisher: '',
  isbn: '',
  price: 0,
  stock: 0,
  description: '',
  cover_image: '',
  category: ''
})

const bookRules: FormRules = {
  title: [{ required: true, message: '请输入书名', trigger: 'blur' }],
  author: [{ required: true, message: '请输入作者', trigger: 'blur' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }]
}

onMounted(() => {
  fetchBooks()
})

watch(activeTab, (newTab) => {
  if (newTab === 'orders' && orders.value.length === 0) {
    fetchOrders()
  }
})

async function fetchBooks() {
  loading.value = true
  try {
    const response = await api.getBooks({
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value || undefined
    })
    books.value = response.items
    total.value = response.total
  } catch (error) {
    console.error('获取图书列表失败:', error)
  } finally {
    loading.value = false
  }
}

async function fetchOrders() {
  ordersLoading.value = true
  try {
    const response = await api.getAllOrders({
      status: orderStatusFilter.value || undefined,
      page: ordersCurrentPage.value,
      page_size: ordersPageSize.value
    })
    orders.value = response.items
    ordersTotal.value = response.total
  } catch (error) {
    console.error('获取订单列表失败:', error)
  } finally {
    ordersLoading.value = false
  }
}

function handleAdd() {
  isEdit.value = false
  editingId.value = null
  resetForm()
  dialogVisible.value = true
}

function handleEdit(book: Book) {
  isEdit.value = true
  editingId.value = book.id
  Object.assign(bookForm, {
    title: book.title,
    author: book.author,
    publisher: book.publisher || '',
    isbn: book.isbn || '',
    price: book.price,
    stock: book.stock,
    description: book.description || '',
    cover_image: book.cover_image || '',
    category: book.category || ''
  })
  dialogVisible.value = true
}

async function handleDelete(id: number) {
  try {
    await api.deleteBook(id)
    ElMessage.success('删除成功')
    fetchBooks()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

async function handleSubmit() {
  if (!bookFormRef.value) return
  
  await bookFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (isEdit.value && editingId.value) {
        await api.updateBook(editingId.value, bookForm)
        ElMessage.success('更新成功')
      } else {
        await api.createBook(bookForm)
        ElMessage.success('添加成功')
      }
      dialogVisible.value = false
      fetchBooks()
    } catch (error) {
      console.error('操作失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

function resetForm() {
  Object.assign(bookForm, {
    title: '',
    author: '',
    publisher: '',
    isbn: '',
    price: 0,
    stock: 0,
    description: '',
    cover_image: '',
    category: ''
  })
}

function handleImageError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultCover
}

function getStatusType(status: OrderStatus): string {
  const map: Record<OrderStatus, string> = {
    pending: 'warning',
    confirmed: 'primary',
    shipped: 'info',
    delivered: 'success',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

function getStatusText(status: OrderStatus): string {
  const map: Record<OrderStatus, string> = {
    pending: '待确认',
    confirmed: '已确认',
    shipped: '已发货',
    delivered: '已完成',
    cancelled: '已取消'
  }
  return map[status] || status
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-CN')
}

function viewOrderDetail(order: Order) {
  currentOrder.value = order
  orderDetailVisible.value = true
}

async function confirmOrder(order: Order) {
  try {
    await api.updateOrderAdmin(order.id, { status: 'confirmed' })
    ElMessage.success('订单已确认')
    fetchOrders()
  } catch (error) {
    console.error('确认订单失败:', error)
  }
}

function openShipDialog(order: Order) {
  shippingOrderId.value = order.id
  shipForm.tracking_company = ''
  shipForm.tracking_number = ''
  shipForm.admin_remark = ''
  shipDialogVisible.value = true
}

async function handleShip() {
  if (!shipFormRef.value || !shippingOrderId.value) return
  
  await shipFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    shipSubmitting.value = true
    try {
      await api.shipOrder(shippingOrderId.value!, shipForm)
      ElMessage.success('发货成功')
      shipDialogVisible.value = false
      fetchOrders()
    } catch (error) {
      console.error('发货失败:', error)
    } finally {
      shipSubmitting.value = false
    }
  })
}

async function completeOrder(order: Order) {
  try {
    await api.updateOrderAdmin(order.id, { status: 'delivered' })
    ElMessage.success('订单已完成')
    fetchOrders()
  } catch (error) {
    console.error('完成订单失败:', error)
  }
}

function openRemarkDialog(order: Order) {
  remarkOrderId.value = order.id
  remarkForm.status = order.status
  remarkForm.admin_remark = order.admin_remark || ''
  remarkDialogVisible.value = true
}

async function handleRemarkSubmit() {
  if (!remarkOrderId.value) return
  
  remarkSubmitting.value = true
  try {
    const updateData: { status?: OrderStatus; admin_remark?: string } = {}
    if (remarkForm.status) {
      updateData.status = remarkForm.status
    }
    if (remarkForm.admin_remark) {
      updateData.admin_remark = remarkForm.admin_remark
    }
    await api.updateOrderAdmin(remarkOrderId.value, updateData)
    ElMessage.success('保存成功')
    remarkDialogVisible.value = false
    fetchOrders()
  } catch (error) {
    console.error('保存备注失败:', error)
  } finally {
    remarkSubmitting.value = false
  }
}
</script>

<style scoped>
.admin-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.admin-tabs {
  width: 100%;
}

.tab-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-top: 16px;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.admin-header h1 {
  font-size: 24px;
  font-weight: 600;
}

.search-bar {
  display: flex;
  gap: 12px;
}

.book-thumbnail {
  width: 40px;
  height: 55px;
  object-fit: cover;
  border-radius: 4px;
}

.book-title {
  font-weight: 500;
}

.price {
  color: var(--secondary-color);
  font-weight: 600;
}

.pagination {
  display: flex;
  justify-content: center;
}

.order-detail {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.order-section h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
}

.order-section p {
  margin: 0;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.order-item {
  display: flex;
  gap: 12px;
  align-items: center;
}

.order-item-cover {
  width: 50px;
  height: 70px;
  object-fit: cover;
  border-radius: 4px;
}

.order-item-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.order-item-title {
  font-weight: 500;
}

.order-item-author {
  font-size: 12px;
  color: #909399;
}
</style>
