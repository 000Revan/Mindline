# Mindline

Mindline 是一个面向自学者、学生、转码学习者和求职准备者的多 Agent 学习陪伴系统。它的目标不是替代普通笔记软件，也不是只做聊天，而是帮助用户守住学习主线、沉淀笔记、记录学习过程、生成复盘，并在焦虑或迷茫时提供可执行的陪伴式支持。

项目的核心理念：

```text
允许好奇，但不让好奇接管主线。
```

## 为什么做

学习时很容易从 A 跳到 A 的基础 B，再跳到 B 的基础 C，最后主线丢失、效率下降。Mindline 希望把这种“想完全理解才敢继续”的压力拆开：主线内容先按最低可用理解推进，分支问题进入停车场；如果确实需要溯源，就开启 5/10/15 分钟限时学习，时间到后总结可用结论并回到主线。

另一个重要动机是缓解学习焦虑。系统会记录学习事实、笔记、目标、复盘与情绪日志，让用户看到自己已经推进了什么，也把“我什么都不会”的模糊焦虑转成下一步可执行任务。

## 当前状态

当前仓库已有后端基础：

- `FastAPI` 应用入口与用户路由
- `SQLAlchemy 2.0 async` ORM 模型
- `Alembic` 初始迁移
- 用户注册、登录、信息更新、修改密码的基础服务
- 统一响应工具

当前暂不包含前端、RAG、LangGraph 编排、Redis、Chroma 与完整 Agent 服务实现。

## MVP 功能范围

当前 MVP 保留：

- 用户注册、登录、JWT 鉴权与用户数据隔离
- 学习主线与学习目标管理
- 每日学习任务与学习记录
- 分支停车场与限时溯源
- 笔记保存、优化、切片与知识点沉淀
- 个人知识库检索问答
- 每日复盘、每周复盘
- 情绪陪伴、焦虑拆解与行动建议
- Agent 运行记录与可恢复执行上下文

当前 MVP 不做：

- 每日题目
- 题库系统
- 错题本
- 间隔复习调度
- 遗忘曲线

注意：当前 ORM 中的 `daily_tasks` 是每日学习任务/计划，不是每日题目。

## 后端架构

```text
routers -> services -> database.crud -> database.models
                         |
                         -> SQLAlchemy async -> MySQL
```

规划中的智能能力边界：

```text
MySQL：正式业务事实数据
Chroma：笔记切片向量与语义检索
Redis：短期上下文、缓存、限时状态
LangGraph Checkpointer：Agent 流程恢复点
```

不要把 Chroma 当主数据库，也不要把 LangGraph state 当业务事实库。

## 当前数据模型

已存在的主要表：

- `users`、`user_profiles`
- `notes`、`note_chunks`、`knowledge_points`、`note_knowledge_points`
- `learning_goals`、`daily_tasks`、`learning_sessions`
- `branch_topics`、`branch_timer_sessions`
- `sessions`、`messages`
- `daily_reviews`、`weekly_reviews`
- `emotion_logs`
- `agent_runs`
- `uploaded_files`

所有用户相关业务数据都必须通过 `user_id` 隔离。

## 本地运行

后端依赖在 `backend/pyproject.toml` 中维护，当前使用 Python `>=3.11`。

```powershell
cd backend
uv sync
uv run uvicorn main:app --reload
```

需要先配置根目录 `.env` 中的数据库连接信息，并确保 MySQL 可用。

## 文档

更完整的项目说明、当前架构适配和迭代计划见：

- [mindline_project_plan.md](./mindline_project_plan.md)
