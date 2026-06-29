<script setup lang="ts">
import { useMindlineStore } from '@/stores/mindline'

const store = useMindlineStore()
</script>

<template>
  <section class="page-shell">
    <div class="page-title-row">
      <div>
        <p class="page-kicker">Learning Goals</p>
        <h2 class="page-title">学习主线</h2>
        <p class="page-subtitle">
          对应 `learning_goals`：保存学习目标、方向、阶段、优先级和当前学习约束。
        </p>
      </div>
      <el-button type="primary">
        <el-icon><Plus /></el-icon>
        新建主线
      </el-button>
    </div>

    <div class="soft-list">
      <article v-for="goal in store.goals" :key="goal.id" class="soft-item goal-card">
        <div>
          <p class="soft-item-title">{{ goal.title }}</p>
          <p class="soft-item-desc">{{ goal.description }}</p>
          <div class="toolbar-row">
            <el-tag type="primary">{{ goal.direction }}</el-tag>
            <el-tag :type="goal.status === 'active' ? 'success' : 'info'">{{ goal.status }}</el-tag>
            <el-tag type="warning">P{{ goal.priority }}</el-tag>
          </div>
        </div>
        <div class="goal-side">
          <strong>{{ goal.currentStage }}</strong>
          <span>{{ goal.currentPrinciple }}</span>
          <small>目标日期：{{ goal.targetDate }}</small>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.goal-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 18px;
}

.goal-side {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px;
  border-radius: var(--ml-radius);
  background: var(--ml-primary-soft);
  color: var(--ml-muted);
}

.goal-side strong {
  color: var(--ml-primary-dark);
}

@media (max-width: 860px) {
  .goal-card {
    grid-template-columns: 1fr;
  }
}
</style>
