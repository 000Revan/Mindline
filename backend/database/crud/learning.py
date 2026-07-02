from datetime import date
from typing import Optional

from sqlalchemy import case, select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import DailyTask, LearningGoal, User
from schemas.learning import LearningGoalCreateRequest


# 创建学习目标
async def create_learning_goal(
        db:AsyncSession,
        user_id: int,
        learning_goal_data: LearningGoalCreateRequest
):
    goal=LearningGoal(
        user_id=user_id,
        status="pending",
        **learning_goal_data.model_dump()
    )
    db.add(goal)
    await db.flush()
    return goal

#获取学习目标列表
async def get_learning_goals_page(
        db:AsyncSession,
        user_id: int,
        page: int=1,
        page_size: int=10,
        status:Optional[str]=None
):
    """分页查询指定用户的学习目标"""
    filters=[LearningGoal.user_id==user_id]

    if status is not None:
        filters.append(LearningGoal.status==status)
    else:
        filters.append(LearningGoal.status != "archived")

    count_query=(
        select(func.count(LearningGoal.id))
        .where(*filters)
    )
    #总数量
    total_result=await db.execute(count_query)
    total=total_result.scalar_one()

    skip=(page-1)*page_size

    # 目标列表
    list_query=(
        select(LearningGoal)
        .where(*filters)
        .order_by(
            LearningGoal.priority.desc(),
            LearningGoal.created_at.desc(),
            LearningGoal.id.desc()
        )
        .offset(skip)
        .limit(page_size)
    )
    list_result=await db.execute(list_query)
    goals=list(list_result.scalars().all())
    return  goals,total

#根据学习目标id查找
async def get_learning_goal_by_id(db:AsyncSession, goal_id:int,user_id:int):
    query=(
        select(LearningGoal)
        .where(LearningGoal.id==goal_id,LearningGoal.user_id==user_id)
    )
    result=await db.execute(query)
    return result.scalar_one_or_none()

#修改学习目标信息
async def update_learning_goal(
    db: AsyncSession,
    goal: LearningGoal,
    update_data: dict,
):
    for field, value in update_data.items():
        setattr(goal, field, value)

    await db.flush()
    return goal


async def lock_user_for_update(db: AsyncSession, user_id: int):
    """锁定用户记录，串行执行该用户的目标激活操作。"""

    query = (
        select(User.id)
        .where(User.id == user_id)
        .with_for_update()
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_learning_goal_for_update(
    db: AsyncSession,
    user_id: int,
    goal_id: int,
):
    """查询并锁定需要激活的学习目标。"""

    query = (
        select(LearningGoal)
        .where(
            LearningGoal.id == goal_id,
            LearningGoal.user_id == user_id,
        )
        .with_for_update()
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def pause_other_active_goals(
    db: AsyncSession,
    user_id: int,
    exclude_goal_id: int,
) -> int:
    """暂停当前用户除指定目标外的其他活跃目标。"""

    query = (
        update(LearningGoal)
        .where(
            LearningGoal.user_id == user_id,
            LearningGoal.status == "active",
            LearningGoal.id != exclude_goal_id,
        )
        .values(status="paused")
    )
    result = await db.execute(query)
    return result.rowcount

#修改目标状态
async def update_learning_goal_status(
    db: AsyncSession,
    user_id: int,
    goal_id: int,
    goal_status: str,
):
    query = (
        update(LearningGoal)
        .where(
            LearningGoal.id == goal_id,
            LearningGoal.user_id == user_id,
        )
        .values(status=goal_status)
    )
    return await db.execute(query)

#归档目标
async def archive_learning_goal(
    db: AsyncSession,
    user_id: int,
    goal_id: int,
):
    query = (
        update(LearningGoal)
        .where(
            LearningGoal.id == goal_id,
            LearningGoal.user_id == user_id,
        )
        .values(status="archived")
    )
    return await db.execute(query)


async def create_daily_task(
    db: AsyncSession,
    user_id: int,
    task_data: dict,
) -> DailyTask:
    """创建每日学习任务并刷新主键，不在 CRUD 层提交事务。"""

    task = DailyTask(user_id=user_id, status="pending", **task_data)
    db.add(task)
    await db.flush()
    return task


async def get_daily_task_by_id(
    db: AsyncSession,
    user_id: int,
    task_id: int,
) -> Optional[DailyTask]:
    """按用户和任务 ID 查询每日学习任务。"""

    query = select(DailyTask).where(
        DailyTask.id == task_id,
        DailyTask.user_id == user_id,
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_daily_task_for_update(
    db: AsyncSession,
    user_id: int,
    task_id: int,
) -> Optional[DailyTask]:
    """查询并锁定每日学习任务，避免并发状态更新互相覆盖。"""

    query = (
        select(DailyTask)
        .where(
            DailyTask.id == task_id,
            DailyTask.user_id == user_id,
        )
        .with_for_update()
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_daily_tasks_page(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
    task_date: Optional[date] = None,
    goal_id: Optional[int] = None,
    task_status: Optional[str] = None,
) -> tuple[list[DailyTask], int]:
    """按日期、目标和状态分页查询当前用户的每日学习任务。"""

    filters = [DailyTask.user_id == user_id]
    if task_date is not None:
        filters.append(DailyTask.task_date == task_date)
    if goal_id is not None:
        filters.append(DailyTask.goal_id == goal_id)
    if task_status is not None:
        filters.append(DailyTask.status == task_status)

    total_result = await db.execute(
        select(func.count(DailyTask.id)).where(*filters)
    )
    total = total_result.scalar_one()

    status_order = case(
        (DailyTask.status == "in_progress", 1),
        (DailyTask.status == "pending", 2),
        (DailyTask.status == "completed", 3),
        else_=4,
    )
    query = (
        select(DailyTask)
        .where(*filters)
        .order_by(
            DailyTask.task_date.asc(),
            status_order.asc(),
            DailyTask.created_at.asc(),
            DailyTask.id.asc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def update_daily_task(
    db: AsyncSession,
    task: DailyTask,
    update_data: dict,
) -> DailyTask:
    """更新每日学习任务字段，不在 CRUD 层处理业务状态机。"""

    for field, value in update_data.items():
        setattr(task, field, value)
    await db.flush()
    return task


async def cancel_unfinished_tasks_by_goal(
    db: AsyncSession,
    user_id: int,
    goal_id: int,
) -> int:
    """取消指定目标下尚未完成的任务。"""

    query = (
        update(DailyTask)
        .where(
            DailyTask.user_id == user_id,
            DailyTask.goal_id == goal_id,
            DailyTask.status.in_(["pending", "in_progress"]),
        )
        .values(status="cancelled", completed_at=None)
    )
    result = await db.execute(query)
    return result.rowcount
