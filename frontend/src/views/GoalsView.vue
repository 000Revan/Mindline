<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import type { LearningGoalCreatePayload, LearningGoalUpdatePayload } from '@/api/client'
import { useMindlineStore } from '@/stores/mindline'
import type { LearningGoal, LearningGoalStatus } from '@/types/mindline'

const store = useMindlineStore()
const statusOptions: Array<{ label: string; value: LearningGoalStatus | '' }> = [
  { label: '全部状态', value: '' },
  { label: '待开始', value: 'pending' },
  { label: '进行中', value: 'active' },
  { label: '已暂停', value: 'paused' },
  { label: '已完成', value: 'completed' },
  { label: '已归档', value: 'archived' },
]
const statusLabels: Record<LearningGoalStatus, string> = {
  pending: '待开始',
  active: '进行中',
  paused: '已暂停',
  completed: '已完成',
  archived: '已归档',
}
const statusTagTypes: Record<LearningGoalStatus, 'primary' | 'success' | 'warning' | 'info'> = {
  pending: 'info',
  active: 'success',
  paused: 'warning',
  completed: 'primary',
  archived: 'info',
}

const createDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const createFormRef = ref<FormInstance>()
const creating = ref(false)
const detailSaving = ref(false)
const statusChanging = ref<Exclude<LearningGoalStatus, 'pending'> | ''>('')
const selectedGoal = ref<LearningGoal>()
const createForm = reactive({
  title: '',
  description: '',
  direction: '',
  priority: 3,
  startDate: '',
  targetDate: '',
  currentStage: '',
  currentPrinciple: '',
})
const detailForm = reactive({
  priority: 3,
  startDate: '',
  targetDate: '',
  currentStage: '',
  currentPrinciple: '',
})
const createRules: FormRules = {
  title: [{ required: true, message: '请输入学习目标标题', trigger: 'blur' }],
  direction: [{ required: true, message: '请输入学习方向', trigger: 'blur' }],
}
const isTerminalGoal = computed(
  () => selectedGoal.value?.status === 'completed' || selectedGoal.value?.status === 'archived',
)

function optionalText(value: string) {
  return value.trim() || undefined
}

function formatDate(value: string | null) {
  return value ? value.replace('T', ' ').slice(0, 16) : '未设置'
}

function validateDateRange(startDate: string, targetDate: string) {
  if (startDate && targetDate && new Date(startDate).getTime() >= new Date(targetDate).getTime()) {
    ElMessage.warning('目标完成时间必须晚于开始时间')
    return false
  }
  return true
}

function resetCreateForm() {
  Object.assign(createForm, {
    title: '',
    description: '',
    direction: '',
    priority: 3,
    startDate: '',
    targetDate: '',
    currentStage: '',
    currentPrinciple: '',
  })
  createFormRef.value?.clearValidate()
}

function openCreateDialog() {
  resetCreateForm()
  createDialogVisible.value = true
}

function openGoalDetail(goal: LearningGoal) {
  selectedGoal.value = goal
  Object.assign(detailForm, {
    priority: goal.priority,
    startDate: goal.startDate || '',
    targetDate: goal.targetDate || '',
    currentStage: goal.currentStage,
    currentPrinciple: goal.currentPrinciple,
  })
  detailDialogVisible.value = true
}

async function loadGoals(page = store.goalPage) {
  try {
    await store.fetchGoals(page, store.goalStatusFilter)
  } catch {
    // 页面错误区已经提供重试入口。
  }
}

async function handleStatusFilterChange(value: LearningGoalStatus | '') {
  try {
    await store.fetchGoals(1, value)
  } catch {
    // 页面错误区已经提供重试入口。
  }
}

async function submitCreate() {
  const valid = await createFormRef.value?.validate().catch(() => false)
  if (!valid || !validateDateRange(createForm.startDate, createForm.targetDate)) return

  const payload: LearningGoalCreatePayload = {
    title: createForm.title.trim(),
    direction: createForm.direction.trim(),
    priority: createForm.priority,
  }
  const optionalFields = {
    description: optionalText(createForm.description),
    start_date: createForm.startDate || undefined,
    target_date: createForm.targetDate || undefined,
    current_stage: optionalText(createForm.currentStage),
    current_principle: optionalText(createForm.currentPrinciple),
  }
  Object.assign(
    payload,
    Object.fromEntries(Object.entries(optionalFields).filter(([, value]) => value)),
  )

  creating.value = true
  try {
    await store.createGoal(payload)
    createDialogVisible.value = false
    ElMessage.success('学习主线已创建，当前状态为待开始')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '学习主线创建失败')
  } finally {
    creating.value = false
  }
}

