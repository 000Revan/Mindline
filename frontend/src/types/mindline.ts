export type StatusTone = 'primary' | 'success' | 'warning' | 'info' | 'danger'
export type LearningGoalStatus = 'active' | 'pending' | 'paused' | 'completed' | 'archived'
export type LearningGoalStatusAction = 'active' | 'paused' | 'completed'

export interface UserProfile {
  id?: number
  username: string
  nickname?: string | null
  avatar_url?: string | null
  gender?: string
  bio?: string | null
  targetDirection?: string
  anxietyLevel?: number
}

export interface LearningGoal {
  id: number
  title: string
  description: string
  direction: string
  status: LearningGoalStatus
  priority: number
  currentStage: string
  currentPrinciple: string
  startDate: string | null
  targetDate: string | null
}

export interface DailyTask {
  id: number
  goalId: number
  title: string
  description: string
  taskType: 'study' | 'review' | 'branch' | 'reflection'
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  estimatedTime: number
  completedAt?: string
}

export interface LearningSession {
  id: number
  title: string
  content: string
  durationMinutes: number
  focusScore: number
  status: 'running' | 'completed' | 'paused'
  summary: string
  startedAt: string
}

export interface BranchTopic {
  id: number
  title: string
  description: string
  reason: string
  status: 'pending' | 'limited_learning' | 'returned' | 'converted_to_goal' | 'archived'
  priority: number
  timeboxMinutes: 5 | 10 | 15
  minimumUnderstanding: string
  returnSummary: string
}

export interface NoteItem {
  id: number
  title: string
  noteType: 'manual' | 'ai_answer' | 'branch_summary' | 'file_import'
  summary: string
  tags: string[]
  status: 'draft' | 'active' | 'archived'
  isVectorized: boolean
}

export interface KnowledgePoint {
  id: number
  name: string
  domain: string
  masteryLevel: number
  importanceLevel: number
}

export interface ReviewItem {
  id: number
  type: 'daily' | 'weekly'
  title: string
  mainlineProgress: string
  learnedSummary: string
  problems: string
  nextPlan: string
  aiFeedback: string
}

export interface EmotionLog {
  id: number
  emotionType: string
  intensity: number
  supportMode: string
  actionSuggestion: string
  riskLevel: 'low' | 'medium' | 'high'
  followUpNeeded: boolean
}

export interface ChatMessage {
  id: number
  role: 'system' | 'user' | 'assistant' | 'tool'
  content: string
  createdAt: string
}

export interface ConversationSession {
  id: number
  publicId: string
  title: string
  sessionType: 'chat' | 'study' | 'review' | 'emotion'
  status: 'active' | 'archived'
  updatedAt: string
  messages: ChatMessage[]
}

export interface AgentRun {
  id: number
  agentName: string
  intent: string
  status: 'queued' | 'running' | 'succeeded' | 'failed' | 'interrupted'
  interruptReason?: string
}
