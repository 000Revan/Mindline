from typing import Literal

from fastapi import APIRouter, Depends
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from database.models import User
from schemas.learning import LearningGoalCreateRequest, LearningGoalStatusRequest, LearningGoalUpdateRequest
from schemas.users import UserInfoResponse
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

#获取学习目标详情
@router.get("/goals/{goal_id}")
async def get_learning_goal_detail(
        goal_id:int,
        user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_db)
):
    result=await learning_service.get_learning_goal_by_id(
        db=db,
        goal_id=goal_id,
        user_id=user.id
    )
    return success_response(
        msg="获取学习目标详情成功",
        data=result
    )


#修改学习目标普通信息
@router.patch("/goals/{goal_id}")
async def update_learning_goal(
        goal_id:int,
        update_data:LearningGoalUpdateRequest,
        user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_db),

):
    result=await learning_service.update_learning_goal(
        db=db,
        user_id=user.id,
        goal_id=goal_id,
        update_data=update_data
    )
    return success_response(
        msg="修改学习目标信息成功",
        data=result
    )


#修改学习目标状态
@router.patch("/goals/{goal_id}/status")
async def update_learning_goal_status(
    goal_id: int,
    status_data: LearningGoalStatusRequest,
    user: UserInfoResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新目标状态；激活目标时自动暂停其他活跃目标。"""

    result = await learning_service.update_learning_goal_status(
        db=db,
        user_id=user.id,
        goal_id=goal_id,
        goal_status=status_data.status,
    )
    return success_response(
        msg="修改学习目标状态成功",
        data=result,
    )



@router.delete("/goals/{goal_id}")
async def archive_learning_goal(
    goal_id: int,
    user: UserInfoResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除学习目标。"""

    result = await learning_service.archive_learning_goal(
        db=db,
        user_id=user.id,
        goal_id=goal_id,
    )
    return success_response(
        msg="删除学习目标成功",
        data=result
    )

#创建今日学习任务
