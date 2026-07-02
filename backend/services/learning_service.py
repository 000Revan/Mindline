from datetime import date, datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from database.crud import learning
from schemas.learning import (
    DailyTaskCreateRequest,
    DailyTaskResponse,
    DailyTasksPageResponse,
    DailyTaskStatusRequest,
    DailyTaskUpdateRequest,
    LearningGoalCreateRequest,
    LearningGoalResponse,
    LearningGoalsPageResponse,
    LearningGoalStatusResponse,
    LearningGoalUpdateRequest,
)


LEARNING_GOAL_STATUS_TRANSITIONS = {
    "pending": {"active"},
    "active": {"paused", "completed"},
    "paused": {"active", "completed"},
    "completed": set(),
    "archived": set(),
}

DAILY_TASK_STATUS_TRANSITIONS = {
    "pending": {"in_progress", "completed", "cancelled"},
    "in_progress": {"pending", "completed", "cancelled"},
    "completed": {"pending"},
    "cancelled": {"pending"},
}


# 创建学习目标
async def create_learning_goal(
        db: AsyncSession,
        user_id: int,
        learning_goal_data: LearningGoalCreateRequest
) -> LearningGoalResponse:
    try:
        goal = await learning.create_learning_goal(
            db=db,
            user_id=user_id,
            learning_goal_data=learning_goal_data
        )
        result = LearningGoalResponse.model_validate(goal)
        await db.commit()
        return result
    except Exception:
        await db.rollback()
        raise


# 获取学习目标列表
async def get_learning_goals_page(
        db: AsyncSession,
        user_id: int,
        page: int,
        page_size: int,
        status: Optional[str] = None
):
    goals,total=await learning.get_learning_goals_page(
        db=db,
        user_id=user_id,
        page=page,
        page_size=page_size,
        status=status
    )

    total_pages = (total + page_size - 1) // page_size

    return LearningGoalsPageResponse(
        items=[LearningGoalResponse.model_validate(goal) for goal in goals],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


async def get_learning_goal_by_id(
        db:AsyncSession,
        goal_id:int,
        user_id:int,
):
    result=await learning.get_learning_goal_by_id(db=db, goal_id=goal_id, user_id=user_id)
    return LearningGoalResponse.model_validate(result)


# 修改学习目标信息
async def update_learning_goal(
        db: AsyncSession,
        user_id: int,
        goal_id: int,
        update_data: LearningGoalUpdateRequest
):
    try:
        goal=await learning.get_learning_goal_by_id(db=db, goal_id=goal_id, user_id=user_id)
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="学习目标不存在"
            )
        if goal.status in {"completed", "archived"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无法修改已完成或已归档的学习目标"
            )

        data=update_data.model_dump(
            exclude_none=True
        )
        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有需要修改的字段"
            )

        start_date=data.get("start_date", goal.start_date)
        target_date=data.get("target_date", goal.target_date)

        if start_date and target_date and start_date >= target_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="目标完成时间必须晚于开始时间"
            )

        goal=await learning.update_learning_goal(
            db=db,
            goal=goal,
            update_data=data
        )
        result=LearningGoalResponse.model_validate(goal)
        await db.commit()
        return  result
    except Exception:
        await db.rollback()
        raise

# 修改学习目标状态
async def update_learning_goal_status(
    db: AsyncSession,
    user_id: int,
    goal_id: int,
    goal_status: str,
) -> LearningGoalStatusResponse:
    """更新学习目标状态，并保证每个用户最多只有一个活跃目标。"""

    try:
        locked_user_id = await learning.lock_user_for_update(db, user_id)
        if locked_user_id is None:
            raise HTTPException(status_code=404, detail="用户不存在")

        goal = await learning.get_learning_goal_for_update(
            db=db,
            user_id=user_id,
            goal_id=goal_id,
        )
        if goal is None:
            raise HTTPException(status_code=404, detail="学习目标不存在")

        allowed_statuses = LEARNING_GOAL_STATUS_TRANSITIONS[goal.status]
        if goal.status != goal_status and goal_status not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"学习目标不能从 {goal.status} 状态变更为 {goal_status} 状态",
            )

        paused_count = 0
        if goal_status == "active":
            paused_count = await learning.pause_other_active_goals(
                db=db,
                user_id=user_id,
                exclude_goal_id=goal_id,
            )

        if goal.status != goal_status:
            await learning.update_learning_goal_status(
                db=db,
                user_id=user_id,
                goal_id=goal_id,
                goal_status=goal_status,
            )

        await db.refresh(goal)

        result = LearningGoalStatusResponse(
            goal=LearningGoalResponse.model_validate(goal),
            paused_goal_count=paused_count,
        )

        await db.commit()
        return result

    except Exception:
        await db.rollback()
        raise




