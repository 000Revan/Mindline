import type { LearningGoal, LearningGoalStatus } from '@/types/mindline'

export interface ApiResponse<T> {
  code: number
  msg: string
  data?: T
}

interface FastApiValidationIssue {
  loc?: Array<string | number>
  msg?: string
}

interface ApiErrorPayload {
  detail?: string | FastApiValidationIssue[]
}

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

export function isTokenExpiredOrInvalid(token: string | null): boolean {
  if (!token) return true

  try {
    const [, payload] = token.split('.')
    if (!payload) return true

    const normalizedPayload = payload.replace(/-/g, '+').replace(/_/g, '/')
    const decodedPayload = JSON.parse(atob(normalizedPayload)) as { exp?: number }

    if (!decodedPayload.exp) return true
    return decodedPayload.exp * 1000 <= Date.now()
  } catch {
    return true
  }
}

export function clearAuthAndRedirect() {
  localStorage.removeItem('mindline_token')
  localStorage.removeItem('mindline_user')
  localStorage.removeItem('mindline_avatar_data_url')

  if (window.location.pathname !== '/auth') {
    const redirect = `${window.location.pathname}${window.location.search}${window.location.hash}`
    window.location.assign(`/auth?redirect=${encodeURIComponent(redirect)}`)
  }
}

export function resolveApiAssetUrl(url?: string | null): string {
  if (!url) return ''
  if (/^(https?:|data:|blob:)/.test(url)) return url
  if (url.startsWith('/')) return new URL(url, API_BASE_URL).href
  return url
}

async function parseResponse<T>(response: Response): Promise<T> {
  const payload = (await response.json().catch(() => ({}))) as ApiResponse<T> | ApiErrorPayload

  if (!response.ok) {
    if (response.status === 401) {
      clearAuthAndRedirect()
    }

    const detail = 'detail' in payload ? payload.detail : undefined
    const message = Array.isArray(detail)
      ? detail
          .map((issue) => {
            const field = issue.loc?.filter((item) => item !== 'body').join('.')
            return [field, issue.msg].filter(Boolean).join('：')
          })
          .filter(Boolean)
          .join('；')
      : detail || `API request failed: ${response.status}`
    throw new Error(message)
  }

  if (payload && typeof payload === 'object' && 'code' in payload && payload.code !== 200) {
    throw new Error(payload.msg || '请求失败')
  }

  if (payload && typeof payload === 'object' && 'data' in payload) {
    return (payload as ApiResponse<T>).data as T
  }

  return payload as T
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('mindline_token')
  const headers = new Headers(options.headers)
  if (!(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  })

  return parseResponse<T>(response)
}

export interface LoginPayload {
  username: string
  password: string
}

export type RegisterPayload = LoginPayload

export interface AuthUser {
  id: number
  username: string
  nickname?: string | null
  avatar_url?: string | null
  gender?: string
  bio?: string | null
}

export interface AuthResult {
  token: string
  token_type: string
  user: AuthUser
}

export interface UpdateUserPayload {
  nickname?: string
  avatar_url?: string
  gender?: string
  bio?: string
}

export interface ChangePasswordPayload {
  old_password: string
  new_password: string
}

interface LearningGoalWire {
  id: number
  title: string
  description?: string | null
  direction: string
  status: LearningGoalStatus
  priority: number
  start_date?: string | null
  target_date?: string | null
  current_stage?: string | null
  current_principle?: string | null
}

interface LearningGoalsPageWire {
  items: LearningGoalWire[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

interface LearningGoalStatusResultWire {
  goal: LearningGoalWire
  paused_goal_count: number
}

export interface LearningGoalCreatePayload {
  title: string
  description?: string
  direction: string
  priority: number
  start_date?: string
  target_date?: string
  current_stage?: string
  current_principle?: string
}

export interface LearningGoalUpdatePayload {
  priority?: number
  start_date?: string
  target_date?: string
  current_stage?: string
  current_principle?: string
}

export interface LearningGoalsQuery {
  page?: number
  pageSize?: number
  status?: LearningGoalStatus
}

export interface LearningGoalsPage {
  items: LearningGoal[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

export interface LearningGoalStatusResult {
  goal: LearningGoal
  pausedGoalCount: number
}

function mapLearningGoal(goal: LearningGoalWire): LearningGoal {
  return {
    id: goal.id,
    title: goal.title,
    description: goal.description ?? '',
    direction: goal.direction,
    status: goal.status,
    priority: goal.priority,
    startDate: goal.start_date ?? null,
    targetDate: goal.target_date ?? null,
    currentStage: goal.current_stage ?? '',
    currentPrinciple: goal.current_principle ?? '',
  }
}

export const authApi = {
  login(payload: LoginPayload) {
    return request<AuthResult>('/api/user/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  register(payload: RegisterPayload) {
    return request<AuthResult>('/api/user/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  info() {
    return request<AuthUser>('/api/user/info')
  },
  update(payload: UpdateUserPayload) {
    return request<AuthUser>('/api/user/update', {
      method: 'PATCH',
      body: JSON.stringify(payload),
    })
  },
  changePassword(payload: ChangePasswordPayload) {
    return request<null>('/api/user/password', {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  },
  uploadAvatar(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return request<AuthUser>('/api/user/avatar', {
      method: 'PUT',
      body: formData,
    })
  },
}

export const learningApi = {
  async listGoals(query: LearningGoalsQuery = {}): Promise<LearningGoalsPage> {
    const params = new URLSearchParams({
      page: String(query.page ?? 1),
      page_size: String(query.pageSize ?? 10),
    })
    if (query.status) params.set('status', query.status)

    const result = await request<LearningGoalsPageWire>(`/api/learning/goals?${params}`)
    return {
      items: result.items.map(mapLearningGoal),
      total: result.total,
      page: result.page,
      pageSize: result.page_size,
      totalPages: result.total_pages,
    }
  },
  async createGoal(payload: LearningGoalCreatePayload): Promise<LearningGoal> {
    const goal = await request<LearningGoalWire>('/api/learning/goals', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    return mapLearningGoal(goal)
  },
  async updateGoal(goalId: number, payload: LearningGoalUpdatePayload): Promise<LearningGoal> {
    const goal = await request<LearningGoalWire>(`/api/learning/goals/${goalId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    })
    return mapLearningGoal(goal)
  },
  async updateGoalStatus(
    goalId: number,
    status: Exclude<LearningGoalStatus, 'pending'>,
  ): Promise<LearningGoalStatusResult> {
    const result = await request<LearningGoalStatusResultWire>(
      `/api/learning/goals/${goalId}/status`,
      {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      },
    )
    return {
      goal: mapLearningGoal(result.goal),
      pausedGoalCount: result.paused_goal_count,
    }
  },
}

export const plannedApi = {
  dailyTasks: '/daily-tasks',
  learningSessions: '/learning-sessions',
  branchTopics: '/branch-topics',
  notes: '/notes',
  reviews: '/reviews',
  conversations: '/sessions',
  agentRuns: '/agent-runs',
}
