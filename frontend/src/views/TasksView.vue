<script setup lang="ts">
import { useMindlineStore } from '@/stores/mindline'

const store = useMindlineStore()
</script>

<template>
  <section class="page-shell">
    <div class="page-title-row">
      <div>
        <p class="page-kicker">Daily Tasks</p>
        <h2 class="page-title">每日学习任务</h2>
        <p class="page-subtitle">
          对应 `daily_tasks`，只表示每日学习任务/计划，不包含每日题目、答题或批改。
        </p>
      </div>
      <el-button type="primary">
        <el-icon><MagicStick /></el-icon>
        按主线生成
      </el-button>
    </div>

    <el-table :data="store.todayTasks" class="panel-card">
      <el-table-column prop="title" label="任务" min-width="220" />
      <el-table-column prop="description" label="说明" min-width="300" />
      <el-table-column prop="taskType" label="类型" width="120" />
      <el-table-column label="状态" width="140">
        <template #default="{ row }">
          <el-tag :type="row.status === 'completed' ? 'success' : row.status === 'in_progress' ? 'primary' : 'warning'">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="预计" width="100">
        <template #default="{ row }">{{ row.estimatedTime }} 分钟</template>
      </el-table-column>
    </el-table>
  </section>
</template>
