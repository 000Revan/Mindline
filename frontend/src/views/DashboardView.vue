<script setup lang="ts">
import { useMindlineStore } from '@/stores/mindline'

const store = useMindlineStore()
</script>

<template>
  <section class="page-shell">
    <div class="page-title-row">
      <div>
        <p class="page-kicker">Dashboard</p>
        <h2 class="page-title">学习工作台</h2>
        <p class="page-subtitle">
          以“学习主线 + 今日任务 + 分支停车场 + 笔记沉淀 + 复盘”为核心，把模糊焦虑转成下一步行动。
        </p>
      </div>
      <div class="toolbar-row">
        <RouterLink to="/chat">
          <el-button type="primary">
            <el-icon><ChatLineRound /></el-icon>
            开始对话
          </el-button>
        </RouterLink>
        <RouterLink to="/branches">
          <el-button plain>
            <el-icon><Timer /></el-icon>
            限时溯源
          </el-button>
        </RouterLink>
      </div>
    </div>

    <div class="metric-grid">
      <div class="metric-card">
        <p class="metric-label">今日任务</p>
        <p class="metric-value">{{ store.taskTotal }}</p>
      </div>
      <div class="metric-card">
        <p class="metric-label">待回收分支</p>
        <p class="metric-value">{{ store.pendingBranches.length }}</p>
      </div>
      <div class="metric-card">
        <p class="metric-label">已沉淀笔记</p>
        <p class="metric-value">{{ store.notes.length }}</p>
      </div>
      <div class="metric-card">
        <p class="metric-label">知识点</p>
        <p class="metric-value">{{ store.knowledgePoints.length }}</p>
      </div>
    </div>

    <div class="content-grid">
      <el-card>
        <template #header>
          <div class="page-title-row">
            <strong>今日推进顺序</strong>
            <el-tag type="primary">不包含每日题目</el-tag>
          </div>
        </template>
        <div class="soft-list">
          <article v-for="task in store.todayTasks" :key="task.id" class="soft-item task-row">
            <div>
              <p class="soft-item-title">{{ task.title }}</p>
              <p class="soft-item-desc">{{ task.description }}</p>
            </div>
            <div class="task-meta">
              <el-tag
                :type="
                  task.status === 'completed'
                    ? 'success'
                    : task.status === 'in_progress'
                      ? 'primary'
                      : 'warning'
                "
              >
                {{ task.status }}
              </el-tag>
              <span>{{ task.estimatedTime }} 分钟</span>
            </div>
          </article>
        </div>
      </el-card>

      <el-card>
        <template #header>
          <strong>主线守护</strong>
        </template>
        <div class="mainline-card">
          <p class="mainline-stage">{{ store.activeGoal?.currentStage }}</p>
          <h3>{{ store.activeGoal?.title }}</h3>
          <p>{{ store.activeGoal?.currentPrinciple }}</p>
          <el-divider />
          <div class="toolbar-row">
            <el-tag type="success">最低可用理解</el-tag>
            <el-tag type="warning">分支先停车</el-tag>
            <el-tag type="info">每日复盘</el-tag>
          </div>
        </div>
      </el-card>
    </div>
  </section>
</template>

<style scoped>
.task-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.task-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-end;
  color: var(--ml-muted);
  white-space: nowrap;
}

.mainline-card h3 {
  margin: 6px 0 10px;
  color: var(--ml-primary-dark);
  font-size: 22px;
}

.mainline-card p {
  color: var(--ml-muted);
  line-height: 1.7;
}

.mainline-stage {
  color: var(--ml-primary) !important;
  font-weight: 700;
}
</style>
