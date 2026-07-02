<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { useMindlineStore } from '@/stores/mindline'
import type { DailyTask, DailyTaskStatus, DailyTaskType, LearningGoal } from '@/types/mindline'

const store = useMindlineStore()
const formRef = ref<FormInstance>()
const dialogVisible = ref(false)
const saving = ref(false)
const editingTask = ref<DailyTask>()
const changingTaskId = ref<number>()

const typeOptions: Array<{ label: string; value: DailyTaskType }> = [
  { label: '主线学习', value: 'study' },
  { label: '复习整理', value: 'review' },
  { label: '分支回收', value: 'branch' },
  { label: '总结反思', value: 'reflection' },
]
const statusOptions: Array<{ label: string; value: DailyTaskStatus | '' }> = [
  { label: '全部状态', value: '' },
  { label: '待开始', value: 'pending' },
  { label: '进行中', value: 'in_progress' },
  { label: '已完成', value: 'completed' },
  { label: '已取消', value: 'cancelled' },
]
const typeLabels: Record<DailyTaskType, string> = {
  study: '主线学习',
  review: '复习整理',
  branch: '分支回收',
  reflection: '总结反思',
}
const statusLabels: Record<DailyTaskStatus, string> = {
  pending: '待开始',
  in_progress: '进行中',
  completed: '已完成',
  cancelled: '已取消',
}
const statusTagTypes: Record<DailyTaskStatus, 'primary' | 'success' | 'warning' | 'info'> = {
  pending: 'warning',
  in_progress: 'primary',
  completed: 'success',
  cancelled: 'info',
}

const form = reactive<{
  goalId?: number
  title: string
  description: string
  taskType: DailyTaskType
  estimatedTime?: number
  taskDate: string
}>({ title: '', description: '', taskType: 'study', estimatedTime: 30, taskDate: store.taskDate })

const rules: FormRules = {
  goalId: [{ required: true, message: '请选择所属学习主线', trigger: 'change' }],
  title: [
    { required: true, message: '请输入任务标题', trigger: 'blur' },
    { max: 255, message: '任务标题不能超过 255 个字符', trigger: 'blur' },
  ],
  taskType: [{ required: true, message: '请选择任务类型', trigger: 'change' }],
  taskDate: [{ required: true, message: '请选择计划日期', trigger: 'change' }],
}

const availableGoals = computed<LearningGoal[]>(() => {
  const goals = [store.activeGoal, ...store.goals].filter(
    (goal): goal is LearningGoal =>
      goal !== undefined && !['completed', 'archived'].includes(goal.status),
  )
  return goals.filter((goal, index) => goals.findIndex((item) => item.id === goal.id) === index)
})
const pendingCount = computed(() => store.tasks.filter((task) => task.status === 'pending').length)
const progressCount = computed(
  () => store.tasks.filter((task) => task.status === 'in_progress').length,
)
const completedCount = computed(
  () => store.tasks.filter((task) => task.status === 'completed').length,
)
const estimatedMinutes = computed(() =>
  store.tasks.reduce((total, task) => total + (task.estimatedTime ?? 0), 0),
)

function localDate() {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
}

function goalTitle(goalId: number) {
  return (
    [store.activeGoal, ...store.goals].find((goal) => goal?.id === goalId)?.title ||
    `目标 #${goalId}`
  )
}

async function loadTasks(page = 1) {
  try {
    await store.fetchDailyTasks(page, store.taskDate, store.taskStatusFilter)
  } catch {
    // 页面统一展示 Store 中的错误状态。
  }
}

async function initialize() {
  await Promise.allSettled([store.fetchGoals(1, ''), store.fetchActiveGoal()])
  await loadTasks(1)
}

function refreshFromFilter() {
  void loadTasks(1)
}

function selectToday() {
  store.taskDate = localDate()
  void loadTasks(1)
}

