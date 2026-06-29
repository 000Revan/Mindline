<script setup lang="ts">
import { useMindlineStore } from '@/stores/mindline'

const store = useMindlineStore()
</script>

<template>
  <section class="page-shell">
    <div class="page-title-row">
      <div>
        <p class="page-kicker">Emotion Companion</p>
        <h2 class="page-title">情绪陪伴</h2>
        <p class="page-subtitle">
          只做倾听、安慰、焦虑拆解和行动建议，不输出医学诊断或治疗承诺。
        </p>
      </div>
      <el-button type="primary" @click="store.createConversation('emotion')">
        <el-icon><ChatDotRound /></el-icon>
        开始陪伴会话
      </el-button>
    </div>

    <div class="content-grid">
      <el-card>
        <template #header>
          <strong>支持记录</strong>
        </template>
        <div class="soft-list">
          <article v-for="log in store.emotionLogs" :key="log.id" class="soft-item emotion-row">
            <div>
              <p class="soft-item-title">{{ log.emotionType }} · 强度 {{ log.intensity }}/5</p>
              <p class="soft-item-desc">{{ log.actionSuggestion }}</p>
            </div>
            <div class="toolbar-row">
              <el-tag type="primary">{{ log.supportMode }}</el-tag>
              <el-tag :type="log.followUpNeeded ? 'warning' : 'success'">
                {{ log.followUpNeeded ? '需跟进' : '稳定' }}
              </el-tag>
            </div>
          </article>
        </div>
      </el-card>

      <el-card>
        <template #header>
          <strong>行动拆解模板</strong>
        </template>
        <div class="soft-list">
          <div class="soft-item">
            <p class="soft-item-title">把模糊焦虑改写为事实</p>
            <p class="soft-item-desc">不是“我什么都不会”，而是“今天还没有完成 FastAPI 路由复习”。</p>
          </div>
          <div class="soft-item">
            <p class="soft-item-title">缩小到 20 分钟动作</p>
            <p class="soft-item-desc">只完成一个可验证步骤，剩余问题进入分支停车场。</p>
          </div>
          <div class="soft-item">
            <p class="soft-item-title">用复盘关闭循环</p>
            <p class="soft-item-desc">记录今天推进了什么，而不是只盯着还不会什么。</p>
          </div>
        </div>
      </el-card>
    </div>
  </section>
</template>

<style scoped>
.emotion-row {
  display: flex;
  justify-content: space-between;
  gap: 18px;
}
</style>
