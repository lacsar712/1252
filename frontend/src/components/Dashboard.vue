<template>
  <div class="dashboard-page">
    <div class="dashboard-header">
      <h1 class="dashboard-title">数据仪表盘</h1>
      <div class="dashboard-actions">
        <el-radio-group v-model="timeRange" size="default" @change="handleTimeRangeChange">
          <el-radio-button :label="7">最近7天</el-radio-button>
          <el-radio-button :label="30">最近30天</el-radio-button>
          <el-radio-button :label="90">最近90天</el-radio-button>
        </el-radio-group>
        <el-button type="primary" :icon="Refresh" :loading="loading" @click="fetchData">
          刷新数据
        </el-button>
      </div>
    </div>

    <div v-loading="loading" element-loading-text="数据加载中..." class="dashboard-content">
      <div v-if="!loading && error" class="error-state">
        <el-empty description="数据加载失败，请稍后重试">
          <el-button type="primary" @click="fetchData">重新加载</el-button>
        </el-empty>
      </div>

      <template v-else>
        <el-row :gutter="16" class="stats-cards">
          <el-col :xs="12" :sm="12" :md="6" v-for="card in statCards" :key="card.key">
            <div 
              class="stat-card" 
              :class="[card.type, { 'stat-card--disabled': !card.route }]"
              @click="handleCardClick(card)"
            >
              <div class="stat-card-icon">
                <el-icon :size="32"><component :is="card.icon" /></el-icon>
              </div>
              <div class="stat-card-info">
                <div class="stat-card-label">{{ card.label }}</div>
                <div class="stat-card-value">
                  <span v-if="card.prefix">{{ card.prefix }}</span>
                  {{ formatNumber(card.value) }}
                  <span v-if="card.suffix">{{ card.suffix }}</span>
                </div>
                <div v-if="card.subLabel" class="stat-card-sublabel">
                  {{ card.subLabel }}: <span class="sub-value">{{ formatNumber(card.subValue) }}{{ card.suffix }}</span>
                </div>
              </div>
              <div v-if="card.route" class="stat-card-arrow">
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </el-col>
        </el-row>

        <el-row :gutter="16" class="dashboard-charts">
          <el-col :lg="12" :md="24" class="chart-col">
            <div class="chart-card">
              <div class="chart-header">
                <h3>分类库存占比</h3>
                <el-tag size="small" type="info">按库存价值</el-tag>
              </div>
              <div class="chart-body">
                <div v-if="!categoryStockData.length" class="empty-chart">
                  <el-empty description="暂无分类数据" :image-size="60" />
                </div>
                <v-chart 
                  v-else
                  ref="categoryChartRef"
                  :option="categoryChartOption" 
                  autoresize
                  class="chart"
                />
              </div>
            </div>
          </el-col>

          <el-col :lg="12" :md="24" class="chart-col">
            <div class="chart-card">
              <div class="chart-header">
                <h3>销售趋势</h3>
                <el-select v-model="salesMetric" size="small" style="width: 100px" @change="updateSalesChart">
                  <el-option label="销售额" value="revenue" />
                  <el-option label="订单数" value="order_count" />
                  <el-option label="图书数" value="book_count" />
                </el-select>
              </div>
              <div class="chart-body">
                <div v-if="!salesTrendData.length" class="empty-chart">
                  <el-empty description="暂无销售数据" :image-size="60" />
                </div>
                <v-chart 
                  v-else
                  ref="salesChartRef"
                  :option="salesChartOption" 
                  autoresize
                  class="chart"
                />
              </div>
            </div>
          </el-col>
        </el-row>

        <el-row :gutter="16" class="dashboard-lists">
          <el-col :lg="12" :md="24" class="list-col">
            <div class="list-card">
              <div class="list-header">
                <h3>最近上架图书</h3>
                <el-button 
                  type="primary" 
                  link 
                  @click="navigateTo('books')"
                >
                  查看全部 <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
              <div class="list-body">
                <div v-if="!recentBooks.length" class="empty-list">
                  <el-empty description="暂无图书数据" :image-size="60" />
                </div>
                <div v-else class="recent-books-list">
                  <div 
                    v-for="book in recentBooks" 
                    :key="book.id" 
                    class="book-item"
                    @click="navigateToBookDetail(book.id)"
                  >
                    <img 
                      :src="book.cover_image || defaultCover" 
                      :alt="book.title"
                      class="book-cover"
                      @error="handleImageError"
                    />
                    <div class="book-info">
                      <div class="book-title">{{ book.title }}</div>
                      <div class="book-meta">
                        <el-tag v-if="book.category" size="small" type="info">{{ book.category }}</el-tag>
                        <span class="book-price">¥{{ book.price.toFixed(2) }}</span>
                        <el-tag 
                          size="small" 
                          :type="book.stock > 10 ? 'success' : book.stock > 0 ? 'warning' : 'danger'"
                        >
                          库存: {{ book.stock }}
                        </el-tag>
                      </div>
                    </div>
                    <div class="book-date">{{ formatDate(book.created_at) }}</div>
                  </div>
                </div>
              </div>
            </div>
          </el-col>

          <el-col :lg="12" :md="24" class="list-col">
            <div class="list-card">
              <div class="list-header">
                <h3>最近订单</h3>
                <el-button 
                  type="primary" 
                  link 
                  @click="navigateTo('orders')"
                >
                  查看全部 <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
              <div class="list-body">
                <div v-if="!recentOrders.length" class="empty-list">
                  <el-empty description="暂无订单数据" :image-size="60" />
                </div>
                <div v-else class="recent-orders-list">
                  <div 
                    v-for="order in recentOrders" 
                    :key="order.id" 
                    class="order-item"
                    @click="navigateToOrderDetail(order.id)"
                  >
                    <div class="order-icon">
                      <el-icon :size="24"><Document /></el-icon>
                    </div>
                    <div class="order-info">
                      <div class="order-no">{{ order.order_no }}</div>
                      <div class="order-meta">
                        <span class="receiver">{{ order.receiver_name }}</span>
                        <span class="order-date">{{ formatDate(order.created_at) }}</span>
                      </div>
                    </div>
                    <div class="order-right">
                      <div class="order-amount">¥{{ order.total_amount.toFixed(2) }}</div>
                      <el-tag :type="getOrderStatusType(order.status)" size="small">
                        {{ getOrderStatusText(order.status) }}
                      </el-tag>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, markRaw } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Refresh, ArrowRight, Document, ShoppingCart, User, Reading, Goods, Money, AlarmClock } from '@element-plus/icons-vue';
