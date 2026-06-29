import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import {
  mockAgentRuns,
  mockBranches,
  mockConversations,
  mockEmotionLogs,
  mockGoals,
  mockKnowledgePoints,
  mockNotes,
  mockReviews,
  mockSessions,
  mockTasks,
  mockUser,
} from '@/data/mockMindline'
import type { ChatMessage, ConversationSession, UserProfile } from '@/types/mindline'

function readStoredUser(): UserProfile | null {
  const rawUser = localStorage.getItem('mindline_user')
  if (!rawUser) return null

  try {
    const parsed = JSON.parse(rawUser) as UserProfile
    return parsed.username ? parsed : null
  } catch {
    return null
  }
}

export const useMindlineStore = defineStore('mindline', () => {
  const user = ref<UserProfile>(readStoredUser() ?? mockUser)
  const goals = ref(mockGoals)
  const tasks = ref(mockTasks)
  const learningSessions = ref(mockSessions)
  const branches = ref(mockBranches)
  const notes = ref(mockNotes)
  const knowledgePoints = ref(mockKnowledgePoints)
  const reviews = ref(mockReviews)
  const emotionLogs = ref(mockEmotionLogs)
  const conversations = ref<ConversationSession[]>(mockConversations)
  const agentRuns = ref(mockAgentRuns)
  const activeConversationId = ref(conversations.value[0]?.id ?? 0)

  const activeGoal = computed(() => goals.value.find((goal) => goal.status === 'active'))
  const activeConversation = computed(() =>
    conversations.value.find((session) => session.id === activeConversationId.value),
  )
  const todayTasks = computed(() => tasks.value)
  const pendingBranches = computed(() =>
    branches.value.filter((branch) => branch.status !== 'returned' && branch.status !== 'archived'),
  )
  const completedTaskCount = computed(
    () => tasks.value.filter((task) => task.status === 'completed').length,
  )

  function selectConversation(id: number) {
    activeConversationId.value = id
  }

  function createConversation(type: ConversationSession['sessionType'] = 'study') {
    const nextId = Math.max(...conversations.value.map((item) => item.id), 0) + 1
    const session: ConversationSession = {
      id: nextId,
      publicId: `local-${Date.now()}`,
      title: type === 'emotion' ? '新的情绪陪伴' : '新的学习会话',
      sessionType: type,
      status: 'active',
      updatedAt: '刚刚',
      messages: [
        {
          id: 1,
          role: 'assistant',
          content: '新的会话已经准备好。你可以直接告诉我今天要推进什么。',
          createdAt: '刚刚',
        },
      ],
    }
    conversations.value.unshift(session)
    activeConversationId.value = nextId
  }

  function deleteConversation(id: number) {
    conversations.value = conversations.value.filter((item) => item.id !== id)
    if (activeConversationId.value === id) {
      activeConversationId.value = conversations.value[0]?.id ?? 0
    }
  }

  function sendMessage(content: string) {
    const session = activeConversation.value
    if (!session || !content.trim()) return

    const nextId = Math.max(...session.messages.map((message) => message.id), 0) + 1
    const userMessage: ChatMessage = {
      id: nextId,
      role: 'user',
      content: content.trim(),
      createdAt: '刚刚',
    }
    const assistantMessage: ChatMessage = {
      id: nextId + 1,
      role: 'assistant',
      content: '已记录。你可以选择把它保存为笔记、加入分支停车场，或生成下一步任务。',
      createdAt: '刚刚',
    }

    session.messages.push(userMessage, assistantMessage)
    session.updatedAt = '刚刚'
  }

  return {
    user,
    goals,
    tasks,
    learningSessions,
    branches,
    notes,
    knowledgePoints,
    reviews,
    emotionLogs,
    conversations,
    agentRuns,
    activeConversationId,
    activeGoal,
    activeConversation,
    todayTasks,
    pendingBranches,
    completedTaskCount,
    selectConversation,
    createConversation,
    deleteConversation,
    sendMessage,
  }
})
