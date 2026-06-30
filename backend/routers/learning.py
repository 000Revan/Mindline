from typing import Literal

from fastapi import APIRouter, Depends
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from database.models import User
from schemas.learning import LearningGoalCreateRequest
from services import learning_service
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/learning", tags=['学习计划相关'])

GoalStatus = Literal[
    "pending",
    "active",
    "paused",
    "completed",
    "archived",
]

#创建学习目标
@router.post("/goals")
async def create_learning_goal(
    learning_goal_data:LearningGoalCreateRequest,
    user:User=Depends(get_current_user),
    db:AsyncSession=Depends(get_db)
):
    result=await learning_service.create_learning_goal(
        db=db,
        user_id=user.id,
        learning_goal_data=learning_goal_data
    )
    return success_response(
        msg="创建学习目标成功",
        data=result
    )


#获取学习目标列表
@router.get("/goals")
async def get_learning_goals_list(
        user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_db),
        page:int=Query(default=1,ge=1),
        page_size:int=Query(default=10,ge=1,le=10),
        status:GoalStatus=Query(default=None)
):
    result=await learning_service.get_learning_goals_page(
        db=db,
        user_id=user.id,
        page=page,
        page_size=page_size,
        status=status
    )
    return success_response(
        msg="获取学习目标列表成功",
        data=result
    )





#创建今日学习任务