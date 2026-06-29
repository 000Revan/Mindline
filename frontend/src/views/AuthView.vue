<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authApi } from '@/api/client'

const mode = ref<'login' | 'register'>('login')
const loading = ref(false)
const message = ref('')
const messageType = ref<'success' | 'warning' | 'info' | 'error'>('info')
const route = useRoute()
const router = useRouter()
const form = reactive({
  username: '',
  password: '',
})

async function submitAuth() {
  message.value = ''
  const username = form.username.trim()
  const password = form.password

  if (!username || !password) {
    messageType.value = 'warning'
    message.value = '请输入用户名和密码'
    return
  }

  loading.value = true
  try {
    const result =
      mode.value === 'login'
        ? await authApi.login({ username, password })
        : await authApi.register({ username, password })

    localStorage.setItem('mindline_token', result.token)
    localStorage.setItem('mindline_user', JSON.stringify(result.user))
    messageType.value = 'success'
    message.value = mode.value === 'login' ? '登录成功，正在进入工作台' : '注册成功，正在进入工作台'
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
    <section class="auth-copy">
      <p class="page-kicker">Mindline</p>
      <h1>允许好奇，但不让好奇接管主线。</h1>
      <p>登录后进入学习工作台，继续推进目标、任务、笔记和复盘闭环。</p>
      <RouterLink to="/dashboard">
        <el-button type="primary">
          进入工作台
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </RouterLink>
    </section>

    <section class="auth-card">
      <el-segmented
        v-model="mode"
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
            autocomplete="current-password"
          />
        </el-form-item>
        <el-button native-type="submit" type="primary" :loading="loading" class="auth-submit">
          {{ mode === 'login' ? '登录' : '创建账号' }}
        </el-button>
      </el-form>
      <el-alert v-if="message" :title="message" :type="messageType" :closable="false" show-icon />
    </section>
  </main>
</template>

<style scoped>
.auth-page {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 420px;
  gap: 28px;
  min-height: 100vh;
  padding: 48px;
  align-items: center;
}

.auth-copy {
  max-width: 680px;
}

.auth-copy h1 {
  margin: 0;
  max-width: 620px;
  color: var(--ml-primary-dark);
  font-size: clamp(36px, 7vw, 72px);
  line-height: 1.06;
}

.auth-copy p:not(.page-kicker) {
  max-width: 560px;
  color: var(--ml-muted);
  font-size: 17px;
  line-height: 1.8;
}

.auth-card {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 28px;
  border: 1px solid var(--ml-line);
  border-radius: 8px;
  background: var(--ml-surface);
  box-shadow: var(--ml-shadow);
}

.auth-form {
  display: flex;
  flex-direction: column;
}

.auth-submit {
  width: 100%;
  min-height: 44px;
}

@media (max-width: 860px) {
  .auth-page {
    grid-template-columns: 1fr;
    padding: 24px;
  }
}
</style>