async function saveGoalDetail() {
  const goal = selectedGoal.value
  if (!goal || isTerminalGoal.value) return
  if (!validateDateRange(detailForm.startDate, detailForm.targetDate)) return

  const payload: LearningGoalUpdatePayload = { priority: detailForm.priority }
  const optionalFields = {
    start_date: detailForm.startDate || undefined,
    target_date: detailForm.targetDate || undefined,
    current_stage: optionalText(detailForm.currentStage),
    current_principle: optionalText(detailForm.currentPrinciple),
  }
  Object.assign(
    payload,
    Object.fromEntries(Object.entries(optionalFields).filter(([, value]) => value)),
  )

  detailSaving.value = true
  try {
    const updatedGoal = await store.updateGoal(goal.id, payload)
    openGoalDetail(updatedGoal)
    ElMessage.success('学习目标信息已更新')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '学习目标更新失败')
  } finally {
    detailSaving.value = false
  }
}

async function confirmStatusChange(status: Exclude<LearningGoalStatus, 'pending'>) {
  const goal = selectedGoal.value
  if (!goal || isTerminalGoal.value) return

  let confirmation = ''
  if (status === 'active' && store.activeGoal && store.activeGoal.id !== goal.id) {
    confirmation = `设为当前主线后，“${store.activeGoal.title}”将自动暂停。`
  } else if (status === 'completed') {
    confirmation = '标记完成后将无法继续编辑或恢复该学习目标。'
  } else if (status === 'archived') {
    confirmation = '归档后将无法继续编辑或恢复该学习目标。'
  }
  if (confirmation) {
    try {
      await ElMessageBox.confirm(confirmation, '确认状态修改', {
        confirmButtonText: '确认修改',
        cancelButtonText: '取消',
        type: status === 'active' ? 'warning' : 'info',
      })
    } catch {
      return
    }
  }

  statusChanging.value = status
  try {
    const result = await store.changeGoalStatus(goal.id, status)
    openGoalDetail(result.goal)
    const pausedMessage = result.pausedGoalCount
      ? `，并自动暂停 ${result.pausedGoalCount} 条原主线`
      : ''
    ElMessage.success(`目标状态已更新为${statusLabels[status]}${pausedMessage}`)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '目标状态修改失败')
  } finally {
    statusChanging.value = ''
  }
}

onMounted(() => void loadGoals(1))
</script>

