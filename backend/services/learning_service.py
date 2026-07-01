from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from database.crud import learning
from schemas.learning import LearningGoalResponse, LearningGoalCreateRequest, LearningGoalsPageResponse, \
    LearningGoalUpdateRequest, LearningGoalStatusResponse


LEARNING_GOAL_STATUS_TRANSITIONS = {
    "pending": {"active"},
    "active": {"paused", "completed"},
    "paused": {"active", "completed"},
    "completed": set(),
    "archived": set(),
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
        # 取消未完成任务
        # await learning.cancel_unfinished_tasks_by_goal(
        #     db=db,
        #     user_id=user_id,
        #     goal_id=goal_id,
        # )
        await db.refresh(goal)
        result = LearningGoalResponse.model_validate(goal)
        await db.commit()
        return result
    except Exception:
        await db.rollback()
        raise

