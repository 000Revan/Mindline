<script setup lang="ts">
import { computed, ref } from 'vue'
import { useMindlineStore } from '@/stores/mindline'

const store = useMindlineStore()
const keyword = ref('')

const filteredNotes = computed(() => {
  const text = keyword.value.trim()
  if (!text) return store.notes
  return store.notes.filter((note) => {
    return note.title.includes(text) || note.summary.includes(text) || note.tags.some((tag) => tag.includes(text))
  })
})
</script>

<template>
  <section class="page-shell">
    <div class="page-title-row">
      <div>
        <p class="page-kicker">Notes & Knowledge</p>
        <h2 class="page-title">笔记库</h2>
        <p class="page-subtitle">
          保存原始笔记、AI 回答、分支总结和文件导入结果，后续通过 note_chunks 与 Chroma 做个人知识库检索。
        </p>
      </div>
      <div class="toolbar-row">
        <el-input v-model="keyword" placeholder="搜索笔记或标签" clearable />
        <el-button type="primary">
          <el-icon><EditPen /></el-icon>
          新建笔记
        </el-button>
      </div>
    </div>

    <div class="content-grid">
      <el-card>
        <template #header>
          <strong>笔记列表</strong>
        </template>
        <div v-if="filteredNotes.length" class="soft-list">
          <article v-for="note in filteredNotes" :key="note.id" class="soft-item">
            <p class="soft-item-title">{{ note.title }}</p>
            <p class="soft-item-desc">{{ note.summary }}</p>
            <div class="toolbar-row">
              <el-tag type="primary">{{ note.noteType }}</el-tag>
              <el-tag :type="note.isVectorized ? 'success' : 'info'">
                {{ note.isVectorized ? '已切片' : '待切片' }}
              </el-tag>
              <el-tag v-for="tag in note.tags" :key="tag" type="info">{{ tag }}</el-tag>
            </div>
          </article>
        </div>
        <div v-else class="empty-hint">暂无匹配笔记</div>
      </el-card>

      <el-card>
        <template #header>
          <strong>知识点沉淀</strong>
        </template>
        <div class="soft-list">
          <article v-for="point in store.knowledgePoints" :key="point.id" class="soft-item">
            <p class="soft-item-title">{{ point.name }}</p>
            <p class="soft-item-desc">{{ point.domain }}</p>
            <el-progress :percentage="point.masteryLevel" color="#4268d6" />
          </article>
        </div>
      </el-card>
    </div>
  </section>
</template>
