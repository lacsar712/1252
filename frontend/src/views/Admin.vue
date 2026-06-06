<template>
  <div class="admin-page">
    <el-tabs v-model="activeTab" class="admin-tabs">
      <el-tab-pane label="数据仪表盘" name="dashboard">
        <Dashboard />
      </el-tab-pane>
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
            <el-select
              v-model="selectedTagFilter"
              placeholder="标签筛选"
              clearable
              style="width: 200px"
              @change="fetchBooks"
            >
              <el-option
                v-for="item in activeTags"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              >
                <div class="tag-option">
                  <el-tag
                    :style="{ backgroundColor: item.color || '#409eff', borderColor: item.color || '#409eff' }"
                    size="small"
                    effect="dark"
                  >
                    {{ item.name }}
                  </el-tag>
                </div>
              </el-option>
            </el-select>
            <el-switch
              v-model="lowStockFilter"
              active-text="低库存"
              inline-prompt
              @change="fetchBooks"
            />
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
            <el-table-column label="标签" width="200">
              <template #default="{ row }">
                <div class="book-tags" v-if="row.tags && row.tags.length > 0">
                  <el-tag
                    v-for="tag in row.tags"
                    :key="tag.id"
                    :style="{ backgroundColor: tag.color || '#409eff', borderColor: tag.color || '#409eff' }"
                    size="small"
                    effect="dark"
                    style="margin-right: 4px; margin-bottom: 4px;"
                  >
                    {{ tag.name }}
                  </el-tag>
                </div>
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
              multiple
              collapse-tags
              collapse-tags-tooltip
              style="min-width: 200px"
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

      <el-tab-pane label="书单管理" name="book-lists">
        <div class="tab-content">
          <div class="admin-header">
            <h1>书单管理</h1>
            <el-button type="primary" @click="handleAddBookList">
              <el-icon><Plus /></el-icon>
              添加书单
            </el-button>
          </div>
          
          <div class="search-bar">
            <el-input
              v-model="bookListSearchQuery"
              placeholder="搜索书单标题或简介..."
              clearable
              @keyup.enter="fetchBookLists"
              style="max-width: 300px"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select
              v-model="bookListStatusFilter"
              placeholder="展示状态"
              clearable
              style="width: 150px"
              @change="fetchBookLists"
            >
              <el-option label="已启用" :value="true" />
              <el-option label="已停用" :value="false" />
            </el-select>
            <el-button @click="fetchBookLists">搜索</el-button>
          </div>
          
          <el-table
            :data="bookLists"
            v-loading="bookListsLoading"
            stripe
            style="width: 100%"
          >
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column label="封面" width="80">
              <template #default="{ row }">
                <img
                  :src="row.cover_image || defaultBookListCover"
                  :alt="row.title"
                  class="booklist-thumbnail"
                  @error="handleBookListCoverError"
                >
              </template>
            </el-table-column>
            <el-table-column prop="title" label="书单标题" min-width="180">
              <template #default="{ row }">
                <span class="booklist-title">{{ row.title }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="category" label="分类" width="120">
              <template #default="{ row }">
                <el-tag v-if="row.category" size="small">{{ row.category }}</el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="sort_weight" label="排序权重" width="100" />
            <el-table-column label="展示状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                  {{ row.is_active ? '已启用' : '已停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="280" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleManageBooks(row)">
                  管理图书
                </el-button>
                <el-button link type="primary" @click="handleEditBookList(row)">
                  编辑
                </el-button>
                <el-popconfirm
                  :title="`确定要删除书单「${row.title}」吗？`"
                  @confirm="handleDeleteBookList(row.id)"
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
              v-model:current-page="bookListsCurrentPage"
              v-model:page-size="bookListsPageSize"
              :total="bookListsTotal"
              layout="total, prev, pager, next"
              @current-change="fetchBookLists"
            />
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="会员等级管理" name="member-levels">
        <div class="tab-content">
          <div class="admin-header">
            <h1>会员等级管理</h1>
            <el-button type="primary" @click="handleAddMemberLevel">
              <el-icon><Plus /></el-icon>
              添加等级
            </el-button>
          </div>
          
          <div class="search-bar">
            <el-select
              v-model="memberLevelStatusFilter"
              placeholder="启用状态"
              clearable
              style="width: 150px"
              @change="fetchMemberLevels"
            >
              <el-option label="已启用" :value="true" />
              <el-option label="已停用" :value="false" />
            </el-select>
            <el-button @click="fetchMemberLevels">搜索</el-button>
          </div>
          
          <el-table
            :data="memberLevels"
            v-loading="memberLevelsLoading"
            stripe
            style="width: 100%"
          >
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column label="等级标识" width="100">
              <template #default="{ row }">
                <el-tag
                  :style="{ backgroundColor: row.badge_color || '#409eff', borderColor: row.badge_color || '#409eff' }"
                  size="small"
                  effect="dark"
                >
                  {{ row.name }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="等级名称" width="120" />
            <el-table-column label="升级门槛(消费金额)" width="160">
              <template #default="{ row }">
                ¥{{ row.threshold_amount.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="折扣比例" width="100">
              <template #default="{ row }">
                <span class="discount-text">{{ (row.discount_rate * 10).toFixed(1) }}折</span>
              </template>
            </el-table-column>
            <el-table-column label="等级标识颜色" width="120">
              <template #default="{ row }">
                <span class="color-preview" :style="{ backgroundColor: row.badge_color || '#409eff' }"></span>
                <span class="color-hex">{{ row.badge_color || '默认' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="sort_order" label="排序权重" width="100" />
            <el-table-column label="启用状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                  {{ row.is_active ? '已启用' : '已停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleEditMemberLevel(row)">
                  编辑
                </el-button>
                <el-popconfirm
                  :title="`确定要删除等级「${row.name}」吗？`"
                  @confirm="handleDeleteMemberLevel(row.id)"
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
              v-model:current-page="memberLevelsCurrentPage"
              v-model:page-size="memberLevelsPageSize"
              :total="memberLevelsTotal"
              layout="total, prev, pager, next"
              @current-change="fetchMemberLevels"
            />
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="用户管理" name="member-users">
        <div class="tab-content">
          <div class="admin-header">
            <h1>用户管理</h1>
          </div>
          
          <div class="search-bar">
            <el-input
              v-model="memberUserSearchQuery"
              placeholder="搜索用户名或邮箱..."
              clearable
              @keyup.enter="fetchMemberUsers"
              style="max-width: 300px"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button @click="fetchMemberUsers">搜索</el-button>
          </div>
          
          <el-table
            :data="memberUsers"
            v-loading="memberUsersLoading"
            stripe
            style="width: 100%"
          >
            <el-table-column prop="id" label="用户ID" width="80" />
            <el-table-column prop="username" label="用户名" width="120" />
            <el-table-column prop="email" label="邮箱" min-width="180" />
            <el-table-column label="累计消费" width="120">
              <template #default="{ row }">
                <span class="price">¥{{ row.total_spent.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="会员等级" width="120">
              <template #default="{ row }">
                <el-tag
                  v-if="row.member_level?.current_level"
                  :style="{ backgroundColor: row.member_level.current_level.badge_color || '#409eff', borderColor: row.member_level.current_level.badge_color || '#409eff' }"
                  size="small"
                  effect="dark"
                >
                  {{ row.member_level.current_level.name }}
                </el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="等级来源" width="100">
              <template #default="{ row }">
                <el-tag
                  v-if="row.member_level?.is_manual"
                  type="warning"
                  size="small"
                >
                  手动
                </el-tag>
                <el-tag
                  v-else
                  type="success"
                  size="small"
                >
                  自动
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="注册时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="300" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="openAdjustLevelDialog(row)">
                  调整等级
                </el-button>
                <el-button
                  v-if="row.member_level?.is_manual"
                  link
                  type="warning"
                  @click="handleClearManualLevel(row)"
                >
                  清除手动等级
                </el-button>
                <el-button link type="info" @click="handleRecalculateUserSpent(row)">
                  重新计算累计消费
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="pagination">
            <el-pagination
              v-model:current-page="memberUsersCurrentPage"
              v-model:page-size="memberUsersPageSize"
              :total="memberUsersTotal"
              layout="total, prev, pager, next"
              @current-change="fetchMemberUsers"
            />
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="标签管理" name="tags">
        <div class="tab-content">
          <div class="admin-header">
            <h1>标签管理</h1>
            <el-button type="primary" @click="handleAddTag">
              <el-icon><Plus /></el-icon>
              添加标签
            </el-button>
          </div>
          
          <div class="search-bar">
            <el-input
              v-model="tagSearchQuery"
              placeholder="搜索标签名称/说明..."
              clearable
              @keyup.enter="fetchTags"
              style="max-width: 300px"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select
              v-model="tagStatusFilter"
              placeholder="启用状态"
              clearable
              style="width: 150px"
              @change="fetchTags"
            >
              <el-option label="已启用" :value="true" />
              <el-option label="已停用" :value="false" />
            </el-select>
            <el-button @click="fetchTags">搜索</el-button>
          </div>
          
          <el-table
            :data="tags"
            v-loading="tagsLoading"
            stripe
            style="width: 100%"
          >
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column label="标签颜色" width="140">
              <template #default="{ row }">
                <span class="color-preview" :style="{ backgroundColor: row.color || '#409eff' }"></span>
                <span class="color-hex">{{ row.color || '#409eff' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="标签名称" width="140" />
            <el-table-column prop="description" label="说明" min-width="180">
              <template #default="{ row }">
                <span>{{ row.description || '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="sort_order" label="排序权重" width="100" />
            <el-table-column label="启用状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                  {{ row.is_active ? '已启用' : '已停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleEditTag(row)">
                  编辑
                </el-button>
                <el-popconfirm
                  :title="`确定要删除标签「${row.name}」吗？`"
                  @confirm="handleDeleteTag(row)"
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
              v-model:current-page="tagsCurrentPage"
              v-model:page-size="tagsPageSize"
              :total="tagsTotal"
              layout="total, prev, pager, next"
              @current-change="fetchTags"
            />
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="消息管理" name="messages">
        <div class="tab-content">
          <div class="admin-header">
            <h1>消息管理</h1>
            <el-button type="primary" @click="openAnnouncementDialog">
              <el-icon><Plus /></el-icon>
              发布公告
            </el-button>
          </div>

          <div class="message-stats">
            <el-row :gutter="16">
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-label">公告总数</div>
                  <div class="stat-value">{{ messageStats.total_messages }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-label">生效中</div>
                  <div class="stat-value">{{ messageStats.active_messages }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-label">接收人次</div>
                  <div class="stat-value">{{ messageStats.total_recipients }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-label">阅读率</div>
                  <div class="stat-value">{{ messageStats.read_rate.toFixed(1) }}%</div>
                </div>
              </el-col>
            </el-row>
          </div>
          
          <el-table
            :data="adminMessages"
            v-loading="adminMessagesLoading"
            stripe
            style="width: 100%"
          >
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="title" label="标题" min-width="200" />
            <el-table-column label="内容" min-width="250">
              <template #default="{ row }">
                <span class="content-preview">{{ row.content }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="recipient_type" label="发送对象" width="120">
              <template #default="{ row }">
                <el-tag size="small" :type="row.recipient_type === 'all_users' ? 'success' : 'warning'">
                  {{ row.recipient_type === 'all_users' ? '全体用户' : '指定用户' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="有效期" width="280">
              <template #default="{ row }">
                <span v-if="row.valid_from && row.valid_to">
                  {{ formatDate(row.valid_from) }} ~ {{ formatDate(row.valid_to) }}
                </span>
                <span v-else>永久有效</span>
              </template>
            </el-table-column>
            <el-table-column prop="sender_name" label="发布人" width="100" />
            <el-table-column prop="created_at" label="发布时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                  {{ row.is_active ? '生效中' : '已停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="toggleMessageActive(row)">
                  {{ row.is_active ? '停用' : '启用' }}
                </el-button>
                <el-popconfirm
                  title="确定要删除此公告吗？"
                  @confirm="handleDeleteAnnouncement(row.id)"
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
              v-model:current-page="adminMessagesCurrentPage"
              v-model:page-size="adminMessagesPageSize"
              :total="adminMessagesTotal"
              layout="total, prev, pager, next"
              @current-change="fetchAdminMessages"
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

        <el-form-item label="关联标签" prop="tag_ids">
          <el-select
            v-model="selectedTagIds"
            multiple
            filterable
            remote
            reserve-keyword
            placeholder="搜索并选择标签（可多选）"
            :remote-method="handleTagSearch"
            :loading="tagSearchLoading"
            style="width: 100%"
          >
            <el-option
              v-for="item in tagSearchOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
              :disabled="!item.is_active"
            >
              <div class="tag-option">
                <el-tag
                  :style="{ backgroundColor: item.color || '#409eff', borderColor: item.color || '#409eff' }"
                  size="small"
                  effect="dark"
                >
                  {{ item.name }}
                </el-tag>
                <el-tag v-if="!item.is_active" size="small" type="info" style="margin-left: 8px;">已禁用</el-tag>
              </div>
            </el-option>
          </el-select>
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
      v-model="bookListDialogVisible"
      :title="isBookListEdit ? '编辑书单' : '添加书单'"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="bookListFormRef"
        :model="bookListForm"
        :rules="bookListRules"
        label-width="100px"
      >
        <el-form-item label="书单标题" prop="title">
          <el-input v-model="bookListForm.title" placeholder="请输入书单标题" maxlength="200" show-word-limit />
        </el-form-item>

        <el-form-item label="书单简介" prop="description">
          <el-input
            v-model="bookListForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入书单简介"
          />
        </el-form-item>

        <el-form-item label="封面URL" prop="cover_image">
          <el-input v-model="bookListForm.cover_image" placeholder="请输入封面图片URL" />
          <div v-if="bookListForm.cover_image" class="cover-preview">
            <img :src="bookListForm.cover_image" alt="封面预览" @error="handleBookListFormCoverError" />
          </div>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="关联分类" prop="category">
              <el-input v-model="bookListForm.category" placeholder="请输入关联分类" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序权重" prop="sort_weight">
              <el-input-number
                v-model="bookListForm.sort_weight"
                :min="0"
                :max="999"
                controls-position="right"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="展示状态" prop="is_active">
          <el-radio-group v-model="bookListForm.is_active">
            <el-radio :value="true">启用</el-radio>
            <el-radio :value="false">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="bookListDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="bookListSubmitting" @click="handleBookListSubmit">
          {{ isBookListEdit ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="bookListBooksDialogVisible"
      :title="`管理图书 - ${currentBookList?.title}`"
      width="900px"
      destroy-on-close
    >
      <div class="book-list-books-manager">
        <div class="add-books-section">
          <h3>添加图书</h3>
          <div class="search-select-row">
            <el-select
              v-model="selectedBookIds"
              multiple
              filterable
              remote
              reserve-keyword
              placeholder="搜索并选择图书（可多选）"
              :remote-method="handleBookSearch"
              :loading="bookSearchLoading"
              style="flex: 1"
            >
              <el-option
                v-for="item in bookSearchOptions"
                :key="item.id"
                :label="`${item.title} - ${item.author}`"
                :value="item.id"
              >
                <div class="book-option">
                  <img :src="item.cover_image || defaultCover" :alt="item.title" class="book-option-cover" @error="handleBookOptionCoverError" />
                  <div class="book-option-info">
                    <span class="book-option-title">{{ item.title }}</span>
                    <span class="book-option-author">{{ item.author }}</span>
                  </div>
                </div>
              </el-option>
            </el-select>
            <el-button type="primary" :disabled="selectedBookIds.length === 0" @click="handleAddBooksToList">
              添加到书单
            </el-button>
          </div>
        </div>

        <div class="books-list-section">
          <h3>书单图书 ({{ currentBookListDetail?.books?.length || 0 }} 本)</h3>
          <el-empty v-if="!currentBookListDetail?.books?.length" description="书单暂无图书，请添加图书" />
          <el-table
            v-else
            :data="currentBookListDetail?.books"
            row-key="id"
            border
            style="width: 100%"
          >
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column label="排序" width="80">
              <template #default="{ row, $index }">
                <div class="sort-buttons">
                  <el-button
                    size="small"
                    circle
                    :disabled="$index === 0"
                    @click="handleMoveBookUp($index)"
                  >
                    <el-icon><Top /></el-icon>
                  </el-button>
                  <el-button
                    size="small"
                    circle
                    :disabled="$index === (currentBookListDetail?.books?.length || 1) - 1"
                    @click="handleMoveBookDown($index)"
                  >
                    <el-icon><Bottom /></el-icon>
                  </el-button>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="图书" min-width="250">
              <template #default="{ row }">
                <div class="book-item">
                  <img
                    :src="row.cover_image || defaultCover"
                    :alt="row.title"
                    class="book-item-cover"
                    @error="handleImageError"
                  >
                  <div class="book-item-info">
                    <div class="book-item-title">{{ row.title }}</div>
                    <div class="book-item-author">{{ row.author }}</div>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="价格" width="100">
              <template #default="{ row }">
                ¥{{ row.price.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="推荐语" min-width="200">
              <template #default="{ row }">
                <el-input
                  v-model="row.recommendation"
                  type="textarea"
                  :rows="2"
                  placeholder="输入推荐语（可选）"
                  @blur="handleUpdateBookRecommendation(row)"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-popconfirm
                  title="确定要移除此图书吗？"
                  @confirm="handleRemoveBook(row.id)"
                >
                  <template #reference>
                    <el-button type="danger" link>移除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="bookListBooksDialogVisible = false">关闭</el-button>
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
                <div v-if="currentOrder.member_discount_amount > 0" class="member-discount">
                  会员优惠：<span class="discount">-¥{{ currentOrder.member_discount_amount.toFixed(2) }}</span>
                </div>
                <div v-if="currentOrder.used_coupon" class="coupon-discount">
                  券优惠：<span class="discount">-¥{{ currentOrder.used_coupon.coupon.discount_amount.toFixed(2) }}</span>
                </div>
                <div v-if="currentOrder.discount_amount > 0" class="discount-amount">
                  共优惠：<span class="discount">-¥{{ currentOrder.discount_amount.toFixed(2) }}</span>
                </div>
                <div class="final-amount">
                  实付：<span class="price">¥{{ currentOrder.total_amount.toFixed(2) }}</span>
                </div>
              </div>
            </el-descriptions-item>
            <el-descriptions-item v-if="currentOrder.member_level_name" label="会员等级">
              <el-tag type="warning" size="small">
                {{ currentOrder.member_level_name }}
                {{ currentOrder.member_discount_rate ? (currentOrder.member_discount_rate * 10).toFixed(1) + '折' : '' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item v-if="currentOrder.used_coupon" label="使用优惠券">
              <el-tag type="warning" size="small">
                {{ currentOrder.used_coupon.coupon.name }}
                (满{{ currentOrder.used_coupon.coupon.threshold_amount }}减{{ currentOrder.used_coupon.coupon.discount_amount }})
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

    <el-dialog
      v-model="memberLevelDialogVisible"
      :title="isMemberLevelEdit ? '编辑会员等级' : '添加会员等级'"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="memberLevelFormRef"
        :model="memberLevelForm"
        :rules="memberLevelRules"
        label-width="100px"
      >
        <el-form-item label="等级名称" prop="name">
          <el-input v-model="memberLevelForm.name" placeholder="请输入等级名称" maxlength="50" show-word-limit />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="升级门槛" prop="threshold_amount">
              <el-input-number
                v-model="memberLevelForm.threshold_amount"
                :min="0"
                :precision="2"
                :step="100"
                controls-position="right"
                style="width: 100%"
              />
              <span class="form-tip">累计消费达到此金额自动升级</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="折扣比例" prop="discount_rate">
              <el-input-number
                v-model="memberLevelForm.discount_rate"
                :min="0.1"
                :max="1"
                :step="0.01"
                :precision="2"
                controls-position="right"
                style="width: 100%"
              />
              <span class="form-tip">0.95表示95折，1表示不打折</span>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="权益描述" prop="benefits">
          <el-input
            v-model="memberLevelForm.benefits"
            type="textarea"
            :rows="3"
            placeholder="请输入该等级的权益说明（可选）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="标识颜色" prop="badge_color">
              <el-color-picker v-model="memberLevelForm.badge_color" show-alpha />
              <span class="form-tip">等级标签的显示颜色</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序权重" prop="sort_order">
              <el-input-number
                v-model="memberLevelForm.sort_order"
                :min="0"
                :max="999"
                controls-position="right"
                style="width: 100%"
              />
              <span class="form-tip">数值越小排序越靠前</span>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="图标URL" prop="icon">
          <el-input v-model="memberLevelForm.icon" placeholder="请输入等级图标图片URL（可选）" />
        </el-form-item>

        <el-form-item label="启用状态" prop="is_active">
          <el-radio-group v-model="memberLevelForm.is_active">
            <el-radio :value="true">启用</el-radio>
            <el-radio :value="false">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="memberLevelDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="memberLevelSubmitting" @click="handleMemberLevelSubmit">
          {{ isMemberLevelEdit ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="adjustLevelDialogVisible"
      :title="`调整用户等级 - ${adjustingUserName}`"
      width="500px"
      destroy-on-close
    >
      <el-form label-width="100px">
        <el-form-item label="选择等级">
          <el-select
            v-model="selectedLevelId"
            placeholder="请选择会员等级"
            style="width: 100%"
          >
            <el-option
              v-for="level in allActiveMemberLevels"
              :key="level.id"
              :label="`${level.name} - 门槛¥${level.threshold_amount.toFixed(2)} - ${(level.discount_rate * 10).toFixed(1)}折`"
              :value="level.id"
            />
          </el-select>
          <span class="form-tip">设置后用户将按此等级享受折扣，不受累计消费影响</span>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="adjustLevelDialogVisible = false">取消</el-button>
        <el-button type="primary" :disabled="selectedLevelId === null" @click="handleAdjustLevel">
          确认
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="tagDialogVisible"
      :title="isTagEdit ? '编辑标签' : '添加标签'"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="tagFormRef"
        :model="tagForm"
        :rules="tagRules"
        label-width="100px"
      >
        <el-form-item label="标签名称" prop="name">
          <el-input
            v-model="tagForm.name"
            placeholder="请输入标签名称"
            maxlength="50"
            show-word-limit
            @blur="checkTagNameUnique"
          />
          <span v-if="tagNameError" class="error-text">{{ tagNameError }}</span>
        </el-form-item>

        <el-form-item label="标签颜色" prop="color">
          <el-color-picker v-model="tagForm.color" />
          <span class="form-tip">标签显示颜色</span>
        </el-form-item>

        <el-form-item label="标签说明" prop="description">
          <el-input
            v-model="tagForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入标签说明（可选）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="排序权重" prop="sort_order">
          <el-input-number
            v-model="tagForm.sort_order"
            :min="0"
            :max="999"
            controls-position="right"
            style="width: 100%"
          />
          <span class="form-tip">数值越小排序越靠前</span>
        </el-form-item>

        <el-form-item label="启用状态" prop="is_active">
          <el-radio-group v-model="tagForm.is_active">
            <el-radio :value="true">启用</el-radio>
            <el-radio :value="false">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="tagDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="tagSubmitting" @click="handleTagSubmit">
          {{ isTagEdit ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="announcementDialogVisible"
      title="发布公告"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="announcementFormRef"
        :model="announcementForm"
        :rules="announcementRules"
        label-width="100px"
      >
        <el-form-item label="公告标题" prop="title">
          <el-input 
            v-model="announcementForm.title" 
            placeholder="请输入公告标题" 
            maxlength="100" 
            show-word-limit 
          />
        </el-form-item>

        <el-form-item label="发送对象" prop="recipient_type">
          <el-radio-group v-model="announcementForm.recipient_type">
            <el-radio value="all_users">全体用户</el-radio>
            <el-radio value="specific_users">指定用户</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item 
          v-if="announcementForm.recipient_type === 'specific_users'" 
          label="选择用户"
          prop="user_ids"
        >
          <el-select
            v-model="selectedUserIds"
            multiple
            filterable
            remote
            reserve-keyword
            placeholder="搜索并选择用户（可多选）"
            :remote-method="fetchAdminUsers"
            :loading="adminUsersLoading"
            style="width: 100%"
          >
            <el-option
              v-for="user in adminUsers"
              :key="user.id"
              :label="`${user.username} (${user.email})`"
              :value="user.id"
            >
              <div class="user-option">
                <el-icon><User /></el-icon>
                <span class="user-option-name">{{ user.username }}</span>
                <span class="user-option-email">{{ user.email }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="有效期开始" prop="valid_from">
              <el-date-picker
                v-model="announcementForm.valid_from"
                type="datetime"
                placeholder="选择开始时间（可选）"
                style="width: 100%"
                value-format="YYYY-MM-DD HH:mm:ss"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="有效期结束" prop="valid_to">
              <el-date-picker
                v-model="announcementForm.valid_to"
                type="datetime"
                placeholder="选择结束时间（可选）"
                style="width: 100%"
                value-format="YYYY-MM-DD HH:mm:ss"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="公告内容" prop="content">
          <el-input
            v-model="announcementForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入公告内容"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="announcementDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="announcementSubmitting" @click="handleAnnouncementSubmit">
          发布公告
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api'
import type { Book, BookCreate, Order, OrderStatus, Coupon, CouponCreate, CouponUpdate, CouponStatus as CouponStatusType, Author, AuthorCreate, AuthorUpdate, AuthorSearchResult, Publisher, PublisherCreate, PublisherUpdate, PublisherSearchResult, Message, MessageType, MessageRecipientType, AnnouncementCreate, MessageStatsResponse, BookList, BookListCreate, BookListUpdate, BookListDetail, BookListBook, MemberLevel, MemberLevelCreate, MemberLevelUpdate, Tag, TagCreate, TagUpdate, UserMemberResponse, UserMemberListResponse, UserMemberLevelUpdate } from '@/types'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Search, User, Top, Bottom } from '@element-plus/icons-vue'
import Dashboard from '@/components/Dashboard.vue'

const route = useRoute()
const initialTab = (route.query.tab as string) || 'dashboard'
const activeTab = ref(initialTab)

const loading = ref(false)
const submitting = ref(false)
const books = ref<Book[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchQuery = ref('')
const lowStockFilter = ref(false)
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
const orderStatusFilter = ref<OrderStatus[]>([])

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

const adminMessagesLoading = ref(false)
const adminMessages = ref<Message[]>([])
const adminMessagesTotal = ref(0)
const adminMessagesCurrentPage = ref(1)
const adminMessagesPageSize = ref(10)

const messageStats = reactive<MessageStatsResponse>({
  total_messages: 0,
  active_messages: 0,
  total_recipients: 0,
  read_recipients: 0,
  read_rate: 0
})

const announcementDialogVisible = ref(false)
const announcementSubmitting = ref(false)
const announcementFormRef = ref<FormInstance>()

const bookListsLoading = ref(false)
const bookLists = ref<BookList[]>([])
const bookListsTotal = ref(0)
const bookListsCurrentPage = ref(1)
const bookListsPageSize = ref(10)
const bookListSearchQuery = ref('')
const bookListStatusFilter = ref<boolean | ''>('')
const bookListDialogVisible = ref(false)
const isBookListEdit = ref(false)
const bookListEditingId = ref<number | null>(null)
const bookListSubmitting = ref(false)
const bookListFormRef = ref<FormInstance>()
const defaultBookListCover = 'https://via.placeholder.com/120x160/10b981/ffffff?text=BookList'

const bookListForm = reactive<BookListCreate>({
  title: '',
  description: '',
  cover_image: '',
  is_active: true,
  sort_weight: 0,
  category: '',
  books: []
})

const bookListRules: FormRules = {
  title: [{ required: true, message: '请输入书单标题', trigger: 'blur' }]
}

const bookListBooksDialogVisible = ref(false)
const currentBookList = ref<BookList | null>(null)
const currentBookListDetail = ref<BookListDetail | null>(null)
const selectedBookIds = ref<number[]>([])
const bookSearchLoading = ref(false)
const bookSearchOptions = ref<Book[]>([])

const memberLevelsLoading = ref(false)
const memberLevels = ref<MemberLevel[]>([])
const memberLevelsTotal = ref(0)
const memberLevelsCurrentPage = ref(1)
const memberLevelsPageSize = ref(10)
const memberLevelStatusFilter = ref<boolean | ''>('')
const memberLevelDialogVisible = ref(false)
const isMemberLevelEdit = ref(false)
const memberLevelEditingId = ref<number | null>(null)
const memberLevelSubmitting = ref(false)
const memberLevelFormRef = ref<FormInstance>()

const memberLevelForm = reactive<MemberLevelCreate>({
  name: '',
  threshold_amount: 0,
  discount_rate: 1,
  benefits: '',
  badge_color: '#409eff',
  icon: '',
  sort_order: 0,
  is_active: true
})

const memberLevelRules: FormRules = {
  name: [{ required: true, message: '请输入等级名称', trigger: 'blur' }],
  threshold_amount: [{ required: true, message: '请输入升级门槛金额', trigger: 'blur' }],
  discount_rate: [{ required: true, message: '请输入折扣比例', trigger: 'blur' }],
  sort_order: [{ required: true, message: '请输入排序权重', trigger: 'blur' }]
}

const tagsLoading = ref(false)
const tags = ref<Tag[]>([])
const tagsTotal = ref(0)
const tagsCurrentPage = ref(1)
const tagsPageSize = ref(10)
const tagSearchQuery = ref('')
const tagStatusFilter = ref<boolean | ''>('')
const tagDialogVisible = ref(false)
const isTagEdit = ref(false)
const tagEditingId = ref<number | null>(null)
const tagSubmitting = ref(false)
const tagFormRef = ref<FormInstance>()
const tagNameError = ref('')

const tagForm = reactive<TagCreate>({
  name: '',
  color: '#409eff',
  description: '',
  sort_order: 0,
  is_active: true
})

const tagRules: FormRules = {
  name: [{ required: true, message: '请输入标签名称', trigger: 'blur' }]
}

const selectedTagIds = ref<number[]>([])
const tagSearchLoading = ref(false)
const tagSearchOptions = ref<Tag[]>([])
const selectedTagFilter = ref<number | null>(null)
const activeTags = ref<Tag[]>([])

const memberUsersLoading = ref(false)
const memberUsers = ref<UserMemberResponse[]>([])
const memberUsersTotal = ref(0)
const memberUsersCurrentPage = ref(1)
const memberUsersPageSize = ref(10)
const memberUserSearchQuery = ref('')
const adjustLevelDialogVisible = ref(false)
const adjustingUserId = ref<number | null>(null)
const adjustingUserName = ref('')
const selectedLevelId = ref<number | null>(null)
const allActiveMemberLevels = ref<MemberLevel[]>([])

const adminUsers = ref<User[]>([])
const adminUsersLoading = ref(false)
const selectedUserIds = ref<number[]>([])

const announcementForm = reactive<AnnouncementCreate>({
  title: '',
  content: '',
  recipient_type: 'all_users',
  valid_from: '',
  valid_to: ''
})

const announcementRules: FormRules = {
  title: [{ required: true, message: '请输入公告标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入公告内容', trigger: 'blur' }],
  recipient_type: [{ required: true, message: '请选择发送对象', trigger: 'change' }]
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

function applyRouteFilters() {
  const q = route.query
  if (q.low_stock !== undefined) {
    lowStockFilter.value = ['1', 'true', 'yes'].includes(String(q.low_stock).toLowerCase())
  }
  if (q.status !== undefined) {
    const statusStr = String(q.status)
    orderStatusFilter.value = statusStr.split(',').map(s => s.trim()).filter(Boolean) as OrderStatus[]
  } else {
    orderStatusFilter.value = []
  }
}

function loadActiveTabData(force = false) {
  const tab = activeTab.value
  if (tab === 'books') {
    applyRouteFilters()
    fetchBooks()
  }
  if (tab === 'orders') {
    applyRouteFilters()
    fetchOrders()
  }
  if (tab === 'coupons' && (force || coupons.value.length === 0)) {
    fetchCoupons()
  }
  if (tab === 'authors' && (force || authors.value.length === 0)) {
    fetchAuthors()
  }
  if (tab === 'publishers' && (force || publishers.value.length === 0)) {
    fetchPublishers()
  }
  if (tab === 'book-lists' && (force || bookLists.value.length === 0)) {
    fetchBookLists()
  }
  if (tab === 'member-levels' && (force || memberLevels.value.length === 0)) {
    fetchMemberLevels()
  }
  if (tab === 'member-users' && (force || memberUsers.value.length === 0)) {
    fetchMemberUsers()
    fetchAllActiveMemberLevels()
  }
  if (tab === 'tags' && (force || tags.value.length === 0)) {
    fetchTags()
  }
  if (tab === 'messages') {
    fetchAdminMessages()
    fetchMessageStats()
  }
}

onMounted(() => {
  loadActiveTabData(true)
  if (activeTags.value.length === 0) {
    fetchActiveTags()
  }
})

watch(
  () => [route.query.tab, route.query.low_stock, route.query.status],
  ([newTab]) => {
    if (newTab && typeof newTab === 'string') {
      activeTab.value = newTab
    }
    loadActiveTabData(true)
  }
)

watch(activeTab, () => {
  loadActiveTabData(false)
})

async function fetchBooks() {
  loading.value = true
  try {
    const response = await api.getBooks({
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value || undefined,
      tag_id: selectedTagFilter.value || undefined,
      low_stock: lowStockFilter.value || undefined
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
    const statusStr = orderStatusFilter.value && orderStatusFilter.value.length
      ? orderStatusFilter.value.join(',')
      : undefined
    const response = await api.getAllOrders({
      status: statusStr,
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
  selectedTagIds.value = book.tags ? book.tags.map(t => t.id) : []
  loadAllTagOptions()
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
  selectedTagIds.value = []
  publisherSearchOptions.value = []
  loadAllTagOptions()
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!bookFormRef.value) return
  
  await bookFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    submitting.value = true
    try {
      const submitData: any = {
        ...bookForm,
        author_ids: selectedAuthorIds.value.length > 0 ? selectedAuthorIds.value : undefined,
        tag_ids: selectedTagIds.value.length > 0 ? selectedTagIds.value : undefined
      }
      if (isEdit.value) {
        submitData.publisher_id = selectedPublisherId.value
      } else {
        submitData.publisher_id = selectedPublisherId.value || undefined
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

async function fetchAdminMessages() {
  adminMessagesLoading.value = true
  try {
    const response = await api.getAdminMessages({
      page: adminMessagesCurrentPage.value,
      page_size: adminMessagesPageSize.value
    })
    adminMessages.value = response.items
    adminMessagesTotal.value = response.total
  } catch (error) {
    console.error('获取公告列表失败:', error)
  } finally {
    adminMessagesLoading.value = false
  }
}

async function fetchMessageStats() {
  try {
    const response = await api.getMessageStats()
    Object.assign(messageStats, response)
  } catch (error) {
    console.error('获取消息统计失败:', error)
  }
}

async function fetchAdminUsers(search?: string) {
  adminUsersLoading.value = true
  try {
    adminUsers.value = await api.getAdminUsers(search)
  } catch (error) {
    console.error('获取用户列表失败:', error)
  } finally {
    adminUsersLoading.value = false
  }
}

function openAnnouncementDialog() {
  resetAnnouncementForm()
  selectedUserIds.value = []
  fetchAdminUsers()
  announcementDialogVisible.value = true
}

function resetAnnouncementForm() {
  Object.assign(announcementForm, {
    title: '',
    content: '',
    recipient_type: 'all_users',
    valid_from: '',
    valid_to: ''
  })
}

async function handleAnnouncementSubmit() {
  if (!announcementFormRef.value) return
  
  await announcementFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    announcementSubmitting.value = true
    try {
      const submitData: AnnouncementCreate = {
        ...announcementForm,
        user_ids: announcementForm.recipient_type === 'specific_users' && selectedUserIds.value.length > 0 
          ? selectedUserIds.value 
          : undefined
      }
      await api.createAnnouncement(submitData)
      ElMessage.success('公告发布成功')
      announcementDialogVisible.value = false
      fetchAdminMessages()
      fetchMessageStats()
    } catch (error) {
      console.error('发布公告失败:', error)
    } finally {
      announcementSubmitting.value = false
    }
  })
}

async function toggleMessageActive(message: Message) {
  try {
    await api.toggleAnnouncementActive(message.id)
    ElMessage.success(message.is_active ? '已停用' : '已启用')
    fetchAdminMessages()
    fetchMessageStats()
  } catch (error) {
    console.error('操作失败:', error)
  }
}

async function handleDeleteAnnouncement(id: number) {
  try {
    await api.deleteAnnouncement(id)
    ElMessage.success('删除成功')
    fetchAdminMessages()
    fetchMessageStats()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

async function fetchBookLists() {
  bookListsLoading.value = true
  try {
    const response = await api.getBookLists({
      page: bookListsCurrentPage.value,
      page_size: bookListsPageSize.value,
      search: bookListSearchQuery.value || undefined,
      is_active: bookListStatusFilter.value === '' ? undefined : bookListStatusFilter.value
    })
    bookLists.value = response.items
    bookListsTotal.value = response.total
  } catch (error) {
    console.error('获取书单列表失败:', error)
  } finally {
    bookListsLoading.value = false
  }
}

function handleAddBookList() {
  isBookListEdit.value = false
  bookListEditingId.value = null
  resetBookListForm()
  bookListDialogVisible.value = true
}

function handleEditBookList(bookList: BookList) {
  isBookListEdit.value = true
  bookListEditingId.value = bookList.id
  Object.assign(bookListForm, {
    title: bookList.title,
    description: bookList.description || '',
    cover_image: bookList.cover_image || '',
    is_active: bookList.is_active,
    sort_weight: bookList.sort_weight,
    category: bookList.category || '',
    books: []
  })
  bookListDialogVisible.value = true
}

async function handleDeleteBookList(id: number) {
  try {
    await api.deleteBookList(id)
    ElMessage.success('删除成功')
    fetchBookLists()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

async function handleBookListSubmit() {
  if (!bookListFormRef.value) return
  
  await bookListFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    bookListSubmitting.value = true
    try {
      if (isBookListEdit.value && bookListEditingId.value) {
        const updateData: BookListUpdate = { ...bookListForm }
        await api.updateBookList(bookListEditingId.value, updateData)
        ElMessage.success('更新成功')
      } else {
        await api.createBookList(bookListForm)
        ElMessage.success('添加成功')
      }
      bookListDialogVisible.value = false
      fetchBookLists()
    } catch (error) {
      console.error('操作失败:', error)
    } finally {
      bookListSubmitting.value = false
    }
  })
}

function resetBookListForm() {
  Object.assign(bookListForm, {
    title: '',
    description: '',
    cover_image: '',
    is_active: true,
    sort_weight: 0,
    category: '',
    books: []
  })
}

function handleBookListCoverError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultBookListCover
}

function handleBookListFormCoverError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultBookListCover
}

async function handleManageBooks(bookList: BookList) {
  currentBookList.value = bookList
  selectedBookIds.value = []
  bookSearchOptions.value = []
  try {
    currentBookListDetail.value = await api.getBookList(bookList.id)
    bookListBooksDialogVisible.value = true
  } catch (error) {
    console.error('获取书单详情失败:', error)
  }
}

async function handleBookSearch(query: string) {
  if (!query || query.trim() === '') {
    bookSearchOptions.value = []
    return
  }
  bookSearchLoading.value = true
  try {
    const response = await api.getBooks({ search: query.trim(), page_size: 20 })
    bookSearchOptions.value = response.items
  } catch (error) {
    console.error('搜索图书失败:', error)
  } finally {
    bookSearchLoading.value = false
  }
}

async function handleAddBooksToList() {
  if (!currentBookList.value || selectedBookIds.value.length === 0) return
  
  const existingIds = new Set(currentBookListDetail.value?.books?.map(b => b.id) || [])
  const newBooks = selectedBookIds.value
    .filter(id => !existingIds.has(id))
    .map((id, index) => ({
      book_id: id,
      sort_order: (currentBookListDetail.value?.books?.length || 0) + index,
      recommendation: ''
    }))
  
  if (newBooks.length === 0) {
    ElMessage.warning('选择的图书已在书单中')
    return
  }
  
  try {
    currentBookListDetail.value = await api.addBooksToBookList(currentBookList.value.id, { books: newBooks })
    ElMessage.success(`成功添加 ${newBooks.length} 本图书`)
    selectedBookIds.value = []
  } catch (error) {
    console.error('添加图书失败:', error)
  }
}

async function handleRemoveBook(bookId: number) {
  if (!currentBookList.value) return
  
  try {
    currentBookListDetail.value = await api.removeBookFromBookList(currentBookList.value.id, bookId)
    ElMessage.success('移除成功')
  } catch (error) {
    console.error('移除图书失败:', error)
  }
}

async function handleMoveBookUp(index: number) {
  if (!currentBookListDetail.value?.books || index === 0) return
  
  const books = [...currentBookListDetail.value.books]
  ;[books[index - 1], books[index]] = [books[index], books[index - 1]]
  
  const bookIds = books.map(b => b.id)
  try {
    currentBookListDetail.value = await api.reorderBooksInBookList(currentBookList.value!.id, { book_ids: bookIds })
  } catch (error) {
    console.error('排序失败:', error)
  }
}

async function handleMoveBookDown(index: number) {
  if (!currentBookListDetail.value?.books || index === currentBookListDetail.value.books.length - 1) return
  
  const books = [...currentBookListDetail.value.books]
  ;[books[index], books[index + 1]] = [books[index + 1], books[index]]
  
  const bookIds = books.map(b => b.id)
  try {
    currentBookListDetail.value = await api.reorderBooksInBookList(currentBookList.value!.id, { book_ids: bookIds })
  } catch (error) {
    console.error('排序失败:', error)
  }
}

async function handleUpdateBookRecommendation(book: BookListBook) {
  if (!currentBookList.value) return
  
  try {
    await api.updateBookInBookList(currentBookList.value.id, book.id, {
      recommendation: book.recommendation
    })
  } catch (error) {
    console.error('更新推荐语失败:', error)
  }
}

function handleBookOptionCoverError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = defaultCover
}

async function fetchMemberLevels() {
  memberLevelsLoading.value = true
  try {
    const response = await api.getAdminMemberLevels({
      is_active: memberLevelStatusFilter.value === '' ? undefined : memberLevelStatusFilter.value,
      page: memberLevelsCurrentPage.value,
      page_size: memberLevelsPageSize.value
    })
    memberLevels.value = response.items
    memberLevelsTotal.value = response.total
  } catch (error) {
    console.error('获取会员等级列表失败:', error)
  } finally {
    memberLevelsLoading.value = false
  }
}

function handleAddMemberLevel() {
  isMemberLevelEdit.value = false
  memberLevelEditingId.value = null
  resetMemberLevelForm()
  memberLevelDialogVisible.value = true
}

function handleEditMemberLevel(level: MemberLevel) {
  isMemberLevelEdit.value = true
  memberLevelEditingId.value = level.id
  Object.assign(memberLevelForm, {
    name: level.name,
    threshold_amount: level.threshold_amount,
    discount_rate: level.discount_rate,
    benefits: level.benefits || '',
    badge_color: level.badge_color || '#409eff',
    icon: level.icon || '',
    sort_order: level.sort_order,
    is_active: level.is_active
  })
  memberLevelDialogVisible.value = true
}

async function handleDeleteMemberLevel(id: number) {
  try {
    await api.deleteMemberLevel(id)
    ElMessage.success('删除成功')
    fetchMemberLevels()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

async function handleMemberLevelSubmit() {
  if (!memberLevelFormRef.value) return
  
  await memberLevelFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    memberLevelSubmitting.value = true
    try {
      if (isMemberLevelEdit.value && memberLevelEditingId.value) {
        const updateData: MemberLevelUpdate = { ...memberLevelForm }
        await api.updateMemberLevel(memberLevelEditingId.value, updateData)
        ElMessage.success('更新成功')
      } else {
        await api.createMemberLevel(memberLevelForm)
        ElMessage.success('添加成功')
      }
      memberLevelDialogVisible.value = false
      fetchMemberLevels()
    } catch (error) {
      console.error('操作失败:', error)
    } finally {
      memberLevelSubmitting.value = false
    }
  })
}

function resetMemberLevelForm() {
  Object.assign(memberLevelForm, {
    name: '',
    threshold_amount: 0,
    discount_rate: 1,
    benefits: '',
    badge_color: '#409eff',
    icon: '',
    sort_order: 0,
    is_active: true
  })
}

async function fetchTags() {
  tagsLoading.value = true
  try {
    const response = await api.getTags({
      page: tagsCurrentPage.value,
      page_size: tagsPageSize.value,
      search: tagSearchQuery.value || undefined,
      is_active: tagStatusFilter.value === '' ? undefined : tagStatusFilter.value
    })
    tags.value = response.items
    tagsTotal.value = response.total
  } catch (error) {
    console.error('获取标签列表失败:', error)
  } finally {
    tagsLoading.value = false
  }
}

async function fetchActiveTags() {
  try {
    activeTags.value = await api.getActiveTags()
  } catch (error) {
    console.error('获取启用标签失败:', error)
  }
}

function handleAddTag() {
  isTagEdit.value = false
  tagEditingId.value = null
  resetTagForm()
  tagNameError.value = ''
  tagDialogVisible.value = true
}

function handleEditTag(tag: Tag) {
  isTagEdit.value = true
  tagEditingId.value = tag.id
  Object.assign(tagForm, {
    name: tag.name,
    color: tag.color || '#409eff',
    description: tag.description || '',
    sort_order: tag.sort_order,
    is_active: tag.is_active
  })
  tagNameError.value = ''
  tagDialogVisible.value = true
}

async function handleDeleteTag(tag: Tag) {
  try {
    const checkResult = await api.checkTagDelete(tag.id)
    if (!checkResult.can_delete) {
      ElMessage.warning(checkResult.message || '该标签有关联的图书，无法删除')
      return
    }
    await api.deleteTag(tag.id)
    ElMessage.success('删除成功')
    fetchTags()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

async function checkTagNameUnique() {
  if (!tagForm.name || tagForm.name.trim() === '') {
    tagNameError.value = ''
    return
  }
  try {
    const result = await api.checkTagName(
      tagForm.name.trim(),
      isTagEdit.value && tagEditingId.value ? tagEditingId.value : undefined
    )
    if (!result.available) {
      tagNameError.value = result.message || '名称已存在'
    } else {
      tagNameError.value = ''
    }
  } catch (error) {
    console.error('校验名称失败:', error)
  }
}

async function handleTagSubmit() {
  if (!tagFormRef.value) return
  
  await tagFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    if (tagNameError.value) {
      ElMessage.error(tagNameError.value)
      return
    }
    
    tagSubmitting.value = true
    try {
      if (isTagEdit.value && tagEditingId.value) {
        const updateData: TagUpdate = { ...tagForm }
        await api.updateTag(tagEditingId.value, updateData)
        ElMessage.success('更新成功')
      } else {
        await api.createTag(tagForm)
        ElMessage.success('添加成功')
      }
      tagDialogVisible.value = false
      fetchTags()
      fetchActiveTags()
    } catch (error) {
      console.error('操作失败:', error)
    } finally {
      tagSubmitting.value = false
    }
  })
}

function resetTagForm() {
  Object.assign(tagForm, {
    name: '',
    color: '#409eff',
    description: '',
    sort_order: 0,
    is_active: true
  })
}

async function loadAllTagOptions() {
  tagSearchLoading.value = true
  try {
    tagSearchOptions.value = await api.getAllTags(true)
  } catch (error) {
    console.error('加载标签列表失败:', error)
  } finally {
    tagSearchLoading.value = false
  }
}

async function handleTagSearch(query: string) {
  if (!query || query.trim() === '') {
    await loadAllTagOptions()
    return
  }
  tagSearchLoading.value = true
  try {
    tagSearchOptions.value = await api.searchTags(query.trim(), 50, true)
  } catch (error) {
    console.error('搜索标签失败:', error)
  } finally {
    tagSearchLoading.value = false
  }
}

async function fetchMemberUsers() {
  memberUsersLoading.value = true
  try {
    const response = await api.getAdminMemberUsers({
      search: memberUserSearchQuery.value || undefined,
      page: memberUsersCurrentPage.value,
      page_size: memberUsersPageSize.value
    })
    memberUsers.value = response.items
    memberUsersTotal.value = response.total
  } catch (error) {
    console.error('获取用户列表失败:', error)
  } finally {
    memberUsersLoading.value = false
  }
}

async function fetchAllActiveMemberLevels() {
  try {
    allActiveMemberLevels.value = await api.getAdminAllActiveMemberLevels()
  } catch (error) {
    console.error('获取启用等级列表失败:', error)
  }
}

function openAdjustLevelDialog(user: UserMemberResponse) {
  adjustingUserId.value = user.id
  adjustingUserName.value = user.username
  selectedLevelId.value = user.member_level?.manual_level?.id || null
  adjustLevelDialogVisible.value = true
}

async function handleAdjustLevel() {
  if (!adjustingUserId.value || selectedLevelId.value === null) return

  try {
    const updateData: UserMemberLevelUpdate = { manual_level_id: selectedLevelId.value }
    await api.updateUserMemberLevel(adjustingUserId.value, updateData)
    ElMessage.success('等级调整成功')
    adjustLevelDialogVisible.value = false
    fetchMemberUsers()
  } catch (error) {
    console.error('调整等级失败:', error)
  }
}

async function handleClearManualLevel(user: UserMemberResponse) {
  try {
    await ElMessageBox.confirm(
      `确定要清除用户「${user.username}」的手动等级吗？清除后将按累计消费自动计算等级。`,
      '清除手动等级',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    const updateData: UserMemberLevelUpdate = { manual_level_id: null }
    await api.updateUserMemberLevel(user.id, updateData)
    ElMessage.success('已清除手动等级')
    fetchMemberUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清除手动等级失败:', error)
    }
  }
}

async function handleRecalculateUserSpent(user: UserMemberResponse) {
  try {
    await ElMessageBox.confirm(
      `确定要重新计算用户「${user.username}」的累计消费吗？`,
      '重新计算累计消费',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await api.recalculateUserSpent(user.id)
    ElMessage.success('累计消费已重新计算')
    fetchMemberUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重新计算累计消费失败:', error)
    }
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

.member-discount {
  font-size: 12px;
}

.coupon-discount {
  font-size: 12px;
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

.message-stats {
  margin-bottom: 8px;
}

.stat-item {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: var(--primary-color);
}

.content-preview {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-secondary);
}

.user-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-option-name {
  font-weight: 500;
}

.user-option-email {
  font-size: 12px;
  color: var(--text-muted);
  margin-left: 4px;
}

.booklist-thumbnail {
  width: 50px;
  height: 70px;
  object-fit: cover;
  border-radius: 4px;
}

.booklist-title {
  font-weight: 500;
}

.cover-preview {
  margin-top: 8px;
}

.cover-preview img {
  width: 100px;
  height: 140px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.book-list-books-manager {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.book-list-books-manager h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
}

.search-select-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.book-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.book-option-cover {
  width: 32px;
  height: 44px;
  object-fit: cover;
  border-radius: 3px;
}

.book-option-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.book-option-title {
  font-weight: 500;
}

.book-option-author {
  font-size: 12px;
  color: var(--text-muted);
}

.sort-buttons {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.book-item {
  display: flex;
  gap: 12px;
  align-items: center;
}

.book-item-cover {
  width: 40px;
  height: 55px;
  object-fit: cover;
  border-radius: 4px;
}

.book-item-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.book-item-title {
  font-weight: 500;
}

.book-item-author {
  font-size: 12px;
  color: var(--text-muted);
}

.discount-text {
  font-weight: 600;
  color: var(--danger-color);
}

.color-preview {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 4px;
  vertical-align: middle;
  margin-right: 6px;
  border: 1px solid var(--border-color);
}

.color-hex {
  font-size: 12px;
  color: var(--text-secondary);
  vertical-align: middle;
}

.tag-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.book-tags {
  display: flex;
  flex-wrap: wrap;
}
</style>
