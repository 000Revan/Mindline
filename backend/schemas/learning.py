from datetime import date, datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


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
    ]

class LearningGoalStatusResponse(BaseModel):
    goal: LearningGoalResponse
    paused_goal_count: int



# 学习目标列表响应
class LearningGoalsPageResponse(BaseModel):
    items: list[LearningGoalResponse]
    total: int
    page:int
    page_size:int
    total_pages:int


DailyTaskType = Literal["study", "review", "branch", "reflection"]
DailyTaskStatus = Literal["pending", "in_progress", "completed", "cancelled"]


class DailyTaskCreateRequest(BaseModel):
    """每日学习任务创建请求。"""

    goal_id: int = Field(..., gt=0, title="所属学习目标ID")
    title: str = Field(..., min_length=1, max_length=255, title="任务标题")
    description: Optional[str] = Field(None, max_length=5000, title="任务描述")
    task_type: DailyTaskType = Field(default="study", title="任务类型")
    estimated_time: Optional[int] = Field(None, ge=1, le=1440, title="预计耗时（分钟）")
    task_date: date = Field(..., title="计划执行日期")

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        """去除标题两侧空白，并拒绝纯空白标题。"""

        normalized = value.strip()
        if not normalized:
            raise ValueError("任务标题不能为空")
        return normalized

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: Optional[str]) -> Optional[str]:
        """将空白描述归一化为空值，避免保存无意义文本。"""

        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class DailyTaskUpdateRequest(BaseModel):
    """每日学习任务普通信息修改请求，不负责状态流转。"""

    goal_id: Optional[int] = Field(None, gt=0, title="所属学习目标ID")
    title: Optional[str] = Field(None, min_length=1, max_length=255, title="任务标题")
    description: Optional[str] = Field(None, max_length=5000, title="任务描述")
    task_type: Optional[DailyTaskType] = Field(None, title="任务类型")
    estimated_time: Optional[int] = Field(None, ge=1, le=1440, title="预计耗时（分钟）")
    task_date: Optional[date] = Field(None, title="计划执行日期")

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: Optional[str]) -> Optional[str]:
        """修改标题时拒绝纯空白内容。"""

        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("任务标题不能为空")
        return normalized

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: Optional[str]) -> Optional[str]:
        """将空白描述归一化为空值。"""

        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @model_validator(mode="after")
    def validate_required_fields_are_not_null(self):
        """非空数据库字段允许缺省，但不允许被显式更新为 null。"""

        required_fields = {"goal_id", "title", "task_type", "task_date"}
        invalid_fields = [
            field_name
            for field_name in required_fields
            if field_name in self.model_fields_set and getattr(self, field_name) is None
        ]
        if invalid_fields:
            raise ValueError(f"以下字段不能设置为空：{', '.join(sorted(invalid_fields))}")
        return self


class DailyTaskStatusRequest(BaseModel):
    """每日学习任务状态修改请求。"""

    status: DailyTaskStatus


class DailyTaskResponse(BaseModel):
    """每日学习任务响应。"""

    id: int
    goal_id: int
    title: str
    description: Optional[str]
    task_type: DailyTaskType
    status: DailyTaskStatus
    estimated_time: Optional[int]
    task_date: date
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DailyTasksPageResponse(BaseModel):
    """每日学习任务分页响应。"""

    items: list[DailyTaskResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
