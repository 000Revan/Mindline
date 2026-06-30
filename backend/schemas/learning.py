from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator


# 学习目标创建请求
class LearningGoalCreateRequest(BaseModel):
    title:str=Field(...,min_length=1,max_length=255,title="学习目标标题")
    description:Optional[str]=Field(None,min_length=1,max_length=255,title="学习目标描述")
    direction:str=Field(...,min_length=1,max_length=255,title="学习目标方向")
    priority:int=Field(default=3,ge=1,le=5,title="学习目标优先级")
    start_date:Optional[datetime]=Field(None,title="学习目标开始时间")
    target_date:Optional[datetime]=Field(None,title="学习目标完成时间")
    current_stage:Optional[str]=Field(None,min_length=1,max_length=255,title="当前学习阶段")
    current_principle:Optional[str]=Field(None,min_length=1,max_length=255,title="当前学习原则")

    @model_validator(mode="after")
    def validate_dates(self):
        if (
                self.start_date is not None
                and self.target_date is not None
                and self.start_date >= self.target_date
        ):
            raise ValueError("目标完成时间必须晚于开始时间")
        return self


# 学习目标响应
class LearningGoalResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    direction: str
    status:str
    priority: int
    start_date: Optional[datetime]
    target_date: Optional[datetime]
    current_stage: Optional[str]
    current_principle: Optional[str]

    model_config = ConfigDict(from_attributes=True)

#学习目标信息修改
class LearningGoalUpdateRequest(BaseModel):
    priority: Optional[int] = Field(None, ge=1, le=5, title="学习目标优先级")
    start_date: Optional[datetime] = Field(None, title="学习目标开始时间")
    target_date: Optional[datetime] = Field(None, title="学习目标完成时间")
    current_stage: Optional[str] = Field(None, min_length=1, max_length=255, title="当前学习阶段")
    current_principle: Optional[str] = Field(None, min_length=1, max_length=255, title="当前学习原则")


#学习目标状态修改
class LearningGoalStatusRequest(BaseModel):
    status: Literal[
        "active",
        "paused",
        "completed",
        "archived",
    ]

class LearningGoalStatusResponse(BaseModel):
    goal: LearningGoalResponse
    paused_goal_count: int


class LearningGoalActivateResponse(LearningGoalStatusResponse):
    """兼容原有激活接口的响应结构。"""

# 学习目标列表响应
class LearningGoalsPageResponse(BaseModel):
    items: list[LearningGoalResponse]
    total: int
    page:int
    page_size:int
    total_pages:int
