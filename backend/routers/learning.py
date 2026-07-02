from datetime import date
from typing import Literal, Optional

from fastapi import APIRouter, Depends
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from database.models import User
from schemas.learning import (
    DailyTaskCreateRequest,
    DailyTaskStatusRequest,
    DailyTaskUpdateRequest,
    LearningGoalCreateRequest,
    LearningGoalStatusRequest,
    LearningGoalUpdateRequest,
)
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

DailyTaskStatus = Literal[
    "pending",
    "in_progress",
    "completed",
    "cancelled",
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

# 创建每日学习任务
@router.post("/daily-tasks")
async def create_daily_task(
    task_data: DailyTaskCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建属于当前用户学习目标的每日任务。"""

    result = await learning_service.create_daily_task(
        db=db,
        user_id=user.id,
        task_data=task_data,
    )
    return success_response(
        msg="创建每日学习任务成功",
        data=result,
    )


@router.get("/daily-tasks")
async def get_daily_tasks_page(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    task_date: Optional[date] = Query(default=None),
    goal_id: Optional[int] = Query(default=None, gt=0),
    status: Optional[DailyTaskStatus] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
):
    """按日期、目标和状态分页查询当前用户的每日任务。"""

    result = await learning_service.get_daily_tasks_page(
        db=db,
        user_id=user.id,
        page=page,
        page_size=page_size,
        task_date=task_date,
        goal_id=goal_id,
        task_status=status,
    )
    return success_response(
        msg="获取每日学习任务列表成功",
        data=result,
    )


@router.get("/daily-tasks/{task_id}")
async def get_daily_task_detail(
    task_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的每日学习任务详情。"""

    result = await learning_service.get_daily_task_by_id(
        db=db,
        user_id=user.id,
        task_id=task_id,
    )
    return success_response(
        msg="获取每日学习任务详情成功",
        data=result,
    )


@router.patch("/daily-tasks/{task_id}")
async def update_daily_task(
    task_id: int,
    update_data: DailyTaskUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """修改每日学习任务普通信息。"""

    result = await learning_service.update_daily_task(
        db=db,
        user_id=user.id,
        task_id=task_id,
        update_data=update_data,
    )
    return success_response(
        msg="修改每日学习任务成功",
        data=result,
    )


@router.patch("/daily-tasks/{task_id}/status")
async def update_daily_task_status(
    task_id: int,
    status_data: DailyTaskStatusRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """修改每日学习任务状态，并同步维护完成时间。"""

    result = await learning_service.update_daily_task_status(
        db=db,
        user_id=user.id,
        task_id=task_id,
        status_data=status_data,
    )
    return success_response(
        msg="修改每日学习任务状态成功",
        data=result,
    )