function resetForm() {
  editingTask.value = undefined
  form.goalId = store.activeGoal?.id ?? availableGoals.value[0]?.id
  form.title = ''
  form.description = ''
  form.taskType = 'study'
  form.estimatedTime = 30
  form.taskDate = store.taskDate
  formRef.value?.clearValidate()
}

function openCreate() {
  if (!availableGoals.value.length) {
    ElMessage.warning('请先创建并激活一条学习主线')
    return
  }
  resetForm()
  dialogVisible.value = true
}

function openEdit(task: DailyTask) {
  if (task.status === 'completed' || task.status === 'cancelled') return
  editingTask.value = task
  form.goalId = task.goalId
  form.title = task.title
  form.description = task.description
  form.taskType = task.taskType
  form.estimatedTime = task.estimatedTime ?? undefined
  form.taskDate = task.taskDate
  dialogVisible.value = true
  formRef.value?.clearValidate()
}

async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid || !form.goalId) return
  saving.value = true
  try {
    const payload = {
      goal_id: form.goalId,
      title: form.title.trim(),
      description: form.description.trim() || null,
      task_type: form.taskType,
      estimated_time: form.estimatedTime ?? null,
      task_date: form.taskDate,
    }
    store.taskDate = form.taskDate
    if (editingTask.value) {
      await store.updateDailyTask(editingTask.value.id, payload)
      ElMessage.success('每日任务已更新')
    } else {
      await store.createDailyTask(payload)
      ElMessage.success('每日任务已创建')
    }
    dialogVisible.value = false
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '每日任务保存失败')
  } finally {
    saving.value = false
  }
}

async function changeStatus(task: DailyTask, status: DailyTaskStatus) {
  if (status === 'cancelled') {
    try {
      await ElMessageBox.confirm(`取消“${task.title}”后仍可恢复。`, '确认取消任务', {
        confirmButtonText: '确认取消',
        cancelButtonText: '返回',
        type: 'warning',
      })
    } catch {
      return
    }
  }
  changingTaskId.value = task.id
  try {
    await store.changeDailyTaskStatus(task.id, status)
    ElMessage.success(`任务状态已更新为${statusLabels[status]}`)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '任务状态修改失败')
  } finally {
    changingTaskId.value = undefined
  }
}

onMounted(() => void initialize())
</script>

