export interface ApiResponse<T> {
  code: number
  msg: string
  data?: T
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
  const payload = (await response.json().catch(() => ({}))) as ApiResponse<T> | { detail?: string }

  if (!response.ok) {
    if (response.status === 401) {
      clearAuthAndRedirect()
    }

    const message =
      'detail' in payload && payload.detail
        ? payload.detail
        : `API request failed: ${response.status}`
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
      method: 'PUT',
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
      method: 'POST',
      body: formData,
    })
  },
}

export const plannedApi = {
  learningGoals: '/learning-goals',
  dailyTasks: '/daily-tasks',
  learningSessions: '/learning-sessions',
  branchTopics: '/branch-topics',
  notes: '/notes',
  reviews: '/reviews',
  conversations: '/sessions',
  agentRuns: '/agent-runs',
}
