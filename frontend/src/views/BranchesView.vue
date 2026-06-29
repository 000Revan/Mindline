<script setup lang="ts">
import { useMindlineStore } from '@/stores/mindline'

const store = useMindlineStore()
</script>

<template>
  <section class="page-shell">
    <div class="page-title-row">
      <div>
        <p class="page-kicker">Branch Parking</p>
        <h2 class="page-title">分支停车场</h2>
        <p class="page-subtitle">
          把偏离主线但值得回收的问题停放起来。必要时开启 5/10/15 分钟限时溯源，时间到后写下最低可用理解并回到主线。
        </p>
      </div>
      <el-button type="primary">
        <el-icon><Plus /></el-icon>
        新增分支
      </el-button>
    </div>

    <div class="branch-grid">
      <article v-for="branch in store.branches" :key="branch.id" class="branch-card">
        <div class="branch-head">
          <el-tag :type="branch.status === 'returned' ? 'success' : 'warning'">
            {{ branch.status }}
          </el-tag>
          <el-tag type="info">P{{ branch.priority }}</el-tag>
        </div>
        <h3>{{ branch.title }}</h3>
        <p>{{ branch.description }}</p>
        <el-divider />
        <dl>
          <div>
            <dt>偏离原因</dt>
            <dd>{{ branch.reason }}</dd>
          </div>
          <div>
            <dt>最低可用理解</dt>
            <dd>{{ branch.minimumUnderstanding || '等待限时溯源后补充' }}</dd>
          </div>
        </dl>
        <div class="branch-actions">
          <el-button type="primary" plain>
            <el-icon><Timer /></el-icon>
            {{ branch.timeboxMinutes }} 分钟溯源
          </el-button>
          <el-button plain>标记回归</el-button>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.branch-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.branch-card {
  padding: 18px;
  border: 1px solid var(--ml-line);
  border-radius: var(--ml-radius);
  background: var(--ml-surface);
}

.branch-head,
.branch-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.branch-card h3 {
  margin: 14px 0 8px;
  color: var(--ml-primary-dark);
}

.branch-card p,
.branch-card dd {
  color: var(--ml-muted);
  line-height: 1.65;
}

.branch-card dl {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 0 0 16px;
}

.branch-card dt {
  color: var(--ml-primary);
  font-size: 12px;
  font-weight: 700;
}

.branch-card dd {
  margin: 4px 0 0;
}

@media (max-width: 900px) {
  .branch-grid {
    grid-template-columns: 1fr;
  }
}
</style>