import { use } from 'echarts/core';
import { PieChart, LineChart } from 'echarts/charts';
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent, DatasetComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import VChart from 'vue-echarts';
import type { EChartsOption } from 'echarts';
import { api } from '@/api';
import type { DashboardResponse, TimeRange, CategoryStock, SalesTrendItem, RecentBook, RecentOrder, DashboardStats } from '@/types';
use([
 TitleComponent,
 TooltipComponent,
 LegendComponent,
 GridComponent,
 DatasetComponent,
 PieChart,
 LineChart,
 CanvasRenderer
]);
const router = useRouter();
const loading = ref(false);
const error = ref(false);
const timeRange = ref<TimeRange>(7);
const salesMetric = ref<'revenue' | 'order_count' | 'book_count'>('revenue');
const categoryChartRef = ref();
const salesChartRef = ref();
const dashboardData = ref<DashboardResponse | null>(null);
const defaultCover = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"%3E%3Crect fill="%23f0f0f0" width="100" height="100"/%3E%3Ctext x="50" y="55" text-anchor="middle" fill="%23999" font-size="14"%3E暂无封面%3C/text%3E%3C/svg%3E';
const stats = computed<DashboardStats>(() => dashboardData.value?.stats || {
 total_books: 0,
 total_users: 0,
 total_orders: 0,
 low_stock_count: 0,
 total_inventory_value: 0,
 pending_orders: 0,
 today_orders: 0,
 today_revenue: 0
});
const recentBooks = computed<RecentBook[]>(() => dashboardData.value?.recent_books || []);
const recentOrders = computed<RecentOrder[]>(() => dashboardData.value?.recent_orders || []);
const categoryStockData = computed<CategoryStock[]>(() => dashboardData.value?.category_stock || []);
const salesTrendData = computed<SalesTrendItem[]>(() => dashboardData.value?.sales_trend || []);
const statCards = computed(() => [
  {
    key: 'books',
    label: '图书总数',
    value: stats.value.total_books,
    subLabel: '低库存',
    subValue: stats.value.low_stock_count,
    icon: markRaw(Reading),
    type: 'primary',
    route: 'books',
    query: { low_stock: 1 }
  },
  {
    key: 'users',
    label: '用户总数',
    value: stats.value.total_users,
    icon: markRaw(User),
    type: 'success',
    route: null,
    query: {}
  },
  {
    key: 'orders',
    label: '订单总数',
    value: stats.value.total_orders,
    subLabel: '待处理',
    subValue: stats.value.pending_orders,
    icon: markRaw(ShoppingCart),
    type: 'warning',
    route: 'orders',
    query: { status: 'pending,confirmed' }
  },
  {
    key: 'inventory',
    label: '库存总价值',
    value: stats.value.total_inventory_value,
    prefix: '¥',
    subLabel: '今日销售',
    subValue: stats.value.today_revenue,
    icon: markRaw(Goods),
    type: 'info',
    route: 'books',
    query: {}
  },
  {
    key: 'today_orders',
    label: '今日订单',
    value: stats.value.today_orders,
    icon: markRaw(AlarmClock),
    type: 'purple',
    route: 'orders',
    query: {}
  },
  {
    key: 'today_revenue',
    label: '今日销售额',
    value: stats.value.today_revenue,
    prefix: '¥',
    icon: markRaw(Money),
    type: 'orange',
    route: 'orders',
    query: {}
  }
]);
const categoryChartOption = computed<EChartsOption>(() => {
 const data = categoryStockData.value.map(item => ({
 name: item.category,
 value: item.value,
 count: item.count,
 percentage: item.percentage
 }));
 return {
 tooltip: {
 trigger: 'item',
 formatter: (params: any) => {
 const data = params.data;
 return `<div style="padding: 4px;">
 <div style="font-weight: bold; margin-bottom: 4px;">${data.name}</div>
 <div>库存数量: ${data.count} 本</div>
 <div>库存价值: ¥${data.value.toFixed(2)}</div>
 <div>占比: ${data.percentage}%</div>
 </div>`;
 }
 },
 legend: {
 orient: 'vertical',
 right: '5%',
 top: 'center',
 itemWidth: 12,
 itemHeight: 12,
 textStyle: {
 fontSize: 12
 }
 },
 series: [
 {
 type: 'pie',
 radius: ['45%', '70%'],
 center: ['35%', '50%'],
 avoidLabelOverlap: false,
 itemStyle: {
 borderRadius: 8,
 borderColor: '#fff',
 borderWidth: 2
 },
 label: {
 show: false,
 position: 'center'
 },
 emphasis: {
 label: {
 show: true,
 fontSize: 16,
 fontWeight: 'bold',
 formatter: '{d}%'
 }
 },
 labelLine: {
 show: false
 },
 data: data,
 color: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#8e44ad', '#16a085', '#d35400']
 }
 ]
 };
});
const salesChartOption = computed<EChartsOption>(() => {
 const dates = salesTrendData.value.map(item => item.date);
 const metricKey = salesMetric.value;
 const values = salesTrendData.value.map(item => {
 const val = item[metricKey] || 0;
 return metricKey === 'revenue' ? Number(val.toFixed(2)) : val;
 });
 const yAxisName = metricKey === 'revenue' ? '销售额(元)' : metricKey === 'order_count' ? '订单数' : '图书数';
 const color = metricKey === 'revenue' ? '#67C23A' : metricKey === 'order_count' ? '#409EFF' : '#E6A23C';
 return {
 tooltip: {
 trigger: 'axis',
 axisPointer: {
 type: 'cross'
 },
 formatter: (params: any) => {
 const data = params[0];
 let value = data.value;
 let suffix = '';
 if (metricKey === 'revenue') {
 suffix = ' 元';
 value = `¥${Number(value).toFixed(2)}`;
 }
 else if (metricKey === 'order_count') {
 suffix = ' 单';
 }
 else {
 suffix = ' 本';
 }
 return `<div style="padding: 4px;">
 <div style="font-weight: bold; margin-bottom: 4px;">${data.axisValue}</div>
 <div><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${color};margin-right:6px;"></span>${yAxisName}: ${value}${suffix}</div>
 </div>`;
 }
 },
 grid: {
 left: '3%',
 right: '4%',
 bottom: '3%',
 top: '10%',
 containLabel: true
 },
 xAxis: {
 type: 'category',
 boundaryGap: false,
 data: dates,
 axisLabel: {
 fontSize: 11,
 rotate: dates.length > 30 ? 45 : 0,
 formatter: (value: string) => {
 if (dates.length > 30) {
 return value.slice(5);
 }
 return value.slice(5);
 }
 },
 axisLine: {
 lineStyle: {
 color: '#e4e7ed'
 }
 }
 },
 yAxis: {
 type: 'value',
 name: yAxisName,
 nameTextStyle: {
 color: '#909399',
 fontSize: 12
 },
 axisLabel: {
 fontSize: 11,
 formatter: (value: number) => {
 if (metricKey === 'revenue' && value >= 10000) {
 return (value / 10000).toFixed(1) + 'w';
 }
 return value.toString();
 }
 },
 splitLine: {
 lineStyle: {
 color: '#f0f2f5',
 type: 'dashed'
 }
 }
 },
 series: [
 {
 type: 'line',
 smooth: true,
 symbol: 'circle',
 symbolSize: 6,
 data: values,
 lineStyle: {
 width: 3,
 color: color
 },
 itemStyle: {
 color: color,
 borderWidth: 2,
 borderColor: '#fff'
 },
 areaStyle: {
 color: {
 type: 'linear',
 x: 0,
 y: 0,
 x2: 0,
 y2: 1,
 colorStops: [
 { offset: 0, color: color + '40' },
 { offset: 1, color: color + '05' }
 ]
 }
 }
 }
 ]
 };
});
let refreshTimer: number | null = null;
const fetchData = async () => {
 loading.value = true;
 error.value = false;
 try {
 dashboardData.value = await api.getDashboardStats(timeRange.value);
 }
 catch (err) {
 console.error('获取仪表盘数据失败:', err);
 error.value = true;
 ElMessage.error('数据加载失败');
 }
 finally {
 loading.value = false;
 }
};
const handleTimeRangeChange = () => {
 fetchData();
};
const updateSalesChart = () => {
};
const handleCardClick = (card: any) => {
 if (card.route) {
 navigateTo(card.route, card.query);
 }
};
const navigateTo = (tab: string, query: Record<string, any> = {}) => {
 router.push({
 path: '/admin',
 query: { tab, ...query }
 });
};
const navigateToBookDetail = (bookId: number) => {
 router.push({ path: `/books/${bookId}` });
};
const navigateToOrderDetail = (orderId: number) => {
 router.push({ path: `/orders/${orderId}` });
};
const formatNumber = (num: number): string => {
 if (num >= 10000) {
 return (num / 10000).toFixed(1) + 'w';
 }
 if (num >= 1000) {
 return (num / 1000).toFixed(1) + 'k';
 }
 return num.toLocaleString();
};
const formatDate = (dateStr: string): string => {
 const date = new Date(dateStr);
 const now = new Date();
 const diff = now.getTime() - date.getTime();
 const minutes = Math.floor(diff / 60000);
 const hours = Math.floor(diff / 3600000);
 const days = Math.floor(diff / 86400000);
 if (minutes < 1)
 return '刚刚';
 if (minutes < 60)
 return `${minutes}分钟前`;
 if (hours < 24)
 return `${hours}小时前`;
 if (days < 7)
 return `${days}天前`;
 return `${date.getMonth() + 1}/${date.getDate()}`;
};
const getOrderStatusType = (status: string): 'success' | 'warning' | 'info' | 'primary' | 'danger' => {
 const types: Record<string, 'success' | 'warning' | 'info' | 'primary' | 'danger'> = {
 pending: 'warning',
 confirmed: 'primary',
 shipped: 'info',
 delivered: 'success',
 cancelled: 'danger'
 };
 return types[status] || 'info';
};
const getOrderStatusText = (status: string): string => {
 const texts: Record<string, string> = {
 pending: '待确认',
 confirmed: '已确认',
 shipped: '已发货',
 delivered: '已完成',
 cancelled: '已取消'
 };
 return texts[status] || status;
};
const handleImageError = (e: Event) => {
 const target = e.target as HTMLImageElement;
 target.src = defaultCover;
};
onMounted(() => {
 fetchData();
 refreshTimer = window.setInterval(() => {
 fetchData();
 }, 60000);
});
onBeforeUnmount(() => {
 if (refreshTimer) {
 clearInterval(refreshTimer);
 }
});
</script>