<template>
  <section class="page-shell">
    <div class="page-title-row">
      <div>
        <p class="page-kicker">Daily Tasks</p>
        <h2 class="page-title">每日学习任务</h2>
        <p class="page-subtitle">围绕学习主线安排任务，实时记录开始、完成、撤销和取消状态。</p>
      </div>
      <el-button type="primary" :disabled="!availableGoals.length" @click="openCreate">
        <el-icon><Plus /></el-icon>新建任务
      </el-button>
    </div>

    <section class="task-toolbar panel-card" aria-label="每日任务筛选">
      <div class="date-control">
        <span>计划日期</span>
        <el-date-picker
          v-model="store.taskDate"
          type="date"
          value-format="YYYY-MM-DD"
          format="YYYY年MM月DD日"
          :clearable="false"
          aria-label="选择计划日期"
          @change="refreshFromFilter"
        />
        <el-button plain @click="selectToday">回到今天</el-button>
      </div>
      <el-select
        v-model="store.taskStatusFilter"
        class="status-filter"
        aria-label="筛选任务状态"
        @change="refreshFromFilter"
      >
        <el-option v-for="option in statusOptions" :key="option.value || 'all'" v-bind="option" />
      </el-select>
    </section>

    <div class="metric-grid">
      <div class="metric-card">
        <p class="metric-label">任务总数</p>
        <p class="metric-value">{{ store.taskTotal }}</p>
      </div>
      <div class="metric-card">
        <p class="metric-label">待开始 / 进行中</p>
        <p class="metric-value">{{ pendingCount }} / {{ progressCount }}</p>
      </div>
      <div class="metric-card">
        <p class="metric-label">本页已完成</p>
        <p class="metric-value">{{ completedCount }}</p>
      </div>
      <div class="metric-card">
        <p class="metric-label">本页预计投入</p>
        <p class="metric-value">{{ estimatedMinutes }}<small> 分钟</small></p>
      </div>
    </div>

    <div v-if="store.tasksLoading" class="loading-list" aria-label="每日任务加载中">
      <el-skeleton v-for="index in 3" :key="index" :rows="2" animated />
    </div>
    <el-result
      v-else-if="store.tasksError"
      icon="error"
      title="每日任务加载失败"
      :sub-title="store.tasksError"
    >
      <template #extra
        ><el-button type="primary" @click="loadTasks(store.taskPage)">重新加载</el-button></template
      >
    </el-result>
    <el-empty v-else-if="!store.tasks.length" description="这一天暂无符合条件的任务">
      <el-button v-if="availableGoals.length" type="primary" @click="openCreate"
        >创建第一个任务</el-button
      >
      <RouterLink v-else to="/goals"
        ><el-button type="primary">先创建学习主线</el-button></RouterLink
      >
    </el-empty>

    <div v-else class="task-list" aria-live="polite">
      <article
        v-for="task in store.tasks"
        :key="task.id"
        class="task-card panel-card"
        :class="`status-${task.status}`"
      >
        <div class="task-copy">
          <div class="task-meta">
            <el-tag :type="statusTagTypes[task.status]">{{ statusLabels[task.status] }}</el-tag>
            <el-tag type="info" effect="plain">{{ typeLabels[task.taskType] }}</el-tag>
            <span>{{ task.estimatedTime ? `${task.estimatedTime} 分钟` : '时长未设置' }}</span>
          </div>
          <h3>{{ task.title }}</h3>
          <p>{{ task.description || '暂无任务说明' }}</p>
          <div class="task-goal">
            <el-icon><Aim /></el-icon><span>{{ goalTitle(task.goalId) }}</span>
          </div>
        </div>
        <div class="task-actions" :aria-label="`${task.title}操作`">
          <el-button
            v-if="task.status === 'pending'"
            type="primary"
            :loading="changingTaskId === task.id"
            @click="changeStatus(task, 'in_progress')"
            >开始</el-button
          >
          <el-button
            v-if="task.status === 'in_progress'"
            :disabled="changingTaskId === task.id"
            @click="changeStatus(task, 'pending')"
            >暂停</el-button
          >
          <el-button
            v-if="['pending', 'in_progress'].includes(task.status)"
            type="success"
            plain
            :disabled="changingTaskId === task.id"
            @click="changeStatus(task, 'completed')"
            >完成</el-button
          >
          <el-button
            v-if="['pending', 'in_progress'].includes(task.status)"
            :disabled="changingTaskId === task.id"
            @click="openEdit(task)"
            >编辑</el-button
          >
          <el-button
            v-if="['pending', 'in_progress'].includes(task.status)"
            type="danger"
            plain
            :disabled="changingTaskId === task.id"
            @click="changeStatus(task, 'cancelled')"
            >取消</el-button
          >
          <el-button
            v-if="['completed', 'cancelled'].includes(task.status)"
            :loading="changingTaskId === task.id"
            @click="changeStatus(task, 'pending')"
            >恢复为待开始</el-button
          >
        </div>
      </article>
    </div>

    <div v-if="store.taskTotalPages > 1" class="pagination">
      <el-pagination
        background
        layout="prev, pager, next"
        :current-page="store.taskPage"
        :page-size="store.taskPageSize"
        :total="store.taskTotal"
        @current-change="loadTasks"
      />
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="editingTask ? '编辑每日任务' : '新建每日任务'"
      width="min(680px, calc(100vw - 32px))"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <div class="form-grid">
          <el-form-item label="所属学习主线" prop="goalId" class="span-all">
            <el-select v-model="form.goalId"
              ><el-option
                v-for="goal in availableGoals"
                :key="goal.id"
                :label="goal.title"
                :value="goal.id"
            /></el-select>
          </el-form-item>
          <el-form-item label="任务标题" prop="title" class="span-all"
            ><el-input v-model="form.title" maxlength="255" show-word-limit
          /></el-form-item>
          <el-form-item label="任务类型" prop="taskType">
            <el-select v-model="form.taskType"
              ><el-option v-for="option in typeOptions" :key="option.value" v-bind="option"
            /></el-select>
          </el-form-item>
          <el-form-item label="预计耗时（分钟）"
            ><el-input-number v-model="form.estimatedTime" :min="1" :max="1440" :step="5"
          /></el-form-item>
          <el-form-item label="计划日期" prop="taskDate" class="span-all"
            ><el-date-picker
              v-model="form.taskDate"
              type="date"
              value-format="YYYY-MM-DD"
              format="YYYY年MM月DD日"
              :clearable="false"
          /></el-form-item>
          <el-form-item label="任务说明" class="span-all"
            ><el-input
              v-model="form.description"
              type="textarea"
              :rows="4"
              maxlength="5000"
              show-word-limit
          /></el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submit">{{
          editingTask ? '保存修改' : '确认创建'
        }}</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<style scoped>
