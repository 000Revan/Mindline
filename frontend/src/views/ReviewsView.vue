<script setup lang="ts">
import { ref } from 'vue'
import { useMindlineStore } from '@/stores/mindline'

const store = useMindlineStore()
const activeTab = ref('daily')
</script>

<template>
  <section class="page-shell">
    <div class="page-title-row">
      <div>
        <p class="page-kicker">Review</p>
        <h2 class="page-title">每日/每周复盘</h2>
        <p class="page-subtitle">
          汇总学习记录、笔记、分支和情绪趋势，帮助用户看到已经推进的事实。
        </p>
      </div>
      <el-button type="primary">
        <el-icon><DocumentChecked /></el-icon>
        生成今日复盘
      </el-button>
    </div>

    <el-tabs v-model="activeTab" class="panel-card review-tabs">
      <el-tab-pane label="每日复盘" name="daily">
        <article
          v-for="review in store.reviews.filter((item) => item.type === 'daily')"
          :key="review.id"
          class="review-card"
        >
          <h3>{{ review.title }}</h3>
          <p><strong>主线推进：</strong>{{ review.mainlineProgress }}</p>
          <p><strong>学到什么：</strong>{{ review.learnedSummary }}</p>
          <p><strong>问题：</strong>{{ review.problems }}</p>
          <p><strong>明日计划：</strong>{{ review.nextPlan }}</p>
          <el-alert :title="review.aiFeedback" type="success" :closable="false" show-icon />
        </article>
      </el-tab-pane>
      <el-tab-pane label="每周复盘" name="weekly">
        <article
          v-for="review in store.reviews.filter((item) => item.type === 'weekly')"
          :key="review.id"
          class="review-card"
        >
          <h3>{{ review.title }}</h3>
          <p><strong>主线推进：</strong>{{ review.mainlineProgress }}</p>
          <p><strong>本周收获：</strong>{{ review.learnedSummary }}</p>
          <p><strong>重复问题：</strong>{{ review.problems }}</p>
          <p><strong>下周计划：</strong>{{ review.nextPlan }}</p>
          <el-alert :title="review.aiFeedback" type="info" :closable="false" show-icon />
        </article>
      </el-tab-pane>
    </el-tabs>
  </section>
</template>

<style scoped>
.review-tabs {
  padding: 18px;
}

.review-card {
  padding: 16px;
  border: 1px solid var(--ml-line);
  border-radius: var(--ml-radius);
  background: var(--ml-surface-strong);
}

.review-card h3 {
  margin: 0 0 12px;
  color: var(--ml-primary-dark);
}

.review-card p {
  color: var(--ml-muted);
  line-height: 1.7;
}
</style>
