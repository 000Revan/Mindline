<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authApi } from '@/api/client'
import { useMindlineStore } from '@/stores/mindline'

const mode = ref<'login' | 'register'>('login')
const loading = ref(false)
const message = ref('')
const messageType = ref<'success' | 'warning' | 'info' | 'error'>('info')
const route = useRoute()
const router = useRouter()
const store = useMindlineStore()
const form = reactive({
  username: '',
  password: '',
})

if (route.query.reason === 'password_changed') {
  messageType.value = 'success'
  message.value = '密码修改成功，请使用新密码重新登录'
} else if (route.query.reason === 'logout') {
  messageType.value = 'info'
  message.value = '你已安全退出登录'
}

async function submitAuth() {
  message.value = ''
  const username = form.username.trim()
  const password = form.password

  if (!username || !password) {
    messageType.value = 'warning'
    message.value = '请输入用户名和密码'
    return
  }

  if (mode.value === 'register' && username.length < 3) {
    messageType.value = 'warning'
    message.value = '用户名至少需要 3 个字符'
    return
  }

  if (
    mode.value === 'register' &&
    (password.length < 8 || !/[A-Za-z]/.test(password) || !/\d/.test(password))
  ) {
    messageType.value = 'warning'
    message.value = '密码至少 8 位，并同时包含字母和数字'
    return
  }

  loading.value = true
  try {
    const result =
      mode.value === 'login'
        ? await authApi.login({ username, password })
        : await authApi.register({ username, password })

    localStorage.setItem('mindline_token', result.token)
    store.setUser(result.user)
    messageType.value = 'success'
    message.value =
      mode.value === 'login' ? '登录成功，正在载入你的学习主线' : '注册成功，正在创建学习空间'
    await router.push((route.query.redirect as string | undefined) ?? '/dashboard')
  } catch (error) {
    messageType.value = 'error'
    message.value = error instanceof Error ? error.message : '请求失败，请检查后端服务'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-story" aria-labelledby="mindline-title">
      <div class="auth-brand">
        <img class="auth-brand-mark" src="/mindline-logo.png" alt="" aria-hidden="true" />
        <div>
          <strong>Mindline</strong>
          <span>多 Agent 学习陪伴系统</span>
        </div>
      </div>

      <div class="auth-intro">
        <p class="page-kicker">守住主线，持续行动</p>
        <h1 id="mindline-title">让每一次学习，都知道下一步往哪里走。</h1>
        <p>从目标拆解到知识沉淀，从每日推进到周期复盘，Mindline 根据你的学习历史持续调整节奏。</p>
      </div>

      <div class="auth-capabilities" aria-label="Mindline 核心能力">
        <article class="auth-capability">
          <span class="capability-icon primary"
            ><el-icon><Aim /></el-icon
          ></span>
          <div>
            <h2>守住学习主线</h2>
            <p>聚焦一个当前目标，管理任务、阶段与分支问题。</p>
          </div>
        </article>
        <article class="auth-capability">
          <span class="capability-icon success"
            ><el-icon><Notebook /></el-icon
          ></span>
          <div>
            <h2>沉淀个人知识</h2>
            <p>整理笔记与知识点，让学习内容能够再次被检索。</p>
          </div>
        </article>
        <article class="auth-capability">
          <span class="capability-icon warning"
            ><el-icon><DataAnalysis /></el-icon
          ></span>
          <div>
            <h2>复盘并调整计划</h2>
            <p>看见真实进展，再决定明天和下一周如何推进。</p>
          </div>
        </article>
        <article class="auth-capability">
          <span class="capability-icon petal"
            ><el-icon><ChatDotRound /></el-icon
          ></span>
          <div>
            <h2>获得陪伴式支持</h2>
            <p>把焦虑与迷茫拆成一个当下可以完成的小行动。</p>
          </div>
        </article>
      </div>

      <div class="auth-agent-note">
        <el-icon><Connection /></el-icon>
        <span>主控 Agent 统一理解上下文，按任务调度专业子 Agent 协作。</span>
      </div>
    </section>

    <section class="auth-panel" aria-labelledby="auth-panel-title">
      <div class="auth-panel-heading">
        <p class="page-kicker">{{ mode === 'login' ? '继续你的学习' : '建立学习空间' }}</p>
        <h2 id="auth-panel-title">{{ mode === 'login' ? '欢迎回来' : '创建 Mindline 账号' }}</h2>
        <p>
          {{ mode === 'login' ? '登录后继续推进当前学习主线。' : '注册后从第一个学习目标开始。' }}
        </p>
      </div>
      <el-segmented
        v-model="mode"
        class="auth-mode"
        :options="[
          { label: '登录', value: 'login' },
          { label: '注册', value: 'register' },
        ]"
      />
      <el-form class="auth-form" label-position="top" @submit.prevent="submitAuth">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            placeholder="请输入密码"
            :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
          />
        </el-form-item>
        <p v-if="mode === 'register'" class="password-hint">至少 8 位，同时包含字母和数字</p>
        <el-button native-type="submit" type="primary" :loading="loading" class="auth-submit">
          {{ mode === 'login' ? '登录' : '创建账号' }}
        </el-button>
      </el-form>
      <div aria-live="polite">
        <el-alert v-if="message" :title="message" :type="messageType" :closable="false" show-icon />
      </div>
    </section>
  </main>
</template>

<style scoped>
.auth-page {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(360px, 440px);
  gap: 56px;
  width: min(1180px, calc(100% - 48px));
  min-height: 100dvh;
  margin: 0 auto;
  padding: 48px 0;
  align-items: center;
}

.auth-story {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 32px;
}

.auth-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.auth-brand-mark {
  display: block;
  width: 44px;
  height: 44px;
  object-fit: cover;
  border: 1px solid var(--ml-line-strong);
  border-radius: var(--ml-radius);
  background: var(--ml-surface-strong);
}

.auth-brand strong,
.auth-brand span {
  display: block;
}

.auth-brand strong {
  color: var(--ml-primary-dark);
  font-size: 18px;
}

.auth-brand span {
  margin-top: 2px;
  color: var(--ml-muted);
  font-size: 13px;
}

.auth-intro h1 {
  max-width: 680px;
  margin: 0;
  color: var(--ml-primary-dark);
  font-size: 48px;
  line-height: 1.16;
  letter-spacing: 0;
}

.auth-intro > p:last-child {
  max-width: 660px;
  margin: 18px 0 0;
  color: var(--ml-muted);
  font-size: 17px;
  line-height: 1.8;
}

.auth-capabilities {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0 28px;
  border-top: 1px solid var(--ml-line);
}

.auth-capability {
  display: grid;
  grid-template-columns: 40px minmax(0, 1fr);
  gap: 12px;
  padding: 20px 0;
  border-bottom: 1px solid var(--ml-line);
}

.capability-icon {
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: var(--ml-radius);
}

.capability-icon.primary {
  color: var(--ml-primary);
  background: var(--ml-primary-soft);
}

.capability-icon.success {
  color: var(--ml-success);
  background: #e4f3ef;
}

.capability-icon.warning {
  color: var(--ml-warning);
  background: #f8efdf;
}

.capability-icon.petal {
  color: var(--ml-danger);
  background: var(--ml-petal);
}

.auth-capability h2 {
  margin: 0 0 6px;
  color: var(--ml-ink);
  font-size: 16px;
}

.auth-capability p {
  margin: 0;
  color: var(--ml-muted);
  font-size: 13px;
  line-height: 1.65;
}

.auth-agent-note {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #40517e;
  font-size: 13px;
  line-height: 1.6;
}

.auth-agent-note .el-icon {
  flex: 0 0 auto;
  color: var(--ml-primary);
  font-size: 20px;
}

.auth-panel {
  display: flex;
  flex-direction: column;
  gap: 22px;
  padding: 32px;
  border: 1px solid var(--ml-line);
  border-radius: var(--ml-radius);
  background: var(--ml-surface);
  box-shadow: var(--ml-shadow);
}

.auth-panel-heading h2 {
  margin: 0;
  color: var(--ml-primary-dark);
  font-size: 26px;
}

.auth-panel-heading > p:last-child {
  margin: 8px 0 0;
  color: var(--ml-muted);
  line-height: 1.6;
}

.auth-mode {
  width: 100%;
}

.auth-form {
  display: flex;
  flex-direction: column;
}

.auth-form :deep(.el-input__wrapper) {
  min-height: 44px;
}

.password-hint {
  margin: -8px 0 16px;
  color: var(--ml-muted);
  font-size: 12px;
}

.auth-submit {
  width: 100%;
  min-height: 44px;
}

@media (max-width: 960px) {
  .auth-page {
    grid-template-columns: 1fr;
    gap: 32px;
    width: min(720px, calc(100% - 40px));
    padding: 32px 0;
  }

  .auth-panel {
    grid-row: 2;
  }

  .auth-intro h1 {
    font-size: 40px;
  }
}

@media (max-width: 600px) {
  .auth-page {
    width: min(100% - 32px, 520px);
    padding: 24px 0;
  }

  .auth-story {
    gap: 24px;
  }

  .auth-intro h1 {
    font-size: 32px;
  }

  .auth-intro > p:last-child {
    font-size: 16px;
  }

  .auth-capabilities {
    grid-template-columns: 1fr;
  }

  .auth-panel {
    padding: 24px;
  }
}
</style>
