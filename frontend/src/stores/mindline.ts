import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import {
  authApi,
  learningApi,
  type LearningGoalCreatePayload,
  type LearningGoalUpdatePayload,
} from '@/api/client'
import {
  mockAgentRuns,
  mockBranches,
  mockConversations,
  mockEmotionLogs,
  mockKnowledgePoints,
  mockNotes,
  mockReviews,
  mockSessions,
  mockTasks,
  mockUser,
} from '@/data/mockMindline'
import type {
  ChatMessage,
  ConversationSession,
  LearningGoal,
  LearningGoalStatus,
  UserProfile,
} from '@/types/mindline'

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
  const goals = ref<LearningGoal[]>([])
  const activeGoal = ref<LearningGoal>()
  const goalsLoading = ref(false)
  const goalsError = ref('')
  const goalPage = ref(1)
  const goalPageSize = ref(10)
  const goalTotal = ref(0)
  const goalTotalPages = ref(0)
  const goalStatusFilter = ref<LearningGoalStatus | ''>('')
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

  function setUser(nextUser: UserProfile) {
    user.value = nextUser
    localStorage.setItem('mindline_user', JSON.stringify(nextUser))
  }

  function clearAuthSession() {
    localStorage.removeItem('mindline_token')
    localStorage.removeItem('mindline_user')
    localStorage.removeItem('mindline_avatar_data_url')

    user.value = { username: '' }
    goals.value = []
    activeGoal.value = undefined
    goalsError.value = ''
    goalPage.value = 1
    goalTotal.value = 0
    goalTotalPages.value = 0
    goalStatusFilter.value = ''
  }

  async function refreshCurrentUser() {
    const nextUser = await authApi.info()
    setUser(nextUser)
    return nextUser
  }

  async function fetchGoals(
    page = goalPage.value,
    status: LearningGoalStatus | '' = goalStatusFilter.value,
  ) {
    goalsLoading.value = true
    goalsError.value = ''
    try {
      const result = await learningApi.listGoals({
        page,
        pageSize: goalPageSize.value,
        status: status || undefined,
      })
      goals.value = result.items
      goalPage.value = result.page
      goalTotal.value = result.total
      goalTotalPages.value = result.totalPages
      goalStatusFilter.value = status
      return result
    } catch (error) {
      goalsError.value = error instanceof Error ? error.message : '学习目标加载失败'
      throw error
    } finally {
      goalsLoading.value = false
    }
  }

  async function fetchActiveGoal() {
    const result = await learningApi.listGoals({ page: 1, pageSize: 1, status: 'active' })
    activeGoal.value = result.items[0]
    return activeGoal.value
  }

  async function createGoal(payload: LearningGoalCreatePayload) {
    const createdGoal = await learningApi.createGoal(payload)
    await fetchGoals(1, goalStatusFilter.value)
    return createdGoal
  }

  async function updateGoal(goalId: number, payload: LearningGoalUpdatePayload) {
    const updatedGoal = await learningApi.updateGoal(goalId, payload)
    const index = goals.value.findIndex((goal) => goal.id === goalId)
    if (index >= 0) goals.value[index] = updatedGoal
    if (activeGoal.value?.id === goalId) activeGoal.value = updatedGoal
    return updatedGoal
  }

  async function changeGoalStatus(goalId: number, status: Exclude<LearningGoalStatus, 'pending'>) {
    const result = await learningApi.updateGoalStatus(goalId, status)

    if (status === 'active') {
      activeGoal.value = result.goal
      goals.value = goals.value.map((goal) => {
        if (goal.id === goalId) return result.goal
        return goal.status === 'active' ? { ...goal, status: 'paused' } : goal
      })
    } else {
      if (activeGoal.value?.id === goalId) activeGoal.value = undefined
      const index = goals.value.findIndex((goal) => goal.id === goalId)
      if (index >= 0) goals.value[index] = result.goal
    }

    await Promise.allSettled([
      fetchGoals(goalPage.value, goalStatusFilter.value),
      fetchActiveGoal(),
    ])
    return result
  }

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
    goalsLoading,
    goalsError,
    goalPage,
    goalPageSize,
    goalTotal,
    goalTotalPages,
    goalStatusFilter,
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
    setUser,
    clearAuthSession,
    refreshCurrentUser,
    fetchGoals,
    fetchActiveGoal,
    createGoal,
    updateGoal,
    changeGoalStatus,
    selectConversation,
    createConversation,
    deleteConversation,
    sendMessage,
  }
})
