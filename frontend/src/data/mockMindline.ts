import type {
  AgentRun,
  BranchTopic,
  ConversationSession,
  EmotionLog,
  KnowledgePoint,
  LearningGoal,
  LearningSession,
  NoteItem,
  ReviewItem,
  UserProfile,
} from '@/types/mindline'

export const mockUser: UserProfile = {
  username: 'mindline_user',
  nickname: '学习者',
  targetDirection: 'Python 后端与 AI 应用开发',
  anxietyLevel: 3,
}

export const mockGoals: LearningGoal[] = [
  {
    id: 1,
    title: '掌握 FastAPI + LangGraph 学习助手主线',
    description: '先完成可用闭环，再逐步沉淀 RAG、Agent 编排和复盘能力。',
    direction: 'AI 后端工程',
    status: 'active',
    priority: 1,
    currentStage: 'MVP 业务接口与前端体验整合',
    currentPrinciple: '今天只推进最小闭环，分支先停车。',
    startDate: '2026-06-01',
    targetDate: '2026-07-20',
  },
  {
    id: 2,
    title: '整理个人知识库检索笔记',
    description: '把已有笔记整理为可切片、可检索、可回查的知识资产。',
    direction: 'RAG 知识库',
    status: 'pending',
    priority: 2,
    currentStage: '等待笔记接口补齐',
    currentPrinciple: '先保存原始事实，再做 AI 优化。',
    startDate: null,
    targetDate: '2026-08-01',
  },
]

export const mockSessions: LearningSession[] = [
  {
    id: 1,
    title: '前端体验整合规划',
    content: '确认三栏工作台、会话历史、分支停车场与复盘入口。',
    durationMinutes: 35,
    focusScore: 86,
    status: 'completed',
    summary: '页面骨架应优先支撑学习主线闭环，而不是单纯聊天。',
    startedAt: '09:15',
  },
  {
    id: 2,
    title: '用户接口适配检查',
    content: '确认当前后端已具备注册、登录、用户信息更新、修改密码等能力。',
    durationMinutes: 25,
    focusScore: 78,
    status: 'completed',
    summary: '前端 API 层先接入 auth/user，其他模块保留模拟数据位。',
    startedAt: '10:10',
  },
]

export const mockBranches: BranchTopic[] = [
  {
    id: 1,
    title: 'LangGraph Checkpointer 是否能替代业务表？',
    description: '容易偏离主线，需要明确边界。',
    reason: '设计文档强调 checkpointer 只保存流程恢复点。',
    status: 'returned',
    priority: 1,
    timeboxMinutes: 10,
    minimumUnderstanding: '不能替代 MySQL 正式业务事实数据。',
    returnSummary: '回到当前 learning_goal，先实现业务事实落表。',
  },
  {
    id: 2,
    title: 'Chroma metadata 需要存哪些字段？',
    description: 'RAG 检索时必须避免跨用户。',
    reason: '关系到 user_id 隔离与回查 MySQL。',
    status: 'limited_learning',
    priority: 2,
    timeboxMinutes: 15,
    minimumUnderstanding: '至少包含 user_id、note_id、chunk_id。',
    returnSummary: '计时结束后写入 note_chunks 设计备注。',
  },
]

export const mockNotes: NoteItem[] = [
  {
    id: 1,
    title: 'Mindline 核心理念',
    noteType: 'manual',
    summary: '允许好奇，但不让好奇接管主线。',
    tags: ['主线', '产品理念'],
    status: 'active',
    isVectorized: true,
  },
  {
    id: 2,
    title: '分支停车场限时溯源规则',
    noteType: 'branch_summary',
    summary: '5/10/15 分钟后总结最低可用理解，并提醒回到当前主线。',
    tags: ['分支', '限时溯源'],
    status: 'active',
    isVectorized: false,
  },
]

export const mockKnowledgePoints: KnowledgePoint[] = [
  { id: 1, name: '用户数据隔离', domain: '后端安全', masteryLevel: 72, importanceLevel: 5 },
  { id: 2, name: '学习主线闭环', domain: '产品设计', masteryLevel: 84, importanceLevel: 5 },
  { id: 3, name: 'Agent 运行追踪', domain: 'LangGraph', masteryLevel: 48, importanceLevel: 4 },
]

export const mockReviews: ReviewItem[] = [
  {
    id: 1,
    type: 'daily',
    title: '今日复盘',
    mainlineProgress: '完成前端页面骨架设计，明确 API 适配层边界。',
    learnedSummary: '学习任务不是题目，分支问题需要停车与回收。',
    problems: 'Agent 接口尚未实现，需要用模拟数据位占位。',
    nextPlan: '补齐学习目标与每日任务接口后替换 mock 数据。',
    aiFeedback: '今天的推进聚焦在主线闭环，节奏稳定。',
  },
  {
    id: 2,
    type: 'weekly',
    title: '本周复盘',
    mainlineProgress: '后端基础、ORM 建模和用户系统已成形。',
    learnedSummary: '业务事实、向量检索、Agent checkpoint 的边界更清晰。',
    problems: '前端体验尚需把学习状态可视化。',
    nextPlan: '先把工作台、对话、分支、复盘串起来。',
    aiFeedback: '继续避免把后续扩展提前塞进 MVP。',
  },
]

export const mockEmotionLogs: EmotionLog[] = [
  {
    id: 1,
    emotionType: '焦虑',
    intensity: 3,
    supportMode: '行动拆解',
    actionSuggestion: '把“不会的太多”拆成一个 20 分钟可完成任务。',
    riskLevel: 'low',
    followUpNeeded: false,
  },
  {
    id: 2,
    emotionType: '迷茫',
    intensity: 2,
    supportMode: '倾听与复盘',
    actionSuggestion: '先回看今日已完成学习事实，再决定下一步。',
    riskLevel: 'low',
    followUpNeeded: true,
  },
]

export const mockConversations: ConversationSession[] = [
  {
    id: 1,
    publicId: 'chat-mainline-001',
    title: '学习主线推进',
    sessionType: 'study',
    status: 'active',
    updatedAt: '09:32',
    messages: [
      {
        id: 1,
        role: 'assistant',
        content: '早上好。今天建议先推进当前主线任务，再把偏离主题的问题放入分支停车场。',
        createdAt: '09:12',
      },
      {
        id: 2,
        role: 'user',
        content: '先帮我生成今天的学习任务。',
        createdAt: '09:13',
      },
      {
        id: 3,
        role: 'assistant',
        content:
          '可以。建议先完成学习目标页面字段梳理，再记录一次学习 session，最后回收一个限时分支。',
        createdAt: '09:14',
      },
    ],
  },
  {
    id: 2,
    publicId: 'chat-emotion-002',
    title: '焦虑拆解',
    sessionType: 'emotion',
    status: 'active',
    updatedAt: '昨天',
    messages: [
      {
        id: 1,
        role: 'assistant',
        content: '我们先不评价你会不会，只把下一步任务缩小到能完成的程度。',
        createdAt: '21:08',
      },
    ],
  },
]

export const mockAgentRuns: AgentRun[] = [
  { id: 1, agentName: 'MainlineAgent', intent: '生成每日学习任务', status: 'succeeded' },
  { id: 2, agentName: 'BranchAgent', intent: '限时溯源与回归主线', status: 'running' },
  { id: 3, agentName: 'NoteAgent', intent: '保存 AI 回答为笔记', status: 'queued' },
]
