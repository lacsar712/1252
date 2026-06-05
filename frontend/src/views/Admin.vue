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

      <el-tab-pane label="优惠券管理" name="coupons">
        <div class="tab-content">
          <div class="admin-header">
            <h1>优惠券管理</h1>
            <el-button type="primary" @click="handleAddCoupon">
              <el-icon><Plus /></el-icon>
              添加优惠券
            </el-button>
          </div>
          
          <div class="search-bar">
            <el-select
              v-model="couponStatusFilter"
              placeholder="优惠券状态"
              clearable
              style="width: 150px"
              @change="fetchCoupons"
            >
              <el-option label="启用中" value="active" />
              <el-option label="已停用" value="inactive" />
              <el-option label="已过期" value="expired" />
              <el-option label="已领完" value="sold_out" />
            </el-select>
            <el-button @click="fetchCoupons">搜索</el-button>
          </div>
          
          <el-table
            :data="coupons"
            v-loading="couponsLoading"
            stripe
            style="width: 100%"
          >
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="name" label="优惠券名称" min-width="150" />
            <el-table-column label="优惠规则" width="180">
              <template #default="{ row }">
                <span class="coupon-rule">
                  满¥{{ row.threshold_amount.toFixed(2) }}减¥{{ row.discount_amount.toFixed(2) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="有效期" width="280">
              <template #default="{ row }">
                <div class="valid-period">
                  <div>{{ formatDate(row.valid_from) }}</div>
                  <div class="arrow">→</div>
                  <div>{{ formatDate(row.valid_to) }}</div>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="发放/已领" width="120">
              <template #default="{ row }">
                <span>{{ row.claimed_quantity }}/{{ row.total_quantity }}</span>
              </template>
            </el-table-column>
            <el-table-column label="每人限领" width="100">
              <template #default="{ row }">
                <span>{{ row.limit_per_user }}张</span>
              </template>
            </el-table-column>
            <el-table-column prop="applicable_categories" label="适用分类" width="120">
              <template #default="{ row }">
                <el-tag v-if="row.applicable_categories" size="small" type="info">
                  {{ row.applicable_categories }}
                </el-tag>
                <span v-else>全品类</span>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getCouponStatusType(row.status)" size="small">
                  {{ getCouponStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleEditCoupon(row)">
                  编辑
                </el-button>
                <el-popconfirm
                  title="确定要删除此优惠券吗？"
                  @confirm="handleDeleteCoupon(row.id)"
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
              v-model:current-page="couponsCurrentPage"
              v-model:page-size="couponsPageSize"
              :total="couponsTotal"
              layout="total, prev, pager, next"
              @current-change="fetchCoupons"
            />
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="作者管理" name="authors">
        <div class="tab-content">
          <div class="admin-header">
            <h1>作者管理</h1>
            <el-button type="primary" @click="handleAddAuthor">
              <el-icon><Plus /></el-icon>
              添加作者
            </el-button>
          </div>
          
          <div class="search-bar">
            <el-input
              v-model="authorSearchQuery"
              placeholder="搜索作者姓名或国家..."
              clearable
              @keyup.enter="fetchAuthors"
              style="max-width: 300px"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select
              v-model="authorStatusFilter"
              placeholder="展示状态"
              clearable
              style="width: 150px"
              @change="fetchAuthors"
            >
              <el-option label="已启用" :value="true" />
              <el-option label="已停用" :value="false" />
            </el-select>
            <el-button @click="fetchAuthors">搜索</el-button>
          </div>
          
          <el-table
            :data="authors"
            v-loading="authorsLoading"
            stripe
            style="width: 100%"
          >
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column label="头像" width="70">
              <template #default="{ row }">
                <img
                  :src="row.avatar || defaultAuthorAvatar"
                  :alt="row.name"
                  class="author-avatar"
                  @error="handleAuthorAvatarError"
                >
              </template>
            </el-table-column>
            <el-table-column prop="name" label="姓名" width="140">
              <template #default="{ row }">
                <span class="author-name">{{ row.name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="country" label="国家/地区" width="120">
              <template #default="{ row }">
                <span>{{ row.country || '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="birth_year" label="出生年份" width="100">
              <template #default="{ row }">
                <span>{{ row.birth_year || '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="代表作" min-width="150">
              <template #default="{ row }">
                <span>{{ row.masterpieces || '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="展示状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                  {{ row.is_active ? '已启用' : '已停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleEditAuthor(row)">
                  编辑
                </el-button>
                <el-popconfirm
                  :title="`确定要删除作者「${row.name}」吗？`"
                  @confirm="handleDeleteAuthor(row)"
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
              v-model:current-page="authorsCurrentPage"
              v-model:page-size="authorsPageSize"
              :total="authorsTotal"
              layout="total, prev, pager, next"
              @current-change="fetchAuthors"
            />
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="出版社管理" name="publishers">
        <div class="tab-content">
          <div class="admin-header">
            <h1>出版社管理</h1>
            <el-button type="primary" @click="handleAddPublisher">
              <el-icon><Plus /></el-icon>
              添加出版社
            </el-button>
          </div>
          
          <div class="search-bar">
            <el-input
              v-model="publisherSearchQuery"
              placeholder="搜索出版社名称或所在地..."
              clearable
              @keyup.enter="fetchPublishers"
              style="max-width: 300px"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select
              v-model="publisherStatusFilter"
              placeholder="启用状态"
              clearable
              style="width: 150px"
              @change="fetchPublishers"
            >
              <el-option label="已启用" :value="true" />
              <el-option label="已停用" :value="false" />
            </el-select>
            <el-button @click="fetchPublishers">搜索</el-button>
          </div>
          
          <el-table
            :data="publishers"
            v-loading="publishersLoading"
            stripe
            style="width: 100%"
          >
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column label="Logo" width="70">
              <template #default="{ row }">
                <img
                  :src="row.logo || defaultPublisherLogo"
                  :alt="row.name"
                  class="publisher-logo"
                  @error="handlePublisherLogoError"
                >
              </template>
            </el-table-column>
            <el-table-column prop="name" label="出版社名称" min-width="160">
              <template #default="{ row }">
                <span class="publisher-name">{{ row.name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="location" label="所在地" width="140">
              <template #default="{ row }">
                <span>{{ row.location || '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="founded_year" label="成立年份" width="100">
              <template #default="{ row }">
                <span>{{ row.founded_year || '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="website" label="官网" min-width="180">
              <template #default="{ row }">
                <a v-if="row.website" :href="row.website" target="_blank" class="link-text">
                  {{ row.website }}
                </a>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="启用状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                  {{ row.is_active ? '已启用' : '已停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleEditPublisher(row)">
                  编辑
                </el-button>
                <el-popconfirm
                  :title="`确定要删除出版社「${row.name}」吗？`"
                  @confirm="handleDeletePublisher(row)"
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
              v-model:current-page="publishersCurrentPage"
              v-model:page-size="publishersPageSize"
              :total="publishersTotal"
              layout="total, prev, pager, next"
              @current-change="fetchPublishers"
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
              <el-input v-model="bookForm.author" placeholder="请输入作者显示文本" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="关联作者" prop="author_ids">
          <el-select
            v-model="selectedAuthorIds"
            multiple
            filterable
            remote
            reserve-keyword
            placeholder="搜索并选择作者（可多选）"
            :remote-method="handleAuthorSearch"
            :loading="authorSearchLoading"
            style="width: 100%"
          >
            <el-option
              v-for="item in authorSearchOptions"
              :key="item.id"
              :label="item.name + (item.country ? `（${item.country}）` : '')"
              :value="item.id"
            >
              <div class="author-option">
                <img :src="item.avatar || defaultAuthorAvatar" :alt="item.name" class="author-option-avatar" @error="handleAuthorOptionAvatarError" />
                <span class="author-option-name">{{ item.name }}</span>
                <span v-if="item.country" class="author-option-country">{{ item.country }}</span>
              </div>
            </el-option>
          </el-select>
          <span class="form-tip">从作者档案中选择，支持多选。若未选择，则仅显示作者文本。</span>
        </el-form-item>

        <el-form-item label="关联出版社" prop="publisher_id">
          <el-select
            v-model="selectedPublisherId"
            filterable
            remote
            reserve-keyword
            placeholder="搜索并选择出版社"
            :remote-method="handlePublisherSearch"
            :loading="publisherSearchLoading"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="item in publisherSearchOptions"
              :key="item.id"
              :label="item.name + (item.location ? `（${item.location}）` : '') + (!item.is_active ? ' - 已禁用' : '')"
              :value="item.id"
              :disabled="!item.is_active"
            >
              <div class="publisher-option">
                <img :src="item.logo || defaultPublisherLogo" :alt="item.name" class="publisher-option-logo" @error="handlePublisherOptionLogoError" />
                <div class="publisher-option-info">
                  <span class="publisher-option-name" :class="{ 'text-muted': !item.is_active }">{{ item.name }}</span>
                  <span v-if="item.location" class="publisher-option-location">{{ item.location }}</span>
                  <el-tag v-if="!item.is_active" size="small" type="info" style="margin-left: 8px;">已禁用</el-tag>
                </div>
              </div>
            </el-option>
          </el-select>
          <span class="form-tip">从出版社档案中选择。选择后将自动填充出版社名称。已禁用的出版社无法选择。</span>
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="出版社文本" prop="publisher">
              <el-input v-model="bookForm.publisher" placeholder="出版社名称（选择关联后自动填充）" />
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
      v-model="couponDialogVisible"
      :title="isCouponEdit ? '编辑优惠券' : '添加优惠券'"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="couponFormRef"
        :model="couponForm"
        :rules="couponRules"
        label-width="100px"
      >
        <el-form-item label="优惠券名称" prop="name">
          <el-input v-model="couponForm.name" placeholder="请输入优惠券名称" maxlength="100" show-word-limit />
        </el-form-item>

        <el-form-item label="优惠券说明" prop="description">
          <el-input
            v-model="couponForm.description"
            type="textarea"
            :rows="2"
            placeholder="请输入优惠券说明（可选）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="门槛金额" prop="threshold_amount">
              <el-input-number
                v-model="couponForm.threshold_amount"
                :min="0"
                :precision="2"
                :step="10"
                controls-position="right"
                style="width: 100%"
              />
              <span class="form-tip">订单满此金额可使用</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优惠金额" prop="discount_amount">
              <el-input-number
                v-model="couponForm.discount_amount"
                :min="0.01"
                :precision="2"
                :step="5"
                controls-position="right"
                style="width: 100%"
              />
              <span class="form-tip">不能大于门槛金额</span>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="有效期开始" prop="valid_from">
              <el-date-picker
                v-model="couponForm.valid_from"
                type="datetime"
                placeholder="选择开始时间"
                style="width: 100%"
                value-format="YYYY-MM-DD HH:mm:ss"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="有效期结束" prop="valid_to">
              <el-date-picker
                v-model="couponForm.valid_to"
                type="datetime"
                placeholder="选择结束时间"
                style="width: 100%"
                value-format="YYYY-MM-DD HH:mm:ss"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="发放数量" prop="total_quantity">
              <el-input-number
                v-model="couponForm.total_quantity"
                :min="1"
                controls-position="right"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="每人限领" prop="limit_per_user">
              <el-input-number
                v-model="couponForm.limit_per_user"
                :min="1"
                :max="10"
                controls-position="right"
                style="width: 100%"
              />
              <span class="form-tip">每人最多领取张数</span>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="适用分类" prop="applicable_categories">
          <el-input
            v-model="couponForm.applicable_categories"
            placeholder="请输入适用分类，多个分类用逗号分隔（留空表示全品类）"
          />
          <span class="form-tip">例如：小说,科技,教育</span>
        </el-form-item>

        <el-form-item label="启用状态" prop="status">
          <el-radio-group v-model="couponForm.status">
            <el-radio value="active">启用</el-radio>
            <el-radio value="inactive">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="couponDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="couponSubmitting" @click="handleCouponSubmit">
          {{ isCouponEdit ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="authorDialogVisible"
      :title="isAuthorEdit ? '编辑作者' : '添加作者'"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="authorFormRef"
        :model="authorForm"
        :rules="authorRules"
        label-width="100px"
      >
        <el-form-item label="作者姓名" prop="name">
          <el-input v-model="authorForm.name" placeholder="请输入作者姓名" maxlength="100" show-word-limit />
        </el-form-item>

        <el-form-item label="头像URL" prop="avatar">
          <el-input v-model="authorForm.avatar" placeholder="请输入头像图片URL（可选）" />
          <div v-if="authorForm.avatar" class="avatar-preview">
            <img :src="authorForm.avatar" alt="头像预览" @error="handleAuthorFormAvatarError" />
          </div>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="国家/地区" prop="country">
              <el-input v-model="authorForm.country" placeholder="请输入国家或地区" maxlength="100" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出生年份" prop="birth_year">
              <el-input-number
                v-model="authorForm.birth_year"
                :min="0"
                :max="3000"
                :precision="0"
                controls-position="right"
                style="width: 100%"
                placeholder="请输入出生年份"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="作者简介" prop="bio">
          <el-input
            v-model="authorForm.bio"
            type="textarea"
            :rows="3"
            placeholder="请输入作者简介（可选）"
          />
        </el-form-item>

        <el-form-item label="代表作说明" prop="masterpieces">
          <el-input
            v-model="authorForm.masterpieces"
            type="textarea"
            :rows="2"
            placeholder="请输入代表作说明（可选）"
          />
        </el-form-item>

        <el-form-item label="展示状态" prop="is_active">
          <el-radio-group v-model="authorForm.is_active">
            <el-radio :value="true">启用</el-radio>
            <el-radio :value="false">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="authorDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="authorSubmitting" @click="handleAuthorSubmit">
          {{ isAuthorEdit ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="publisherDialogVisible"
      :title="isPublisherEdit ? '编辑出版社' : '添加出版社'"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="publisherFormRef"
        :model="publisherForm"
        :rules="publisherRules"
        label-width="100px"
      >
        <el-form-item label="出版社名称" prop="name">
          <el-input
            v-model="publisherForm.name"
            placeholder="请输入出版社名称"
            maxlength="100"
            show-word-limit
            @blur="checkPublisherNameUnique"
          />
          <span v-if="publisherNameError" class="error-text">{{ publisherNameError }}</span>
        </el-form-item>

        <el-form-item label="Logo URL" prop="logo">
          <el-input v-model="publisherForm.logo" placeholder="请输入Logo图片URL（可选）" />
          <div v-if="publisherForm.logo" class="logo-preview">
            <img :src="publisherForm.logo" alt="Logo预览" @error="handlePublisherFormLogoError" />
          </div>
          <span class="form-tip">建议尺寸：200x200像素。如果Logo加载失败将显示默认图标。</span>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="所在地" prop="location">
              <el-input v-model="publisherForm.location" placeholder="请输入所在地" maxlength="200" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="成立年份" prop="founded_year">
              <el-input-number
                v-model="publisherForm.founded_year"
                :min="0"
                :max="3000"
                :precision="0"
                controls-position="right"
                style="width: 100%"
                placeholder="请输入成立年份"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="官网地址" prop="website">
          <el-input v-model="publisherForm.website" placeholder="请输入官网地址（可选）" maxlength="500" />
        </el-form-item>

        <el-form-item label="出版社简介" prop="description">
          <el-input
            v-model="publisherForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入出版社简介（可选）"
          />
        </el-form-item>

        <el-form-item label="启用状态" prop="is_active">
          <el-radio-group v-model="publisherForm.is_active">
            <el-radio :value="true">启用</el-radio>
            <el-radio :value="false">停用</el-radio>
          </el-radio-group>
          <span class="form-tip">注意：已有关联图书的出版社无法停用。</span>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="publisherDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="publisherSubmitting" @click="handlePublisherSubmit">
          {{ isPublisherEdit ? '保存' : '添加' }}
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
              <div class="order-amount-info">
                <div v-if="currentOrder.discount_amount > 0" class="original-amount">
                  原价：<span class="line-through">¥{{ currentOrder.original_amount.toFixed(2) }}</span>
                </div>
                <div v-if="currentOrder.discount_amount > 0" class="discount-amount">
                  优惠：<span class="discount">-¥{{ currentOrder.discount_amount.toFixed(2) }}</span>
                </div>
                <div class="final-amount">
                  实付：<span class="price">¥{{ currentOrder.total_amount.toFixed(2) }}</span>
                </div>
              </div>
            </el-descriptions-item>
            <el-descriptions-item v-if="currentOrder.used_coupon" label="使用优惠券">
              <el-tag type="warning" size="small">
                {{ currentOrder.used_coupon.coupon.name }}
              </el-tag>
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
import type { Book, BookCreate, Order, OrderStatus, Coupon, CouponCreate, CouponUpdate, CouponStatus as CouponStatusType, Author, AuthorCreate, AuthorUpdate, AuthorSearchResult, Publisher, PublisherCreate, PublisherUpdate, PublisherSearchResult } from '@/types'
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

const couponsLoading = ref(false)
const coupons = ref<Coupon[]>([])
const couponsTotal = ref(0)
const couponsCurrentPage = ref(1)
const couponsPageSize = ref(10)
const couponStatusFilter = ref<CouponStatusType | ''>('')
const couponDialogVisible = ref(false)
const isCouponEdit = ref(false)
const couponEditingId = ref<number | null>(null)
const couponSubmitting = ref(false)
const couponFormRef = ref<FormInstance>()

const couponForm = reactive<CouponCreate>({
  name: '',
  description: '',
  threshold_amount: 0,
  discount_amount: 0,
  valid_from: '',
  valid_to: '',
  total_quantity: 100,
  limit_per_user: 1,
  applicable_categories: '',
  status: 'active'
})

const couponRules: FormRules = {
  name: [{ required: true, message: '请输入优惠券名称', trigger: 'blur' }],
  threshold_amount: [{ required: true, message: '请输入门槛金额', trigger: 'blur' }],
  discount_amount: [{ required: true, message: '请输入优惠金额', trigger: 'blur' }],
  valid_from: [{ required: true, message: '请选择有效期开始时间', trigger: 'change' }],
  valid_to: [{ required: true, message: '请选择有效期结束时间', trigger: 'change' }],
  total_quantity: [{ required: true, message: '请输入发放数量', trigger: 'blur' }],
  limit_per_user: [{ required: true, message: '请输入每人限领次数', trigger: 'blur' }]
}

const authorsLoading = ref(false)
const authors = ref<Author[]>([])
const authorsTotal = ref(0)
const authorsCurrentPage = ref(1)
const authorsPageSize = ref(10)
const authorSearchQuery = ref('')
const authorStatusFilter = ref<boolean | ''>('')
const authorDialogVisible = ref(false)
const isAuthorEdit = ref(false)
const authorEditingId = ref<number | null>(null)
const authorSubmitting = ref(false)
const authorFormRef = ref<FormInstance>()
const defaultAuthorAvatar = 'https://via.placeholder.com/60x60/8b5cf6/ffffff?text=Author'

const authorSearchLoading = ref(false)
const authorSearchOptions = ref<AuthorSearchResult[]>([])
const selectedAuthorIds = ref<number[]>([])

const authorForm = reactive<AuthorCreate>({
  name: '',
  avatar: '',
  bio: '',
  country: '',
  birth_year: undefined,
  masterpieces: '',
  is_active: true
})

const authorRules: FormRules = {
  name: [{ required: true, message: '请输入作者姓名', trigger: 'blur' }]
}

const publishersLoading = ref(false)
const publishers = ref<Publisher[]>([])
const publishersTotal = ref(0)
const publishersCurrentPage = ref(1)
const publishersPageSize = ref(10)
const publisherSearchQuery = ref('')
const publisherStatusFilter = ref<boolean | ''>('')
const publisherDialogVisible = ref(false)
const isPublisherEdit = ref(false)
const publisherEditingId = ref<number | null>(null)
const publisherSubmitting = ref(false)
const publisherFormRef = ref<FormInstance>()
const defaultPublisherLogo = 'https://via.placeholder.com/60x60/f59e0b/ffffff?text=Pub'
const publisherNameError = ref('')

const publisherSearchLoading = ref(false)
const publisherSearchOptions = ref<PublisherSearchResult[]>([])
const selectedPublisherId = ref<number | null>(null)

const publisherForm = reactive<PublisherCreate>({
  name: '',
  logo: '',
  website: '',
  location: '',
  description: '',
  founded_year: undefined,
  is_active: true
})

const publisherRules: FormRules = {
  name: [{ required: true, message: '请输入出版社名称', trigger: 'blur' }]
}

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
  if (newTab === 'coupons' && coupons.value.length === 0) {
    fetchCoupons()
  }
  if (newTab === 'authors' && authors.value.length === 0) {
    fetchAuthors()
  }
  if (newTab === 'publishers' && publishers.value.length === 0) {
    fetchPublishers()
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

async function handleDelete(id: number) {
  try {
    await api.deleteBook(id)
    ElMessage.success('删除成功')
    fetchBooks()
  } catch (error) {
    console.error('删除失败:', error)
  }
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

async function fetchCoupons() {
  couponsLoading.value = true
  try {
    const response = await api.getAdminCoupons({
      status: couponStatusFilter.value || undefined,
      page: couponsCurrentPage.value,
      page_size: couponsPageSize.value
    })
    coupons.value = response.items
    couponsTotal.value = response.total
  } catch (error) {
    console.error('获取优惠券列表失败:', error)
  } finally {
    couponsLoading.value = false
  }
}

function handleAddCoupon() {
  isCouponEdit.value = false
  couponEditingId.value = null
  resetCouponForm()
  couponDialogVisible.value = true
}

function handleEditCoupon(coupon: Coupon) {
  isCouponEdit.value = true
  couponEditingId.value = coupon.id
  Object.assign(couponForm, {
    name: coupon.name,
    description: coupon.description || '',
    threshold_amount: coupon.threshold_amount,
    discount_amount: coupon.discount_amount,
    valid_from: coupon.valid_from,
    valid_to: coupon.valid_to,
    total_quantity: coupon.total_quantity,
    limit_per_user: coupon.limit_per_user,
    applicable_categories: coupon.applicable_categories || '',
    status: coupon.status
  })
  couponDialogVisible.value = true
}

async function handleDeleteCoupon(id: number) {
  try {
    await api.deleteCoupon(id)
    ElMessage.success('删除成功')
    fetchCoupons()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

async function handleCouponSubmit() {
  if (!couponFormRef.value) return
  
  await couponFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    couponSubmitting.value = true
    try {
      if (isCouponEdit.value && couponEditingId.value) {
        const updateData: CouponUpdate = { ...couponForm }
        await api.updateCoupon(couponEditingId.value, updateData)
        ElMessage.success('更新成功')
      } else {
        await api.createCoupon(couponForm)
        ElMessage.success('添加成功')
      }
      couponDialogVisible.value = false
      fetchCoupons()
    } catch (error) {
      console.error('操作失败:', error)
    } finally {
      couponSubmitting.value = false
    }
  })
}

function resetCouponForm() {
  Object.assign(couponForm, {
    name: '',
    description: '',
    threshold_amount: 0,
    discount_amount: 0,
    valid_from: '',
    valid_to: '',
    total_quantity: 100,
    limit_per_user: 1,
    applicable_categories: '',
    status: 'active'
  })
}

function getCouponStatusType(status: CouponStatusType): string {
  const map: Record<CouponStatusType, string> = {
    active: 'success',
    inactive: 'info',
    expired: 'danger',
    sold_out: 'warning'
  }
  return map[status] || 'info'
}

function getCouponStatusText(status: CouponStatusType): string {
  const map: Record<CouponStatusType, string> = {
    active: '启用中',
    inactive: '已停用',
    expired: '已过期',
    sold_out: '已领完'
  }
  return map[status] || status
}

async function fetchAuthors() {
  authorsLoading.value = true
  try {
    const response = await api.getAuthors({
      page: authorsCurrentPage.value,
      page_size: authorsPageSize.value,
      search: authorSearchQuery.value || undefined,
      is_active: authorStatusFilter.value === '' ? undefined : authorStatusFilter.value
    })
    authors.value = response.items
    authorsTotal.value = response.total
  } catch (error) {
    console.error('获取作者列表失败:', error)
  } finally {
    authorsLoading.value = false
  }
}

function handleAddAuthor() {
  isAuthorEdit.value = false
  authorEditingId.value = null
  resetAuthorForm()
  authorDialogVisible.value = true
}

function handleEditAuthor(author: Author) {
  isAuthorEdit.value = true
  authorEditingId.value = author.id
  Object.assign(authorForm, {
    name: author.name,
    avatar: author.avatar || '',
    bio: author.bio || '',
    country: author.country || '',
    birth_year: author.birth_year || undefined,
    masterpieces: author.masterpieces || '',
    is_active: author.is_active
  })
  authorDialogVisible.value = true
}

async function handleDeleteAuthor(author: Author) {
  try {
    const checkResult = await api.checkAuthorDelete(author.id)
    if (!checkResult.can_delete) {
      ElMessage.warning(checkResult.message || '该作者有关联的图书，无法删除')
      return
    }
    await api.deleteAuthor(author.id)
    ElMessage.success('删除成功')
    fetchAuthors()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

async function handleAuthorSubmit() {
  if (!authorFormRef.value) return
  
  await authorFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    authorSubmitting.value = true
    try {
      if (isAuthorEdit.value && authorEditingId.value) {
        const updateData: AuthorUpdate = { ...authorForm }
        await api.updateAuthor(authorEditingId.value, updateData)
        ElMessage.success('更新成功')
      } else {
        await api.createAuthor(authorForm)
        ElMessage.success('添加成功')
      }
      authorDialogVisible.value = false
      fetchAuthors()
    } catch (error) {
      console.error('操作失败:', error)
    } finally {
      authorSubmitting.value = false
    }
  })
}

function resetAuthorForm() {
  Object.assign(authorForm, {
    name: '',
    avatar: '',
    bio: '',
    country: '',
    birth_year: undefined,
    masterpieces: '',
    is_active: true
  })
}

async function handleAuthorSearch(query: string) {
  if (!query || query.trim() === '') {
    authorSearchOptions.value = []
    return
  }
  authorSearchLoading.value = true
  try {
    authorSearchOptions.value = await api.searchAuthors(query.trim(), 20)
  } catch (error) {
    console.error('搜索作者失败:', error)
  } finally {
    authorSearchLoading.value = false
  }
}

function handleAuthorAvatarError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultAuthorAvatar
}

function handleAuthorFormAvatarError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultAuthorAvatar
}

function handleAuthorOptionAvatarError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultAuthorAvatar
}

async function fetchPublishers() {
  publishersLoading.value = true
  try {
    const response = await api.getPublishers({
      page: publishersCurrentPage.value,
      page_size: publishersPageSize.value,
      search: publisherSearchQuery.value || undefined,
      is_active: publisherStatusFilter.value === '' ? undefined : publisherStatusFilter.value
    })
    publishers.value = response.items
    publishersTotal.value = response.total
  } catch (error) {
    console.error('获取出版社列表失败:', error)
  } finally {
    publishersLoading.value = false
  }
}

function handleAddPublisher() {
  isPublisherEdit.value = false
  publisherEditingId.value = null
  resetPublisherForm()
  publisherNameError.value = ''
  publisherDialogVisible.value = true
}

function handleEditPublisher(publisher: Publisher) {
  isPublisherEdit.value = true
  publisherEditingId.value = publisher.id
  Object.assign(publisherForm, {
    name: publisher.name,
    logo: publisher.logo || '',
    website: publisher.website || '',
    location: publisher.location || '',
    description: publisher.description || '',
    founded_year: publisher.founded_year || undefined,
    is_active: publisher.is_active
  })
  publisherNameError.value = ''
  publisherDialogVisible.value = true
}

async function handleDeletePublisher(publisher: Publisher) {
  try {
    const checkResult = await api.checkPublisherDelete(publisher.id)
    if (!checkResult.can_delete) {
      ElMessage.warning(checkResult.message || '该出版社有关联的图书，无法删除')
      return
    }
    await api.deletePublisher(publisher.id)
    ElMessage.success('删除成功')
    fetchPublishers()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

async function checkPublisherNameUnique() {
  if (!publisherForm.name || publisherForm.name.trim() === '') {
    publisherNameError.value = ''
    return
  }
  try {
    const result = await api.checkPublisherName(
      publisherForm.name.trim(),
      isPublisherEdit.value && publisherEditingId.value ? publisherEditingId.value : undefined
    )
    if (!result.available) {
      publisherNameError.value = result.message || '名称已存在'
    } else {
      publisherNameError.value = ''
    }
  } catch (error) {
    console.error('校验名称失败:', error)
  }
}

async function handlePublisherSubmit() {
  if (!publisherFormRef.value) return
  
  await publisherFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    if (publisherNameError.value) {
      ElMessage.error(publisherNameError.value)
      return
    }
    
    publisherSubmitting.value = true
    try {
      if (isPublisherEdit.value && publisherEditingId.value) {
        const updateData: PublisherUpdate = { ...publisherForm }
        await api.updatePublisher(publisherEditingId.value, updateData)
        ElMessage.success('更新成功')
      } else {
        await api.createPublisher(publisherForm)
        ElMessage.success('添加成功')
      }
      publisherDialogVisible.value = false
      fetchPublishers()
    } catch (error) {
      console.error('操作失败:', error)
    } finally {
      publisherSubmitting.value = false
    }
  })
}

function resetPublisherForm() {
  Object.assign(publisherForm, {
    name: '',
    logo: '',
    website: '',
    location: '',
    description: '',
    founded_year: undefined,
    is_active: true
  })
}

async function handlePublisherSearch(query: string) {
  if (!query || query.trim() === '') {
    publisherSearchOptions.value = []
    return
  }
  publisherSearchLoading.value = true
  try {
    publisherSearchOptions.value = await api.searchPublishers(query.trim(), 20, true)
  } catch (error) {
    console.error('搜索出版社失败:', error)
  } finally {
    publisherSearchLoading.value = false
  }
}

function handlePublisherLogoError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultPublisherLogo
}

function handlePublisherFormLogoError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultPublisherLogo
}

function handlePublisherOptionLogoError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultPublisherLogo
}

watch(selectedPublisherId, (newVal) => {
  if (newVal) {
    const selected = publisherSearchOptions.value.find(p => p.id === newVal)
    if (selected) {
      bookForm.publisher = selected.name
    }
  }
})

function handleEdit(book: Book) {
  isEdit.value = true
  editingId.value = book.id
  Object.assign(bookForm, {
    title: book.title,
    author: book.author,
    publisher: book.publisher || '',
    publisher_id: book.publisher_id || null,
    isbn: book.isbn || '',
    price: book.price,
    stock: book.stock,
    description: book.description || '',
    cover_image: book.cover_image || '',
    category: book.category || ''
  })
  selectedAuthorIds.value = book.authors ? book.authors.map(a => a.id) : []
  selectedPublisherId.value = book.publisher_id || null
  if (book.publisher_id) {
    publisherSearchOptions.value = [{
      id: book.publisher_id,
      name: book.publisher || '',
      location: book.publisher_info?.location || null,
      logo: book.publisher_info?.logo || null,
      is_active: book.publisher_info?.is_active ?? true
    }]
  }
  dialogVisible.value = true
}

function handleAdd() {
  isEdit.value = false
  editingId.value = null
  resetForm()
  selectedAuthorIds.value = []
  selectedPublisherId.value = null
  publisherSearchOptions.value = []
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!bookFormRef.value) return
  
  await bookFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    submitting.value = true
    try {
      const submitData: BookCreate = {
        ...bookForm,
        author_ids: selectedAuthorIds.value.length > 0 ? selectedAuthorIds.value : undefined,
        publisher_id: selectedPublisherId.value || undefined
      }
      if (isEdit.value && editingId.value) {
        await api.updateBook(editingId.value, submitData)
        ElMessage.success('更新成功')
      } else {
        await api.createBook(submitData)
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

.coupon-rule {
  font-weight: 600;
  color: var(--danger-color);
}

.valid-period {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 12px;
}

.valid-period .arrow {
  color: var(--text-muted);
  text-align: center;
}

.form-tip {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-muted);
}

.order-amount-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.original-amount {
  font-size: 12px;
}

.line-through {
  text-decoration: line-through;
  color: var(--text-muted);
}

.discount-amount {
  font-size: 12px;
}

.discount {
  color: var(--danger-color);
  font-weight: 600;
}

.final-amount {
  font-size: 14px;
}

.author-avatar {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 50%;
}

.author-name {
  font-weight: 500;
}

.avatar-preview {
  margin-top: 8px;
}

.avatar-preview img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.author-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-option-avatar {
  width: 24px;
  height: 24px;
  object-fit: cover;
  border-radius: 50%;
}

.author-option-name {
  font-weight: 500;
}

.author-option-country {
  font-size: 12px;
  color: var(--text-muted);
  margin-left: 4px;
}

.publisher-logo {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 6px;
}

.publisher-name {
  font-weight: 500;
}

.link-text {
  color: var(--primary-color);
  text-decoration: none;
  font-size: 12px;
}

.link-text:hover {
  text-decoration: underline;
}

.logo-preview {
  margin-top: 8px;
}

.logo-preview img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.publisher-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.publisher-option-logo {
  width: 28px;
  height: 28px;
  object-fit: cover;
  border-radius: 4px;
}

.publisher-option-info {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}

.publisher-option-name {
  font-weight: 500;
}

.publisher-option-location {
  font-size: 12px;
  color: var(--text-muted);
  margin-left: 4px;
}

.text-muted {
  color: var(--text-muted);
}

.error-text {
  color: var(--danger-color);
  font-size: 12px;
  margin-top: 4px;
  display: block;
}
</style>
