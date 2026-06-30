from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import LearningGoal
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
        .where(LearningGoal.user_id==user_id)
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



