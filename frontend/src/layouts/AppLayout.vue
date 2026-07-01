<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { authApi, resolveApiAssetUrl } from '@/api/client'
import { useMindlineStore } from '@/stores/mindline'

const route = useRoute()
const router = useRouter()
const store = useMindlineStore()

const navItems = [
  { path: '/dashboard', label: '学习工作台', icon: 'DataBoard' },
  { path: '/chat', label: '智能体对话', icon: 'ChatLineRound' },
  { path: '/goals', label: '学习主线', icon: 'Aim' },
  { path: '/tasks', label: '每日任务', icon: 'List' },
  { path: '/sessions', label: '学习记录', icon: 'Clock' },
  { path: '/branches', label: '分支停车场', icon: 'Connection' },
  { path: '/notes', label: '笔记库', icon: 'Notebook' },
  { path: '/reviews', label: '复盘', icon: 'DocumentChecked' },
  { path: '/emotion', label: '情绪陪伴', icon: 'MoonNight' },
]

const activePath = computed(() => route.path)
const userDisplayName = computed(
  () => store.user.nickname || store.user.username || 'Mindline 用户',
)
const userAvatarUrl = computed(() => resolveApiAssetUrl(store.user.avatar_url))
const userAvatarInitial = computed(() => userDisplayName.value.slice(0, 1).toUpperCase())
const genderLabel = computed(() => getGenderLabel(store.user.gender))

const userDialogVisible = ref(false)
const editProfileVisible = ref(false)
const changePasswordVisible = ref(false)
const activeUserPanel = ref<'account' | 'portrait'>('account')
const avatarInputRef = ref<HTMLInputElement | null>(null)
const profileSaving = ref(false)
const passwordSaving = ref(false)
const avatarUploading = ref(false)
const loggingOut = ref(false)

const profileForm = reactive({
  nickname: '',
  gender: 'unknown',
  bio: '',
})
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})
const portraitDraft = ref(
  localStorage.getItem('mindline_user_portrait') ||
    '这里记录用户的学习偏好、目标方向、情绪支持方式和长期成长画像。后端接口完成后可替换为真实个人画像数据。',
)

const allowedAvatarTypes = new Set(['image/jpeg', 'image/png', 'image/webp', 'image/gif'])
const maxAvatarSize = 2 * 1024 * 1024

onMounted(() => {
  void Promise.allSettled([store.refreshCurrentUser(), store.fetchActiveGoal()])
})

function getGenderLabel(gender?: string | null) {
  if (gender === 'male') return '男'
  if (gender === 'female') return '女'
  return '未设置'
}

function openUserDialog() {
  activeUserPanel.value = 'account'
  userDialogVisible.value = true
}

function openEditProfileDialog() {
  profileForm.nickname = store.user.nickname || ''
  profileForm.gender = store.user.gender || 'unknown'
  profileForm.bio = store.user.bio || ''
  editProfileVisible.value = true
}

function openChangePasswordDialog() {
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
  changePasswordVisible.value = true
}

function triggerAvatarUpload() {
  if (avatarUploading.value) return
  avatarInputRef.value?.click()
}

async function handleAvatarUpload(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  if (!allowedAvatarTypes.has(file.type)) {
    ElMessage.warning('头像仅支持 jpg、png、webp、gif 格式')
    input.value = ''
    return
  }

  if (file.size > maxAvatarSize) {
    ElMessage.warning('头像文件不能超过 2MB')
    input.value = ''
    return
  }

  avatarUploading.value = true
  try {
    const updatedUser = await authApi.uploadAvatar(file)
    store.setUser(updatedUser)
    localStorage.removeItem('mindline_avatar_data_url')
    ElMessage.success('头像已更新')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '头像更新失败')
  } finally {
    avatarUploading.value = false
    input.value = ''
  }
}