<template>
  <section class="page-shell">
    <div class="page-title-row">
      <div>
        <p class="page-kicker">Learning Goals</p>
        <h2 class="page-title">学习主线</h2>
        <p class="page-subtitle">集中管理学习方向、当前阶段和推进原则。</p>
      </div>
      <el-button type="primary" @click="openCreateDialog"
        ><el-icon><Plus /></el-icon>新建主线</el-button
      >
    </div>

    <div class="goal-filter-row">
      <el-select
        v-model="store.goalStatusFilter"
        aria-label="筛选学习目标状态"
        class="status-filter"
        @change="handleStatusFilterChange"
      >
        <el-option
          v-for="option in statusOptions"
          :key="option.value || 'all'"
          :label="option.label"
          :value="option.value"
        />
      </el-select>
      <span>共 {{ store.goalTotal }} 条学习目标</span>
    </div>

    <div v-if="store.goalsLoading" class="goal-loading" aria-label="学习目标加载中">
      <el-skeleton v-for="index in 3" :key="index" :rows="3" animated />
    </div>
    <el-result
      v-else-if="store.goalsError"
      icon="error"
      title="学习目标加载失败"
      :sub-title="store.goalsError"
    >
      <template #extra
        ><el-button type="primary" @click="loadGoals(store.goalPage)">重新加载</el-button></template
      >
    </el-result>
    <el-empty v-else-if="!store.goals.length" description="当前筛选条件下暂无学习目标">
      <el-button type="primary" @click="openCreateDialog">新建主线</el-button>
    </el-empty>
    <div v-else class="soft-list">
      <article
        v-for="goal in store.goals"
        :key="goal.id"
        class="soft-item goal-card"
        role="button"
        tabindex="0"
        @click="openGoalDetail(goal)"
        @keydown.enter="openGoalDetail(goal)"
        @keydown.space.prevent="openGoalDetail(goal)"
      >
        <div>
          <p class="soft-item-title">{{ goal.title }}</p>
          <p class="soft-item-desc">{{ goal.description || '暂无目标描述' }}</p>
          <div class="toolbar-row">
            <el-tag type="primary">{{ goal.direction }}</el-tag>
            <el-tag :type="statusTagTypes[goal.status]">{{ statusLabels[goal.status] }}</el-tag>
            <el-tag type="warning">P{{ goal.priority }}</el-tag>
          </div>
        </div>
        <div class="goal-side">
          <strong>{{ goal.currentStage || '当前阶段未设置' }}</strong>
          <span>{{ goal.currentPrinciple || '当前原则未设置' }}</span>
          <small>目标时间：{{ formatDate(goal.targetDate) }}</small>
        </div>
      </article>
    </div>

    <div v-if="store.goalTotalPages > 1" class="goal-pagination">
      <el-pagination
        background
        layout="prev, pager, next"
        :current-page="store.goalPage"
        :page-size="store.goalPageSize"
        :total="store.goalTotal"
        @current-change="loadGoals"
      />
    </div>

    <el-dialog
      v-model="createDialogVisible"
      title="新建学习主线"
      width="min(720px, calc(100vw - 32px))"
    >
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-position="top">
        <div class="goal-form-grid">
          <el-form-item label="目标标题" prop="title" class="span-all"
            ><el-input v-model="createForm.title" maxlength="255" show-word-limit
          /></el-form-item>
          <el-form-item label="学习方向" prop="direction"
            ><el-input v-model="createForm.direction" maxlength="255"
          /></el-form-item>
          <el-form-item label="优先级"
            ><el-input-number v-model="createForm.priority" :min="1" :max="5"
          /></el-form-item>
          <el-form-item label="目标描述" class="span-all"
            ><el-input
              v-model="createForm.description"
              type="textarea"
              :rows="3"
              maxlength="255"
              show-word-limit
          /></el-form-item>
          <el-form-item label="开始时间"
            ><el-date-picker
              v-model="createForm.startDate"
              type="datetime"
              value-format="YYYY-MM-DDTHH:mm:ss"
              placeholder="选择开始时间"
          /></el-form-item>
          <el-form-item label="目标完成时间"
            ><el-date-picker
              v-model="createForm.targetDate"
              type="datetime"
              value-format="YYYY-MM-DDTHH:mm:ss"
              placeholder="选择目标时间"
          /></el-form-item>
          <el-form-item label="当前阶段"
            ><el-input v-model="createForm.currentStage" maxlength="255"
          /></el-form-item>
          <el-form-item label="当前原则"
            ><el-input v-model="createForm.currentPrinciple" maxlength="255"
          /></el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="submitCreate">确认创建</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="detailDialogVisible"
      title="学习目标详情"
      width="min(720px, calc(100vw - 32px))"
    >
      <template v-if="selectedGoal">
        <dl class="goal-readonly-details">
          <div>
            <dt>目标标题</dt>
            <dd>{{ selectedGoal.title }}</dd>
          </div>
          <div>
            <dt>学习方向</dt>
            <dd>{{ selectedGoal.direction }}</dd>
          </div>
          <div>
            <dt>当前状态</dt>
            <dd>{{ statusLabels[selectedGoal.status] }}</dd>
          </div>
          <div class="span-all">
            <dt>目标描述</dt>
            <dd>{{ selectedGoal.description || '未设置' }}</dd>
          </div>
        </dl>
        <el-alert
          v-if="isTerminalGoal"
          title="已完成或已归档的学习目标不可继续编辑和恢复"
          type="info"
          :closable="false"
          show-icon
        />
        <el-form label-position="top" :disabled="isTerminalGoal" class="detail-form">
          <div class="goal-form-grid">
            <el-form-item label="优先级"
              ><el-input-number v-model="detailForm.priority" :min="1" :max="5"
            /></el-form-item>
            <div />
            <el-form-item label="开始时间"
              ><el-date-picker
                v-model="detailForm.startDate"
                type="datetime"
                value-format="YYYY-MM-DDTHH:mm:ss"
                placeholder="选择开始时间"
            /></el-form-item>
            <el-form-item label="目标完成时间"
              ><el-date-picker
                v-model="detailForm.targetDate"
                type="datetime"
                value-format="YYYY-MM-DDTHH:mm:ss"
                placeholder="选择目标时间"
            /></el-form-item>
            <el-form-item label="当前阶段"
              ><el-input v-model="detailForm.currentStage" maxlength="255"
            /></el-form-item>
            <el-form-item label="当前原则"
              ><el-input v-model="detailForm.currentPrinciple" maxlength="255"
            /></el-form-item>
          </div>
        </el-form>
        <div v-if="!isTerminalGoal" class="goal-status-actions">
          <el-button
            v-if="selectedGoal.status !== 'active'"
            type="primary"
            plain
            :loading="statusChanging === 'active'"
            :disabled="Boolean(statusChanging)"
            @click="confirmStatusChange('active')"
            >设为当前主线</el-button
          >
          <el-button
            v-else
            type="warning"
            plain
            :loading="statusChanging === 'paused'"
            :disabled="Boolean(statusChanging)"
            @click="confirmStatusChange('paused')"
            >暂停主线</el-button
          >
          <el-button
            plain
            :loading="statusChanging === 'completed'"
            :disabled="Boolean(statusChanging)"
            @click="confirmStatusChange('completed')"
            >标记完成</el-button
          >
          <el-button
            plain
            :loading="statusChanging === 'archived'"
            :disabled="Boolean(statusChanging)"
            @click="confirmStatusChange('archived')"
            >归档</el-button
          >
        </div>
      </template>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button
          v-if="!isTerminalGoal"
          type="primary"
          :loading="detailSaving"
          :disabled="Boolean(statusChanging)"
          @click="saveGoalDetail"
          >保存修改</el-button
        >
      </template>
    </el-dialog>
  </section>
