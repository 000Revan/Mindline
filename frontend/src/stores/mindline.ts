import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import {
  authApi,
  learningApi,
  type DailyTaskCreatePayload,
  type DailyTaskUpdatePayload,
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
  mockUser,
} from '@/data/mockMindline'
import type {
  ChatMessage,
  ConversationSession,
  DailyTask,
  DailyTaskStatus,
  LearningGoal,
  LearningGoalStatus,
  LearningGoalStatusAction,
  UserProfile,
} from '@/types/mindline'

function getLocalDateString(date = new Date()) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

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
  const tasks = ref<DailyTask[]>([])
  const tasksLoading = ref(false)
  const tasksError = ref('')
  const taskDate = ref(getLocalDateString())
  const taskStatusFilter = ref<DailyTaskStatus | ''>('')
  const taskPage = ref(1)
  const taskPageSize = ref(10)
  const taskTotal = ref(0)
  const taskTotalPages = ref(0)
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
    localStorage.removeItem('mindline_user_portrait')

    user.value = { username: '' }
    goals.value = []
    activeGoal.value = undefined
    goalsError.value = ''
    goalPage.value = 1
    goalTotal.value = 0
    goalTotalPages.value = 0
    goalStatusFilter.value = ''
    tasks.value = []
    tasksError.value = ''
    taskDate.value = getLocalDateString()
    taskStatusFilter.value = ''
    taskPage.value = 1
    taskTotal.value = 0
    taskTotalPages.value = 0
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

  async function changeGoalStatus(goalId: number, status: LearningGoalStatusAction) {
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

  async function archiveGoal(goalId: number) {
    const archivedGoal = await learningApi.archiveGoal(goalId)
    if (activeGoal.value?.id === goalId) activeGoal.value = undefined

    const [goalsResult] = await Promise.allSettled([
      fetchGoals(goalPage.value, goalStatusFilter.value),
      fetchActiveGoal(),
    ])
    if (
      goalsResult.status === 'fulfilled' &&
      goalsResult.value.items.length === 0 &&
      goalsResult.value.page > 1
    ) {
      await fetchGoals(goalsResult.value.page - 1, goalStatusFilter.value)
    }
    return archivedGoal
  }

  async function fetchDailyTasks(
    page = taskPage.value,
    date = taskDate.value,
    status: DailyTaskStatus | '' = taskStatusFilter.value,
  ) {
    tasksLoading.value = true
    tasksError.value = ''
    try {
      const result = await learningApi.listDailyTasks({
        page,
        pageSize: taskPageSize.value,
        taskDate: date,
        status: status || undefined,
      })
      tasks.value = result.items
      taskDate.value = date
      taskStatusFilter.value = status
      taskPage.value = result.page
      taskTotal.value = result.total
      taskTotalPages.value = result.totalPages
      return result
    } catch (error) {
      tasksError.value = error instanceof Error ? error.message : '每日学习任务加载失败'
      throw error
    } finally {
      tasksLoading.value = false
    }
  }

  async function createDailyTask(payload: DailyTaskCreatePayload) {
    const createdTask = await learningApi.createDailyTask(payload)
    await fetchDailyTasks(1, taskDate.value, taskStatusFilter.value)
    return createdTask
  }

  async function updateDailyTask(taskId: number, payload: DailyTaskUpdatePayload) {
    const updatedTask = await learningApi.updateDailyTask(taskId, payload)
    await fetchDailyTasks(taskPage.value, taskDate.value, taskStatusFilter.value)
    return updatedTask
  }

  async function changeDailyTaskStatus(taskId: number, status: DailyTaskStatus) {
    const updatedTask = await learningApi.updateDailyTaskStatus(taskId, status)
    const result = await fetchDailyTasks(taskPage.value, taskDate.value, taskStatusFilter.value)
    if (!result.items.length && result.page > 1) {
      await fetchDailyTasks(result.page - 1, taskDate.value, taskStatusFilter.value)
    }
    return updatedTask
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
    tasksLoading,
    tasksError,
    taskDate,
    taskStatusFilter,
    taskPage,
    taskPageSize,
    taskTotal,
    taskTotalPages,
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
    archiveGoal,
    fetchDailyTasks,
    createDailyTask,
    updateDailyTask,
    changeDailyTaskStatus,
    selectConversation,
    createConversation,
    deleteConversation,
    sendMessage,
  }
})