async function saveProfile() {
  profileSaving.value = true
  try {
    const updatedUser = await authApi.update({
      nickname: profileForm.nickname,
      gender: profileForm.gender,
      bio: profileForm.bio,
    })
    store.setUser(updatedUser)
    editProfileVisible.value = false
    ElMessage.success('个人信息已更新')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '个人信息更新失败')
  } finally {
    profileSaving.value = false
  }
}

async function savePassword() {
  if (!passwordForm.old_password || !passwordForm.new_password || !passwordForm.confirm_password) {
    ElMessage.warning('请完整填写密码信息')
    return
  }

  if (passwordForm.new_password !== passwordForm.confirm_password) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }

  passwordSaving.value = true
  try {
    await authApi.changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password,
    })
    changePasswordVisible.value = false
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
    store.clearAuthSession()
    await router.replace({ name: 'auth', query: { reason: 'password_changed' } })
    ElMessage.success('密码已修改，请使用新密码重新登录')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '密码修改失败')
  } finally {
    passwordSaving.value = false
  }
}

function savePortrait() {
  localStorage.setItem('mindline_user_portrait', portraitDraft.value)
  ElMessage.success('个人画像模板已保存到本地')
}

async function logout() {
  try {
    await ElMessageBox.confirm('退出后需要重新登录才能继续使用 Mindline。', '确认退出登录', {
      confirmButtonText: '退出登录',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }

  loggingOut.value = true
  try {
    userDialogVisible.value = false
    editProfileVisible.value = false
    changePasswordVisible.value = false
    store.clearAuthSession()
    await router.replace({ name: 'auth', query: { reason: 'logout' } })
    ElMessage.success('已退出登录')
  } finally {
    loggingOut.value = false
  }
}
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <RouterLink class="brand" to="/dashboard" aria-label="Mindline 学习工作台">
        <span class="brand-mark">M</span>
        <span>
          <strong>Mindline</strong>
          <small>学习陪伴工作台</small>
        </span>
      </RouterLink>

      <el-menu class="nav-menu" :default-active="activePath" router>
        <el-menu-item v-for="item in navItems" :key="item.path" :index="item.path">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>

      <div class="user-footer">
        <section
          class="user-profile"
          aria-label="查看个人信息"
          role="button"
          tabindex="0"
          @click="openUserDialog"
          @keydown.enter="openUserDialog"
          @keydown.space.prevent="openUserDialog"
        >
          <el-avatar :size="42" :src="userAvatarUrl" class="user-avatar">
            {{ userAvatarInitial }}
          </el-avatar>
          <div class="user-meta">
            <p>当前用户</p>
            <strong>{{ userDisplayName }}</strong>
          </div>
        </section>
        <el-tooltip content="退出登录" placement="top">
          <el-button
            class="logout-button"
            circle
            aria-label="退出登录"
            :loading="loggingOut"
            @click="logout"
          >
            <el-icon><SwitchButton /></el-icon>
          </el-button>
        </el-tooltip>
      </div>
    </aside>

    <main class="main-area">
      <header class="topbar">
        <div>
          <p class="topbar-label">当前主线</p>
          <h1>{{ store.activeGoal?.title || '暂未设置当前主线' }}</h1>
        </div>
        <div class="toolbar-row">
          <el-tag type="primary" effect="light">Agent 在线</el-tag>
          <el-tag type="warning" effect="light">
            {{ store.pendingBranches.length }} 个分支待回收
          </el-tag>
        </div>
      </header>

      <RouterView />
    </main>

    <aside class="context-panel">
      <section class="context-card highlight">
        <div class="context-title-row">
          <div>
            <p class="context-kicker">主线状态</p>
            <h2>{{ store.activeGoal?.currentStage }}</h2>
          </div>
          <el-progress
            type="circle"
            :percentage="68"
            :width="64"
            color="#4268d6"
            :stroke-width="8"
          />
        </div>
        <p>{{ store.activeGoal?.description }}</p>
      </section>

      <section class="context-card">
        <div class="context-title-row">
          <h2>今日任务</h2>
          <el-tag type="success"
            >{{ store.completedTaskCount }}/{{ store.todayTasks.length }}</el-tag
          >
        </div>
        <div class="mini-list">
          <div v-for="task in store.todayTasks.slice(0, 3)" :key="task.id" class="mini-item">
            <span class="mini-dot" :class="task.status" />
            <span>{{ task.title }}</span>
          </div>
        </div>
      </section>

      <section class="context-card">
        <div class="context-title-row">
          <h2>分支停车场</h2>
          <RouterLink to="/branches">
            <el-button text>查看</el-button>
          </RouterLink>
        </div>
        <div v-if="store.pendingBranches.length" class="mini-list">
          <div v-for="branch in store.pendingBranches" :key="branch.id" class="mini-item branch">
            <span>{{ branch.timeboxMinutes }} 分钟</span>
            <strong>{{ branch.title }}</strong>
          </div>
        </div>
        <div v-else class="empty-mini">暂无待回收分支</div>
      </section>
    </aside>

    <el-dialog v-model="userDialogVisible" title="个人信息" width="760px" class="user-dialog">
      <div class="user-dialog-body">
        <aside class="user-dialog-nav">
          <button
            class="user-dialog-nav-item"
            :class="{ active: activeUserPanel === 'account' }"
            type="button"
            @click="activeUserPanel = 'account'"
          >
            账户
          </button>
          <button
            class="user-dialog-nav-item"
            :class="{ active: activeUserPanel === 'portrait' }"
            type="button"
            @click="activeUserPanel = 'portrait'"
          >
            个人画像
          </button>
        </aside>

        <section v-if="activeUserPanel === 'account'" class="user-dialog-panel">
          <div class="account-summary">
            <div class="avatar-edit-wrap">
              <el-avatar :size="72" :src="userAvatarUrl" class="account-avatar">
                {{ userAvatarInitial }}
              </el-avatar>
              <button
                class="avatar-edit-button"
                type="button"
                aria-label="修改头像"
                :disabled="avatarUploading"
                @click="triggerAvatarUpload"
              >
                <el-icon><EditPen /></el-icon>
              </button>
              <input
                ref="avatarInputRef"
                class="avatar-input"
                type="file"
                accept="image/jpeg,image/png,image/webp,image/gif"
                @change="handleAvatarUpload"
              />
            </div>
            <h2>{{ userDisplayName }}</h2>
            <p>@{{ store.user.username }}</p>
          </div>

          <dl class="account-details">
            <div>
              <dt>账号名</dt>
              <dd>{{ store.user.username }}</dd>
            </div>
            <div>
              <dt>昵称</dt>
              <dd>{{ store.user.nickname || '未设置' }}</dd>
            </div>
            <div>
              <dt>性别</dt>
              <dd>{{ genderLabel }}</dd>
            </div>
            <div>
              <dt>个人简介</dt>
              <dd>{{ store.user.bio || '未设置' }}</dd>
            </div>
          </dl>

          <div class="account-action-buttons">
            <el-button plain @click="openEditProfileDialog">编辑个人信息</el-button>
            <el-button plain @click="openChangePasswordDialog">修改密码</el-button>
          </div>
        </section>

        <section v-else class="user-dialog-panel">
          <div class="portrait-header">
            <h2>个人画像</h2>
            <p>后端接口暂未实现，当前先提供可编辑模板并保存在本地。</p>
          </div>
          <el-input v-model="portraitDraft" type="textarea" :rows="13" resize="none" />
          <div class="portrait-actions">
            <el-button type="primary" @click="savePortrait">保存画像模板</el-button>
          </div>
        </section>
      </div>
    </el-dialog>

    <el-dialog v-model="editProfileVisible" title="编辑个人信息" width="460px">
      <el-form label-position="top">
        <el-form-item label="昵称">
          <el-input v-model="profileForm.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="profileForm.gender">
            <el-radio-button value="male">男</el-radio-button>
            <el-radio-button value="female">女</el-radio-button>
            <el-radio-button value="unknown">未设置</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="个人简介">
          <el-input
            v-model="profileForm.bio"
            type="textarea"
            :rows="4"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editProfileVisible = false">取消</el-button>
        <el-button type="primary" :loading="profileSaving" @click="saveProfile">
          保存个人信息
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="changePasswordVisible" title="修改密码" width="460px">
      <el-form label-position="top">
        <el-form-item label="旧密码">
          <el-input v-model="passwordForm.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="再次输入新密码">
          <el-input v-model="passwordForm.confirm_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="changePasswordVisible = false">取消</el-button>
        <el-button type="primary" :loading="passwordSaving" @click="savePassword">
          确认修改密码
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.app-shell {
  display: grid;
  grid-template-columns: 252px minmax(0, 1fr) 340px;
  min-height: 100vh;
  border: 1px solid var(--ml-line);
  background: rgba(255, 255, 255, 0.5);
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 24px 18px;
  border-right: 1px solid var(--ml-line);
  background: rgba(252, 252, 255, 0.74);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 52px;
}

.brand-mark {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border: 1px solid #abc0ef;
  border-radius: 14px;
  color: var(--ml-primary);
  font-weight: 900;
  background: linear-gradient(145deg, #ffffff, #eaf0ff);
}

.brand strong,
.brand small {
  display: block;
}

.brand strong {
  color: var(--ml-primary-dark);
  font-size: 17px;
}

.brand small {
  margin-top: 3px;
  color: var(--ml-muted);
}

.nav-menu {
  border-right: 0;
  background: transparent;
}

.nav-menu :deep(.el-menu-item) {
  height: 46px;
  margin-bottom: 6px;
  border-radius: 999px;
  color: #40517e;
}

.nav-menu :deep(.el-menu-item.is-active) {
  color: var(--ml-primary-dark);
  background: var(--ml-primary-soft);
}

.user-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid var(--ml-line);
}

.user-profile {
  display: flex;
  min-width: 0;
  flex: 1;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-radius: var(--ml-radius);
  cursor: pointer;
}

.user-profile:hover,
.user-profile:focus-visible {
  outline: none;
  background: rgba(240, 245, 255, 0.72);
}

.logout-button {
  width: 44px;
  height: 44px;
  flex: 0 0 44px;
  color: var(--ml-danger);
}

.user-avatar,
.account-avatar {
  flex: 0 0 auto;
  color: var(--ml-primary-dark);
  font-weight: 800;
  background: var(--ml-primary-soft);
}

.user-meta {
  min-width: 0;
}

.user-meta p {
  margin: 0 0 4px;
  color: var(--ml-primary);
  font-size: 12px;
  font-weight: 700;
}

.user-meta strong {
  display: block;
  overflow: hidden;
  color: var(--ml-primary-dark);
  font-size: 15px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-dialog-body {
  display: grid;
  grid-template-columns: 148px minmax(0, 1fr);
  min-height: 520px;
  border: 1px solid var(--ml-line);
  border-radius: 8px;
  overflow: hidden;
}

.user-dialog-nav {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 14px;
  border-right: 1px solid var(--ml-line);
  background: rgba(248, 250, 255, 0.86);
}

.user-dialog-nav-item {
  width: 100%;
  min-height: 40px;
  padding: 0 12px;
  border: 0;
  border-radius: 8px;
  color: #40517e;
  font: inherit;
  text-align: left;
  background: transparent;
  cursor: pointer;
}

.user-dialog-nav-item.active,
.user-dialog-nav-item:hover {
  color: var(--ml-primary-dark);
  background: var(--ml-primary-soft);
}

.user-dialog-panel {
  min-width: 0;
  padding: 24px;
}

.account-summary {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--ml-line);
}

.avatar-edit-wrap {
  position: relative;
  width: 72px;
  height: 72px;
}

.avatar-edit-button {
  position: absolute;
  right: -4px;
  bottom: -4px;
  display: grid;
  width: 28px;
  height: 28px;
  place-items: center;
  border: 1px solid var(--ml-line);
  border-radius: 999px;
  color: var(--ml-primary-dark);
  background: #ffffff;
  box-shadow: 0 6px 16px rgba(66, 104, 214, 0.18);
  cursor: pointer;
}

.avatar-edit-button:disabled {
  cursor: wait;
  opacity: 0.58;
}

.avatar-input {
  display: none;
}

.account-avatar {
  font-size: 24px;
  font-weight: 900;
}

.account-summary h2,
.portrait-header h2 {
  margin: 0;
  color: var(--ml-primary-dark);
  font-size: 20px;
}

.account-summary p,
.portrait-header p {
  margin: 0;
  color: var(--ml-muted);
}

.account-details {
  display: flex;
  flex-direction: column;
  gap: 0;
  margin: 18px 0 0;
  padding: 4px 0;
  border-bottom: 1px solid var(--ml-line);
}

.account-details div {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  min-height: 44px;
  padding: 12px 0;
  border-top: 1px solid var(--ml-line);
}

.account-details dt {
  color: var(--ml-muted);
  font-size: 13px;
}

.account-details dd {
  max-width: 68%;
  margin: 0;
  color: var(--ml-primary-dark);
  font-weight: 700;
  text-align: right;
  overflow-wrap: anywhere;
}

.account-action-buttons {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 18px;
}

.account-action-buttons :deep(.el-button) {
  width: 100%;
  min-height: 42px;
  margin-left: 0;
}

.portrait-header {
  margin-bottom: 16px;
}

.portrait-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
}

.topbar-label,
.context-kicker {
  margin: 0 0 6px;
  color: var(--ml-primary);
  font-size: 12px;
  font-weight: 700;
}

.main-area {
  min-width: 0;
  padding: 22px;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin: -22px -22px 18px;
  padding: 22px;
  border-bottom: 1px solid var(--ml-line);
  background: rgba(255, 255, 255, 0.58);
}

.topbar h1 {
  margin: 0;
  color: var(--ml-primary-dark);
  font-size: 22px;
}

.context-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 22px 20px;
  border-left: 1px solid var(--ml-line);
  background: rgba(248, 250, 255, 0.7);
}