</template>

<style scoped>
.goal-filter-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
  color: var(--ml-muted);
  font-size: 13px;
}
.status-filter {
  width: 160px;
}
.goal-loading {
  display: grid;
  gap: 12px;
}
.goal-loading :deep(.el-skeleton) {
  padding: 18px;
  border: 1px solid var(--ml-line);
  border-radius: var(--ml-radius);
}
.goal-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(240px, 320px);
  gap: 18px;
  cursor: pointer;
  transition:
    border-color 180ms ease,
    box-shadow 180ms ease;
}
.goal-card:hover,
.goal-card:focus-visible {
  border-color: #9bb2e7;
  outline: none;
  box-shadow: 0 8px 22px rgba(66, 104, 214, 0.1);
}
.goal-side {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px;
  border-radius: var(--ml-radius);
  background: var(--ml-primary-soft);
  color: var(--ml-muted);
}
.goal-side strong {
  color: var(--ml-primary-dark);
}
.goal-pagination {
  display: flex;
  justify-content: center;
  margin-top: 22px;
}
.goal-form-grid,
.goal-readonly-details {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0 16px;
}
.goal-form-grid :deep(.el-date-editor),
.goal-form-grid :deep(.el-input-number) {
  width: 100%;
}
.span-all {
  grid-column: 1 / -1;
}
.goal-readonly-details {
  margin: 0 0 18px;
  padding: 14px 16px;
  border: 1px solid var(--ml-line);
  border-radius: var(--ml-radius);
}
.goal-readonly-details div {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 9px 0;
}
.goal-readonly-details dt {
  color: var(--ml-muted);
}
.goal-readonly-details dd {
  margin: 0;
  color: var(--ml-primary-dark);
  font-weight: 700;
  text-align: right;
  overflow-wrap: anywhere;
}
.detail-form {
  margin-top: 18px;
}
.goal-status-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding-top: 16px;
  border-top: 1px solid var(--ml-line);
}
.goal-status-actions :deep(.el-button) {
  min-height: 40px;
  margin-left: 0;
}
@media (max-width: 860px) {
  .goal-card,
  .goal-form-grid,
  .goal-readonly-details {
    grid-template-columns: 1fr;
  }
  .span-all {
    grid-column: auto;
  }
  .goal-form-grid > div:empty {
    display: none;
  }
}
@media (max-width: 560px) {
  .goal-filter-row {
    align-items: stretch;
    flex-direction: column;
  }
  .status-filter {
    width: 100%;
  }
  .goal-status-actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
  }
}
</style>