<style scoped>
.dashboard-page {
  padding: 20px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.dashboard-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: #303133;
}

.dashboard-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.dashboard-content {
  min-height: 400px;
}

.error-state {
  padding: 60px 0;
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 12px;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #f0f2f5;
  position: relative;
  overflow: hidden;
  margin-bottom: 16px;
}

.stat-card--disabled {
  cursor: default;
}

.stat-card--disabled:hover {
  transform: none;
  box-shadow: none;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: currentColor;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-card.primary { color: #409EFF; }
.stat-card.success { color: #67C23A; }
.stat-card.warning { color: #E6A23C; }
.stat-card.info { color: #909399; }
.stat-card.purple { color: #8e44ad; }
.stat-card.orange { color: #d35400; }

.stat-card.primary .stat-card-icon { background: linear-gradient(135deg, #409EFF, #66b1ff); }
.stat-card.success .stat-card-icon { background: linear-gradient(135deg, #67C23A, #85ce61); }
.stat-card.warning .stat-card-icon { background: linear-gradient(135deg, #E6A23C, #ebb563); }
.stat-card.info .stat-card-icon { background: linear-gradient(135deg, #909399, #a6a9ad); }
.stat-card.purple .stat-card-icon { background: linear-gradient(135deg, #8e44ad, #9b59b6); }
.stat-card.orange .stat-card-icon { background: linear-gradient(135deg, #d35400, #e67e22); }

.stat-card-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.stat-card-info {
  flex: 1;
  margin-left: 16px;
  min-width: 0;
}

.stat-card-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-card-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.stat-card-sublabel {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.stat-card-sublabel .sub-value {
  color: #67C23A;
  font-weight: 500;
}

.stat-card-arrow {
  color: #c0c4cc;
  margin-left: 8px;
  transition: transform 0.3s;
}

.stat-card:hover .stat-card-arrow {
  transform: translateX(4px);
}

.dashboard-charts {
  margin-bottom: 20px;
}

.chart-col {
  margin-bottom: 16px;
}

.chart-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #f0f2f5;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #303133;
}

.chart-body {
  flex: 1;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart {
  width: 100%;
  height: 300px;
}

.empty-chart {
  width: 100%;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dashboard-lists {
  margin-bottom: 20px;
}

.list-col {
  margin-bottom: 16px;
}

.list-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #f0f2f5;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.list-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #303133;
}

.list-body {
  flex: 1;
  min-height: 300px;
}

.empty-list {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.recent-books-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.book-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  gap: 12px;
}

.book-item:hover {
  background: #f5f7fa;
}

.book-cover {
  width: 50px;
  height: 65px;
  object-fit: cover;
  border-radius: 4px;
  flex-shrink: 0;
}

.book-info {
  flex: 1;
  min-width: 0;
}

.book-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 4px;
}

.book-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.book-price {
  color: #F56C6C;
  font-weight: 500;
  font-size: 13px;
}

.book-date {
  font-size: 12px;
  color: #909399;
  flex-shrink: 0;
}

.recent-orders-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.order-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  gap: 12px;
}

.order-item:hover {
  background: #f5f7fa;
}

.order-icon {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.order-info {
  flex: 1;
  min-width: 0;
}

.order-no {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  font-family: 'Monaco', 'Consolas', monospace;
}

.order-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.order-right {
  text-align: right;
  flex-shrink: 0;
}

.order-amount {
  font-size: 16px;
  font-weight: 600;
  color: #F56C6C;
  margin-bottom: 4px;
}

@media (max-width: 768px) {
  .dashboard-page {
    padding: 12px;
  }
  
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .dashboard-actions {
    width: 100%;
  }
  
  .dashboard-actions .el-radio-group {
    flex: 1;
  }
  
  .stat-card {
    padding: 16px;
  }
  
  .stat-card-icon {
    width: 48px;
    height: 48px;
  }
  
  .stat-card-value {
    font-size: 20px;
  }
  
  .chart-card,
  .list-card {
    padding: 16px;
  }
}
</style>