.context-card {
  padding: 18px;
  border: 1px solid var(--ml-line);
  border-radius: var(--ml-radius);
  background: var(--ml-surface);
}

.context-card.highlight {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.94), rgba(235, 241, 255, 0.9));
}

.context-card h2 {
  margin: 0;
  color: var(--ml-primary-dark);
  font-size: 16px;
}

.context-card p {
  margin: 12px 0 0;
  color: var(--ml-muted);
  line-height: 1.65;
}

.context-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.mini-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 14px;
}

.mini-item {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 40px;
  padding: 10px 12px;
  border-radius: var(--ml-radius);
  background: rgba(240, 245, 255, 0.72);
  color: #33446f;
  font-size: 13px;
}

.mini-item.branch {
  align-items: flex-start;
  flex-direction: column;
}

.mini-item.branch span {
  color: var(--ml-warning);
  font-size: 12px;
}

.mini-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: var(--ml-muted);
}

.mini-dot.in_progress {
  background: var(--ml-primary);
}

.mini-dot.completed {
  background: var(--ml-success);
}

.mini-dot.pending {
  background: var(--ml-warning);
}

.empty-mini {
  margin-top: 12px;
  color: var(--ml-muted);
  font-size: 13px;
}

@media (max-width: 1180px) {
  .app-shell {
    grid-template-columns: 220px minmax(0, 1fr);
  }

  .context-panel {
    display: none;
  }
}

@media (max-width: 760px) {
  .app-shell {
    display: block;
  }

  .sidebar {
    position: static;
  }

  .topbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .user-dialog-body {
    grid-template-columns: 1fr;
  }

  .user-dialog-nav {
    flex-direction: row;
    border-right: 0;
    border-bottom: 1px solid var(--ml-line);
  }
}
</style>
