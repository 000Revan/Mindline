<script setup lang="ts">
import { ref } from 'vue'
import { useMindlineStore } from '@/stores/mindline'

const store = useMindlineStore()
const draft = ref('')

function send() {
  store.sendMessage(draft.value)
  draft.value = ''
}
</script>

<template>
  <section class="chat-page">
    <div class="chat-main panel-card">
      <header class="chat-header">
        <div>
          <p class="page-kicker">Agent Conversation</p>
          <h2 class="page-title">智能体对话</h2>
          <p class="page-subtitle">
            围绕当前学习主线对话，并把 AI 回答保存为笔记、把偏题问题转入分支停车场。
          </p>
        </div>
        <el-button plain>
          <el-icon><Delete /></el-icon>
          清空本轮
        </el-button>
      </header>

      <div class="chat-tags">
        <el-tag type="primary">MainlineAgent 在线</el-tag>
        <el-tag type="success">可保存为笔记</el-tag>
        <el-tag type="warning">可加入分支停车场</el-tag>
      </div>

      <section class="message-list" aria-label="当前会话消息">
        <article
          v-for="message in store.activeConversation?.messages"
          :key="message.id"
          class="message"
          :class="message.role"
        >
          <span class="message-meta">{{ message.role }} · {{ message.createdAt }}</span>
          <p>{{ message.content }}</p>
          <div v-if="message.role === 'assistant'" class="toolbar-row">
            <el-button size="small" plain>保存为笔记</el-button>
            <el-button size="small" plain>加入分支</el-button>
            <el-button size="small" plain>生成任务</el-button>
          </div>
        </article>
      </section>

      <footer class="composer">
        <el-input
          v-model="draft"
          size="large"
          placeholder="直接交代今天要做什么，例如：先帮我生成学习任务"
          @keyup.enter="send"
        />
        <el-button type="primary" size="large" @click="send">发送</el-button>
      </footer>
    </div>

    <aside class="conversation-panel panel-card">
      <div class="conversation-header">
        <div>
          <p class="page-kicker">History</p>
          <h3>会话历史</h3>
        </div>
        <el-button type="primary" plain @click="store.createConversation('study')">
          <el-icon><Plus /></el-icon>
          新建
        </el-button>
      </div>

      <div class="soft-list">
        <article
          v-for="session in store.conversations"
          :key="session.id"
          class="conversation-item"
          :class="{ active: session.id === store.activeConversationId }"
          @click="store.selectConversation(session.id)"
        >
          <div>
            <p class="soft-item-title">{{ session.title }}</p>
            <p class="soft-item-desc">{{ session.sessionType }} · {{ session.updatedAt }}</p>
          </div>
          <el-button
            text
            type="danger"
            aria-label="删除会话"
            @click.stop="store.deleteConversation(session.id)"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
        </article>
      </div>
    </aside>
  </section>
</template>

<style scoped>
.chat-page {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 16px;
  min-height: calc(100vh - 120px);
}

.chat-main,
.conversation-panel {
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 18px;
}

.chat-header,
.conversation-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.chat-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 16px 0;
}

.message-list {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 14px;
  overflow: auto;
  padding: 12px 0;
}

.message {
  max-width: 78%;
  padding: 16px 18px;
  border: 1px solid var(--ml-line);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.74);
}

.message.user {
  align-self: flex-end;
  background: var(--ml-primary-soft);
}

.message-meta {
  color: var(--ml-muted);
  font-size: 12px;
}

.message p {
  margin: 8px 0 12px;
  color: var(--ml-primary-dark);
  line-height: 1.7;
}

.composer {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid var(--ml-line);
}

.conversation-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px;
  border: 1px solid var(--ml-line);
  border-radius: var(--ml-radius);
  cursor: pointer;
  background: rgba(255, 255, 255, 0.66);
}

.conversation-item.active {
  border-color: var(--ml-primary);
  background: var(--ml-primary-soft);
}

@media (max-width: 1020px) {
  .chat-page {
    grid-template-columns: 1fr;
  }
}
</style>
