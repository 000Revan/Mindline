<script setup lang="ts">
import { useMindlineStore } from '@/stores/mindline'

const store = useMindlineStore()
</script>

<template>
  <section class="page-shell">
    <div class="page-title-row">
      <div>
        <p class="page-kicker">Learning Sessions</p>
        <h2 class="page-title">学习记录</h2>
        <p class="page-subtitle">
          对应 `learning_sessions`，保存一次真实学习过程、专注度、总结和可复盘事实。
        </p>
      </div>
      <el-button type="primary">
        <el-icon><VideoPlay /></el-icon>
        开始学习
      </el-button>
    </div>

    <div class="soft-list">
      <article v-for="session in store.learningSessions" :key="session.id" class="soft-item session-card">
        <div>
          <p class="soft-item-title">{{ session.title }}</p>
          <p class="soft-item-desc">{{ session.content }}</p>
          <p class="session-summary">{{ session.summary }}</p>
        </div>
        <div class="session-score">
          <el-progress type="circle" :percentage="session.focusScore" :width="72" color="#4268d6" />
          <span>{{ session.durationMinutes }} 分钟</span>
          <el-tag type="success">{{ session.status }}</el-tag>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.session-card {
  display: flex;
  justify-content: space-between;
  gap: 18px;
}

.session-summary {
  margin: 12px 0 0;
  color: var(--ml-primary-dark);
  font-weight: 600;
}

.session-score {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
  color: var(--ml-muted);
}
</style>
