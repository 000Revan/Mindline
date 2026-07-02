# Mindline

Mindline 是一个面向自学者、学生、转码学习者和求职准备者的多 Agent 学习陪伴系统。它围绕学习主线组织每日任务、学习过程、分支问题、笔记、复盘和情绪支持，把“不会的太多”转化为可追踪事实与下一步行动。

```text
允许好奇，但不让好奇接管主线。
```

## 当前状态

当前仓库已经具备 Vue 前端与 FastAPI 后端，并真实接通：

- 用户注册、登录、JWT 鉴权、资料、头像和密码修改
- 学习主线创建、分页、编辑、激活、暂停、完成和归档
- 每日任务按日期/状态查询、创建、编辑、开始、暂停、完成、取消和恢复
- 工作台与右侧上下文的真实主线、任务统计
- SQLAlchemy async ORM 与 Alembic 迁移

以下模块已有 ORM 和前端页面骨架，但仍主要使用 mock 数据，尚未形成真实后端闭环：

- 学习记录与分支停车场
- 笔记、知识点与文件导入
- 会话、消息和 Agent 运行记录
- 每日/每周复盘与情绪陪伴
- RAG、Redis、Chroma、SSE 和 LangGraph 编排

## 技术栈

| 层级 | 技术 |
| --- | --- |
| 前端 | Vue 3、TypeScript、Pinia、Vue Router、Element Plus、Vite |
| 后端 | Python 3.11+、FastAPI、Pydantic、SQLAlchemy 2.0 async |
| 数据库 | MySQL、Alembic、aiomysql |
| 鉴权 | JWT、Argon2 |
| 规划中的智能层 | LangChain、LangGraph、Redis、Chroma、SSE |

当前后端依赖方向：

```text
routers → services → database.crud → database.models → MySQL
```

数据边界：MySQL 保存正式业务事实；Redis 保存短期状态与缓存；Chroma 保存按用户隔离的向量数据；LangGraph Checkpointer 只保存流程恢复点。

## MVP 范围

MVP 聚焦：

- 用户与画像
- 学习主线、每日任务和学习记录
- 分支停车场与限时溯源
- 笔记、知识点和个人知识库
- 每日/每周复盘
- 情绪陪伴与行动建议
- Agent 运行追踪和可恢复执行

MVP 暂不包含每日题目、题库、错题本、自动批改、间隔复习和遗忘曲线。`daily_tasks` 表示学习任务/计划，不表示每日题目。

## 项目目录

```text
Mindline/
├── backend/                    # FastAPI、ORM、迁移与后端分层
│   ├── routers/
│   ├── services/
│   ├── schemas/
│   ├── database/
│   ├── agent/
│   └── alembic/
├── frontend/                   # Vue 3 单页应用
│   └── src/
│       ├── api/
│       ├── stores/
│       ├── layouts/
│       ├── views/
│       └── styles/
└── *.md                        # 产品、进度、计划与问题文档
```

## 本地运行

先配置根目录 `.env` 并启动 MySQL。

### 后端

```powershell
cd backend
uv sync
alembic upgrade head
uv run uvicorn main:app --reload
```

Alembic 必须从 `backend` 目录执行，否则当前顶层包导入可能报 `ModuleNotFoundError`。

检查迁移：

```powershell
cd backend
alembic current
alembic check
```

### 前端

```powershell
cd frontend
npm install
npm run dev
```

类型与构建检查：

```powershell
npm run type-check
npm run build
```

默认 API 地址为 `http://127.0.0.1:8000`，可通过 `VITE_API_BASE_URL` 调整。

## 文档导航

- [program_description.md](./program_description.md)：产品、架构、视觉与配色总览
- [current_progress.md](./current_progress.md)：当前实现状态和下一阶段
- [task_plan.md](./task_plan.md)：后续详细任务与验收计划
- [problem_solving.md](./problem_solving.md)：问题、踩坑和解决方案
- [mindline_project_plan.md](./mindline_project_plan.md)：完整历史规划与长期路线

出现描述冲突时，以当前代码和 [current_progress.md](./current_progress.md) 为事实依据。