async def archive_learning_goal(
    db: AsyncSession,
    user_id: int,
    goal_id: int,
) -> LearningGoalResponse:
    """删除学习目标。"""

    try:
        locked_user_id = await learning.lock_user_for_update(db, user_id)
        if locked_user_id is None:
            raise HTTPException(status_code=404, detail="用户不存在")

        goal = await learning.get_learning_goal_for_update(
            db=db,
            goal_id=goal_id,
            user_id=user_id,
        )
        if goal is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="学习目标不存在",
            )
        if goal.status == "archived":
            result = LearningGoalResponse.model_validate(goal)
            await db.commit()
            return result
        # 归档学习目标
        await learning.archive_learning_goal(
            db=db,
            user_id=user_id,
            goal_id=goal_id,
        )
        # 目标归档后继续保留历史任务，但未完成任务不能再推进。
        await learning.cancel_unfinished_tasks_by_goal(
            db=db,
            user_id=user_id,
            goal_id=goal_id,
        )
        await db.refresh(goal)
        result = LearningGoalResponse.model_validate(goal)
        await db.commit()
        return result
    except Exception:
        await db.rollback()
        raise


async def _validate_task_goal(
    db: AsyncSession,
    user_id: int,
    goal_id: int,
):
    """校验任务所属目标存在、归属当前用户且仍允许安排任务。"""

    goal = await learning.get_learning_goal_by_id(
        db=db,
        goal_id=goal_id,
        user_id=user_id,
    )
    if goal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习目标不存在",
        )
    if goal.status in {"completed", "archived"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法为已完成或已归档的学习目标安排任务",
        )
    return goal


async def create_daily_task(
    db: AsyncSession,
    user_id: int,
    task_data: DailyTaskCreateRequest,
) -> DailyTaskResponse:
    """创建每日学习任务，并校验所属学习目标的用户与状态。"""

    try:
        await _validate_task_goal(
            db=db,
            user_id=user_id,
            goal_id=task_data.goal_id,
        )
        task = await learning.create_daily_task(
            db=db,
            user_id=user_id,
            task_data=task_data.model_dump(),
        )
        # created_at/updated_at 使用数据库默认值，刷新后再构造响应。
        await db.refresh(task)
        result = DailyTaskResponse.model_validate(task)
        await db.commit()
        return result
    except Exception:
        await db.rollback()
        raise


async def get_daily_tasks_page(
    db: AsyncSession,
    user_id: int,
    page: int,
    page_size: int,
    task_date: Optional[date] = None,
    goal_id: Optional[int] = None,
    task_status: Optional[str] = None,
) -> DailyTasksPageResponse:
    """分页查询当前用户的每日学习任务。"""

    tasks, total = await learning.get_daily_tasks_page(
        db=db,
        user_id=user_id,
        page=page,
        page_size=page_size,
        task_date=task_date,
        goal_id=goal_id,
        task_status=task_status,
    )
    return DailyTasksPageResponse(
        items=[DailyTaskResponse.model_validate(task) for task in tasks],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


async def get_daily_task_by_id(
    db: AsyncSession,
    user_id: int,
    task_id: int,
) -> DailyTaskResponse:
    """查询当前用户的每日学习任务详情。"""

    task = await learning.get_daily_task_by_id(
        db=db,
        user_id=user_id,
        task_id=task_id,
    )
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="每日学习任务不存在",
        )
    return DailyTaskResponse.model_validate(task)


async def update_daily_task(
    db: AsyncSession,
    user_id: int,
    task_id: int,
    update_data: DailyTaskUpdateRequest,
) -> DailyTaskResponse:
    """修改任务普通信息；状态修改由独立状态接口处理。"""

    try:
        task = await learning.get_daily_task_for_update(
            db=db,
            user_id=user_id,
            task_id=task_id,
        )
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="每日学习任务不存在",
            )
        if task.status in {"completed", "cancelled"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="已完成或已取消的任务不能修改，请先恢复为待开始",
            )

        data = update_data.model_dump(exclude_unset=True)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有需要修改的字段",
            )

        await _validate_task_goal(
            db=db,
            user_id=user_id,
            goal_id=data.get("goal_id", task.goal_id),
        )

        task = await learning.update_daily_task(
            db=db,
            task=task,
            update_data=data,
        )
        result = DailyTaskResponse.model_validate(task)
        await db.commit()
        return result
    except Exception:
        await db.rollback()
        raise


async def update_daily_task_status(
    db: AsyncSession,
    user_id: int,
    task_id: int,
    status_data: DailyTaskStatusRequest,
) -> DailyTaskResponse:
    """按状态机更新每日任务，并同步维护完成时间。"""

    try:
        task = await learning.get_daily_task_for_update(
            db=db,
            user_id=user_id,
            task_id=task_id,
        )
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="每日学习任务不存在",
            )

        next_status = status_data.status
        if task.status == next_status:
            result = DailyTaskResponse.model_validate(task)
            await db.commit()
            return result

        allowed_statuses = DAILY_TASK_STATUS_TRANSITIONS[task.status]
        if next_status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"每日学习任务不能从 {task.status} 变更为 {next_status}",
            )

        if next_status != "cancelled":
            await _validate_task_goal(
                db=db,
                user_id=user_id,
                goal_id=task.goal_id,
            )

        # 完成时间只描述当前的完成状态；撤销完成或取消时必须清空。
        completed_at = datetime.now() if next_status == "completed" else None
        task = await learning.update_daily_task(
            db=db,
            task=task,
            update_data={
                "status": next_status,
                "completed_at": completed_at,
            },
        )
        result = DailyTaskResponse.model_validate(task)
        await db.commit()
        return result
    except Exception:
        await db.rollback()
        raise

