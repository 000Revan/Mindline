from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import learning
from schemas.learning import LearningGoalResponse, LearningGoalCreateRequest, LearningGoalsPageResponse


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