.task-toolbar,
.date-control,
.task-meta,
.task-goal,
.task-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.task-toolbar {
  justify-content: space-between;
  padding: 14px 16px;
}
.date-control > span {
  color: var(--ml-muted);
  font-size: 13px;
  font-weight: 700;
}
.status-filter {
  width: 160px;
}
.metric-value small {
  color: var(--ml-muted);
  font-size: 13px;
  font-weight: 500;
}
.loading-list,
.task-list {
  display: grid;
  gap: 12px;
}
.loading-list :deep(.el-skeleton) {
  padding: 18px;
  border: 1px solid var(--ml-line);
  border-radius: var(--ml-radius);
  background: var(--ml-surface);
}
.task-card {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 20px;
  padding: 18px;
  overflow: hidden;
}
.task-card::before {
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: var(--ml-warning);
  content: '';
}
.task-card.status-in_progress::before {
  background: var(--ml-primary);
}
.task-card.status-completed::before {
  background: var(--ml-success);
}
.task-card.status-cancelled::before {
  background: var(--ml-muted);
}
.task-copy {
  min-width: 0;
}
.task-copy h3 {
  margin: 10px 0;
  color: var(--ml-primary-dark);
  font-size: 18px;
  overflow-wrap: anywhere;
}
.task-copy > p {
  margin: 0 0 12px;
  color: var(--ml-muted);
  line-height: 1.65;
}
.task-meta {
  flex-wrap: wrap;
  color: var(--ml-muted);
  font-size: 13px;
}
.task-goal {
  color: #40517e;
  font-size: 13px;
}
.task-actions {
  max-width: 300px;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.task-actions :deep(.el-button) {
  min-height: 44px;
  margin-left: 0;
}
.pagination {
  display: flex;
  justify-content: center;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0 16px;
}
.form-grid :deep(.el-select),
.form-grid :deep(.el-date-editor),
.form-grid :deep(.el-input-number) {
  width: 100%;
}
.span-all {
  grid-column: 1/-1;
}
@media (max-width: 860px) {
  .task-card {
    grid-template-columns: 1fr;
  }
  .task-actions {
    max-width: none;
    justify-content: flex-start;
    padding-top: 12px;
    border-top: 1px solid var(--ml-line);
  }
}
@media (max-width: 640px) {
  .task-toolbar,
  .date-control {
    align-items: stretch;
    flex-direction: column;
  }
  .status-filter {
    width: 100%;
  }
  .form-grid {
    grid-template-columns: 1fr;
  }
  .span-all {
    grid-column: auto;
  }
  .task-actions {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
